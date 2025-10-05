"""
Enhanced LanguageTool server communication inspired by LanguageTool Sublime patterns
"""
import asyncio
import aiohttp
import logging
import subprocess
import time
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import language_tool_python
from .grammar_config import GrammarCheckerConfig, ServerType

logger = logging.getLogger(__name__)

@dataclass
class LanguageToolMatch:
    """Represents a match from LanguageTool"""
    offset: int
    error_length: int
    rule_id: str
    message: str
    replacements: List[str]
    context: str
    context_offset: int
    confidence: float = 0.0

class LanguageToolServerError(Exception):
    """Custom exception for LanguageTool server errors"""
    def __init__(self, message: str, error_type: str, fallback_available: bool = False):
        self.message = message
        self.error_type = error_type
        self.fallback_available = fallback_available
        super().__init__(message)

class LanguageToolServer:
    """Enhanced LanguageTool server communication with fallback mechanisms"""
    
    def __init__(self, config: GrammarCheckerConfig):
        self.config = config
        self.local_tool: Optional[language_tool_python.LanguageTool] = None
        self.remote_available = True
        self.local_server_process: Optional[subprocess.Popen] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self._initialized = False
    
    async def initialize(self) -> bool:
        """Initialize the LanguageTool server"""
        if self._initialized:
            return True
        
        try:
            # Initialize based on server type
            if self.config.server_type == ServerType.LOCAL:
                success = await self._initialize_local()
            elif self.config.server_type == ServerType.REMOTE:
                success = await self._initialize_remote()
            else:  # AUTO
                success = await self._initialize_auto()
            
            if success:
                self._initialized = True
                logger.info(f"LanguageTool server initialized successfully: {self.config.server_type}")
            else:
                logger.warning("Failed to initialize LanguageTool server")
            
            return success
            
        except Exception as e:
            logger.error(f"Error initializing LanguageTool server: {e}")
            return False
    
    async def _initialize_local(self) -> bool:
        """Initialize local LanguageTool server"""
        try:
            # Try to start local server if jar path is provided
            if self.config.local_jar_path:
                await self._start_local_server()
            
            # Initialize local tool
            self.local_tool = language_tool_python.LanguageTool(self.config.language)
            logger.info("Local LanguageTool initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize local LanguageTool: {e}")
            return False
    
    async def _initialize_remote(self) -> bool:
        """Initialize remote LanguageTool server"""
        try:
            # Test remote server availability
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.request_timeout)
            )
            
            # Test with a simple request
            test_data = {
                'text': 'This is a test.',
                'language': self.config.language
            }
            
            async with self.session.post(
                f"{self.config.remote_server_url}/check",
                json=test_data
            ) as response:
                if response.status == 200:
                    self.remote_available = True
                    logger.info("Remote LanguageTool server is available")
                    return True
                else:
                    logger.warning(f"Remote server returned status {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to initialize remote LanguageTool: {e}")
            self.remote_available = False
            return False
    
    async def _initialize_auto(self) -> bool:
        """Initialize with auto-detection (local first, then remote)"""
        # Try local first
        if await self._initialize_local():
            return True
        
        # Fallback to remote
        logger.info("Local server failed, trying remote server")
        return await self._initialize_remote()
    
    async def _start_local_server(self) -> bool:
        """Start local LanguageTool server"""
        if not self.config.local_jar_path:
            return False
        
        try:
            # Start the server process
            cmd = [
                'java', '-cp', self.config.local_jar_path,
                'org.languagetool.server.HTTPServer',
                '--port', '8081',
                '--allow-origin', '*'
            ]
            
            self.local_server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait a bit for server to start
            await asyncio.sleep(2)
            
            # Check if server is running
            if self.local_server_process.poll() is None:
                logger.info("Local LanguageTool server started successfully")
                return True
            else:
                logger.error("Local server failed to start")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start local server: {e}")
            return False
    
    async def check_text(self, text: str) -> List[LanguageToolMatch]:
        """Check text for grammar issues with retry and fallback logic"""
        if not self._initialized:
            await self.initialize()
        
        # Validate text length
        if len(text) > self.config.max_text_length:
            text = text[:self.config.max_text_length]
            logger.warning(f"Text truncated to {self.config.max_text_length} characters")
        
        # Try with retry logic
        for attempt in range(self.config.max_retries + 1):
            try:
                if self.config.server_type == ServerType.LOCAL and self.local_tool:
                    return await self._check_local(text)
                elif self.config.server_type == ServerType.REMOTE and self.remote_available:
                    return await self._check_remote(text)
                else:  # AUTO mode
                    return await self._check_auto(text)
                    
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                
                if attempt < self.config.max_retries:
                    await asyncio.sleep(self.config.retry_delay * (attempt + 1))
                else:
                    if self.config.fallback_on_error:
                        return await self._fallback_check(text)
                    else:
                        raise LanguageToolServerError(
                            f"All attempts failed: {e}",
                            "server_error",
                            fallback_available=False
                        )
        
        return []
    
    async def _check_local(self, text: str) -> List[LanguageToolMatch]:
        """Check text using local LanguageTool"""
        if not self.local_tool:
            raise LanguageToolServerError("Local tool not available", "local_unavailable")
        
        try:
            matches = await asyncio.to_thread(self.local_tool.check, text)
            return self._convert_matches(matches, text)
        except Exception as e:
            raise LanguageToolServerError(f"Local check failed: {e}", "local_error")
    
    async def _check_remote(self, text: str) -> List[LanguageToolMatch]:
        """Check text using remote LanguageTool server"""
        if not self.session or not self.remote_available:
            raise LanguageToolServerError("Remote server not available", "remote_unavailable")
        
        try:
            data = {
                'text': text,
                'language': self.config.language,
                'enabledOnly': 'false',
                'level': 'default'
            }
            
            async with self.session.post(
                f"{self.config.remote_server_url}/check",
                json=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return self._convert_remote_matches(result.get('matches', []), text)
                else:
                    raise LanguageToolServerError(
                        f"Remote server returned status {response.status}",
                        "remote_error"
                    )
                    
        except aiohttp.ClientError as e:
            raise LanguageToolServerError(f"Network error: {e}", "network_error")
        except Exception as e:
            raise LanguageToolServerError(f"Remote check failed: {e}", "remote_error")
    
    async def _check_auto(self, text: str) -> List[LanguageToolMatch]:
        """Check text with auto-detection (local first, then remote)"""
        # Try local first
        if self.local_tool:
            try:
                return await self._check_local(text)
            except LanguageToolServerError:
                logger.info("Local check failed, trying remote")
        
        # Fallback to remote
        if self.remote_available:
            return await self._check_remote(text)
        
        raise LanguageToolServerError("No server available", "no_server")
    
    async def _fallback_check(self, text: str) -> List[LanguageToolMatch]:
        """Fallback check when all servers fail"""
        logger.warning("Using fallback check - limited functionality")
        # Implement basic fallback logic here
        # For now, return empty list
        return []
    
    def _convert_matches(self, matches: List, text: str) -> List[LanguageToolMatch]:
        """Convert LanguageTool matches to our format"""
        converted = []
        
        for match in matches:
            # Get context around the match
            context_start = max(0, match.offset - self.config.context_window_size)
            context_end = min(len(text), match.offset + match.errorLength + self.config.context_window_size)
            context = text[context_start:context_end]
            context_offset = match.offset - context_start
            
            converted_match = LanguageToolMatch(
                offset=match.offset,
                error_length=match.errorLength,
                rule_id=match.ruleId,
                message=match.message,
                replacements=match.replacements or [],
                context=context,
                context_offset=context_offset,
                confidence=0.8  # Default confidence for local matches
            )
            converted.append(converted_match)
        
        return converted
    
    def _convert_remote_matches(self, matches: List[Dict], text: str) -> List[LanguageToolMatch]:
        """Convert remote server matches to our format"""
        converted = []
        
        for match in matches:
            # Get context around the match
            context_start = max(0, match['offset'] - self.config.context_window_size)
            context_end = min(len(text), match['offset'] + match['length'] + self.config.context_window_size)
            context = text[context_start:context_end]
            context_offset = match['offset'] - context_start
            
            converted_match = LanguageToolMatch(
                offset=match['offset'],
                error_length=match['length'],
                rule_id=match.get('rule', {}).get('id', 'unknown'),
                message=match.get('message', ''),
                replacements=[r['value'] for r in match.get('replacements', [])],
                context=context,
                context_offset=context_offset,
                confidence=match.get('rule', {}).get('confidence', 0.8)
            )
            converted.append(converted_match)
        
        return converted
    
    async def close(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()
        
        if self.local_server_process:
            self.local_server_process.terminate()
            self.local_server_process.wait()
        
        self._initialized = False
        logger.info("LanguageTool server closed")
    
    def __del__(self):
        """Cleanup on destruction"""
        if self.session and not self.session.closed:
            asyncio.create_task(self.session.close())
