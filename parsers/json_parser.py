"""JSON parser for structured API documentation."""
import json
import logging
from typing import List
from .base_parser import BaseParser
from models import DocumentationSource, EndpointInfo

logger = logging.getLogger("documenter")


class JSONParser(BaseParser):
    """Parser for generic JSON documentation files."""
    
    def parse(self) -> DocumentationSource:
        """Parse the JSON file.
        
        Returns:
            DocumentationSource object with extracted content
        """
        logger.info(f"Parsing JSON file: {self.file_path}")
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
            
            doc_source = DocumentationSource(
                file_path=self.file_path,
                file_type='json',
                content=content
            )
            
            # Extract endpoints from JSON structure
            doc_source.endpoints = self.extract_endpoints()
            
            logger.info(f"Extracted {len(doc_source.endpoints)} endpoints from JSON")
            return doc_source
            
        except Exception as e:
            logger.error(f"Error parsing JSON: {e}")
            raise
    
    def extract_endpoints(self) -> List[EndpointInfo]:
        """Extract endpoint information from JSON content.
        
        Returns:
            List of EndpointInfo objects
        """
        # Basic JSON parsing - will be enhanced by AI analysis
        # This handles generic JSON structures
        endpoints = []
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
            
            # Check if it's an OpenAPI/Swagger spec (will be handled by OpenAPIParser)
            if 'openapi' in content or 'swagger' in content:
                logger.info("Detected OpenAPI spec, use OpenAPIParser instead")
                return []
            
            # For generic JSON, we'll let AI analyze the structure
            logger.info("Generic JSON detected, will be analyzed by AI")
            
        except Exception as e:
            logger.error(f"Error extracting endpoints from JSON: {e}")
        
        return endpoints

