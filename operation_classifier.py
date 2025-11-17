"""Operation classifier to identify production vs safe operations using AI."""
import json
import logging
import time
from typing import Dict, Any, List, Optional
from openai import OpenAI
from config import Config
from models import EndpointInfo, SOAPOperation

logger = logging.getLogger("documenter")


class OperationClassifier:
    """Classifies operations to identify production/risky operations."""
    
    # High-risk keywords that indicate production operations
    PRODUCTION_KEYWORDS = {
        'criar': ['criar', 'gravar', 'inserir', 'salvar', 'cadastrar', 'digitar', 'registrar'],
        'aprovar': ['aprovar', 'confirmar', 'efetivar', 'finalizar', 'concluir', 'validar'],
        'modificar': ['atualizar', 'modificar', 'alterar', 'editar', 'mudar'],
        'deletar': ['deletar', 'remover', 'excluir', 'cancelar', 'apagar'],
        'enviar': ['enviar', 'submeter', 'processar', 'executar']
    }
    
    def __init__(self, use_ai: bool = True, openai_logger: Optional[Any] = None):
        """Initialize the classifier.
        
        Args:
            use_ai: Whether to use AI for classification (more accurate)
            openai_logger: Optional OpenAI logger for request logging
        """
        self.use_ai = use_ai
        self.openai_logger = openai_logger
        
        if use_ai:
            try:
                Config.validate()
                self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
                self.model = Config.OPENAI_MODEL
            except:
                logger.warning("Could not initialize AI for classification, using keyword-based")
                self.use_ai = False
        
        self._cache = {}
    
    def classify_operation(
        self, 
        endpoint: EndpointInfo,
        context: str = ""
    ) -> Dict[str, Any]:
        """Classify an operation to determine if it affects production.
        
        Args:
            endpoint: Endpoint or operation to classify
            context: Additional context from documentation
            
        Returns:
            Classification dict with is_production, risk_level, reason, effects
        """
        # Create cache key
        path_str = endpoint.path or '(no path)'
        cache_key = f"{endpoint.method.value}_{path_str}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Extract operation name
        operation_name = self._extract_operation_name(endpoint)
        
        # Try AI classification first if enabled
        if self.use_ai:
            classification = self._classify_with_ai(operation_name, endpoint, context)
        else:
            classification = self._classify_with_keywords(operation_name, endpoint)
        
        # Cache result
        self._cache[cache_key] = classification
        
        return classification
    
    def _classify_with_ai(
        self,
        operation_name: str,
        endpoint: EndpointInfo,
        context: str
    ) -> Dict[str, Any]:
        """Use AI to classify operation.
        
        Args:
            operation_name: Name of the operation
            endpoint: Endpoint information
            context: Additional context
            
        Returns:
            Classification dictionary
        """
        prompt = f"""Analyze this API operation and determine if it creates or modifies PERMANENT data in a PRODUCTION system.

Operation Name: {operation_name}
HTTP Method: {endpoint.method.value}
Path: {endpoint.path or '(no path)'}
Description: {endpoint.description or 'Not provided'}

Context: {context[:500] if context else 'No additional context'}

PRODUCTION operations include those that:
- Create real data (proposals, contracts, customers)
- Approve/confirm/finalize transactions
- Register/save in production databases
- Send to external systems
- Perform financial operations
- Delete permanent data

Examples of PRODUCTION operations:
- gravarProposta (saves proposal to production)
- digitarContrato (registers contract)
- aprovarProposta (approves proposal)
- criarCliente (creates customer)
- efetivarPagamento (executes payment)

Examples of SAFE operations:
- buscarProposta (search/query)
- consultarStatus (check status)
- simular (simulate, no persistence)
- validar (validate without saving)
- listar (list/read)

Return JSON:
{{
  "is_production": true or false,
  "risk_level": "LOW" or "MEDIUM" or "HIGH",
  "effects": ["creates_data", "permanent", "production"],
  "reason": "Clear explanation of why this is/isn't production"
}}

Importante: Responda em português brasileiro.

Retorne apenas JSON válido."""
        
        try:
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing API operations and identifying which ones affect production systems. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            duration = time.time() - start_time
            result_text = response.choices[0].message.content.strip()
            
            # Log request
            if self.openai_logger:
                self.openai_logger.log_request(
                    purpose=f"Classify operation: {operation_name}",
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
            
            # Extract JSON if wrapped
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0].strip()
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0].strip()
            
            result = json.loads(result_text)
            
            logger.info(f"AI classified '{operation_name}': {'PRODUCTION' if result.get('is_production') else 'SAFE'}")
            
            return {
                'is_production': result.get('is_production', False),
                'risk_level': result.get('risk_level', 'LOW'),
                'effects': result.get('effects', []),
                'reason': result.get('reason', 'AI analysis')
            }
            
        except Exception as e:
            logger.error(f"Error in AI classification: {e}")
            # Fallback to keyword-based
            return self._classify_with_keywords(operation_name, endpoint)
    
    def _classify_with_keywords(
        self,
        operation_name: str,
        endpoint: EndpointInfo
    ) -> Dict[str, Any]:
        """Classify operation using keywords.
        
        Args:
            operation_name: Operation name
            endpoint: Endpoint information
            
        Returns:
            Classification dictionary
        """
        operation_lower = operation_name.lower()
        description_lower = (endpoint.description or '').lower()
        combined_text = f"{operation_lower} {description_lower}"
        
        is_production = False
        risk_level = "LOW"
        effects = []
        reason = "Safe operation"
        
        # Check for production keywords
        for category, keywords in self.PRODUCTION_KEYWORDS.items():
            for keyword in keywords:
                if keyword in combined_text:
                    is_production = True
                    risk_level = "HIGH" if category in ['criar', 'aprovar', 'deletar'] else "MEDIUM"
                    effects.append(f"{category}_operation")
                    reason = f"Contains '{keyword}' - indicates {category} operation"
                    break
            if is_production:
                break
        
        # Additional checks for safe operations
        safe_keywords = ['buscar', 'consultar', 'listar', 'obter', 'simular', 'validar', 'verificar', 'search', 'list', 'get', 'find', 'check', 'validate']
        for safe_keyword in safe_keywords:
            if safe_keyword in combined_text:
                is_production = False
                risk_level = "LOW"
                effects = ['read_only']
                reason = f"Contains '{safe_keyword}' - read-only operation"
                break
        
        # HTTP method check (additional heuristic)
        if endpoint.method.value == 'GET' and not is_production:
            risk_level = "LOW"
            effects = ['read_only']
        
        return {
            'is_production': is_production,
            'risk_level': risk_level,
            'effects': effects,
            'reason': reason
        }
    
    def _extract_operation_name(self, endpoint: EndpointInfo) -> str:
        """Extract operation name from endpoint.
        
        Args:
            endpoint: Endpoint information
            
        Returns:
            Operation name
        """
        # Try to get from path (handle None case)
        if endpoint.path:
            try:
                path_parts = endpoint.path.strip('/').split('/')
                
                # For SOAP, last part might be operation
                if '?' in endpoint.path:
                    # WSDL URL - try to extract operation name
                    wsdl_part = path_parts[-1].split('?')[0] if path_parts else ''
                    if wsdl_part:
                        return wsdl_part
                
                # For REST, last part or description
                if path_parts:
                    operation_name = path_parts[-1]
                    # Remove path parameters
                    if '{' in operation_name:
                        operation_name = path_parts[-2] if len(path_parts) > 1 else operation_name
                    if operation_name:
                        return operation_name
            except (AttributeError, TypeError):
                # Path might be None or not a string
                pass
        
        # For SOAP operations, try to extract from description or other fields
        # Check if description contains operation name
        if endpoint.description:
            # Try to extract first meaningful word from description
            words = endpoint.description.split()
            for word in words:
                # Skip common words
                if word.lower() not in ['a', 'o', 'de', 'da', 'do', 'em', 'para', 'com', 'the', 'a', 'an']:
                    # Clean word (remove punctuation)
                    clean_word = ''.join(c for c in word if c.isalnum())
                    if clean_word and len(clean_word) > 2:
                        return clean_word
        
        # Last resort: return a default name based on method
        if endpoint.method:
            return f"{endpoint.method.value.lower()}_operation"
        
        return 'unknown'
    
    def classify_all_operations(
        self,
        endpoints: List[EndpointInfo],
        context: str = ""
    ) -> Dict[str, Dict[str, Any]]:
        """Classify all operations.
        
        Args:
            endpoints: List of endpoints to classify
            context: Documentation context
            
        Returns:
            Dictionary mapping endpoint keys to classifications
        """
        classifications = {}
        
        for endpoint in endpoints:
            path_str = endpoint.path or '(no path)'
            key = f"{endpoint.method.value} {path_str}"
            classification = self.classify_operation(endpoint, context)
            classifications[key] = classification
        
        return classifications

