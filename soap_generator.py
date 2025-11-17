"""SOAP-specific Postman Collection generator."""
import json
import uuid
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from models import SOAPOperation, SOAPParameter, TestResult, Pattern

logger = logging.getLogger("documenter")


class SOAPCollectionGenerator:
    """Generates Postman Collection for SOAP APIs."""
    
    def __init__(self, collection_name: str = "SOAP API Documentation"):
        """Initialize the SOAP generator.
        
        Args:
            collection_name: Name of the Postman collection
        """
        self.collection_name = collection_name
        self.collection_id = str(uuid.uuid4())
    
    def generate(
        self,
        operations: List[SOAPOperation],
        test_results: Optional[Dict[str, List[TestResult]]] = None,
        patterns: Optional[Dict[str, List[Pattern]]] = None,
        wsdl_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a Postman Collection for SOAP.
        
        Args:
            operations: List of SOAP operations
            test_results: Optional test results
            patterns: Optional patterns discovered
            wsdl_url: Optional WSDL URL
            
        Returns:
            Postman Collection as dictionary
        """
        logger.info(f"Generating SOAP Postman Collection with {len(operations)} operations")
        
        # Create collection structure
        collection = {
            "info": self._create_info(),
            "item": [],
            "variable": self._create_variables(wsdl_url)
        }
        
        # Add each SOAP operation as an item
        for operation in operations:
            item = self._create_soap_item(
                operation=operation,
                patterns=patterns.get(operation.name, []) if patterns else []
            )
            collection["item"].append(item)
        
        logger.info("SOAP Postman Collection generated successfully")
        return collection
    
    def save(self, collection: Dict[str, Any], output_path: str):
        """Save collection to a JSON file.
        
        Args:
            collection: Postman Collection dictionary
            output_path: Path to save the file
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(collection, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved SOAP Postman Collection to: {output_path}")
    
    def _create_info(self) -> Dict[str, Any]:
        """Create the info section of the collection.
        
        Returns:
            Info dictionary
        """
        return {
            "name": self.collection_name,
            "_postman_id": self.collection_id,
            "description": f"SOAP API - Auto-generated and AI-enriched documentation\nGenerated: {datetime.now().isoformat()}\n\nThis is a SOAP API collection. All requests use XML with SOAP Envelope structure.",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        }
    
    def _create_variables(self, wsdl_url: Optional[str]) -> List[Dict[str, Any]]:
        """Create collection variables.
        
        Args:
            wsdl_url: WSDL URL
            
        Returns:
            List of variable dictionaries
        """
        variables = []
        
        if wsdl_url:
            # Extract base URL from WSDL
            if '?wsdl' in wsdl_url.lower():
                base_url = wsdl_url.split('?')[0]
            else:
                base_url = wsdl_url
            
            variables.append({
                "key": "soap_endpoint",
                "value": base_url,
                "type": "string"
            })
            
            variables.append({
                "key": "wsdl_url",
                "value": wsdl_url,
                "type": "string"
            })
        
        return variables
    
    def _create_soap_item(
        self,
        operation: SOAPOperation,
        patterns: List[Pattern]
    ) -> Dict[str, Any]:
        """Create a Postman item for a SOAP operation.
        
        Args:
            operation: SOAP operation
            patterns: Discovered patterns
            
        Returns:
            Postman item dictionary
        """
        # Create SOAP request
        item = {
            "name": f"SOAP: {operation.name}",
            "request": self._create_soap_request(operation),
            "response": []
        }
        
        # Add enriched description
        description = self._create_soap_description(operation, patterns)
        if description:
            item["request"]["description"] = description
        
        # Add tests
        tests = self._create_soap_tests(operation)
        if tests:
            item["event"] = [
                {
                    "listen": "test",
                    "script": {
                        "type": "text/javascript",
                        "exec": tests
                    }
                }
            ]
        
        return item
    
    def _create_soap_request(self, operation: SOAPOperation) -> Dict[str, Any]:
        """Create SOAP request object.
        
        Args:
            operation: SOAP operation
            
        Returns:
            Request dictionary
        """
        # SOAP always uses POST
        request = {
            "method": "POST",
            "header": self._create_soap_headers(operation),
            "body": self._create_soap_body(operation),
            "url": {
                "raw": operation.wsdl_url.replace('?wsdl', '').replace('?WSDL', ''),
                "protocol": "https" if operation.wsdl_url.startswith('https') else "http",
                "host": self._extract_host(operation.wsdl_url),
                "path": self._extract_path(operation.wsdl_url)
            }
        }
        
        return request
    
    def _create_soap_headers(self, operation: SOAPOperation) -> List[Dict[str, Any]]:
        """Create SOAP headers.
        
        Args:
            operation: SOAP operation
            
        Returns:
            List of header dictionaries
        """
        headers = [
            {
                "key": "Content-Type",
                "value": "text/xml; charset=utf-8",
                "description": "SOAP Content Type"
            }
        ]
        
        # Add SOAPAction header if present
        if operation.soap_action:
            headers.append({
                "key": "SOAPAction",
                "value": f'"{operation.soap_action}"',
                "description": "SOAP Action for this operation"
            })
        
        return headers
    
    def _create_soap_body(self, operation: SOAPOperation) -> Dict[str, Any]:
        """Create SOAP body with XML envelope.
        
        Args:
            operation: SOAP operation
            
        Returns:
            Body dictionary
        """
        # Generate XML body
        xml_body = self._generate_soap_xml(operation)
        
        return {
            "mode": "raw",
            "raw": xml_body,
            "options": {
                "raw": {
                    "language": "xml"
                }
            }
        }
    
    def _generate_soap_xml(self, operation: SOAPOperation) -> str:
        """Generate SOAP XML envelope.
        
        Args:
            operation: SOAP operation
            
        Returns:
            SOAP XML string
        """
        # Generate parameters XML
        params_xml = self._generate_params_xml(operation.input_params, indent=6)
        
        # Determine namespace prefix
        ns_prefix = "ns" if operation.namespace else ""
        ns_declaration = f' xmlns:ns="{operation.namespace}"' if operation.namespace else ''
        
        # Build SOAP envelope
        xml = f'''<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               xmlns:xsd="http://www.w3.org/2001/XMLSchema"{ns_declaration}>
  <soap:Body>
    <{ns_prefix + ":" if ns_prefix else ""}{operation.name}>
{params_xml}
    </{ns_prefix + ":" if ns_prefix else ""}{operation.name}>
  </soap:Body>
</soap:Envelope>'''
        
        return xml
    
    def _generate_params_xml(
        self, 
        params: List[SOAPParameter],
        indent: int = 6
    ) -> str:
        """Generate XML for parameters.
        
        Args:
            params: List of parameters
            indent: Indentation level
            
        Returns:
            Parameters XML string
        """
        if not params:
            return ""
        
        xml_lines = []
        indent_str = " " * indent
        
        for param in params:
            # Get example value
            value = param.example_value or self._get_default_value(param)
            
            # Add parameter XML
            xml_lines.append(f"{indent_str}<{param.name}>{value}</{param.name}>")
        
        return "\n".join(xml_lines)
    
    def _get_default_value(self, param: SOAPParameter) -> str:
        """Get default value for a parameter based on its type.
        
        Args:
            param: SOAP parameter
            
        Returns:
            Default value as string
        """
        xml_type = param.xml_type.lower()
        
        if 'string' in xml_type or 'str' in xml_type:
            if 'email' in param.name.lower():
                return 'user@example.com'
            elif 'cpf' in param.name.lower():
                return '12345678901'
            elif 'data' in param.name.lower() or 'date' in param.name.lower():
                return '2024-01-01'
            else:
                return f'example_{param.name}'
        
        elif 'int' in xml_type or 'integer' in xml_type:
            return '1'
        
        elif 'double' in xml_type or 'decimal' in xml_type or 'float' in xml_type:
            return '1.0'
        
        elif 'bool' in xml_type:
            return 'true'
        
        elif 'date' in xml_type:
            return '2024-01-01'
        
        elif 'datetime' in xml_type:
            return '2024-01-01T00:00:00'
        
        else:
            return 'value'
    
    def _create_soap_description(
        self,
        operation: SOAPOperation,
        patterns: List[Pattern]
    ) -> str:
        """Create enriched description for SOAP operation.
        
        Args:
            operation: SOAP operation
            patterns: Discovered patterns
            
        Returns:
            Enriched description
        """
        description_parts = []
        
        # Basic description
        if operation.description:
            description_parts.append(operation.description)
        
        description_parts.append(f"\n## SOAP Operation: {operation.name}\n")
        
        # WSDL info
        description_parts.append(f"**WSDL URL**: {operation.wsdl_url}")
        
        if operation.namespace:
            description_parts.append(f"**Namespace**: {operation.namespace}")
        
        if operation.soap_action:
            description_parts.append(f"**SOAPAction**: {operation.soap_action}")
        
        # Input parameters
        if operation.input_params:
            description_parts.append("\n## Input Parameters (XML)\n")
            for param in operation.input_params:
                param_doc = self._document_soap_param(param)
                description_parts.append(param_doc)
        
        # Output parameters
        if operation.output_params:
            description_parts.append("\n## Output Parameters (XML)\n")
            for param in operation.output_params:
                param_doc = self._document_soap_param(param)
                description_parts.append(param_doc)
        
        # Patterns
        if patterns:
            description_parts.append("\n## Discovered Patterns & Rules\n")
            for pattern in patterns:
                description_parts.append(f"- **{pattern.description}** ({pattern.pattern_type})")
        
        # SOAP usage note
        description_parts.append("\n## Usage Notes\n")
        description_parts.append("This is a SOAP operation. The request must:")
        description_parts.append("- Use POST method")
        description_parts.append("- Set Content-Type: text/xml; charset=utf-8")
        description_parts.append("- Include SOAP Envelope in the body")
        description_parts.append(f"- Set SOAPAction header (if required)")
        
        return "\n".join(description_parts)
    
    def _document_soap_param(self, param: SOAPParameter) -> str:
        """Create documentation for a SOAP parameter.
        
        Args:
            param: SOAP parameter
            
        Returns:
            Parameter documentation
        """
        parts = [f"- **`{param.name}`**"]
        
        # Type and requirement
        type_info = []
        if param.xml_type:
            type_info.append(f"*{param.xml_type}*")
        if param.required:
            type_info.append("**required**")
        else:
            type_info.append("*optional*")
        
        if type_info:
            parts.append(f" ({', '.join(type_info)})")
        
        # Description
        if param.description:
            parts.append(f": {param.description}")
        
        # Example value
        if param.example_value:
            parts.append(f"\n  - Example: `{param.example_value}`")
        
        return ''.join(parts)
    
    def _create_soap_tests(self, operation: SOAPOperation) -> List[str]:
        """Create Postman test scripts for SOAP operation.
        
        Args:
            operation: SOAP operation
            
        Returns:
            List of test script lines
        """
        tests = []
        
        # Basic status code test
        tests.append("// Verify SOAP response status")
        tests.append("pm.test('SOAP request successful', function() {")
        tests.append("    pm.expect(pm.response.code).to.be.oneOf([200, 202]);")
        tests.append("});")
        tests.append("")
        
        # Response time test
        tests.append("// Verify response time")
        tests.append("pm.test('Response time is acceptable', function() {")
        tests.append("    pm.expect(pm.response.responseTime).to.be.below(10000);")
        tests.append("});")
        tests.append("")
        
        # XML response test
        tests.append("// Verify XML response")
        tests.append("pm.test('Response is valid XML', function() {")
        tests.append("    pm.expect(pm.response.headers.get('Content-Type')).to.include('xml');")
        tests.append("});")
        tests.append("")
        
        # Check for SOAP fault
        tests.append("// Check for SOAP Fault")
        tests.append("pm.test('No SOAP Fault returned', function() {")
        tests.append("    const responseText = pm.response.text();")
        tests.append("    pm.expect(responseText).to.not.include('soap:Fault');")
        tests.append("    pm.expect(responseText).to.not.include('faultcode');")
        tests.append("});")
        tests.append("")
        
        return tests
    
    def _extract_host(self, url: str) -> List[str]:
        """Extract host from URL.
        
        Args:
            url: Full URL
            
        Returns:
            List with host parts
        """
        # Remove protocol
        url_without_protocol = url.replace('https://', '').replace('http://', '')
        
        # Extract host (before first /)
        host = url_without_protocol.split('/')[0]
        
        # Remove ?wsdl if present
        host = host.split('?')[0]
        
        return [host]
    
    def _extract_path(self, url: str) -> List[str]:
        """Extract path from URL.
        
        Args:
            url: Full URL
            
        Returns:
            List with path parts
        """
        # Remove protocol
        url_without_protocol = url.replace('https://', '').replace('http://', '')
        
        # Extract path (after first /)
        parts = url_without_protocol.split('/')[1:]
        
        # Remove ?wsdl from last part if present
        if parts and '?' in parts[-1]:
            parts[-1] = parts[-1].split('?')[0]
        
        return parts if parts else []

