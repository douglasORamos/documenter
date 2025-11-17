"""Authentication handlers for different auth types."""
import base64
import logging
import requests
from typing import Dict, Any, Optional
from requests import Session

logger = logging.getLogger("documenter")


class AuthHandler:
    """Base class for authentication handlers."""
    
    def __init__(self, credentials: Dict[str, Any]):
        """Initialize with credentials.
        
        Args:
            credentials: Credentials dictionary
        """
        self.credentials = credentials
    
    def apply(self, session: Session) -> Session:
        """Apply authentication to a requests session.
        
        Args:
            session: Requests session
            
        Returns:
            Session with auth applied
        """
        raise NotImplementedError


class BearerAuthHandler(AuthHandler):
    """Handler for Bearer Token authentication."""
    
    def apply(self, session: Session) -> Session:
        """Apply Bearer token to session.
        
        Args:
            session: Requests session
            
        Returns:
            Session with Bearer auth
        """
        token = self.credentials.get('token', '')
        if token:
            session.headers['Authorization'] = f'Bearer {token}'
            logger.debug("Applied Bearer token authentication")
        else:
            logger.warning("Bearer token not found in credentials")
        
        return session


class BasicAuthHandler(AuthHandler):
    """Handler for Basic Authentication."""
    
    def apply(self, session: Session) -> Session:
        """Apply Basic auth to session.
        
        Args:
            session: Requests session
            
        Returns:
            Session with Basic auth
        """
        username = self.credentials.get('username', '')
        password = self.credentials.get('password', '')
        
        if username and password:
            # Encode credentials
            credentials_str = f"{username}:{password}"
            encoded = base64.b64encode(credentials_str.encode()).decode()
            session.headers['Authorization'] = f'Basic {encoded}'
            logger.debug(f"Applied Basic authentication for user: {username}")
        else:
            logger.warning("Username or password not found in credentials")
        
        return session


class APIKeyHandler(AuthHandler):
    """Handler for API Key authentication."""
    
    def apply(self, session: Session) -> Session:
        """Apply API Key to session.
        
        Args:
            session: Requests session
            
        Returns:
            Session with API Key
        """
        key = self.credentials.get('key', '')
        header_name = self.credentials.get('header', 'X-API-Key')
        location = self.credentials.get('location', 'header')
        
        if key:
            if location == 'header':
                session.headers[header_name] = key
                logger.debug(f"Applied API Key in header: {header_name}")
            else:
                logger.info(f"API Key in query will be added per-request")
        else:
            logger.warning("API Key not found in credentials")
        
        return session


class SOAPSecurityHandler(AuthHandler):
    """Handler for SOAP WS-Security."""
    
    def apply(self, session: Session) -> Session:
        """Apply basic session setup for SOAP.
        
        Note: SOAP security is applied in the XML body, not headers.
        
        Args:
            session: Requests session
            
        Returns:
            Session (SOAP auth is in XML body)
        """
        username = self.credentials.get('username', '')
        password = self.credentials.get('password', '')
        
        if username and password:
            # Store credentials for SOAP envelope generation
            session.soap_username = username
            session.soap_password = password
            logger.debug(f"Stored SOAP credentials for user: {username}")
        else:
            logger.warning("SOAP username or password not found")
        
        return session
    
    def generate_security_header(self) -> str:
        """Generate WS-Security header XML.
        
        Returns:
            WS-Security XML string
        """
        username = self.credentials.get('username', '')
        password = self.credentials.get('password', '')
        
        return f'''<soap:Header>
    <wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
      <wsse:UsernameToken>
        <wsse:Username>{username}</wsse:Username>
        <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">{password}</wsse:Password>
      </wsse:UsernameToken>
    </wsse:Security>
  </soap:Header>'''


