"""Generator for creating enriched Postman Collection files."""
import json
import uuid
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from models import EndpointInfo, TestResult, Pattern, FieldInfo, HTTPMethod

logger = logging.getLogger("documenter")


class PostmanCollectionGenerator:
    """Generates enriched Postman Collection v2.1 files."""
    
    def __init__(self, collection_name: str = "Enriched API Documentation"):
        """Initialize the generator.
        
        Args:
            collection_name: Name of the Postman collection
        """
        self.collection_name = collection_name
        self.collection_id = str(uuid.uuid4())
    
    def generate(
        self,
        endpoints: List[EndpointInfo],
        test_results: Optional[Dict[str, List[TestResult]]] = None,
        patterns: Optional[Dict[str, List[Pattern]]] = None,
        base_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a Postman Collection.
        
        Args:
            endpoints: List of endpoints to include
            test_results: Optional test results by endpoint
            patterns: Optional patterns by endpoint
            base_url: Optional base URL for the API
            
        Returns:
            Postman Collection as dictionary
        """
        logger.info(f"Generating Postman Collection with {len(endpoints)} endpoints")
        
        # Create collection structure
        collection = {
            "info": self._create_info(),
            "item": [],
            "variable": self._create_variables(base_url)
        }
        
        # Add each endpoint as an item
        for endpoint in endpoints:
            path_str = endpoint.path or '(no path)'
            endpoint_key = f"{endpoint.method.value} {path_str}"
            
            item = self._create_endpoint_item(
                endpoint=endpoint,
                test_results=test_results.get(endpoint_key, []) if test_results else [],
                patterns=patterns.get(endpoint_key, []) if patterns else []
            )
            
            collection["item"].append(item)
        
        logger.info("Postman Collection generated successfully")
        return collection
    
    def save(self, collection: Dict[str, Any], output_path: str):
        """Save collection to a JSON file.
        
        Args:
            collection: Postman Collection dictionary
            output_path: Path to save the file
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(collection, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved Postman Collection to: {output_path}")
    
    def _create_info(self) -> Dict[str, Any]:
        """Create the info section of the collection.
        
        Returns:
            Info dictionary
        """
        return {
            "name": self.collection_name,
            "_postman_id": self.collection_id,
            "description": f"Auto-generated and AI-enriched API documentation\nGenerated: {datetime.now().isoformat()}",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        }
    
    def _create_variables(self, base_url: Optional[str]) -> List[Dict[str, Any]]:
        """Create collection variables.
        
        Args:
            base_url: Base URL for the API
            
        Returns:
            List of variable dictionaries
        """
        variables = []
        
        if base_url:
            variables.append({
                "key": "base_url",
                "value": base_url,
                "type": "string"
            })
        
        return variables
    
    def _create_endpoint_item(
        self,
        endpoint: EndpointInfo,
        test_results: List[TestResult],
        patterns: List[Pattern]
    ) -> Dict[str, Any]:
        """Create a Postman item for an endpoint.
        
        Args:
            endpoint: Endpoint information
            test_results: Test results for this endpoint
            patterns: Discovered patterns for this endpoint
            
        Returns:
            Postman item dictionary
        """
        # Create base item
        path_str = endpoint.path or '(no path)'
        item = {
            "name": f"{endpoint.method.value} {path_str}",
            "request": self._create_request(endpoint),
            "response": []
        }
        
        # Add description with enriched information
        description = self._create_enriched_description(endpoint, patterns)
        if description:
            item["request"]["description"] = description
        
        # Add examples from test results
        if test_results:
            item["response"] = self._create_response_examples(test_results, endpoint)
        # Add examples from endpoint if no test results
        elif endpoint.examples:
            item["response"] = self._create_response_examples_from_endpoint(endpoint)
        
        # Skip test scripts for cleaner collection
        # Tests make the collection more complex without adding value for documentation
        
        return item
    
    def _clean_path(self, path: Optional[str]) -> str:
        """Clean path by removing duplicate base_url references.
        
        Args:
            path: Original path (can be None)
            
        Returns:
            Cleaned path (defaults to '/' if path is None)
        """
        if not path:
            return '/'
        # Remove any existing {{base_url}} or {{BASE_URL}} references
        cleaned = path.replace('{{base_url}}', '').replace('{{BASE_URL}}', '')
        # Ensure starts with /
        cleaned = '/' + cleaned.lstrip('/')
        return cleaned
    
    def _get_path_parts(self, path: Optional[str]) -> List[str]:
        """Get path parts without base_url variables.
        
        Args:
            path: Path string (can be None)
            
        Returns:
            List of path parts
        """
        cleaned = self._clean_path(path)
        parts = [p for p in cleaned.strip('/').split('/') if p and '{{' not in p]
        return parts
    
    def _create_request(self, endpoint: EndpointInfo) -> Dict[str, Any]:
        """Create the request object for an endpoint.
        
        Args:
            endpoint: Endpoint information
            
        Returns:
            Request dictionary
        """
        # Build clean URL
        path = endpoint.path or ''
        clean_path = self._clean_path(path)
        path_parts = self._get_path_parts(path)
        
        url = {
            "raw": "{{base_url}}" + clean_path,
            "host": ["{{base_url}}"],
            "path": path_parts
        }
        
        # Add query parameters
        if endpoint.query_params:
            url["query"] = [
                {
                    "key": key,
                    "value": str(value),
                    "description": f"Query parameter: {key}"
                }
                for key, value in endpoint.query_params.items()
            ]
        
        # Build request
        request = {
            "method": endpoint.method.value,
            "header": self._create_headers(endpoint),
            "url": url
        }
        
        # ALWAYS add body for POST, PUT, PATCH (even if empty)
        if endpoint.method in [HTTPMethod.POST, HTTPMethod.PUT, HTTPMethod.PATCH]:
            if endpoint.request_fields:
                request["body"] = self._create_request_body(endpoint)
            else:
                # Empty body structure for POST/PUT/PATCH without fields
                request["body"] = {
                    "mode": "raw",
                    "raw": "{}",
                    "options": {
                        "raw": {
                            "language": "json"
                        }
                    }
                }
        
        return request
    
    def _deduplicate_headers(self, headers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate headers.
        
        Args:
            headers: List of header dictionaries
            
        Returns:
            Deduplicated list of headers
        """
        seen = set()
        unique = []
        
        for header in headers:
            key = header.get('key', '').lower()
            if key and key not in seen:
                seen.add(key)
                unique.append(header)
        
        return unique
    
    def _create_headers(self, endpoint: EndpointInfo) -> List[Dict[str, Any]]:
        """Create headers for the request.
        
        Args:
            endpoint: Endpoint information
            
        Returns:
            List of header dictionaries (deduplicated)
        """
        headers = []
        
        # Add default content-type for POST/PUT/PATCH
        if endpoint.method in [HTTPMethod.POST, HTTPMethod.PUT, HTTPMethod.PATCH]:
            headers.append({
                "key": "Content-Type",
                "value": "application/json"
            })
        
        # Add endpoint-specific headers (without description for cleaner look)
        for key, value in endpoint.headers.items():
            headers.append({
                "key": key,
                "value": str(value)
            })
        
        # Deduplicate headers
        return self._deduplicate_headers(headers)
    
    def _create_request_body(self, endpoint: EndpointInfo) -> Dict[str, Any]:
        """Create request body with example payload.
        
        Args:
            endpoint: Endpoint information
            
        Returns:
            Body dictionary
        """
        # Create example payload
        example_payload = self._create_example_payload(endpoint.request_fields)
        
        return {
            "mode": "raw",
            "raw": json.dumps(example_payload, indent=2),
            "options": {
                "raw": {
                    "language": "json"
                }
            }
        }
    
    def _create_example_payload(self, fields: List[FieldInfo]) -> Dict[str, Any]:
        """Create an example payload from field definitions.
        
        Args:
            fields: List of field information
            
        Returns:
            Example payload dictionary
        """
        payload = {}
        
        for field in fields:
            # Skip nested fields (handle them separately)
            if '.' in field.name:
                continue
            
            # Generate example value
            value = self._get_example_value(field)
            payload[field.name] = value
        
        return payload
    
    def _get_example_value(self, field: FieldInfo) -> Any:
        """Get an example value for a field.
        
        Args:
            field: Field information
            
        Returns:
            Example value
        """
        # Use possible values if available
        if field.possible_values:
            return field.possible_values[0]
        
        # Generate based on type
        field_type = (field.field_type or 'string').lower()
        
        if field_type in ['string', 'str']:
            if 'email' in field.name.lower():
                return "user@example.com"
            elif 'name' in field.name.lower():
                return "Example Name"
            elif 'id' in field.name.lower():
                return "12345"
            else:
                return f"example_{field.name}"
        
        elif field_type in ['integer', 'int']:
            return 1
        
        elif field_type in ['number', 'float', 'double']:
            return 1.0
        
        elif field_type in ['boolean', 'bool']:
            return True
        
        elif field_type == 'array':
            if field.nested_fields:
                return [self._create_example_payload(field.nested_fields)]
            return []
        
        elif field_type == 'object':
            if field.nested_fields:
                return self._create_example_payload(field.nested_fields)
            return {}
        
        else:
            return "example_value"
    
    def _create_enriched_description(
        self,
        endpoint: EndpointInfo,
        patterns: List[Pattern]
    ) -> str:
        """Create a simple, clean description.
        
        Args:
            endpoint: Endpoint information
            patterns: Discovered patterns (unused for simplicity)
            
        Returns:
            Simple description text
        """
        description_parts = []
        
        # Basic description (first line only)
        if endpoint.description:
            first_line = endpoint.description.split('\n')[0].split('.')[0]
            description_parts.append(first_line)
        
        # Request fields (simple list)
        if endpoint.request_fields:
            field_names = [f.name for f in endpoint.request_fields]
            description_parts.append(f"\nRequest: {', '.join(field_names)}")
        
        # Response fields (simple list)
        if endpoint.response_fields:
            field_names = [f.name for f in endpoint.response_fields[:5]]
            description_parts.append(f"Response: {', '.join(field_names)}")
        
        return "\n".join(description_parts) if description_parts else None
    
    def _document_field(self, field: FieldInfo) -> str:
        """Create documentation for a single field.
        
        Args:
            field: Field information
            
        Returns:
            Field documentation string
        """
        parts = [f"- **`{field.name}`**"]
        
        # Type and requirement
        type_info = []
        if field.field_type:
            type_info.append(f"*{field.field_type}*")
        if field.required is not None:
            type_info.append("**required**" if field.required else "*optional*")
        
        if type_info:
            parts.append(f" ({', '.join(type_info)})")
        
        # Description
        if field.description:
            parts.append(f": {field.description}")
        
        # Constraints
        if field.constraints:
            constraint_strs = []
            for key, value in field.constraints.items():
                constraint_strs.append(f"{key}={value}")
            if constraint_strs:
                parts.append(f"\n  - Constraints: {', '.join(constraint_strs)}")
        
        # Possible values
        if field.possible_values:
            values_str = ', '.join(f'`{v}`' for v in field.possible_values[:10])
            parts.append(f"\n  - Possible values: {values_str}")
        
        return ''.join(parts)
    
    def _create_response_examples(
        self,
        test_results: List[TestResult],
        endpoint: EndpointInfo
    ) -> List[Dict[str, Any]]:
        """Create response examples from test results.
        
        Args:
            test_results: Test results
            endpoint: Endpoint information
            
        Returns:
            List of response example dictionaries
        """
        examples = []
        
        # Group by status code
        status_groups = {}
        for result in test_results:
            status = result.response_status
            if status not in status_groups:
                status_groups[status] = []
            status_groups[status].append(result)
        
        # Create examples for each status code (limit to first result per status)
        for status, results in sorted(status_groups.items()):
            result = results[0]  # Use first result for this status
            
            example = {
                "name": self._get_response_name(status, result),
                "originalRequest": self._create_request(endpoint),
                "status": self._get_status_text(status),
                "code": status,
                "_postman_previewlanguage": "json",
                "header": [
                    {
                        "key": key,
                        "value": value
                    }
                    for key, value in result.response_headers.items()
                ],
                "body": json.dumps(result.response_body, indent=2) if result.response_body else ""
            }
            
            examples.append(example)
        
        return examples
    
    def _create_response_examples_from_endpoint(
        self,
        endpoint: EndpointInfo
    ) -> List[Dict[str, Any]]:
        """Create response examples from endpoint examples.
        
        Args:
            endpoint: Endpoint information
            
        Returns:
            List of response example dictionaries
        """
        examples = []
        
        for ex in endpoint.examples:
            example = {
                "name": ex.get('name', 'Example Response'),
                "originalRequest": self._create_request(endpoint),
                "status": self._get_status_text(ex.get('status', 200)),
                "code": ex.get('status', 200),
                "_postman_previewlanguage": "json",
                "header": [
                    {"key": "Content-Type", "value": "application/json"}
                ],
                "body": json.dumps(ex.get('body', {}), indent=2)
            }
            examples.append(example)
        
        return examples
    
    def _get_response_name(self, status: int, result: TestResult) -> str:
        """Get a descriptive name for a response example.
        
        Args:
            status: HTTP status code
            result: Test result
            
        Returns:
            Response name
        """
        if status >= 200 and status < 300:
            return f"Success ({status})"
        elif status >= 400 and status < 500:
            error_msg = result.response_body if isinstance(result.response_body, str) else ""
            if error_msg:
                return f"Client Error ({status}) - {error_msg[:50]}"
            return f"Client Error ({status})"
        elif status >= 500:
            return f"Server Error ({status})"
        else:
            return f"Response ({status})"
    
    def _get_status_text(self, status: int) -> str:
        """Get status text for a status code.
        
        Args:
            status: HTTP status code
            
        Returns:
            Status text
        """
        status_texts = {
            200: "OK",
            201: "Created",
            204: "No Content",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            409: "Conflict",
            422: "Unprocessable Entity",
            500: "Internal Server Error"
        }
        return status_texts.get(status, "Unknown")
    
    def _create_tests(
        self,
        endpoint: EndpointInfo,
        patterns: List[Pattern]
    ) -> List[str]:
        """Create Postman test scripts for an endpoint.
        
        Args:
            endpoint: Endpoint information
            patterns: Discovered patterns
            
        Returns:
            List of test script lines
        """
        tests = []
        
        # Basic status code test
        tests.append("// Verify response status")
        tests.append("pm.test('Status code is successful', function() {")
        tests.append("    pm.expect(pm.response.code).to.be.oneOf([200, 201, 204]);")
        tests.append("});")
        tests.append("")
        
        # Response time test
        tests.append("// Verify response time")
        tests.append("pm.test('Response time is acceptable', function() {")
        tests.append("    pm.expect(pm.response.responseTime).to.be.below(5000);")
        tests.append("});")
        tests.append("")
        
        # Response structure tests based on response fields
        if endpoint.response_fields:
            tests.append("// Verify response structure")
            tests.append("pm.test('Response has expected fields', function() {")
            tests.append("    const jsonData = pm.response.json();")
            
            for field in endpoint.response_fields[:5]:  # Limit to 5 fields
                if '.' not in field.name:
                    tests.append(f"    pm.expect(jsonData).to.have.property('{field.name}');")
            
            tests.append("});")
            tests.append("")
        
        return tests

