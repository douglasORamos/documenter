"""Postman Collection parser."""
import json
import logging
from typing import List, Dict, Any
from .base_parser import BaseParser
from models import (
    DocumentationSource, EndpointInfo, HTTPMethod, 
    FieldInfo
)

logger = logging.getLogger("documenter")


class PostmanParser(BaseParser):
    """Parser for Postman Collection files."""
    
    def parse(self) -> DocumentationSource:
        """Parse the Postman Collection file.
        
        Returns:
            DocumentationSource object with extracted content
        """
        logger.info(f"Parsing Postman Collection: {self.file_path}")
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
            
            doc_source = DocumentationSource(
                file_path=self.file_path,
                file_type='postman',
                content=content
            )
            
            # Extract endpoints from Postman collection
            doc_source.endpoints = self.extract_endpoints()
            
            logger.info(f"Extracted {len(doc_source.endpoints)} endpoints from Postman Collection")
            return doc_source
            
        except Exception as e:
            logger.error(f"Error parsing Postman Collection: {e}")
            raise
    
    def extract_endpoints(self) -> List[EndpointInfo]:
        """Extract endpoint information from Postman Collection.
        
        Returns:
            List of EndpointInfo objects
        """
        endpoints = []
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                collection = json.load(f)
            
            # Parse items recursively (Postman can have nested folders)
            items = collection.get('item', [])
            endpoints = self._parse_items(items)
            
        except Exception as e:
            logger.error(f"Error extracting endpoints from Postman Collection: {e}")
        
        return endpoints
    
    def _parse_items(self, items: List[Dict[str, Any]]) -> List[EndpointInfo]:
        """Recursively parse Postman items (folders and requests).
        
        Args:
            items: List of Postman items
            
        Returns:
            List of EndpointInfo objects
        """
        endpoints = []
        
        for item in items:
            # If it's a folder, recurse into it
            if 'item' in item:
                endpoints.extend(self._parse_items(item['item']))
            # If it's a request, parse it
            elif 'request' in item:
                endpoint = self._parse_request(item)
                if endpoint:
                    endpoints.append(endpoint)
        
        return endpoints
    
    def _parse_request(self, item: Dict[str, Any]) -> EndpointInfo:
        """Parse a single Postman request.
        
        Args:
            item: Postman request item
            
        Returns:
            EndpointInfo object or None
        """
        try:
            request = item['request']
            
            # Extract method
            method_str = request.get('method', 'GET')
            try:
                method = HTTPMethod[method_str]
            except KeyError:
                method = HTTPMethod.GET
            
            # Extract URL
            url = request.get('url', {})
            if isinstance(url, str):
                path = url
            else:
                path = url.get('raw', '')
                # Try to extract just the path
                path_parts = url.get('path', [])
                if path_parts:
                    path = '/' + '/'.join(path_parts)
            
            # Extract description
            description = item.get('name', '') or request.get('description', '')
            
            # Extract headers
            headers = {}
            for header in request.get('header', []):
                if not header.get('disabled', False):
                    headers[header.get('key', '')] = header.get('value', '')
            
            # Extract query parameters
            query_params = {}
            if isinstance(url, dict):
                for query in url.get('query', []):
                    if not query.get('disabled', False):
                        query_params[query.get('key', '')] = query.get('value', '')
            
            # Extract body (request fields)
            request_fields = []
            body = request.get('body', {})
            if body.get('mode') == 'raw':
                try:
                    body_data = json.loads(body.get('raw', '{}'))
                    request_fields = self._extract_fields_from_json(body_data)
                except:
                    pass
            
            # Extract examples from response
            examples = []
            for response in item.get('response', []):
                try:
                    example = {
                        'name': response.get('name', ''),
                        'status': response.get('code', 200),
                        'body': json.loads(response.get('body', '{}'))
                    }
                    examples.append(example)
                except:
                    pass
            
            endpoint = EndpointInfo(
                path=path,
                method=method,
                description=description,
                request_fields=request_fields,
                headers=headers,
                query_params=query_params,
                examples=examples
            )
            
            return endpoint
            
        except Exception as e:
            logger.error(f"Error parsing Postman request: {e}")
            return None
    
    def _extract_fields_from_json(self, data: Any, parent_name: str = "") -> List[FieldInfo]:
        """Extract field information from JSON data.
        
        Args:
            data: JSON data (dict, list, or primitive)
            parent_name: Parent field name for nested fields
            
        Returns:
            List of FieldInfo objects
        """
        fields = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                field_name = f"{parent_name}.{key}" if parent_name else key
                field_type = type(value).__name__
                
                field = FieldInfo(
                    name=field_name,
                    field_type=field_type
                )
                
                # Handle nested objects
                if isinstance(value, (dict, list)):
                    field.nested_fields = self._extract_fields_from_json(value, field_name)
                
                fields.append(field)
        
        elif isinstance(data, list) and data:
            # Analyze first item of array
            if isinstance(data[0], dict):
                fields = self._extract_fields_from_json(data[0], parent_name)
        
        return fields

