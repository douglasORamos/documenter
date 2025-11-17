"""Authentication endpoint detector from API documentation."""
import logging
import re
from typing import List, Dict, Any, Optional
from models import EndpointInfo, DocumentationSource, HTTPMethod

logger = logging.getLogger("documenter")


class AuthEndpointDetector:
    """Detects authentication endpoints from API documentation."""
    
    # Common authentication endpoint patterns
    AUTH_PATH_PATTERNS = [
        r'/auth',
        r'/login',
        r'/token',
        r'/oauth',
        r'/oauth/token',
        r'/oauth2/token',
        r'/authenticate',
        r'/session',
        r'/signin',
        r'/sign-in',
        r'/access',
        r'/accesstoken',
        r'/access-token',
    ]
    
    # Keywords in endpoint names/descriptions that indicate auth endpoints
    AUTH_KEYWORDS = [
        'login', 'auth', 'authenticate', 'token', 'oauth', 'session',
        'signin', 'sign-in', 'signin', 'access', 'credential', 'password',
        'bearer', 'jwt', 'authorization', 'grant', 'refresh'
    ]
    
    # Common request field names in auth endpoints
    AUTH_REQUEST_FIELDS = [
        'username', 'password', 'email', 'login', 'client_id', 'client_secret',
        'grant_type', 'code', 'refresh_token', 'scope', 'apikey', 'api_key'
    ]
    
    # Common response field names from auth endpoints
    AUTH_RESPONSE_FIELDS = [
        'access_token', 'token', 'accessToken', 'bearer_token', 'jwt',
        'refresh_token', 'refreshToken', 'expires_in', 'expires_at', 'expiresAt',
        'token_type', 'tokenType', 'scope', 'user_id', 'userId'
    ]
    
    def detect_auth_endpoint(
        self,
        endpoints: List[EndpointInfo],
        doc_source: Optional[DocumentationSource] = None
    ) -> Optional[EndpointInfo]:
        """Detect authentication endpoint from list of endpoints.
        
        Args:
            endpoints: List of endpoints to search
            doc_source: Optional documentation source for additional context
            
        Returns:
            EndpointInfo for auth endpoint or None if not found
        """
        logger.info("Detecting authentication endpoint...")
        
        # Score each endpoint
        scored_endpoints = []
        for endpoint in endpoints:
            score = self._score_endpoint(endpoint)
            if score > 0:
                scored_endpoints.append((score, endpoint))
        
        if not scored_endpoints:
            logger.info("No authentication endpoint detected")
            return None
        
        # Sort by score (highest first)
        scored_endpoints.sort(key=lambda x: x[0], reverse=True)
        
        best_match = scored_endpoints[0][1]
        best_score = scored_endpoints[0][0]
        
        logger.info(f"Detected auth endpoint: {best_match.method.value} {best_match.path} (score: {best_score})")
        return best_match
    
    def _score_endpoint(self, endpoint: EndpointInfo) -> int:
        """Score an endpoint for likelihood of being an auth endpoint.
        
        Args:
            endpoint: Endpoint to score
            
        Returns:
            Score (higher = more likely to be auth endpoint)
        """
        score = 0
        
        # Check path patterns
        if endpoint.path:
            path_lower = endpoint.path.lower()
            for pattern in self.AUTH_PATH_PATTERNS:
                if re.search(pattern, path_lower, re.IGNORECASE):
                    score += 10
                    break
        
        # Check endpoint name/description for auth keywords
        path_str = endpoint.path or ''
        name_desc = f"{path_str} {endpoint.description or ''}".lower()
        for keyword in self.AUTH_KEYWORDS:
            if keyword in name_desc:
                score += 5
        
        # Check if POST method (most auth endpoints are POST)
        if endpoint.method == HTTPMethod.POST:
            score += 3
        
        # Check request fields
        if endpoint.request_fields:
            auth_field_count = sum(
                1 for field in endpoint.request_fields
                if any(auth_field in field.name.lower() 
                      for auth_field in self.AUTH_REQUEST_FIELDS)
            )
            score += auth_field_count * 2
        
        # Check response fields
        if endpoint.response_fields:
            auth_response_count = sum(
                1 for field in endpoint.response_fields
                if any(auth_field in field.name.lower() 
                      for auth_field in self.AUTH_RESPONSE_FIELDS)
            )
            score += auth_response_count * 3  # Response fields are stronger indicators
        
        # Check examples for token responses
        if endpoint.examples:
            for example in endpoint.examples:
                body = example.get('body', {})
                if isinstance(body, dict):
                    if any(key in str(body).lower() for key in ['token', 'access_token', 'bearer']):
                        score += 5
        
        return score
    
    def extract_auth_info(self, endpoint: EndpointInfo) -> Dict[str, Any]:
        """Extract authentication information from an auth endpoint.
        
        Args:
            endpoint: Authentication endpoint
            
        Returns:
            Dictionary with auth information
        """
        path = endpoint.path or ''
        info = {
            'method': endpoint.method.value,
            'path': path,
            'base_path': path.split('?')[0] if path else '',  # Remove query params
            'request_fields': {},
            'response_token_field': None,
            'response_expires_field': None,
        }
        
        # Extract request fields
        if endpoint.request_fields:
            for field in endpoint.request_fields:
                field_name_lower = field.name.lower()
                if any(auth_field in field_name_lower for auth_field in self.AUTH_REQUEST_FIELDS):
                    info['request_fields'][field.name] = {
                        'required': field.required,
                        'type': field.field_type,
                        'description': field.description
                    }
        
        # Extract response token field
        if endpoint.response_fields:
            for field in endpoint.response_fields:
                field_name_lower = field.name.lower()
                if any(token_field in field_name_lower 
                      for token_field in ['access_token', 'token', 'bearer_token', 'jwt']):
                    info['response_token_field'] = field.name
                if any(exp_field in field_name_lower 
                      for exp_field in ['expires_in', 'expires_at', 'expiresat', 'expires']):
                    info['response_expires_field'] = field.name
        
        # Check examples for response structure
        if endpoint.examples:
            for example in endpoint.examples:
                body = example.get('body', {})
                if isinstance(body, dict):
                    # Look for token in response
                    for key in ['token', 'access_token', 'accessToken', 'data']:
                        if key in body:
                            if isinstance(body[key], dict) and 'token' in body[key]:
                                info['response_token_field'] = f"{key}.token"
                            elif key in ['token', 'access_token', 'accessToken']:
                                info['response_token_field'] = key
                            break
        
        return info
    
    def detect_token_endpoint_url(
        self,
        endpoints: List[EndpointInfo],
        base_url: str
    ) -> Optional[str]:
        """Detect and construct full token endpoint URL.
        
        Args:
            endpoints: List of endpoints
            base_url: Base URL of the API
            
        Returns:
            Full URL to token endpoint or None
        """
        auth_endpoint = self.detect_auth_endpoint(endpoints)
        if not auth_endpoint:
            return None
        
        # Clean path
        path = auth_endpoint.path or ''
        # Remove {{base_url}} or {{BASE_URL}} references
        if path:
            path = re.sub(r'\{\{base_url\}\}', '', path, flags=re.IGNORECASE)
            path = re.sub(r'\{\{[^}]+\}\}', '', path)  # Remove other variables
            path = path.strip('/')
        
        # Construct full URL
        base_url = base_url.rstrip('/')
        full_url = f"{base_url}/{path}" if path else base_url
        
        return full_url

