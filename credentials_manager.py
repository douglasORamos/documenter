"""Credentials manager for loading API authentication credentials."""
import json
import os
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger("documenter")


class CredentialsManager:
    """Manages API authentication credentials from multiple sources."""
    
    # Possible credential file names to search
    CREDENTIAL_FILE_NAMES = [
        'input/credentials.json',
        'credentials.json',
        '.credentials.json',
        'input/credentials.yaml',
        'credentials.yaml',
        '.credentials.yaml',
        'input/.env',
        '.env'
    ]
    
    def __init__(self):
        """Initialize credentials manager."""
        self.credentials = None
        self.auth_type = None
        self.source = None
    
    def load_credentials(self) -> Optional[Dict[str, Any]]:
        """Load credentials from available sources.
        
        Priority:
        1. input/credentials.json
        2. credentials.json (root)
        3. .credentials.json (root)
        4. input/credentials.yaml
        5. credentials.yaml (root)
        6. .credentials.yaml (root)
        7. input/.env
        8. .env (root)
        9. Environment variables
        10. Return None (will prompt user)
        
        Returns:
            Credentials dictionary or None
        """
        # Try multiple file locations
        for file_path in self.CREDENTIAL_FILE_NAMES:
            creds = self._load_from_file(file_path)
            if creds:
                self.source = file_path
                logger.info(f"Credentials loaded from: {self.source}")
                # Validate loaded credentials
                if self.validate_credentials(creds.get('credentials', {})):
                    return creds
                else:
                    logger.warning(f"Credentials from {file_path} failed validation, trying next source...")
        
        # Try environment variables
        creds = self._load_from_env()
        if creds:
            self.source = 'environment'
            logger.info(f"Credentials loaded from: {self.source}")
            if self.validate_credentials(creds.get('credentials', {})):
                return creds
        
        logger.info("No credentials found, will need interactive input")
        return None
    
    def _load_from_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Load credentials from file (JSON, YAML, or .env format).
        
        The file should contain raw credential data (username, password, token, etc.)
        The AI will determine how to use them based on the documentation.
        
        Args:
            file_path: Path to credentials file
            
        Returns:
            Credentials dictionary or None
        """
        if not os.path.exists(file_path):
            logger.debug(f"Credentials file not found: {file_path}")
            return None
        
        try:
            file_ext = Path(file_path).suffix.lower()
            
            # Load based on file extension
            if file_ext in ['.yaml', '.yml']:
                return self._load_yaml_file(file_path)
            elif file_path.endswith('.env') or file_ext == '':
                return self._load_env_file(file_path)
            else:
                # Default to JSON
                return self._load_json_file(file_path)
                
        except Exception as e:
            logger.error(f"Error loading credentials from file {file_path}: {e}")
            return None
    
    def _load_json_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Load credentials from JSON file.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Credentials dictionary or None
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle nested structure (auth_type + credentials) or flat structure
        if isinstance(data, dict) and 'credentials' in data:
            credentials = data['credentials']
            auth_type = data.get('auth_type')
        else:
            credentials = data
            auth_type = None
        
        # Filter out comments and instructions
        credentials = {
            k: v for k, v in credentials.items() 
            if not k.startswith('_') and v and v != ""
        }
        
        if not credentials:
            logger.warning(f"No valid credentials found in {file_path}")
            return None
        
        # Store raw credentials (AI will determine auth_type if not provided)
        self.credentials = credentials
        self.auth_type = auth_type
        
        return {
            'auth_type': auth_type,  # May be None, AI will determine
            'credentials': credentials
        }
    
    def _load_yaml_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Load credentials from YAML file.
        
        Args:
            file_path: Path to YAML file
            
        Returns:
            Credentials dictionary or None
        """
        try:
            import yaml
        except ImportError:
            logger.warning("PyYAML not installed, cannot load YAML files. Install with: pip install pyyaml")
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Handle nested or flat structure
        if isinstance(data, dict) and 'credentials' in data:
            credentials = data['credentials']
            auth_type = data.get('auth_type')
        else:
            credentials = data
            auth_type = None
        
        # Filter out comments and instructions
        credentials = {
            k: v for k, v in credentials.items() 
            if not k.startswith('_') and v and v != ""
        }
        
        if not credentials:
            logger.warning(f"No valid credentials found in {file_path}")
            return None
        
        self.credentials = credentials
        self.auth_type = auth_type
        
        return {
            'auth_type': auth_type,
            'credentials': credentials
        }
    
    def _load_env_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Load credentials from .env file.
        
        Args:
            file_path: Path to .env file
            
        Returns:
            Credentials dictionary or None
        """
        credentials = {}
        auth_type = None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # Parse KEY=VALUE
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    
                    # Map common env var names to credential keys
                    if key == 'API_AUTH_TYPE':
                        auth_type = value.lower()
                    elif key == 'API_TOKEN':
                        credentials['token'] = value
                    elif key == 'API_USERNAME':
                        credentials['username'] = value
                    elif key == 'API_PASSWORD':
                        credentials['password'] = value
                    elif key == 'API_KEY':
                        credentials['api_key'] = value
                    elif key == 'API_KEY_NAME':
                        credentials['header'] = value
                    elif key == 'CLIENT_ID':
                        credentials['client_id'] = value
                    elif key == 'CLIENT_SECRET':
                        credentials['client_secret'] = value
                    elif key == 'ACCESS_TOKEN':
                        credentials['access_token'] = value
                    else:
                        # Use key as-is if it matches credential field names
                        if key.lower() in ['token', 'username', 'password', 'api_key', 'client_id', 
                                          'client_secret', 'access_token', 'key', 'header']:
                            credentials[key.lower()] = value
        
        if not credentials:
            logger.warning(f"No valid credentials found in {file_path}")
            return None
        
        self.credentials = credentials
        self.auth_type = auth_type
        
        return {
            'auth_type': auth_type,
            'credentials': credentials
        }
    
    def _load_from_env(self) -> Optional[Dict[str, Any]]:
        """Load credentials from environment variables.
        
        Returns:
            Credentials dictionary or None
        """
        credentials = {}
        auth_type = os.getenv('API_AUTH_TYPE', '').lower()
        
        # Try to load all possible credential fields from env
        if os.getenv('API_TOKEN'):
            credentials['token'] = os.getenv('API_TOKEN')
        if os.getenv('API_USERNAME'):
            credentials['username'] = os.getenv('API_USERNAME')
        if os.getenv('API_PASSWORD'):
            credentials['password'] = os.getenv('API_PASSWORD')
        if os.getenv('API_KEY'):
            credentials['api_key'] = os.getenv('API_KEY')
            credentials['key'] = os.getenv('API_KEY')  # Also support 'key' field
        if os.getenv('API_KEY_NAME'):
            credentials['header'] = os.getenv('API_KEY_NAME')
        if os.getenv('CLIENT_ID'):
            credentials['client_id'] = os.getenv('CLIENT_ID')
        if os.getenv('CLIENT_SECRET'):
            credentials['client_secret'] = os.getenv('CLIENT_SECRET')
        if os.getenv('ACCESS_TOKEN'):
            credentials['access_token'] = os.getenv('ACCESS_TOKEN')
        
        # If no credentials found, return None
        if not credentials:
            return None
        
        # If auth_type not specified, try to infer
        if not auth_type:
            if 'token' in credentials:
                auth_type = 'bearer'
            elif 'api_key' in credentials or 'key' in credentials:
                auth_type = 'api_key'
            elif 'client_id' in credentials or 'access_token' in credentials:
                auth_type = 'oauth'
            elif 'username' in credentials and 'password' in credentials:
                auth_type = 'basic'
        
        self.auth_type = auth_type
        self.credentials = credentials
        
        return {
            'auth_type': auth_type,
            'credentials': credentials
        }
    
    def validate_credentials(self, credentials: Dict[str, Any]) -> bool:
        """Validate that credentials have required fields for their auth type.
        
        Args:
            credentials: Credentials dictionary to validate
            
        Returns:
            True if credentials are valid, False otherwise
        """
        if not credentials:
            logger.warning("Credentials dictionary is empty")
            return False
        
        # Check for at least one credential field
        valid_fields = ['token', 'username', 'password', 'api_key', 'key', 
                       'client_id', 'client_secret', 'access_token']
        has_any_field = any(field in credentials and credentials[field] 
                           for field in valid_fields)
        
        if not has_any_field:
            logger.warning("No valid credential fields found")
            return False
        
        # Validate specific auth type requirements if auth_type is known
        if self.auth_type:
            if self.auth_type == 'basic':
                if 'username' not in credentials or 'password' not in credentials:
                    logger.warning("Basic auth requires both username and password")
                    return False
            elif self.auth_type == 'oauth':
                # OAuth can work with access_token OR client_id+client_secret
                has_token = 'access_token' in credentials and credentials['access_token']
                has_client_creds = ('client_id' in credentials and credentials['client_id'] and
                                  'client_secret' in credentials and credentials['client_secret'])
                if not (has_token or has_client_creds):
                    logger.warning("OAuth requires either access_token or client_id+client_secret")
                    return False
        
        logger.debug("Credentials validation passed")
        return True
    
    def get_auth_type(self) -> str:
        """Get the authentication type.
        
        Returns:
            Auth type string
        """
        return self.auth_type or 'none'
    
    def get_credentials(self) -> Dict[str, Any]:
        """Get the credentials.
        
        Returns:
            Credentials dictionary
        """
        return self.credentials or {}
    
    def get_source(self) -> str:
        """Get the source of credentials.
        
        Returns:
            Source string
        """
        return self.source or 'none'

