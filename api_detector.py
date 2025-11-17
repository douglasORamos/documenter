"""API type detector module - identifies REST, SOAP, GraphQL, etc."""
import logging
from typing import List, Any
from models import EndpointInfo

logger = logging.getLogger("documenter")


class APIDetector:
    """Detects the type of API from documentation and endpoints."""
    
    # SOAP indicators
    SOAP_KEYWORDS = [
        'soap', 'wsdl', 'xmlns', 'soap:envelope', 'soap:body',
        'soapaction', 'webservice', 'soap 1.1', 'soap 1.2',
        'soap-env', 'soap-enc', '<envelope', '</envelope>',
        'xml schema', 'xsd:', 'targetnamespace'
    ]
    
    # REST indicators
    REST_KEYWORDS = [
        'rest', 'restful', 'json', 'application/json',
        'resource', 'get ', 'post ', 'put ', 'delete ',
        'http methods', 'rest api'
    ]
    
    # GraphQL indicators
    GRAPHQL_KEYWORDS = [
        'graphql', 'query', 'mutation', 'subscription',
        'schema', 'type query', 'type mutation'
    ]
    
    def detect_api_type(
        self, 
        endpoints: List[EndpointInfo], 
        content: Any
    ) -> str:
        """Detect the type of API.
        
        Args:
            endpoints: List of extracted endpoints
            content: Raw documentation content
            
        Returns:
            API type: "SOAP", "REST", "GRAPHQL", or "UNKNOWN"
        """
        logger.info("Detecting API type...")
        
        # Convert content to string for analysis
        content_str = self._content_to_string(content).lower()
        
        # Calculate scores for each API type
        soap_score = self._calculate_soap_score(endpoints, content_str)
        rest_score = self._calculate_rest_score(endpoints, content_str)
        graphql_score = self._calculate_graphql_score(content_str)
        
        logger.debug(f"API type scores - SOAP: {soap_score}, REST: {rest_score}, GraphQL: {graphql_score}")
        
        # Determine API type based on highest score
        max_score = max(soap_score, rest_score, graphql_score)
        
        if max_score == 0:
            logger.warning("Could not determine API type, defaulting to REST")
            return "UNKNOWN"
        
        if soap_score == max_score and soap_score > 0:
            logger.info("Detected API type: SOAP")
            return "SOAP"
        elif graphql_score == max_score:
            logger.info("Detected API type: GraphQL")
            return "GRAPHQL"
        else:
            logger.info("Detected API type: REST")
            return "REST"
    
    def _calculate_soap_score(
        self, 
        endpoints: List[EndpointInfo], 
        content: str
    ) -> int:
        """Calculate SOAP likelihood score.
        
        Args:
            endpoints: List of endpoints
            content: Documentation content
            
        Returns:
            SOAP score (higher = more likely SOAP)
        """
        score = 0
        
        # Check for WSDL in URLs
        for endpoint in endpoints:
            if endpoint.path and ('?wsdl' in endpoint.path.lower() or '.wsdl' in endpoint.path.lower()):
                score += 10
                logger.debug("Found WSDL in endpoint path")
            
            # SOAP typically uses POST method
            if endpoint.method.value == 'POST' and len(endpoints) > 0:
                score += 1
        
        # Check for SOAP keywords in content
        for keyword in self.SOAP_KEYWORDS:
            if keyword in content:
                score += 2
                logger.debug(f"Found SOAP keyword: {keyword}")
        
        # Check for XML namespaces pattern
        if 'xmlns:' in content or 'namespace' in content:
            score += 3
        
        # Check for SOAP-specific structures
        if '<soap:' in content or '<s:' in content or '<soapenv:' in content:
            score += 5
        
        # If only one endpoint with WSDL, very likely SOAP
        if len(endpoints) == 1 and endpoints[0].path and '?wsdl' in endpoints[0].path.lower():
            score += 15
        
        return score
    
    def _calculate_rest_score(
        self, 
        endpoints: List[EndpointInfo], 
        content: str
    ) -> int:
        """Calculate REST likelihood score.
        
        Args:
            endpoints: List of endpoints
            content: Documentation content
            
        Returns:
            REST score (higher = more likely REST)
        """
        score = 0
        
        # Check for RESTful HTTP methods
        methods = set()
        for endpoint in endpoints:
            methods.add(endpoint.method.value)
        
        # REST typically uses multiple HTTP methods
        if len(methods) > 2:
            score += 5
        
        # Check for typical REST paths (resources)
        for endpoint in endpoints:
            path = endpoint.path.lower() if endpoint.path else ''
            # REST paths typically have resource names without .wsdl
            if '/' in path and '?wsdl' not in path and '.wsdl' not in path:
                score += 2
            
            # REST often has path parameters
            if '{' in path and '}' in path:
                score += 2
        
        # Check for REST keywords in content
        for keyword in self.REST_KEYWORDS:
            if keyword in content:
                score += 1
        
        # Check for JSON mentions
        if 'json' in content or 'application/json' in content:
            score += 5
        
        return score
    
    def _calculate_graphql_score(self, content: str) -> int:
        """Calculate GraphQL likelihood score.
        
        Args:
            content: Documentation content
            
        Returns:
            GraphQL score (higher = more likely GraphQL)
        """
        score = 0
        
        # Check for GraphQL keywords
        for keyword in self.GRAPHQL_KEYWORDS:
            if keyword in content:
                score += 3
        
        # GraphQL-specific patterns
        if 'type query' in content or 'type mutation' in content:
            score += 10
        
        if 'schema {' in content:
            score += 5
        
        return score
    
    def _content_to_string(self, content: Any) -> str:
        """Convert content to string for analysis.
        
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
        elif isinstance(content, list):
            return ' '.join(str(item) for item in content)
        else:
            return str(content)
    
    def is_soap(self, endpoints: List[EndpointInfo], content: Any) -> bool:
        """Quick check if API is SOAP.
        
        Args:
            endpoints: List of endpoints
            content: Documentation content
            
        Returns:
            True if SOAP, False otherwise
        """
        return self.detect_api_type(endpoints, content) == "SOAP"
    
    def is_rest(self, endpoints: List[EndpointInfo], content: Any) -> bool:
        """Quick check if API is REST.
        
        Args:
            endpoints: List of endpoints
            content: Documentation content
            
        Returns:
            True if REST, False otherwise
        """
        api_type = self.detect_api_type(endpoints, content)
        return api_type in ["REST", "UNKNOWN"]  # Default to REST if unknown