class OAuthHandler(AuthHandler):
    """Handler for OAuth 2.0 authentication with token generation."""
    
    def __init__(self, credentials: Dict[str, Any], token_manager=None, auth_endpoint_info=None):
        """Initialize OAuth handler.
        
        Args:
            credentials: Credentials dictionary
            token_manager: Optional TokenManager instance for caching
            auth_endpoint_info: Optional auth endpoint information
        """
        super().__init__(credentials)
        self.token_manager = token_manager
        self.auth_endpoint_info = auth_endpoint_info
        self._generated_token = None
    
    def apply(self, session: Session) -> Session:
        """Apply OAuth token to session.
        
        Args:
            session: Requests session
            
        Returns:
            Session with OAuth
        """
        access_token = self._get_access_token()
        
        if access_token:
            session.headers['Authorization'] = f'Bearer {access_token}'
            logger.debug("Applied OAuth 2.0 access token")
        else:
            logger.warning("OAuth access_token not available")
        
        return session
    
    def _get_access_token(self) -> Optional[str]:
        """Get access token from credentials, cache, or generate new one.
        
        Returns:
            Access token string or None
        """
        # First, try direct access_token from credentials
        access_token = self.credentials.get('access_token', '')
        if access_token:
            return access_token
        
        # Try to get from cache if token_manager is available
        if self.token_manager and self.auth_endpoint_info:
            api_identifier = self._get_api_identifier()
            cached_token = self.token_manager.get_access_token(api_identifier)
            if cached_token:
                logger.debug("Using cached OAuth token")
                return cached_token
        
        # Try to generate token if we have client credentials
        if self._can_generate_token():
            generated_token = self.generate_token()
            if generated_token:
                return generated_token
        
        return None
    
    def _get_api_identifier(self) -> str:
        """Get API identifier for token cache.
        
        Returns:
            API identifier string
        """
        if self.auth_endpoint_info:
            # Use base URL from auth endpoint if available
            base_url = getattr(self.auth_endpoint_info, 'base_url', None)
            if base_url:
                # Extract domain from URL
                from urllib.parse import urlparse
                try:
                    parsed = urlparse(base_url)
                    return parsed.netloc or base_url
                except Exception:
                    return base_url
        
        # Fallback to a generic identifier
        return 'default_api'
    
    def _can_generate_token(self) -> bool:
        """Check if we can generate a token.
        
        Returns:
            True if we have credentials to generate token
        """
        has_client_creds = (
            'client_id' in self.credentials and self.credentials['client_id'] and
            'client_secret' in self.credentials and self.credentials['client_secret']
        )
        
        has_username_password = (
            'username' in self.credentials and self.credentials['username'] and
            'password' in self.credentials and self.credentials['password']
        )
        
        return has_client_creds or has_username_password
    
    def generate_token(
        self,
        token_url: Optional[str] = None,
        grant_type: Optional[str] = None
    ) -> Optional[str]:
        """Generate OAuth token from credentials.
        
        Args:
            token_url: Optional token endpoint URL (if not provided, will try to detect)
            grant_type: Optional grant type (client_credentials, password, etc.)
            
        Returns:
            Access token string or None if generation failed
        """
        if not self._can_generate_token():
            logger.warning("Cannot generate token: missing client_id/client_secret or username/password")
            return None
        
        # Determine grant type
        if not grant_type:
            if 'client_id' in self.credentials and 'client_secret' in self.credentials:
                # Try password grant if username/password available, otherwise client_credentials
                if 'username' in self.credentials and 'password' in self.credentials:
                    grant_type = 'password'
                else:
                    grant_type = 'client_credentials'
            else:
                grant_type = 'password'
        
        # Get token URL
        if not token_url and self.auth_endpoint_info:
            token_url = getattr(self.auth_endpoint_info, 'token_url', None)
        
        if not token_url:
            logger.warning("Token URL not provided and cannot be detected")
            return None
        
        logger.info(f"Generating OAuth token using {grant_type} grant type")
        
        try:
            # Prepare request data based on grant type
            data = {'grant_type': grant_type}
            
            if grant_type == 'client_credentials':
                data['client_id'] = self.credentials['client_id']
                data['client_secret'] = self.credentials['client_secret']
            elif grant_type == 'password':
                data['username'] = self.credentials.get('username', '')
                data['password'] = self.credentials.get('password', '')
                # Some APIs require client_id/secret even for password grant
                if 'client_id' in self.credentials:
                    data['client_id'] = self.credentials['client_id']
                if 'client_secret' in self.credentials:
                    data['client_secret'] = self.credentials['client_secret']
            
            # Add scope if provided
            if 'scope' in self.credentials:
                data['scope'] = self.credentials['scope']
            
            # Make token request
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            response = requests.post(token_url, data=data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                token_data = response.json()
                
                # Extract access token (handle different response formats)
                access_token = (
                    token_data.get('access_token') or
                    token_data.get('token') or
                    token_data.get('data', {}).get('token') or
                    token_data.get('data', {}).get('access_token')
                )
                
                if access_token:
                    # Save to cache if token_manager is available
                    if self.token_manager:
                        api_identifier = self._get_api_identifier()
                        self.token_manager.update_token_from_response(api_identifier, token_data)
                    
                    self._generated_token = access_token
                    logger.info("OAuth token generated successfully")
                    return access_token
                else:
                    logger.error(f"Token response missing access_token: {token_data}")
            else:
                logger.error(f"Token generation failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Error generating OAuth token: {e}")
        
        return None


def get_auth_handler(
    auth_type: str,
    credentials: Dict[str, Any],
    token_manager=None,
    auth_endpoint_info=None
) -> AuthHandler:
    """Get appropriate auth handler for auth type.
    
    Args:
        auth_type: Type of authentication (can be None if AI should determine)
        credentials: Generic credentials dictionary
        token_manager: Optional TokenManager instance for OAuth token caching
        auth_endpoint_info: Optional auth endpoint information for OAuth
        
    Returns:
        AuthHandler instance
    """
    # If no auth_type specified, try to infer from available credentials
    if not auth_type or auth_type == 'none':
        auth_type = _infer_auth_type(credentials)
    
    auth_type_lower = auth_type.lower() if auth_type else 'none'
    
    if auth_type_lower == 'bearer':
        return BearerAuthHandler(credentials)
    elif auth_type_lower == 'basic':
        return BasicAuthHandler(credentials)
    elif auth_type_lower == 'api_key':
        return APIKeyHandler(credentials)
    elif auth_type_lower == 'soap_security':
        return SOAPSecurityHandler(credentials)
    elif auth_type_lower == 'oauth':
        return OAuthHandler(credentials, token_manager=token_manager, auth_endpoint_info=auth_endpoint_info)
    else:
        logger.warning(f"No valid auth type determined, using no auth")
        return AuthHandler(credentials)  # No-op handler


def _infer_auth_type(credentials: Dict[str, Any]) -> str:
    """Infer auth type from available credential fields.
    
    Args:
        credentials: Generic credentials dictionary
        
    Returns:
        Inferred auth type
    """
    # Check what fields are available
    has_token = 'token' in credentials and credentials['token']
    has_username_password = 'username' in credentials and 'password' in credentials
    has_api_key = 'api_key' in credentials and credentials['api_key']
    has_oauth = 'access_token' in credentials or 'client_id' in credentials
    
    # Infer based on available fields
    if has_token:
        logger.info("Inferred auth type: bearer (has token)")
        return 'bearer'
    elif has_api_key:
        logger.info("Inferred auth type: api_key (has api_key)")
        return 'api_key'
    elif has_oauth:
        logger.info("Inferred auth type: oauth (has oauth fields)")
        return 'oauth'
    elif has_username_password:
        logger.info("Inferred auth type: basic (has username/password)")
        return 'basic'
    else:
        logger.warning("Could not infer auth type from credentials")
        return 'none'

