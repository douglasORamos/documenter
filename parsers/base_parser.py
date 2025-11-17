"""Base parser class for all documentation parsers."""
from abc import ABC, abstractmethod
from typing import List
from models import DocumentationSource, EndpointInfo


class BaseParser(ABC):
    """Abstract base class for documentation parsers."""
    
    def __init__(self, file_path: str):
        """Initialize the parser with a file path.
        
        Args:
            file_path: Path to the documentation file
        """
        self.file_path = file_path
    
    @abstractmethod
    def parse(self) -> DocumentationSource:
        """Parse the documentation file.
        
        Returns:
            DocumentationSource object containing parsed information
        """
        pass
    
    @abstractmethod
    def extract_endpoints(self) -> List[EndpointInfo]:
        """Extract endpoint information from the documentation.
        
        Returns:
            List of EndpointInfo objects
        """
        pass

