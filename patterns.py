"""Pattern detector for discovering hidden rules and patterns in API behavior."""
import json
import logging
from typing import List, Dict, Any, Tuple
from collections import defaultdict
from openai import OpenAI
from config import Config
from models import TestResult, Pattern, EndpointInfo

logger = logging.getLogger("documenter")


class PatternDetector:
    """Detects patterns and hidden rules from API test results."""
    
    def __init__(self):
        """Initialize the pattern detector."""
        Config.validate()
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.OPENAI_MODEL
    
    def analyze_test_results(
        self, 
        endpoint: EndpointInfo,
        test_results: List[TestResult]
    ) -> List[Pattern]:
        """Analyze test results to discover patterns.
        
        Args:
            endpoint: The endpoint being tested
            test_results: List of test results for the endpoint
            
        Returns:
            List of discovered patterns
        """
        logger.info(f"Analyzing patterns for {endpoint.method.value} {endpoint.path}")
        
        if not test_results:
            return []
        
        patterns = []
        
        # Detect input-output patterns
        io_patterns = self._detect_input_output_patterns(test_results)
        patterns.extend(io_patterns)
        
        # Detect validation patterns
        validation_patterns = self._detect_validation_patterns(test_results)
        patterns.extend(validation_patterns)
        
        # Detect error patterns
        error_patterns = self._detect_error_patterns(test_results)
        patterns.extend(error_patterns)
        
        # Detect field dependency patterns
        dependency_patterns = self._detect_field_dependencies(test_results)
        patterns.extend(dependency_patterns)
        
        # Use AI to discover more complex patterns
        ai_patterns = self._ai_pattern_discovery(endpoint, test_results)
        patterns.extend(ai_patterns)
        
        logger.info(f"Discovered {len(patterns)} patterns")
        return patterns
    
    def _detect_input_output_patterns(self, test_results: List[TestResult]) -> List[Pattern]:
        """Detect patterns relating input to output.
        
        Args:
            test_results: List of test results
            
        Returns:
            List of input-output patterns
        """
        patterns = []
        
        # Group results by input values
        input_output_map = defaultdict(list)
        
        for result in test_results:
            if result.error or result.response_status >= 400:
                continue
            
            # Create a simplified representation of input
            input_key = self._simplify_payload(result.request_payload)
            input_output_map[input_key].append(result)
        
        # Look for consistent patterns
        for input_key, results in input_output_map.items():
            if len(results) > 1:
                # Check if all results have the same response structure
                if self._check_consistent_responses(results):
                    pattern = Pattern(
                        pattern_type='input_output',
                        description=f"Consistent response structure for input pattern: {input_key}",
                        examples=[
                            {
                                'input': r.request_payload,
                                'output': r.response_body,
                                'status': r.response_status
                            }
                            for r in results[:3]  # Include up to 3 examples
                        ],
                        confidence=0.9
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _detect_validation_patterns(self, test_results: List[TestResult]) -> List[Pattern]:
        """Detect validation patterns from test results.
        
        Args:
            test_results: List of test results
            
        Returns:
            List of validation patterns
        """
        patterns = []
        
        # Analyze failed validations (400 errors)
        validation_failures = [r for r in test_results if r.response_status == 400]
        
        for result in validation_failures:
            # Try to identify what caused the validation failure
            payload = result.request_payload
            response = result.response_body
            
            # Look for error messages in response
            error_message = self._extract_error_message(response)
            
            if error_message:
                # Find which field caused the error
                failed_field = self._identify_failed_field(payload, error_message)
                
                if failed_field:
                    pattern = Pattern(
                        pattern_type='validation',
                        description=f"Validation rule for field '{failed_field}': {error_message}",
                        conditions=[f"Field: {failed_field}"],
                        examples=[{
                            'input': payload,
                            'error': error_message,
                            'status': result.response_status
                        }],
                        confidence=0.8
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _detect_error_patterns(self, test_results: List[TestResult]) -> List[Pattern]:
        """Detect error patterns from test results.
        
        Args:
            test_results: List of test results
            
        Returns:
            List of error patterns
        """
        patterns = []
        
        # Group by status code
        status_groups = defaultdict(list)
        for result in test_results:
            if result.response_status >= 400:
                status_groups[result.response_status].append(result)
        
        for status_code, results in status_groups.items():
            # Find common characteristics
            common_cause = self._find_common_error_cause(results)
            
            if common_cause:
                pattern = Pattern(
                    pattern_type='error',
                    description=f"HTTP {status_code} occurs when: {common_cause}",
                    examples=[
                        {
                            'input': r.request_payload,
                            'status': r.response_status,
                            'error': self._extract_error_message(r.response_body)
                        }
                        for r in results[:3]
                    ],
                    confidence=0.85
                )
                patterns.append(pattern)
        
        return patterns
    
    def _detect_field_dependencies(self, test_results: List[TestResult]) -> List[Pattern]:
        """Detect dependencies between fields.
        
        Args:
            test_results: List of test results
            
        Returns:
            List of dependency patterns
        """
        patterns = []
        
        # Look for cases where presence of one field affects another
        for i, result1 in enumerate(test_results):
            for result2 in test_results[i+1:]:
                # Compare payloads
                diff = self._compare_payloads(
                    result1.request_payload,
                    result2.request_payload
                )
                
                if diff and len(diff) == 1:
                    # Only one field is different
                    changed_field = list(diff.keys())[0]
                    
                    # Check if response differs significantly
                    if result1.response_status != result2.response_status:
                        pattern = Pattern(
                            pattern_type='dependency',
                            description=f"Field '{changed_field}' affects response status",
                            conditions=[
                                f"When {changed_field}={diff[changed_field][0]} -> Status {result1.response_status}",
                                f"When {changed_field}={diff[changed_field][1]} -> Status {result2.response_status}"
                            ],
                            examples=[
                                {'input': result1.request_payload, 'status': result1.response_status},
                                {'input': result2.request_payload, 'status': result2.response_status}
                            ],
                            confidence=0.75
                        )
                        patterns.append(pattern)
        
        return patterns
    
    def _ai_pattern_discovery(
        self, 
        endpoint: EndpointInfo,
        test_results: List[TestResult]
    ) -> List[Pattern]:
        """Use AI to discover complex patterns.
        
        Args:
            endpoint: The endpoint being tested
            test_results: List of test results
            
        Returns:
            List of AI-discovered patterns
        """
        if len(test_results) < 3:
            return []
        
        # Prepare test results summary for AI
        results_summary = []
        for i, result in enumerate(test_results[:10]):  # Limit to 10 results
            results_summary.append({
                'test_num': i + 1,
                'request': result.request_payload,
                'status': result.response_status,
                'response': self._simplify_response(result.response_body),
                'error': result.error
            })
        
        prompt = f"""Analyze these API test results and discover any patterns, rules, or relationships.

Endpoint: {endpoint.method.value} {endpoint.path}

Test Results:
{json.dumps(results_summary, indent=2)}

Look for:
1. Patterns between input values and outputs
2. Validation rules and constraints
3. Field dependencies and relationships
4. Conditions that trigger specific errors
5. Business logic rules

Return JSON with discovered patterns:
{{
  "patterns": [
    {{
      "type": "validation|input_output|dependency|error",
      "description": "Clear description of the pattern",
      "conditions": ["condition 1", "condition 2"],
      "confidence": 0.0-1.0
    }}
  ]
}}

Only return valid JSON."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing API behavior and discovering patterns."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            result_text = response.choices[0].message.content
            result = json.loads(result_text)
            
            patterns = []
            for pattern_data in result.get('patterns', []):
                pattern = Pattern(
                    pattern_type=pattern_data.get('type', 'unknown'),
                    description=pattern_data.get('description', ''),
                    conditions=pattern_data.get('conditions', []),
                    confidence=pattern_data.get('confidence', 0.5)
                )
                patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error in AI pattern discovery: {e}")
            return []
    
    def _simplify_payload(self, payload: Dict[str, Any]) -> str:
        """Create a simplified representation of a payload.
        
        Args:
            payload: Request payload
            
        Returns:
            Simplified string representation
        """
        if not payload:
            return "empty"
        
        # Create a signature based on which fields are present and their types
        signature = []
        for key, value in sorted(payload.items()):
            value_type = type(value).__name__
            signature.append(f"{key}:{value_type}")
        
        return ",".join(signature)
    
    def _check_consistent_responses(self, results: List[TestResult]) -> bool:
        """Check if responses have consistent structure.
        
        Args:
            results: List of test results to compare
            
        Returns:
            True if responses are consistent
        """
        if not results:
            return False
        
        first_structure = self._get_response_structure(results[0].response_body)
        
        for result in results[1:]:
            structure = self._get_response_structure(result.response_body)
            if structure != first_structure:
                return False
        
        return True
    
    def _get_response_structure(self, response_body: Any) -> str:
        """Get a simplified structure signature of a response.
        
        Args:
            response_body: Response body
            
        Returns:
            Structure signature string
        """
        if isinstance(response_body, dict):
            keys = sorted(response_body.keys())
            return f"dict:{','.join(keys)}"
        elif isinstance(response_body, list):
            if response_body:
                return f"list:{self._get_response_structure(response_body[0])}"
            return "list:empty"
        else:
            return type(response_body).__name__
    
    def _extract_error_message(self, response_body: Any) -> str:
        """Extract error message from response body.
        
        Args:
            response_body: Response body
            
        Returns:
            Error message string
        """
        if isinstance(response_body, dict):
            # Common error message keys
            for key in ['error', 'message', 'error_message', 'detail', 'msg']:
                if key in response_body:
                    return str(response_body[key])
        
        return str(response_body)[:200]  # First 200 chars
    
    def _identify_failed_field(self, payload: Dict[str, Any], error_message: str) -> str:
        """Identify which field caused a validation failure.
        
        Args:
            payload: Request payload
            error_message: Error message
            
        Returns:
            Field name that likely caused the error
        """
        error_lower = error_message.lower()
        
        # Look for field names mentioned in error message
        for field_name in payload.keys():
            if field_name.lower() in error_lower:
                return field_name
        
        return ""
    
    def _find_common_error_cause(self, results: List[TestResult]) -> str:
        """Find common cause for a group of errors.
        
        Args:
            results: List of error results
            
        Returns:
            Description of common cause
        """
        if not results:
            return ""
        
        # Check for common missing fields
        all_payloads = [r.request_payload for r in results if r.request_payload]
        if not all_payloads:
            return "empty or missing request body"
        
        # Find fields that are consistently missing or invalid
        first_payload = all_payloads[0]
        common_fields = set(first_payload.keys())
        
        for payload in all_payloads[1:]:
            common_fields &= set(payload.keys())
        
        # Look for fields mentioned in error messages
        error_messages = [self._extract_error_message(r.response_body) for r in results]
        common_terms = set()
        
        for msg in error_messages:
            words = msg.lower().split()
            common_terms.update(words)
        
        # Find most common non-trivial words
        relevant_terms = [
            term for term in common_terms 
            if len(term) > 3 and term not in ['the', 'and', 'for', 'with']
        ]
        
        if relevant_terms:
            return f"related to: {', '.join(list(relevant_terms)[:3])}"
        
        return "specific input conditions"
    
    def _compare_payloads(
        self, 
        payload1: Dict[str, Any], 
        payload2: Dict[str, Any]
    ) -> Dict[str, Tuple[Any, Any]]:
        """Compare two payloads and return differences.
        
        Args:
            payload1: First payload
            payload2: Second payload
            
        Returns:
            Dictionary of differences {field: (value1, value2)}
        """
        differences = {}
        
        all_keys = set(payload1.keys()) | set(payload2.keys())
        
        for key in all_keys:
            val1 = payload1.get(key)
            val2 = payload2.get(key)
            
            if val1 != val2:
                differences[key] = (val1, val2)
        
        return differences
    
    def _simplify_response(self, response_body: Any) -> Any:
        """Simplify response body for AI analysis.
        
        Args:
            response_body: Response body
            
        Returns:
            Simplified response
        """
        if isinstance(response_body, str):
            # Truncate long strings
            return response_body[:200] if len(response_body) > 200 else response_body
        
        return response_body

