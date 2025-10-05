"""
Document parsing service for extracting text from Word documents
"""

import io
import re
from typing import List, Dict, Any, Optional
from docx import Document
import textract
from models.schemas import DocumentData, DocumentLine

class DocumentParser:
    """Service for parsing Word documents and extracting text with line information"""
    
    def __init__(self):
        self.supported_formats = ['.doc', '.docx']
    
    async def parse_document(self, file_content: bytes, filename: str) -> Optional[DocumentData]:
        """
        Parse a document and extract text with line-by-line information
        
        Args:
            file_content: Raw file content as bytes
            file_content: Original filename
            
        Returns:
            DocumentData object with parsed content
        """
        try:
            file_extension = filename.lower().split('.')[-1]
            
            if file_extension == 'docx':
                return await self._parse_docx(file_content, filename)
            elif file_extension == 'doc':
                return await self._parse_doc(file_content, filename)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
                
        except Exception as e:
            print(f"Error parsing document {filename}: {str(e)}")
            return None
    
    async def _parse_docx(self, file_content: bytes, filename: str) -> DocumentData:
        """Parse DOCX file using python-docx"""
        try:
            # Create file-like object from bytes
            doc_stream = io.BytesIO(file_content)
            doc = Document(doc_stream)
            
            lines = []
            line_number = 1
            total_sentences = 0
            
            # Extract text from paragraphs
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():  # Skip empty paragraphs
                    # Split paragraph into lines (handle manual line breaks)
                    paragraph_lines = paragraph.text.split('\n')
                    
                    for line_text in paragraph_lines:
                        if line_text.strip():  # Skip empty lines
                            # Split line into sentences
                            sentences = self._split_into_sentences(line_text.strip())
                            
                            lines.append(DocumentLine(
                                line_number=line_number,
                                content=line_text.strip(),
                                sentences=sentences
                            ))
                            
                            total_sentences += len(sentences)
                            line_number += 1
            
            # Extract metadata
            metadata = {
                'filename': filename,
                'format': 'docx',
                'paragraph_count': len(doc.paragraphs),
                'has_tables': len(doc.tables) > 0,
                'has_images': len(doc.inline_shapes) > 0
            }
            
            return DocumentData(
                filename=filename,
                lines=lines,
                total_lines=len(lines),
                total_sentences=total_sentences,
                metadata=metadata
            )
            
        except Exception as e:
            raise Exception(f"Failed to parse DOCX file: {str(e)}")
    
    async def _parse_doc(self, file_content: bytes, filename: str) -> DocumentData:
        """Parse DOC file using textract"""
        try:
            # Save content to temporary file for textract
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(suffix='.doc', delete=False) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
            
            try:
                # Extract text using textract
                text = textract.process(temp_file_path).decode('utf-8')
                
                # Split into lines
                lines = []
                line_number = 1
                total_sentences = 0
                
                for line_text in text.split('\n'):
                    if line_text.strip():  # Skip empty lines
                        # Split line into sentences
                        sentences = self._split_into_sentences(line_text.strip())
                        
                        lines.append(DocumentLine(
                            line_number=line_number,
                            content=line_text.strip(),
                            sentences=sentences
                        ))
                        
                        total_sentences += len(sentences)
                        line_number += 1
                
                # Extract metadata
                metadata = {
                    'filename': filename,
                    'format': 'doc',
                    'extraction_method': 'textract'
                }
                
                return DocumentData(
                    filename=filename,
                    lines=lines,
                    total_lines=len(lines),
                    total_sentences=total_sentences,
                    metadata=metadata
                )
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            raise Exception(f"Failed to parse DOC file: {str(e)}")
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences, handling common abbreviations and edge cases
        
        Args:
            text: Text to split into sentences
            
        Returns:
            List of sentences
        """
        if not text.strip():
            return []
        
        # Common abbreviations that shouldn't end sentences
        abbreviations = {
            'mr.', 'mrs.', 'ms.', 'dr.', 'prof.', 'sr.', 'jr.', 'inc.', 'ltd.', 'corp.',
            'co.', 'st.', 'ave.', 'blvd.', 'rd.', 'etc.', 'vs.', 'e.g.', 'i.e.', 'a.m.',
            'p.m.', 'u.s.', 'u.k.', 'ph.d.', 'm.d.', 'b.a.', 'm.a.', 'b.s.', 'm.s.'
        }
        
        # Pattern to match sentence endings, but not abbreviations
        sentence_pattern = r'(?<!\b(?:' + '|'.join(re.escape(abbr) for abbr in abbreviations) + r'))[.!?]+(?=\s+[A-Z]|\s*$)'
        
        # Split text into sentences
        sentences = re.split(sentence_pattern, text)
        
        # Clean up sentences and filter out empty ones
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                # Add back the punctuation if it was removed
                if not sentence.endswith(('.', '!', '?')):
                    # Find the original punctuation for this sentence
                    original_text = text
                    if sentence in original_text:
                        start_pos = original_text.find(sentence)
                        end_pos = start_pos + len(sentence)
                        if end_pos < len(original_text):
                            next_char = original_text[end_pos]
                            if next_char in '.!?':
                                sentence += next_char
                
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences
    
    def get_line_range_for_sentence(self, lines: List[DocumentLine], sentence_text: str) -> tuple:
        """
        Find the line range for a sentence that might span multiple lines
        
        Args:
            lines: List of document lines
            sentence_text: The sentence to find
            
        Returns:
            Tuple of (start_line, end_line) or (line_number, line_number) if single line
        """
        for i, line in enumerate(lines):
            if sentence_text in line.content:
                # Check if sentence spans multiple lines
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    # Simple heuristic: if sentence ends with lowercase and next line starts with lowercase,
                    # it might be a continuation
                    if (sentence_text[-1].islower() and 
                        next_line.content and 
                        next_line.content[0].islower()):
                        return (line.line_number, next_line.line_number)
                
                return (line.line_number, line.line_number)
        
        return (0, 0)
