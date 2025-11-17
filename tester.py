"""API tester module for making real API requests and discovering patterns."""
import time
import logging
import json
import re
from typing import List, Dict, Any, Optional
import requests
from config import Config
from models import EndpointInfo, TestResult, HTTPMethod, FieldInfo

logger = logging.getLogger("documenter")


class APITester:
    """Class for testing API endpoints with various payloads."""
    
    def __init__(
        self, 
        base_url: str, 
        default_headers: Optional[Dict[str, str]] = None,
        auth_handler: Optional[Any] = None,
        operation_classifier: Optional[Any] = None,
        enable_production_ops: Optional[bool] = None,
        api_logger: Optional[Any] = None
    ):
        """Initialize the API tester.
        
        Args:
            base_url: Base URL of the API to test
            default_headers: Default headers to include in all requests
            auth_handler: Authentication handler instance
            operation_classifier: Operation classifier for risk assessment
            enable_production_ops: Whether to test production operations (overrides config)
            api_logger: Optional API logger for request/response logging
        """
        self.base_url = base_url.rstrip('/')
        self.default_headers = default_headers or {}
        self.auth_handler = auth_handler
        self.classifier = operation_classifier
        self.enable_production_ops = enable_production_ops if enable_production_ops is not None else Config.ENABLE_PRODUCTION_OPERATIONS
        self.api_logger = api_logger
        
        self.session = requests.Session()
        self.session.headers.update(self.default_headers)
        
        # Apply authentication if handler provided
        if self.auth_handler:
            self._apply_authentication()
            logger.info("Authentication applied to test session")
    
    def _apply_authentication(self):
        """Apply authentication to the session, refreshing if needed."""
        if self.auth_handler:
            self.session = self.auth_handler.apply(self.session)
            # Verify authentication is present
            if 'Authorization' not in self.session.headers:
                logger.warning("Authentication handler did not set Authorization header")
    
    def _ensure_authentication(self):
        """Ensure authentication is present and valid before making requests."""
        if not self.auth_handler:
            return
        
        # Check if Authorization header is present
        if 'Authorization' not in self.session.headers:
            logger.debug("Re-applying authentication (header missing)")
            self._apply_authentication()
        
        # For OAuth handlers, check if token needs refresh
        if hasattr(self.auth_handler, '_get_access_token'):
            try:
                # Try to get token to trigger refresh if needed
                token = self.auth_handler._get_access_token()
                if not token:
                    logger.warning("Authentication token not available, attempting to refresh")
                    self._apply_authentication()
            except Exception as e:
                logger.warning(f"Error checking authentication: {e}")
    
    def test_endpoint(
        self, 
        endpoint: EndpointInfo,
        auth_token: Optional[str] = None
    ) -> List[TestResult]:
        """Test an endpoint with various payload variations.
        
        Args:
            endpoint: Endpoint to test
            auth_token: Optional authentication token (deprecated - use auth_handler)
            
        Returns:
            List of TestResult objects
        """
        path_str = endpoint.path or '(no path)'
        logger.info(f"Testing endpoint: {endpoint.method.value} {path_str}")
        
        # Classify operation if classifier is available
        if self.classifier:
            classification = self.classifier.classify_operation(endpoint)
            
            # Skip production operations if disabled
            if classification['is_production'] and not self.enable_production_ops:
                path_str = endpoint.path or '(no path)'
                logger.warning(f"⚠ PULANDO OPERAÇÃO DE PRODUÇÃO: {endpoint.method.value} {path_str}")
                logger.info(f"   Risco: {classification['risk_level']}")
                logger.info(f"   Motivo: {classification['reason']}")
                logger.info(f"   Config: ENABLE_PRODUCTION_OPERATIONS={self.enable_production_ops}")
                
                # Return empty results (operation skipped)
                return []
        
        # Set up headers (auth already in session if auth_handler provided)
        headers = self.default_headers.copy()
        
        # Legacy auth_token support (deprecated)
        if auth_token and not self.auth_handler:
            headers['Authorization'] = f'Bearer {auth_token}'
        
        # Generate test payloads
        test_payloads = self._generate_test_payloads(endpoint)
        
        results = []
        for i, payload in enumerate(test_payloads):
            logger.debug(f"Test {i+1}/{len(test_payloads)}: {payload.get('description', 'Test')}")
            
            result = self._execute_request(
                endpoint=endpoint,
                payload=payload['data'],
                headers=headers,
                test_name=payload.get('description', f'Test {i+1}')
            )
            
            if result:
                results.append(result)
            
            # Small delay to avoid rate limiting
            time.sleep(0.5)
        
        path_str = endpoint.path or '(no path)'
        logger.info(f"Completed {len(results)} tests for {endpoint.method.value} {path_str}")
        return results
    
    def test_all_endpoints(
        self, 
        endpoints: List[EndpointInfo],
        auth_token: Optional[str] = None
    ) -> Dict[str, List[TestResult]]:
        """Test all endpoints.
        
        Args:
            endpoints: List of endpoints to test
            auth_token: Optional authentication token
            
        Returns:
            Dictionary mapping endpoint keys to their test results
        """
        all_results = {}
        
        for endpoint in endpoints:
            path_str = endpoint.path or '(no path)'
            endpoint_key = f"{endpoint.method.value} {path_str}"
            results = self.test_endpoint(endpoint, auth_token)
            all_results[endpoint_key] = results
        
        return all_results
    
    def _clean_endpoint_path(self, path: Optional[str]) -> str:
        """Clean endpoint path from Postman variables and templates.
        
        Args:
            path: Original path with {{variables}} (can be None)
            
        Returns:
            Clean path (defaults to '/' if path is None)
        """
        # Handle None path
        if not path:
            return '/'
        
        # Remove {{base_url}} and {{BASE_URL}} references
        cleaned = path.replace('{{base_url}}', '')
        cleaned = cleaned.replace('{{BASE_URL}}', '')
        
        # Remove other Postman variables like {{variable}}
        cleaned = re.sub(r'\{\{[^}]+\}\}', '', cleaned)
        
        # Ensure starts with /
        if not cleaned.startswith('/'):
            cleaned = '/' + cleaned
        
        # Remove duplicate slashes
        cleaned = re.sub(r'/+', '/', cleaned)
        
        return cleaned
    
    def _execute_request(
        self,
        endpoint: EndpointInfo,
        payload: Optional[Dict[str, Any]],
        headers: Dict[str, str],
        test_name: str
    ) -> Optional[TestResult]:
        """Execute a single API request.
        
        Args:
            endpoint: Endpoint information
            payload: Request payload
            headers: Request headers
            test_name: Name/description of the test
            
        Returns:
            TestResult object or None if request failed
        """
        # Clean path from Postman variables
        clean_path = self._clean_endpoint_path(endpoint.path)
        url = self.base_url + clean_path
        method = endpoint.method.value
        
        # Prepare request parameters
        kwargs = {
            'headers': headers,
            'timeout': Config.DEFAULT_TIMEOUT
        }
        
        # Add payload based on method
        if method in ['POST', 'PUT', 'PATCH'] and payload is not None:
            kwargs['json'] = payload
        elif method == 'GET' and payload:
            kwargs['params'] = payload
        
        # Add query parameters if present
        if endpoint.query_params:
            kwargs['params'] = kwargs.get('params', {})
            kwargs['params'].update(endpoint.query_params)
        
        try:
            # Ensure authentication is valid before request
            self._ensure_authentication()
            
            start_time = time.time()
            
            response = self.session.request(
                method=method,
                url=url,
                **kwargs
            )
            
            execution_time = time.time() - start_time
            
            # Check for authentication errors and retry once
            if response.status_code == 401 and self.auth_handler:
                logger.warning(f"Received 401 Unauthorized, attempting to refresh authentication")
                # Try to refresh token (for OAuth handlers)
                if hasattr(self.auth_handler, 'generate_token'):
                    try:
                        token = self.auth_handler.generate_token()
                        if token:
                            logger.info("Token refreshed, retrying request")
                            # Re-apply authentication
                            self._apply_authentication()
                            # Retry the request
                            start_time = time.time()
                            response = self.session.request(
                                method=method,
                                url=url,
                                **kwargs
                            )
                            execution_time = time.time() - start_time
                    except Exception as e:
                        logger.error(f"Error refreshing token: {e}")
            
            # Also check for 403 Forbidden (might indicate expired token)
            if response.status_code == 403 and self.auth_handler:
                logger.warning(f"Received 403 Forbidden, authentication may have expired")
            
            # Try to parse response as JSON
            try:
                response_body = response.json()
            except:
                response_body = response.text
            
            result = TestResult(
                endpoint=endpoint,
                request_payload=payload or {},
                response_status=response.status_code,
                response_body=response_body,
                response_headers=dict(response.headers),
                execution_time=execution_time
            )
            
            logger.debug(f"{test_name}: Status {response.status_code}, Time {execution_time:.2f}s")
            
            # Log if logger provided
            if self.api_logger:
                self.api_logger.log_test(
                    method=method,
                    url=url,
                    headers=kwargs.get('headers', {}),
                    body=payload,
                    response_status=response.status_code,
                    response_headers=dict(response.headers),
                    response_body=response_body,
                    duration=execution_time,
                    test_name=test_name
                )
            
            return result
            
        except requests.exceptions.Timeout:
            logger.warning(f"{test_name}: Request timeout")
            return TestResult(
                endpoint=endpoint,
                request_payload=payload or {},
                response_status=0,
                response_body=None,
                response_headers={},
                execution_time=Config.DEFAULT_TIMEOUT,
                error="Request timeout"
            )
        except Exception as e:
            logger.error(f"{test_name}: Error - {str(e)}")
            return TestResult(
                endpoint=endpoint,
                request_payload=payload or {},
                response_status=0,
                response_body=None,
                response_headers={},
                execution_time=0,
                error=str(e)
            )
    
    def _generate_test_payloads(self, endpoint: EndpointInfo) -> List[Dict[str, Any]]:
        """Generate various test payloads for an endpoint.
        
        Args:
            endpoint: Endpoint to generate payloads for
            
        Returns:
            List of test payload dictionaries with descriptions
        """
        payloads = []
        
        # PRIORITY: Use real examples from documentation if available
        if endpoint.examples:
            logger.info(f"Using {len(endpoint.examples)} real examples from documentation")
            for example in endpoint.examples:
                if 'body' in example:
                    payloads.append({
                        'description': example.get('description', 'Real example from documentation'),
                        'data': example['body']
                    })
            
            # If we have real examples, use only those (more reliable)
            if payloads:
                return payloads
        
        # For GET requests, we might not need complex payloads
        if endpoint.method == HTTPMethod.GET:
            payloads.append({
                'description': 'Basic GET request',
                'data': None
            })
            return payloads
        
        # If no request fields defined, try empty payload
        if not endpoint.request_fields:
            payloads.append({
                'description': 'Empty payload',
                'data': {}
            })
            return payloads
        
        # 1. Valid payload with all required fields
        valid_payload = self._generate_valid_payload(endpoint)
        if valid_payload:
            payloads.append({
                'description': 'Valid payload with all required fields',
                'data': valid_payload
            })
        
        # 2. Missing required fields (one at a time)
        required_fields = [f for f in endpoint.request_fields if f.required]
        for field in required_fields[:3]:  # Test up to 3 required fields
            invalid_payload = valid_payload.copy()
            if field.name in invalid_payload:
                del invalid_payload[field.name]
                payloads.append({
                    'description': f'Missing required field: {field.name}',
                    'data': invalid_payload
                })
        
        # 3. Invalid data types
        for field in endpoint.request_fields[:3]:  # Test up to 3 fields
            invalid_type_payload = valid_payload.copy()
            invalid_type_payload[field.name] = self._get_invalid_type_value(field.field_type)
            payloads.append({
                'description': f'Invalid type for field: {field.name}',
                'data': invalid_type_payload
            })
        
        # 4. Null values for optional fields
        optional_fields = [f for f in endpoint.request_fields if not f.required]
        if optional_fields:
            null_payload = valid_payload.copy()
            for field in optional_fields[:2]:  # Test up to 2 optional fields
                null_payload[field.name] = None
            payloads.append({
                'description': 'Null values for optional fields',
                'data': null_payload
            })
        
        # 5. Empty strings
        string_fields = [f for f in endpoint.request_fields if f.field_type == 'string']
        if string_fields:
            empty_string_payload = valid_payload.copy()
            empty_string_payload[string_fields[0].name] = ""
            payloads.append({
                'description': f'Empty string for: {string_fields[0].name}',
                'data': empty_string_payload
            })
        
        # 6. Boundary values
        for field in endpoint.request_fields[:2]:
            if field.constraints:
                boundary_payload = valid_payload.copy()
                boundary_value = self._get_boundary_value(field)
                if boundary_value is not None:
                    boundary_payload[field.name] = boundary_value
                    payloads.append({
                        'description': f'Boundary value for: {field.name}',
                        'data': boundary_payload
                    })
        
        return payloads
    
    def _generate_valid_payload(self, endpoint: EndpointInfo) -> Dict[str, Any]:
        """Generate a valid payload for an endpoint.
        
        Args:
            endpoint: Endpoint to generate payload for
            
        Returns:
            Valid payload dictionary
        """
        payload = {}
        
        for field in endpoint.request_fields:
            # Skip nested fields for now
            if '.' in field.name:
                continue
            
            value = self._generate_field_value(field)
            if value is not None or field.required:
                payload[field.name] = value
        
        return payload
    
    def _generate_field_value(self, field: FieldInfo) -> Any:
        """Generate a valid value for a field.
        
        Args:
            field: Field to generate value for
            
        Returns:
            Generated value
        """
        # If possible values are specified, use the first one
        if field.possible_values:
            return field.possible_values[0]
        
        # Generate based on type
        field_type = (field.field_type or 'string').lower()
        
        if field_type in ['string', 'str']:
            # Check for format constraints
            if field.constraints.get('format') == 'email':
                return 'test@example.com'
            elif field.constraints.get('format') == 'uuid':
                return '123e4567-e89b-12d3-a456-426614174000'
            elif field.constraints.get('format') == 'date':
                return '2024-01-01'
            elif field.constraints.get('format') == 'date-time':
                return '2024-01-01T00:00:00Z'
            else:
                min_len = field.constraints.get('minLength', 1)
                return 'test_' + 'x' * max(0, min_len - 5)
        
        elif field_type in ['integer', 'int', 'number']:
            min_val = field.constraints.get('minimum', 1)
            max_val = field.constraints.get('maximum', 100)
            return int((min_val + max_val) / 2) if max_val else min_val
        
        elif field_type in ['boolean', 'bool']:
            return True
        
        elif field_type == 'array':
            return []
        
        elif field_type == 'object':
            return {}
        
        else:
            return 'test_value'
    
    def _get_invalid_type_value(self, field_type: Optional[str]) -> Any:
        """Get an invalid value for a given field type.
        
        Args:
            field_type: Field type
            
        Returns:
            Invalid value
        """
        field_type = (field_type or 'string').lower()
        
        if field_type in ['string', 'str']:
            return 12345  # Number instead of string
        elif field_type in ['integer', 'int']:
            return "not_a_number"  # String instead of integer
        elif field_type in ['boolean', 'bool']:
            return "not_a_boolean"  # String instead of boolean
        elif field_type == 'array':
            return "not_an_array"  # String instead of array
        elif field_type == 'object':
            return "not_an_object"  # String instead of object
        else:
            return None
    
    def _get_boundary_value(self, field: FieldInfo) -> Any:
        """Get a boundary value for testing field constraints.
        
        Args:
            field: Field with constraints
            
        Returns:
            Boundary value or None
        """
        field_type = (field.field_type or 'string').lower()
        
        if field_type in ['string', 'str']:
            max_len = field.constraints.get('maxLength')
            if max_len:
                return 'x' * (max_len + 1)  # Exceed max length
        
        elif field_type in ['integer', 'int', 'number']:
            max_val = field.constraints.get('maximum')
            if max_val:
                return max_val + 1  # Exceed maximum
        
        return None

