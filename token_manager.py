"""Token manager for caching and managing authentication tokens."""
import json
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger("documenter")


class TokenManager:
    """Manages authentication tokens with caching and expiration validation."""
    
    CACHE_FILE = 'input/.token_cache.json'
    
    def __init__(self, cache_file: Optional[str] = None):
        """Initialize token manager.
        
        Args:
            cache_file: Optional custom path for token cache file
        """
        self.cache_file = cache_file or self.CACHE_FILE
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict[str, Any]:
        """Load token cache from file.
        
        Returns:
            Cache dictionary
        """
        if not os.path.exists(self.cache_file):
            return {'tokens': {}}
        
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache = json.load(f)
                # Ensure 'tokens' key exists
                if 'tokens' not in cache:
                    cache['tokens'] = {}
                return cache
        except Exception as e:
            logger.warning(f"Error loading token cache: {e}")
            return {'tokens': {}}
    
    def _save_cache(self):
        """Save token cache to file."""
        try:
            # Ensure directory exists
            cache_dir = os.path.dirname(self.cache_file)
            if cache_dir and not os.path.exists(cache_dir):
                os.makedirs(cache_dir, exist_ok=True)
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Token cache saved to {self.cache_file}")
        except Exception as e:
            logger.error(f"Error saving token cache: {e}")
    
    def get_token(self, api_identifier: str) -> Optional[Dict[str, Any]]:
        """Get cached token for an API.
        
        Args:
            api_identifier: Unique identifier for the API (e.g., base URL or domain)
            
        Returns:
            Token dictionary or None if not found/expired
        """
        tokens = self.cache.get('tokens', {})
        token_data = tokens.get(api_identifier)
        
        if not token_data:
            logger.debug(f"No cached token found for {api_identifier}")
            return None
        
        # Check if token is expired
        if self._is_token_expired(token_data):
            logger.info(f"Cached token for {api_identifier} is expired")
            # Remove expired token
            del tokens[api_identifier]
            self._save_cache()
            return None
        
        logger.debug(f"Using cached token for {api_identifier}")
        return token_data
    
    def save_token(
        self,
        api_identifier: str,
        access_token: str,
        token_type: str = 'Bearer',
        expires_in: Optional[int] = None,
        expires_at: Optional[str] = None,
        refresh_token: Optional[str] = None,
        scope: Optional[str] = None,
        **extra_fields
    ):
        """Save token to cache.
        
        Args:
            api_identifier: Unique identifier for the API
            access_token: The access token
            token_type: Type of token (default: Bearer)
            expires_in: Token expiration time in seconds (from now)
            expires_at: Token expiration datetime (ISO format string)
            refresh_token: Optional refresh token
            scope: Optional token scope
            **extra_fields: Additional fields to store
        """
        if 'tokens' not in self.cache:
            self.cache['tokens'] = {}
        
        # Calculate expires_at if expires_in is provided
        if expires_in and not expires_at:
            expires_at = (datetime.utcnow() + timedelta(seconds=expires_in)).isoformat() + 'Z'
        elif not expires_at:
            # Default to 1 hour if no expiration info
            expires_at = (datetime.utcnow() + timedelta(hours=1)).isoformat() + 'Z'
            logger.warning(f"No expiration info for token, defaulting to 1 hour")
        
        token_data = {
            'access_token': access_token,
            'token_type': token_type,
            'expires_at': expires_at,
            'created_at': datetime.utcnow().isoformat() + 'Z',
            **extra_fields
        }
        
        if refresh_token:
            token_data['refresh_token'] = refresh_token
        if scope:
            token_data['scope'] = scope
        
        self.cache['tokens'][api_identifier] = token_data
        self._save_cache()
        
        logger.info(f"Token saved to cache for {api_identifier}")
    
    def _is_token_expired(self, token_data: Dict[str, Any]) -> bool:
        """Check if a token is expired.
        
        Args:
            token_data: Token data dictionary
            
        Returns:
            True if expired, False otherwise
        """
        expires_at = token_data.get('expires_at')
        if not expires_at:
            # If no expiration info, assume not expired (but warn)
            logger.warning("Token has no expiration info, assuming valid")
            return False
        
        try:
            # Parse ISO format datetime
            if expires_at.endswith('Z'):
                expires_at = expires_at[:-1] + '+00:00'
            expires_dt = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            
            # Add 5 minute buffer to avoid using tokens that expire soon
            buffer = timedelta(minutes=5)
            now = datetime.utcnow()
            
            return expires_dt <= (now + buffer)
        except Exception as e:
            logger.warning(f"Error parsing token expiration: {e}, assuming expired")
            return True
    
    def clear_token(self, api_identifier: str):
        """Clear cached token for an API.
        
        Args:
            api_identifier: Unique identifier for the API
        """
        tokens = self.cache.get('tokens', {})
        if api_identifier in tokens:
            del tokens[api_identifier]
            self._save_cache()
            logger.info(f"Token cleared for {api_identifier}")
    
    def clear_all_tokens(self):
        """Clear all cached tokens."""
        self.cache['tokens'] = {}
        self._save_cache()
        logger.info("All tokens cleared from cache")
    
    def get_access_token(self, api_identifier: str) -> Optional[str]:
        """Get access token string for an API.
        
        Args:
            api_identifier: Unique identifier for the API
            
        Returns:
            Access token string or None
        """
        token_data = self.get_token(api_identifier)
        if token_data:
            return token_data.get('access_token')
        return None
    
    def get_refresh_token(self, api_identifier: str) -> Optional[str]:
        """Get refresh token for an API.
        
        Args:
            api_identifier: Unique identifier for the API
            
        Returns:
            Refresh token string or None
        """
        tokens = self.cache.get('tokens', {})
        token_data = tokens.get(api_identifier)
        if token_data:
            return token_data.get('refresh_token')
        return None
    
    def update_token_from_response(
        self,
        api_identifier: str,
        response_data: Dict[str, Any]
    ):
        """Update token cache from OAuth token response.
        
        Args:
            api_identifier: Unique identifier for the API
            response_data: Response data from token endpoint
        """
        access_token = response_data.get('access_token') or response_data.get('token')
        if not access_token:
            logger.error("No access_token found in response data")
            return
        
        token_type = response_data.get('token_type', 'Bearer')
        expires_in = response_data.get('expires_in')
        expires_at = response_data.get('expires_at')
        refresh_token = response_data.get('refresh_token')
        scope = response_data.get('scope')
        
        # Extract any additional fields
        extra_fields = {
            k: v for k, v in response_data.items()
            if k not in ['access_token', 'token', 'token_type', 'expires_in', 
                        'expires_at', 'refresh_token', 'scope']
        }
        
        self.save_token(
            api_identifier=api_identifier,
            access_token=access_token,
            token_type=token_type,
            expires_in=expires_in,
            expires_at=expires_at,
            refresh_token=refresh_token,
            scope=scope,
            **extra_fields
        )

