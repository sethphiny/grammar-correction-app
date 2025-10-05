import os
import re
from typing import List
from docx import Document
import textract
from models.schemas import DocumentLine

class DocumentParser:
    """Handles parsing of .doc and .docx files"""
    
    def __init__(self):
        self.sentence_endings = re.compile(r'[.!?]+')
        self.abbreviations = re.compile(r'\b(Mr|Mrs|Ms|Dr|Prof|Inc|Ltd|Corp|Co|etc|vs|e\.g|i\.e)\b\.', re.IGNORECASE)
        
    async def parse_document(self, file_path: str) -> List[DocumentLine]:
        """Parse document and extract lines with sentences"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.docx':
                return await self._parse_docx(file_path)
            elif file_ext == '.doc':
                return await self._parse_doc(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
                
        except Exception as e:
            raise Exception(f"Failed to parse document: {str(e)}")
    
    async def _parse_docx(self, file_path: str) -> List[DocumentLine]:
        """Parse .docx file with improved structure preservation"""
        try:
            doc = Document(file_path)
            lines = []
            
            for para in doc.paragraphs:
                # Check if this is a table of contents or special element
                if self._is_toc_or_special_element(para):
                    # Keep TOC entries separate - don't merge with body text
                    content = para.text.strip()
                    if content:
                        sentences = self._split_into_sentences_with_structure(content)
                        lines.append(DocumentLine(
                            line_number=len(lines) + 1,
                            content=content,
                            sentences=sentences
                        ))
                    continue
                
                # Preserve paragraph structure - treat each paragraph as a separate line/block
                if para.text.strip():  # Skip completely empty paragraphs
                    content = para.text.strip()
                    
                    # Handle manual line breaks (Shift+Enter) within paragraphs
                    # Replace manual line breaks with \n markers for preservation
                    content = self._preserve_line_breaks(content, para)
                    
                    # For grammar checking, treat each line break as a separate sentence
                    # This ensures we don't merge multiple lines into one grammar check
                    if '\n' in content:
                        # Split by line breaks and create separate DocumentLine for each
                        line_parts = content.split('\n')
                        for part in line_parts:
                            if part.strip():
                                sentences = [part.strip()]  # Each line is one sentence
                                lines.append(DocumentLine(
                                    line_number=len(lines) + 1,
                                    content=part.strip(),
                                    sentences=sentences
                                ))
                    else:
                        # Single line paragraph - split normally
                        sentences = self._split_into_sentences_with_structure(content)
                        lines.append(DocumentLine(
                            line_number=len(lines) + 1,
                            content=content,
                            sentences=sentences
                        ))
                else:
                    # Preserve empty paragraphs as empty lines to maintain structure
                    lines.append(DocumentLine(
                        line_number=len(lines) + 1,
                        content="",
                        sentences=[]
                    ))
            
            return lines
            
        except Exception as e:
            raise Exception(f"Failed to parse DOCX file: {str(e)}")
    
    async def _parse_doc(self, file_path: str) -> List[DocumentLine]:
        """Parse .doc file using textract with improved structure preservation"""
        try:
            # Extract text from .doc file
            text = textract.process(file_path).decode('utf-8')
            
            # Split into lines while preserving structure
            raw_lines = text.split('\n')
            lines = []
            
            for line_content in raw_lines:
                # Preserve whitespace and structure - don't collapse everything
                if line_content.strip() or line_content == '':  # Include empty lines to preserve structure
                    # Clean up excessive whitespace but preserve line breaks
                    cleaned_content = ' '.join(line_content.split()) if line_content.strip() else ''
                    
                    # Split into sentences while preserving structure
                    sentences = self._split_into_sentences_with_structure(cleaned_content)
                    
                    lines.append(DocumentLine(
                        line_number=len(lines) + 1,
                        content=cleaned_content,
                        sentences=sentences
                    ))
            
            return lines
            
        except Exception as e:
            raise Exception(f"Failed to parse DOC file: {str(e)}")
    
    def _is_toc_or_special_element(self, paragraph) -> bool:
        """Check if paragraph is a table of contents or special element that should be kept separate"""
        text = paragraph.text.strip().lower()
        
        # Check for TOC indicators
        toc_indicators = [
            'table of contents',
            'contents',
            'index',
            'chapter',
            'section',
            'page',
            '......',  # Dotted lines in TOC
            '....',    # Dotted lines in TOC
            '...',     # Dotted lines in TOC
        ]
        
        # Check if text contains TOC patterns
        for indicator in toc_indicators:
            if indicator in text:
                return True
        
        # Check for page number patterns (common in TOC)
        if re.search(r'\d+\s*$', text):  # Ends with page number
            return True
        
        # Check for heading patterns that might be TOC entries
        if re.match(r'^\d+\.?\s+', text):  # Starts with number
            return True
        
        return False
    
    def _preserve_line_breaks(self, content: str, paragraph) -> str:
        """Preserve manual line breaks (Shift+Enter) within paragraphs"""
        # In python-docx, manual line breaks are represented as '\n' in the text
        # We need to preserve these while cleaning up other whitespace
        lines = content.split('\n')
        preserved_lines = []
        
        for line in lines:
            # Preserve the line but clean up excessive whitespace
            cleaned_line = ' '.join(line.split())  # Normalize whitespace
            preserved_lines.append(cleaned_line)
        
        # Join with \n to preserve manual line breaks
        return '\n'.join(preserved_lines)
    
    def _split_into_sentences_with_structure(self, text: str) -> List[str]:
        """Split text into sentences while preserving line break structure"""
        if not text.strip():
            return []
        
        # If text contains manual line breaks, treat each line as a separate sentence
        # This ensures we don't merge multiple lines into one sentence
        if '\n' in text:
            lines = text.split('\n')
            sentences = []
            
            for line in lines:
                if line.strip():
                    # Each line should be treated as a separate unit for grammar checking
                    # Don't split lines into multiple sentences - treat the whole line as one sentence
                    sentences.append(line.strip())
            
            return sentences
        else:
            # Use regular sentence splitting for single-line text
            return self._split_into_sentences(text)
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences, handling abbreviations and special cases"""
        if not text.strip():
            return []
        
        # Handle abbreviations by temporarily replacing them
        text = self.abbreviations.sub(r'\1<ABBREV>', text)
        
        # Split on sentence endings
        sentences = re.split(r'[.!?]+', text)
        
        # Clean up and filter empty sentences
        result = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                # Restore abbreviations
                sentence = sentence.replace('<ABBREV>', '.')
                result.append(sentence)
        
        return result
    
    def _handle_multi_line_sentences(self, lines: List[DocumentLine]) -> List[DocumentLine]:
        """Handle sentences that span multiple lines"""
        processed_lines = []
        current_sentence = ""
        sentence_start_line = 1
        
        for i, line in enumerate(lines):
            sentences = line.sentences
            
            # If we have a continuation from previous line
            if current_sentence:
                if sentences:
                    # Combine with first sentence of current line
                    current_sentence += " " + sentences[0]
                    sentences = sentences[1:]
                    
                    if not sentences:  # No more sentences in this line
                        # Create a combined line entry
                        processed_lines.append(DocumentLine(
                            line_number=f"{sentence_start_line}-{line.line_number}",
                            content=current_sentence,
                            sentences=[current_sentence]
                        ))
                        current_sentence = ""
                        continue
            
            # Process remaining sentences in current line
            for j, sentence in enumerate(sentences):
                if j == 0 and current_sentence:
                    # This is a continuation
                    current_sentence += " " + sentence
                    processed_lines.append(DocumentLine(
                        line_number=f"{sentence_start_line}-{line.line_number}",
                        content=current_sentence,
                        sentences=[current_sentence]
                    ))
                    current_sentence = ""
                else:
                    # Check if sentence ends properly
                    if sentence.endswith(('.', '!', '?')):
                        processed_lines.append(DocumentLine(
                            line_number=line.line_number,
                            content=sentence,
                            sentences=[sentence]
                        ))
                    else:
                        # This sentence continues to next line
                        current_sentence = sentence
                        sentence_start_line = line.line_number
        
        return processed_lines
