"""AI analyzer using OpenAI to validate and enhance API documentation."""
import json
import logging
import time
from typing import List, Dict, Any, Optional
from openai import OpenAI
from config import Config
from context_manager import ContextManager
from models import (
    DocumentationSource, EndpointInfo, FieldInfo, 
    Pattern, HTTPMethod, SOAPOperation, SOAPParameter
)

logger = logging.getLogger("documenter")


class AIAnalyzer:
    """Analyzer that uses OpenAI to extract and validate API documentation."""
    
    def __init__(self, context_manager: Optional[ContextManager] = None, openai_logger: Optional[Any] = None):
        """Initialize the AI analyzer with OpenAI client.
        
        Args:
            context_manager: Optional context manager for maintaining execution context
            openai_logger: Optional OpenAI logger for request/response logging
        """
        Config.validate()
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.OPENAI_MODEL
        self._cache = {}  # Simple cache to avoid duplicate API calls
        self.context = context_manager or ContextManager()
        self.openai_logger = openai_logger
    
    def analyze_documentation(self, doc_source: DocumentationSource) -> DocumentationSource:
        """Analyze documentation and extract/enhance endpoint information.
        
        Args:
            doc_source: Documentation source to analyze
            
        Returns:
            Enhanced DocumentationSource with AI-extracted information
        """
        logger.info("Starting AI analysis of documentation")
        
        # Check if SOAP and handle differently
        if doc_source.api_type == "SOAP":
            return self.analyze_soap_documentation(doc_source)
        
        # If no endpoints were extracted by parser, extract them using AI
        if not doc_source.endpoints:
            doc_source.endpoints = self.extract_endpoints_from_text(doc_source)
        
        # Enhance each endpoint with AI analysis
        enhanced_endpoints = []
        total_endpoints = len(doc_source.endpoints)
        
        for i, endpoint in enumerate(doc_source.endpoints, 1):
            path_str = endpoint.path or '(no path)'
            logger.info(f"Analyzing endpoint {i}/{total_endpoints}: {endpoint.method.value} {path_str}")
            
            try:
                enhanced_endpoint = self.analyze_endpoint(endpoint, doc_source)
                enhanced_endpoints.append(enhanced_endpoint)
                
                # Partial save every 5 endpoints to avoid losing progress
                if i % 5 == 0:
                    doc_source.endpoints = enhanced_endpoints
                    logger.info(f"💾 Progress checkpoint: {i}/{total_endpoints} endpoints analyzed")
                
            except Exception as e:
                path_str = endpoint.path or '(no path)'
                logger.error(f"Error analyzing endpoint {path_str}: {e}")
                # Keep original endpoint if analysis fails
                enhanced_endpoints.append(endpoint)
                continue
        
        doc_source.endpoints = enhanced_endpoints
        
        logger.info(f"AI analysis complete. Analyzed {len(enhanced_endpoints)}/{total_endpoints} endpoints")
        return doc_source
    
    def extract_endpoints_from_text(self, doc_source: DocumentationSource) -> List[EndpointInfo]:
        """Extract endpoint information from unstructured text using AI.
        
        Args:
            doc_source: Documentation source with text content
            
        Returns:
            List of extracted EndpointInfo objects
        """
        logger.info("Extracting endpoints from text using AI")
        
        content_str = self._prepare_content_for_ai(doc_source.content)
        
        prompt = f"""Analyze the following API documentation and extract all endpoints.
        
For each endpoint, identify:
- HTTP method (GET, POST, PUT, PATCH, DELETE, etc.)
- URL path
- Description
- Request parameters and their types
- Response structure
- Error codes mentioned

Documentation:
{content_str}

Return a JSON array of endpoints with this structure:
[
  {{
    "method": "POST",
    "path": "/api/users",
    "description": "Create a new user",
    "request_fields": [
      {{"name": "username", "type": "string", "required": true, "description": "User's username"}},
      {{"name": "email", "type": "string", "required": true, "description": "User's email"}}
    ],
    "response_fields": [
      {{"name": "id", "type": "integer", "description": "User ID"}},
      {{"name": "username", "type": "string", "description": "Username"}}
    ],
    "error_codes": {{
      "400": "Invalid input",
      "409": "User already exists"
    }}
  }}
]

Importante: Responda em português brasileiro.

Retorne apenas JSON válido, sem texto adicional."""
        
        try:
            # Get context for better analysis
            context_info = self.context.get_context_for_prompt('endpoints')
            
            # Add context to prompt if available
            if context_info:
                prompt = f"{context_info}\n\n{prompt}"
            
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert API documentation analyst. Extract structured information from API documentation. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            duration = time.time() - start_time
            result_text = response.choices[0].message.content
            
            # Log request if logger provided
            if self.openai_logger:
                self.openai_logger.log_request(
                    purpose="Extract endpoints from text",
                    prompt=prompt,
                    response=result_text,
                    tokens={
                        'prompt_tokens': response.usage.prompt_tokens,
                        'completion_tokens': response.usage.completion_tokens,
                        'total_tokens': response.usage.total_tokens
                    },
                    duration=duration,
                    model=self.model
                )
            
            # Safe parse with retry
            result = self._safe_parse_json(result_text)
            
            if not result:
                logger.error("Failed to parse endpoints from AI, returning empty list")
                return []
            
            # Handle both direct array and object with array
            if isinstance(result, dict):
                endpoints_data = result.get('endpoints', [])
            else:
                endpoints_data = result
            
            endpoints = self._parse_ai_endpoints(endpoints_data)
            logger.info(f"Extracted {len(endpoints)} endpoints using AI")
            
            # Update context with extracted endpoints
            for endpoint in endpoints:
                self.context.add_operation(
                    f"{endpoint.method.value} {endpoint.path or '(no path)'}",
                    endpoint.description or ''
                )
                # Add fields to context
                for field in endpoint.request_fields + endpoint.response_fields:
                    self.context.add_field(
                        field.name,
                        field.field_type or 'unknown',
                        field.description or ''
                    )
            
            return endpoints
            
        except Exception as e:
            logger.error(f"Error extracting endpoints with AI: {e}")
            return []
    
    def analyze_endpoint(
        self, 
        endpoint: EndpointInfo, 
        doc_source: DocumentationSource
    ) -> EndpointInfo:
        """Analyze and enhance a single endpoint with AI.
        
        Args:
            endpoint: Endpoint to analyze
            doc_source: Full documentation source for context
            
        Returns:
            Enhanced EndpointInfo
        """
        path_str = endpoint.path or '(no path)'
        logger.info(f"Analyzing endpoint: {endpoint.method.value} {path_str}")
        
        # Extract real examples from documentation (for testing)
        real_examples = self.extract_request_examples(doc_source, endpoint)
        if real_examples:
            endpoint.examples = real_examples
            logger.info(f"Saved {len(real_examples)} real examples for testing")
        
        # Analyze request fields
        if endpoint.request_fields:
            endpoint.request_fields = self.analyze_fields(
                endpoint.request_fields,
                f"{endpoint.method.value} {endpoint.path} request",
                doc_source
            )
        
        # Analyze response fields
        if endpoint.response_fields:
            endpoint.response_fields = self.analyze_fields(
                endpoint.response_fields,
                f"{endpoint.method.value} {endpoint.path} response",
                doc_source
            )
        
        # Discover business rules
        business_rules = self.discover_business_rules(endpoint, doc_source)
        if business_rules:
            # Add business rules to endpoint description
            rules_text = "\n\nBusiness Rules:\n" + "\n".join(f"- {rule}" for rule in business_rules)
            endpoint.description = (endpoint.description or "") + rules_text
        
        return endpoint
    
    def analyze_fields(
        self, 
        fields: List[FieldInfo], 
        context: str,
        doc_source: DocumentationSource
    ) -> List[FieldInfo]:
        """Analyze and enhance field information using AI.
        
        Args:
            fields: List of fields to analyze
            context: Context description (e.g., "POST /users request")
            doc_source: Full documentation source
            
        Returns:
            Enhanced list of FieldInfo objects
        """
        if not fields:
            return fields
        
        # Create cache key
        cache_key = f"fields_{context}_{len(fields)}"
        if cache_key in self._cache:
            logger.debug(f"Using cached analysis for {context}")
            return self._cache[cache_key]
        
        # Prepare field data for AI
        fields_data = [
            {
                "name": f.name,
                "type": f.field_type,
                "required": f.required,
                "description": f.description
            }
            for f in fields
        ]
        
        content_preview = self._prepare_content_for_ai(doc_source.content, max_length=2000)
        
        prompt = f"""Analyze these API fields for: {context}

Current field information:
{json.dumps(fields_data, indent=2)}

Documentation context:
{content_preview}

For each field, provide:
1. Confirmed or corrected data type (string, integer, boolean, object, array, etc.)
2. Whether it's required or optional
3. Clear description of the field's purpose
4. Any validation rules or constraints (min/max length, format, allowed values, etc.)
5. Possible values if it's an enum or has limited options

Return JSON with this structure:
{{
  "fields": [
    {{
      "name": "field_name",
      "type": "string",
      "required": true,
      "description": "Clear description",
      "constraints": {{
        "minLength": 3,
        "maxLength": 50,
        "pattern": "regex pattern if applicable"
      }},
      "possible_values": ["value1", "value2"]
    }}
  ]
}}

Importante: Responda em português brasileiro.

Retorne apenas JSON válido."""
        
        try:
            # Add context to improve analysis
            context_info = self.context.get_context_for_prompt('fields')
            if context_info:
                prompt = f"{context_info}\n\n{prompt}"
            
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing API field specifications and validation rules."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            duration = time.time() - start_time
            result_text = response.choices[0].message.content
            
            # Log request
            if self.openai_logger:
                self.openai_logger.log_request(
                    purpose=f"Analyze fields for {context}",
                    prompt=prompt,
                    response=result_text,
                    tokens={
                        'prompt_tokens': response.usage.prompt_tokens,
                        'completion_tokens': response.usage.completion_tokens,
                        'total_tokens': response.usage.total_tokens
                    },
                    duration=duration,
                    model=self.model
                )
            
            result = self._safe_parse_json(result_text)
            
            if not result:
                logger.warning(f"Failed to analyze fields for {context}, keeping original")
                return fields
            
            # Update fields with AI analysis
            enhanced_fields = []
            ai_fields = result.get('fields', [])
            
            for field in fields:
                # Find matching AI analysis
                ai_field = next((f for f in ai_fields if f['name'] == field.name), None)
                
                if ai_field:
                    field.field_type = ai_field.get('type', field.field_type)
                    field.required = ai_field.get('required', field.required)
                    field.description = ai_field.get('description', field.description)
                    field.constraints = ai_field.get('constraints', field.constraints)
                    field.possible_values = ai_field.get('possible_values', field.possible_values)
                
                enhanced_fields.append(field)
            
            # Cache the result
            self._cache[cache_key] = enhanced_fields
            
            return enhanced_fields
            
        except Exception as e:
            logger.error(f"Error analyzing fields with AI: {e}")
            return fields
    
    def discover_business_rules(
        self, 
        endpoint: EndpointInfo,
        doc_source: DocumentationSource
    ) -> List[str]:
        """Discover hidden business rules for an endpoint.
        
        Args:
            endpoint: Endpoint to analyze
            doc_source: Full documentation source
            
        Returns:
            List of discovered business rules
        """
        path_str = endpoint.path or '(no path)'
        cache_key = f"rules_{endpoint.method.value}_{path_str}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        content_preview = self._prepare_content_for_ai(doc_source.content, max_length=2000)
        
        prompt = f"""Analyze this API endpoint and discover any business rules, validation logic, or behavioral patterns.

Endpoint: {endpoint.method.value} {endpoint.path or '(no path)'}
Description: {endpoint.description or 'Not provided'}

Documentation context:
{content_preview}

Look for:
- Validation rules not explicitly stated
- Conditional logic (if X then Y)
- Field dependencies (field A requires field B)
- Value constraints and relationships
- Error conditions and their causes
- State transitions or workflow rules

Return JSON:
{{
  "rules": [
    "Rule description 1",
    "Rule description 2"
  ]
}}

Importante: Responda em português brasileiro.

Retorne apenas JSON válido."""
        
        try:
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at discovering implicit business rules and validation logic in API documentation."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            duration = time.time() - start_time
            result_text = response.choices[0].message.content
            
            # Log request
            if self.openai_logger:
                self.openai_logger.log_request(
                    purpose=f"Discover business rules for {endpoint.method.value} {endpoint.path}",
                    prompt=prompt,
                    response=result_text,
                    tokens={
                        'prompt_tokens': response.usage.prompt_tokens,
                        'completion_tokens': response.usage.completion_tokens,
                        'total_tokens': response.usage.total_tokens
                    },
                    duration=duration,
                    model=self.model
                )
            
            result = self._safe_parse_json(result_text)
            
            if not result:
                logger.warning("Failed to discover business rules")
                return []
            
            rules = result.get('rules', [])
            
            # Cache the result
            self._cache[cache_key] = rules
            
            # Add rules to context
            for rule in rules:
                self.context.add_business_rule(rule)
            
            return rules
            
        except Exception as e:
            logger.error(f"Error discovering business rules with AI: {e}")
            return []
    
    def _parse_ai_endpoints(self, endpoints_data: List[Dict[str, Any]]) -> List[EndpointInfo]:
        """Parse AI-extracted endpoint data into EndpointInfo objects.
        
        Args:
            endpoints_data: Raw endpoint data from AI
            
        Returns:
            List of EndpointInfo objects
        """
        endpoints = []
        
        for ep_data in endpoints_data:
            try:
                # Parse method
                method_str = ep_data.get('method', 'GET')
                try:
                    method = HTTPMethod[method_str]
                except KeyError:
                    method = HTTPMethod.GET
                
                # Parse request fields
                request_fields = []
                for field_data in ep_data.get('request_fields', []):
                    field = FieldInfo(
                        name=field_data.get('name', ''),
                        field_type=field_data.get('type'),
                        required=field_data.get('required'),
                        description=field_data.get('description', '')
                    )
                    request_fields.append(field)
                
                # Parse response fields
                response_fields = []
                for field_data in ep_data.get('response_fields', []):
                    field = FieldInfo(
                        name=field_data.get('name', ''),
                        field_type=field_data.get('type'),
                        description=field_data.get('description', '')
                    )
                    response_fields.append(field)
                
                # Parse error codes
                error_codes = {}
                error_codes_data = ep_data.get('error_codes', {})
                if isinstance(error_codes_data, dict):
                    for code, desc in error_codes_data.items():
                        try:
                            error_codes[int(code)] = desc
                        except (ValueError, TypeError):
                            pass
                
                endpoint = EndpointInfo(
                    path=ep_data.get('path', ''),
                    method=method,
                    description=ep_data.get('description', ''),
                    request_fields=request_fields,
                    response_fields=response_fields,
                    error_codes=error_codes
                )
                
                endpoints.append(endpoint)
                
            except Exception as e:
                logger.error(f"Error parsing AI endpoint data: {e}")
                continue
        
        return endpoints
    
    def _chunk_content(self, content: Any, chunk_size: int = 4000) -> List[str]:
        """Divide content into smaller chunks for processing.
        
        Args:
            content: Content to chunk
            chunk_size: Size of each chunk
            
        Returns:
            List of content chunks
        """
        text = str(content)
        chunks = []
        
        for i in range(0, len(text), chunk_size):
            chunks.append(text[i:i + chunk_size])
        
        logger.info(f"Divided content into {len(chunks)} chunks of ~{chunk_size} chars")
        return chunks
    
    def _deduplicate_soap_operations(self, operations: List[SOAPOperation]) -> List[SOAPOperation]:
        """Remove duplicate SOAP operations.
        
        Args:
            operations: List of operations (may have duplicates)
            
        Returns:
            List of unique operations
        """
        seen_names = set()
        unique = []
        
        for op in operations:
            if op.name not in seen_names:
                seen_names.add(op.name)
                unique.append(op)
        
        logger.info(f"Deduplicated {len(operations)} operations to {len(unique)} unique")
        return unique
    
    def analyze_soap_documentation(self, doc_source: DocumentationSource) -> DocumentationSource:
        """Analyze SOAP documentation and extract operations.
        
        Args:
            doc_source: Documentation source
            
        Returns:
            Enhanced DocumentationSource with SOAP operations
        """
        logger.info("Analyzing SOAP documentation with AI (using chunking)")
        
        # Chunk content to avoid missing operations
        chunks = self._chunk_content(doc_source.content, chunk_size=5000)
        all_operations = []
        
        # Process each chunk
        for i, chunk in enumerate(chunks, 1):
            logger.info(f"Processing chunk {i}/{len(chunks)} for SOAP operations")
            
            ops = self._extract_soap_operations_from_chunk(chunk, doc_source)
            all_operations.extend(ops)
            
            if len(chunks) > 1:
                import time
                time.sleep(1)  # Avoid rate limiting
        
        # Deduplicate operations
        unique_operations = self._deduplicate_soap_operations(all_operations)
        
        doc_source.soap_operations = unique_operations
        doc_source.endpoints = [op.to_endpoint_info() for op in unique_operations]
        
        logger.info(f"Total SOAP operations extracted: {len(unique_operations)}")
        return doc_source
    
    def _extract_soap_operations_from_chunk(
        self,
        content_chunk: str,
        doc_source: DocumentationSource
    ) -> List[SOAPOperation]:
        """Extract SOAP operations from a content chunk.
        
        Args:
            content_chunk: Chunk of content
            doc_source: Documentation source (for metadata)
            
        Returns:
            List of SOAP operations found in this chunk
        """
        content_str = content_chunk[:5000]  # Limit chunk size
        
        prompt = f"""Analise esta documentação SOAP/Web Service e extraia TODAS as operações SOAP encontradas.

Documentação:
{content_str}

Para cada operação SOAP encontrada, identifique:
- Operation name
- Namespace (if mentioned)
- SOAPAction (if mentioned)
- WSDL URL
- Input parameters (name, XML type, required/optional, description)
- Output parameters (name, XML type, description)

Return a JSON array of SOAP operations with this structure:
{{
  "operations": [
    {{
      "name": "operationName",
      "namespace": "http://example.com/namespace",
      "soap_action": "operationName",
      "wsdl_url": "https://example.com/service?wsdl",
      "description": "What this operation does",
      "input_params": [
        {{"name": "param1", "xml_type": "string", "required": true, "description": "Parameter description"}},
        {{"name": "param2", "xml_type": "int", "required": false, "description": "Optional parameter"}}
      ],
      "output_params": [
        {{"name": "result1", "xml_type": "string", "description": "Result description"}},
        {{"name": "result2", "xml_type": "double", "description": "Another result"}}
      ]
    }}
  ]
}}

Important:
- Use XML/XSD types (string, int, double, boolean, date, dateTime, etc.)
- Identify which parameters are required vs optional
- Extract the actual WSDL URL from the documentation
- Importante: Responda em português brasileiro.

Retorne apenas JSON válido."""
        
        try:
            # Get context for better SOAP analysis
            context_info = self.context.get_context_for_prompt('operations')
            
            # Add context to prompt
            if context_info:
                prompt = f"{context_info}\n\n{prompt}"
            
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing SOAP/Web Service documentation and WSDL specifications. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            duration = time.time() - start_time
            result_text = response.choices[0].message.content.strip()
            
            # Log request
            if self.openai_logger:
                self.openai_logger.log_request(
                    purpose="Analyze SOAP documentation",
                    prompt=prompt,
                    response=result_text,
                    tokens={
                        'prompt_tokens': response.usage.prompt_tokens,
                        'completion_tokens': response.usage.completion_tokens,
                        'total_tokens': response.usage.total_tokens
                    },
                    duration=duration,
                    model=self.model
                )
            
            # Use safe JSON parsing
            result = self._safe_parse_json(result_text)
            
            if not result:
                logger.error("Failed to parse SOAP operations from AI response")
                return []  # Return empty list, not doc_source!
            
            operations_data = result.get('operations', [])
            
            # Convert to SOAPOperation objects
            soap_operations = []
            for op_data in operations_data:
                operation = self._parse_soap_operation(op_data)
                if operation:
                    soap_operations.append(operation)
            
            # Update context with SOAP operations from this chunk
            for operation in soap_operations:
                self.context.add_operation(operation.name, operation.description or '')
                if operation.namespace:
                    self.context.add_namespace(operation.namespace)
                
                # Add parameters to context
                for param in operation.input_params + operation.output_params:
                    self.context.add_field(
                        param.name,
                        param.xml_type,
                        param.description or ''
                    )
            
            logger.info(f"Extracted {len(soap_operations)} SOAP operations from chunk")
            return soap_operations  # Return list, not doc_source!
            
        except Exception as e:
            logger.error(f"Error analyzing SOAP chunk: {e}")
            return []  # Return empty list on error
    
    def _parse_soap_operation(self, op_data: Dict[str, Any]) -> Optional[SOAPOperation]:
        """Parse SOAP operation data from AI response.
        
        Args:
            op_data: Operation data dictionary
            
        Returns:
            SOAPOperation object or None
        """
        try:
            # Parse input parameters
            input_params = []
            for param_data in op_data.get('input_params', []):
                param = SOAPParameter(
                    name=param_data.get('name', ''),
                    xml_type=param_data.get('xml_type', 'string'),
                    required=param_data.get('required', False),
                    namespace=param_data.get('namespace'),
                    description=param_data.get('description', ''),
                    example_value=param_data.get('example_value')
                )
                input_params.append(param)
            
            # Parse output parameters
            output_params = []
            for param_data in op_data.get('output_params', []):
                param = SOAPParameter(
                    name=param_data.get('name', ''),
                    xml_type=param_data.get('xml_type', 'string'),
                    required=False,  # Output params are not "required"
                    namespace=param_data.get('namespace'),
                    description=param_data.get('description', '')
                )
                output_params.append(param)
            
            # Create SOAPOperation
            operation = SOAPOperation(
                name=op_data.get('name', ''),
                namespace=op_data.get('namespace', ''),
                soap_action=op_data.get('soap_action', op_data.get('name', '')),
                wsdl_url=op_data.get('wsdl_url', ''),
                description=op_data.get('description', ''),
                input_params=input_params,
                output_params=output_params
            )
            
            return operation
            
        except Exception as e:
            logger.error(f"Error parsing SOAP operation: {e}")
            return None
    
    def _safe_parse_json(self, response_text: str, retry_count: int = 0) -> Optional[Dict[str, Any]]:
        """Safely parse JSON from AI response with robust error handling.
        
        Args:
            response_text: Response text from AI
            retry_count: Current retry attempt
            
        Returns:
            Parsed JSON dict or None
        """
        text = response_text.strip()
        
        # Check if empty
        if not text:
            logger.error("Empty response from AI")
            return None
        
        # Extract JSON from markdown code blocks
        if '```json' in text:
            try:
                text = text.split('```json')[1].split('```')[0].strip()
            except IndexError:
                logger.warning("Malformed JSON markdown block")
        elif '```' in text:
            try:
                text = text.split('```')[1].split('```')[0].strip()
            except IndexError:
                logger.warning("Malformed markdown block")
        
        # Try to parse
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {str(e)}")
            logger.debug(f"Response preview: {text[:300]}...")
            
            # Try to find JSON in the text
            if '{' in text and '}' in text:
                try:
                    start = text.find('{')
                    # Find matching closing brace
                    count = 0
                    for i, char in enumerate(text[start:], start):
                        if char == '{':
                            count += 1
                        elif char == '}':
                            count -= 1
                        if count == 0:
                            json_text = text[start:i+1]
                            return json.loads(json_text)
                except:
                    pass
            
            return None
    
    def extract_base_url(self, doc_source: DocumentationSource) -> Optional[str]:
        """Extract base URL from documentation using AI.
        
        Args:
            doc_source: Documentation source
            
        Returns:
            Base URL or None
        """
        logger.info("Extracting base URL from documentation...")
        
        content_str = self._prepare_content_for_ai(doc_source.content, max_length=3000)
        
        prompt = f"""Extract the base URL/API endpoint from this documentation.

Documentation:
{content_str}

Look for mentions of:
- "base URL", "API endpoint", "server URL", "endpoint"
- URLs like "https://api.example.com" or "http://..."
- "production environment", "staging", "prod"
- "WSDL URL" (for SOAP)

Return JSON with the base URL (prefer production over staging):
{{
  "base_url": "https://api.example.com/api",
  "environment": "production"
}}

Important:
- Return the URL WITHOUT trailing slash
- If WSDL, return the service endpoint (without ?wsdl)
- Prefer production over staging/dev
- Only return valid JSON"""
        
        try:
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at extracting API base URLs from documentation. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            duration = time.time() - start_time
            result_text = response.choices[0].message.content
            
            # Log request
            if self.openai_logger:
                self.openai_logger.log_request(
                    purpose="Extract base URL from documentation",
                    prompt=prompt,
                    response=result_text,
                    tokens={
                        'prompt_tokens': response.usage.prompt_tokens,
                        'completion_tokens': response.usage.completion_tokens,
                        'total_tokens': response.usage.total_tokens
                    },
                    duration=duration,
                    model=self.model
                )
            
            result = self._safe_parse_json(result_text)
            
            if result and 'base_url' in result:
                base_url = result['base_url'].rstrip('/')
                environment = result.get('environment', 'production')
                
                logger.info(f"Extracted base URL: {base_url} ({environment})")
                return base_url
            else:
                logger.warning("Could not extract base URL from documentation")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting base URL: {e}")
            return None
    
    def extract_request_examples(
        self,
        doc_source: DocumentationSource,
        endpoint: EndpointInfo
    ) -> List[Dict[str, Any]]:
        """Extract real, working request examples from documentation.
        
        Args:
            doc_source: Documentation source
            endpoint: Endpoint to extract examples for
            
        Returns:
            List of example request dictionaries
        """
        logger.info(f"Extracting real examples for {endpoint.method.value} {endpoint.path}")
        
        # Prepare content focusing on this specific endpoint
        content_str = self._prepare_content_for_ai(doc_source.content, max_length=5000)
        
        prompt = f"""Extract REAL, WORKING request examples from this API documentation.

Endpoint: {endpoint.method.value} {endpoint.path or '(no path)'}
Description: {endpoint.description or 'Not provided'}

Documentation:
{content_str}

Find and extract:
- Real request body examples that actually WORK
- Valid values shown in examples
- Sample data from documentation
- Working credentials if shown (test accounts)
- Response examples

Look for sections like:
- "Example request"
- "Sample payload"
- "Request body example"
- Body in response examples

Return JSON:
{{
  "examples": [
    {{
      "body": {{"field1": "real_value", "field2": "real_value"}},
      "description": "Valid example from documentation",
      "expected_status": 200
    }}
  ]
}}

Important:
- Only use values/examples FROM THE DOCUMENTATION
- If documentation shows "CC00000000" as login, use that
- If no real examples found, return empty array
- Prefer complete examples over partial ones

Importante: Responda em português brasileiro.

Retorne apenas JSON válido."""
        
        try:
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at extracting working API examples from documentation. Extract only real examples shown in the documentation."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            duration = time.time() - start_time
            result_text = response.choices[0].message.content
            
            # Log request
            if self.openai_logger:
                self.openai_logger.log_request(
                    purpose=f"Extract real examples for {endpoint.method.value} {endpoint.path}",
                    prompt=prompt,
                    response=result_text,
                    tokens={
                        'prompt_tokens': response.usage.prompt_tokens,
                        'completion_tokens': response.usage.completion_tokens,
                        'total_tokens': response.usage.total_tokens
                    },
                    duration=duration,
                    model=self.model
                )
            
            result = self._safe_parse_json(result_text)
            
            if result and 'examples' in result:
                examples = result['examples']
                logger.info(f"Extracted {len(examples)} real examples")
                return examples
            else:
                logger.warning("No real examples found in documentation")
                return []
                
        except Exception as e:
            logger.error(f"Error extracting examples: {e}")
            return []
    
    def _prepare_content_for_ai(self, content: Any, max_length: int = 4000) -> str:
        """Prepare documentation content for AI analysis.
        
        Args:
            content: Documentation content (string, dict, etc.)
            max_length: Maximum length of text to send to AI
            
        Returns:
            String representation of content
        """
        if isinstance(content, str):
            text = content
        elif isinstance(content, (dict, list)):
            text = json.dumps(content, indent=2)
        else:
            text = str(content)
        
        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length] + "\n... (truncated)"
        
        return text

