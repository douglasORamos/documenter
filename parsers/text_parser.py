"""Text parser for plain text and markdown documentation."""
import logging
from typing import List
from .base_parser import BaseParser
from models import DocumentationSource, EndpointInfo

logger = logging.getLogger("documenter")


class TextParser(BaseParser):
    """Parser for plain text and markdown documentation files."""
    
    def parse(self) -> DocumentationSource:
        """Parse the text file.
        
        Returns:
            DocumentationSource object with extracted content
        """
        logger.info(f"Parsing text file: {self.file_path}")
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            doc_source = DocumentationSource(
                file_path=self.file_path,
                file_type='txt',
                content=content
            )
            
            # Extract endpoints from text
            doc_source.endpoints = self.extract_endpoints()
            
            logger.info(f"Extracted {len(doc_source.endpoints)} endpoints from text file")
            return doc_source
            
        except Exception as e:
            logger.error(f"Error parsing text file: {e}")
            raise
    
    def extract_endpoints(self) -> List[EndpointInfo]:
        """Extract endpoint information from text content.
        
        Note: Text endpoint extraction is basic and will be enhanced by AI.
        
        Returns:
            List of EndpointInfo objects (may be empty, to be enriched by AI)
        """
        # Text endpoint extraction is complex and will be handled primarily by AI
        # This returns an empty list that will be populated during AI analysis
        return []

