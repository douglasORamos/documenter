"""OpenAPI/Swagger specification parser."""
import json
import yaml
import logging
from typing import List, Dict, Any
from .base_parser import BaseParser
from models import (
    DocumentationSource, EndpointInfo, HTTPMethod, 
    FieldInfo
)

logger = logging.getLogger("documenter")


class OpenAPIParser(BaseParser):
    """Parser for OpenAPI/Swagger specification files."""
    
    def parse(self) -> DocumentationSource:
        """Parse the OpenAPI specification file.
        
        Returns:
            DocumentationSource object with extracted content
        """
        logger.info(f"Parsing OpenAPI spec: {self.file_path}")
        
        try:
            # Try to load as JSON first, then YAML
            content = None
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
            except json.JSONDecodeError:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    content = yaml.safe_load(f)
            
            doc_source = DocumentationSource(
                file_path=self.file_path,
                file_type='openapi',
                content=content
            )
            
            # Extract endpoints from OpenAPI spec
            doc_source.endpoints = self.extract_endpoints()
            
            logger.info(f"Extracted {len(doc_source.endpoints)} endpoints from OpenAPI spec")
            return doc_source
            
        except Exception as e:
            logger.error(f"Error parsing OpenAPI spec: {e}")
            raise
    
    def extract_endpoints(self) -> List[EndpointInfo]:
        """Extract endpoint information from OpenAPI specification.
        
        Returns:
            List of EndpointInfo objects
        """
        endpoints = []
        
        try:
            # Load spec
            content = None
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
            except json.JSONDecodeError:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    content = yaml.safe_load(f)
            
            # Extract paths
            paths = content.get('paths', {})
            
            for path, path_item in paths.items():
                # Each path can have multiple methods
                for method_str in ['get', 'post', 'put', 'patch', 'delete', 'options', 'head']:
                    if method_str in path_item:
                        operation = path_item[method_str]
                        endpoint = self._parse_operation(path, method_str.upper(), operation, content)
                        if endpoint:
                            endpoints.append(endpoint)
            
        except Exception as e:
            logger.error(f"Error extracting endpoints from OpenAPI spec: {e}")
        
        return endpoints
    
    def _parse_operation(
        self, 
        path: str, 
        method_str: str, 
        operation: Dict[str, Any],
        spec: Dict[str, Any]
    ) -> EndpointInfo:
        """Parse an OpenAPI operation.
        
        Args:
            path: API path
            method_str: HTTP method
            operation: Operation object from OpenAPI spec
            spec: Full OpenAPI specification
            
        Returns:
            EndpointInfo object
        """
        try:
            method = HTTPMethod[method_str]
        except KeyError:
            method = HTTPMethod.GET
        
        description = operation.get('summary', '') or operation.get('description', '')
        
        # Extract request body fields
        request_fields = []
        request_body = operation.get('requestBody', {})
        if request_body:
            content = request_body.get('content', {})
            for content_type, content_obj in content.items():
                if 'application/json' in content_type:
                    schema = content_obj.get('schema', {})
                    request_fields = self._parse_schema(schema, spec)
        
        # Extract parameters (query, header, path)
        query_params = {}
        headers = {}
        for param in operation.get('parameters', []):
            param_in = param.get('in', '')
            param_name = param.get('name', '')
            
            if param_in == 'query':
                query_params[param_name] = param.get('description', '')
            elif param_in == 'header':
                headers[param_name] = param.get('description', '')
        
        # Extract response fields
        response_fields = []
        responses = operation.get('responses', {})
        for status_code, response_obj in responses.items():
            if status_code.startswith('2'):  # Success responses
                content = response_obj.get('content', {})
                for content_type, content_obj in content.items():
                    if 'application/json' in content_type:
                        schema = content_obj.get('schema', {})
                        response_fields = self._parse_schema(schema, spec)
                        break
        
        # Extract error codes
        error_codes = {}
        for status_code, response_obj in responses.items():
            try:
                code = int(status_code)
                if code >= 400:
                    error_codes[code] = response_obj.get('description', '')
            except ValueError:
                pass
        
        endpoint = EndpointInfo(
            path=path,
            method=method,
            description=description,
            request_fields=request_fields,
            response_fields=response_fields,
            headers=headers,
            query_params=query_params,
            error_codes=error_codes
        )
        
        return endpoint
    
    def _parse_schema(
        self, 
        schema: Dict[str, Any], 
        spec: Dict[str, Any],
        parent_name: str = ""
    ) -> List[FieldInfo]:
        """Parse an OpenAPI schema to extract field information.
        
        Args:
            schema: Schema object
            spec: Full OpenAPI specification (for resolving $ref)
            parent_name: Parent field name for nested fields
            
        Returns:
            List of FieldInfo objects
        """
        fields = []
        
        # Handle $ref
        if '$ref' in schema:
            ref_path = schema['$ref']
            schema = self._resolve_ref(ref_path, spec)
        
        schema_type = schema.get('type', 'object')
        
        if schema_type == 'object':
            properties = schema.get('properties', {})
            required_fields = schema.get('required', [])
            
            for prop_name, prop_schema in properties.items():
                field_name = f"{parent_name}.{prop_name}" if parent_name else prop_name
                
                # Handle $ref in property
                if '$ref' in prop_schema:
                    prop_schema = self._resolve_ref(prop_schema['$ref'], spec)
                
                field = FieldInfo(
                    name=field_name,
                    field_type=prop_schema.get('type', 'string'),
                    required=prop_name in required_fields,
                    description=prop_schema.get('description', '')
                )
                
                # Handle nested objects
                if prop_schema.get('type') == 'object':
                    field.nested_fields = self._parse_schema(prop_schema, spec, field_name)
                
                # Handle enums
                if 'enum' in prop_schema:
                    field.possible_values = prop_schema['enum']
                
                fields.append(field)
        
        elif schema_type == 'array':
            items_schema = schema.get('items', {})
            if '$ref' in items_schema:
                items_schema = self._resolve_ref(items_schema['$ref'], spec)
            
            if items_schema.get('type') == 'object':
                fields = self._parse_schema(items_schema, spec, parent_name)
        
        return fields
    
    def _resolve_ref(self, ref_path: str, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve a $ref reference in OpenAPI spec.
        
        Args:
            ref_path: Reference path (e.g., '#/components/schemas/User')
            spec: Full OpenAPI specification
            
        Returns:
            Resolved schema object
        """
        if not ref_path.startswith('#/'):
            return {}
        
        # Remove '#/' and split by '/'
        parts = ref_path[2:].split('/')
        
        # Navigate the spec
        result = spec
        for part in parts:
            result = result.get(part, {})
        
        return result

