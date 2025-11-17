"""Authentication method detector from documentation."""
import logging
from typing import Any, List, Dict, Optional
from models import EndpointInfo, DocumentationSource

logger = logging.getLogger("documenter")


class AuthDetector:
    """Detects authentication method from API documentation."""
    
    # Keywords for each auth type
    BEARER_KEYWORDS = [
        'bearer', 'bearer token', 'jwt', 'json web token',
        'authorization: bearer', 'token authentication'
    ]
    
    BASIC_KEYWORDS = [
        'basic auth', 'basic authentication', 'username and password',
        'user:password', 'authorization: basic', 'http basic'
    ]
    
    API_KEY_KEYWORDS = [
        'api key', 'api-key', 'x-api-key', 'key in header',
        'api_key', 'application key'
    ]
    
    OAUTH_KEYWORDS = [
        'oauth', 'oauth 2.0', 'oauth2', 'access token',
        'client_id', 'client_secret', 'authorization code'
    ]
    
    SOAP_KEYWORDS = [
        'ws-security', 'wsse', 'usernametoken', 'security header',
        'soap security', 'soap authentication'
    ]
    
    def detect_auth_method(
        self,
        doc_source: DocumentationSource,
        endpoints: List[EndpointInfo],
        available_credentials: Optional[Dict[str, Any]] = None
    ) -> str:
        """Detect authentication method from documentation.
        
        Args:
            doc_source: Documentation source
            endpoints: List of endpoints
            available_credentials: Available credential fields from credentials.json
            
        Returns:
            Auth method: 'bearer', 'basic', 'api_key', 'oauth', 'soap_security', 'none'
        """
        logger.info("Detecting authentication method from documentation...")
        
        # If we have credentials, log what's available
        if available_credentials:
            logger.debug(f"Available credential fields: {list(available_credentials.keys())}")
        
        # Convert content to string
        content_str = self._content_to_string(doc_source.content).lower()
        
        # Check headers in endpoints
        headers_text = self._extract_headers_text(endpoints).lower()
        combined_text = f"{content_str} {headers_text}"
        
        # Calculate scores
        scores = {
            'bearer': self._count_keywords(combined_text, self.BEARER_KEYWORDS),
            'basic': self._count_keywords(combined_text, self.BASIC_KEYWORDS),
            'api_key': self._count_keywords(combined_text, self.API_KEY_KEYWORDS),
            'oauth': self._count_keywords(combined_text, self.OAUTH_KEYWORDS),
            'soap_security': self._count_keywords(combined_text, self.SOAP_KEYWORDS)
        }
        
        # For SOAP APIs, prefer SOAP security if mentioned
        if doc_source.api_type == "SOAP" and scores['soap_security'] > 0:
            logger.info("Detected auth method: SOAP WS-Security")
            return 'soap_security'
        
        # Get highest score
        max_score = max(scores.values())
        
        if max_score == 0:
            logger.info("No authentication method detected")
            return 'none'
        
        # Find auth type with highest score
        for auth_type, score in scores.items():
            if score == max_score:
                logger.info(f"Detected auth method: {auth_type}")
                return auth_type
        
        return 'none'
    
    def _content_to_string(self, content: Any) -> str:
        """Convert content to string.
        
        Args:
            content: Content in any format
            
        Returns:
            String representation
        """
        if isinstance(content, str):
            return content
        elif isinstance(content, dict):
            import json
            return json.dumps(content)
        else:
            return str(content)
    
    def _extract_headers_text(self, endpoints: List[EndpointInfo]) -> str:
        """Extract text from headers in endpoints.
        
        Args:
            endpoints: List of endpoints
            
        Returns:
            Combined headers text
        """
        headers_list = []
        
        for endpoint in endpoints:
            for header_name, header_value in endpoint.headers.items():
                headers_list.append(f"{header_name}: {header_value}")
        
        return ' '.join(headers_list)
    
    def _count_keywords(self, text: str, keywords: List[str]) -> int:
        """Count keyword occurrences in text.
        
        Args:
            text: Text to search
            keywords: List of keywords
            
        Returns:
            Count of keyword matches
        """
        count = 0
        for keyword in keywords:
            if keyword in text:
                count += text.count(keyword)
        return count

