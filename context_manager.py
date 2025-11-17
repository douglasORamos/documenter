"""Context manager for maintaining analysis context and reducing AI costs."""
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger("documenter")


class ContextManager:
    """Manages execution context to improve AI analysis quality with cheaper models."""
    
    def __init__(self):
        """Initialize the context manager."""
        self.context = {
            'api_type': 'UNKNOWN',
            'api_name': '',
            'wsdl_url': '',
            'base_url': '',
            'namespaces': [],
            'common_terms': [],
            'field_names': set(),
            'field_types': {},
            'operations': [],
            'patterns_found': [],
            'business_rules': [],
            'error_codes': {},
            'validation_rules': [],
            'timestamp': datetime.now().isoformat()
        }
        self.term_frequency = defaultdict(int)
    
    def add_api_info(self, api_type: str, api_name: str = '', base_url: str = ''):
        """Add basic API information.
        
        Args:
            api_type: Type of API (REST, SOAP, etc.)
            api_name: Name of the API
            base_url: Base URL or WSDL URL
        """
        self.context['api_type'] = api_type
        self.context['api_name'] = api_name
        
        if api_type == 'SOAP':
            self.context['wsdl_url'] = base_url
        else:
            self.context['base_url'] = base_url
        
        logger.debug(f"Context updated: API type={api_type}, name={api_name}")
    
    def add_field(self, field_name: str, field_type: str, description: str = ''):
        """Add field information to context.
        
        Args:
            field_name: Name of the field
            field_type: Type of the field
            description: Field description
        """
        self.context['field_names'].add(field_name)
        self.context['field_types'][field_name] = field_type
        
        # Extract important terms from description
        if description:
            self._extract_terms(description)
    
    def add_operation(self, operation_name: str, description: str = ''):
        """Add operation information.
        
        Args:
            operation_name: Name of the operation
            description: Operation description
        """
        self.context['operations'].append({
            'name': operation_name,
            'description': description
        })
        self._extract_terms(description)
    
    def add_business_rule(self, rule: str):
        """Add a business rule to context.
        
        Args:
            rule: Business rule description
        """
        if rule and rule not in self.context['business_rules']:
            self.context['business_rules'].append(rule)
            self._extract_terms(rule)
    
    def add_validation_rule(self, rule: str):
        """Add validation rule to context.
        
        Args:
            rule: Validation rule
        """
        if rule and rule not in self.context['validation_rules']:
            self.context['validation_rules'].append(rule)
    
    def add_error_code(self, code: int, description: str):
        """Add error code information.
        
        Args:
            code: Error code
            description: Error description
        """
        self.context['error_codes'][str(code)] = description
    
    def add_namespace(self, namespace: str):
        """Add XML namespace (for SOAP).
        
        Args:
            namespace: Namespace URI
        """
        if namespace and namespace not in self.context['namespaces']:
            self.context['namespaces'].append(namespace)
    
    def get_context_for_prompt(self, prompt_type: str = 'general') -> str:
        """Get formatted context to include in AI prompts.
        
        Args:
            prompt_type: Type of prompt ('general', 'fields', 'operations', etc.)
            
        Returns:
            Formatted context string
        """
        # Build context summary
        context_parts = []
        
        # API basic info
        context_parts.append(f"API Type: {self.context['api_type']}")
        
        if self.context['api_name']:
            context_parts.append(f"API Name: {self.context['api_name']}")
        
        # SOAP-specific context
        if self.context['api_type'] == 'SOAP':
            if self.context['wsdl_url']:
                context_parts.append(f"WSDL URL: {self.context['wsdl_url']}")
            
            if self.context['namespaces']:
                context_parts.append(f"Namespaces: {', '.join(self.context['namespaces'][:3])}")
        
        # REST-specific context
        elif self.context['base_url']:
            context_parts.append(f"Base URL: {self.context['base_url']}")
        
        # Common terms (domain knowledge)
        if self.context['common_terms']:
            top_terms = self.context['common_terms'][:10]
            context_parts.append(f"Domain Terms: {', '.join(top_terms)}")
        
        # Known fields (for field analysis)
        if prompt_type in ['fields', 'operations'] and self.context['field_names']:
            known_fields = list(self.context['field_names'])[:15]
            context_parts.append(f"Known Fields: {', '.join(known_fields)}")
        
        # Known operations (for pattern analysis)
        if self.context['operations'] and len(self.context['operations']) > 0:
            op_names = [op['name'] for op in self.context['operations'][:10]]
            context_parts.append(f"Operations: {', '.join(op_names)}")
        
        # Business rules (important context)
        if self.context['business_rules'] and len(self.context['business_rules']) > 0:
            context_parts.append(f"Known Rules: {len(self.context['business_rules'])} rules already identified")
        
        # Validation rules
        if self.context['validation_rules'] and len(self.context['validation_rules']) > 0:
            context_parts.append(f"Validations: {len(self.context['validation_rules'])} validation rules found")
        
        if not context_parts:
            return ""
        
        return "CONTEXT:\n" + "\n".join(f"- {part}" for part in context_parts)
    
    def get_full_context(self) -> Dict[str, Any]:
        """Get the full context dictionary.
        
        Returns:
            Complete context dictionary
        """
        # Convert set to list for JSON serialization
        context_copy = self.context.copy()
        context_copy['field_names'] = list(self.context['field_names'])
        context_copy['common_terms'] = self.context['common_terms']
        return context_copy
    
    def save_context(self, output_path: str):
        """Save context to a file.
        
        Args:
            output_path: Path to save the context file
        """
        context_text = self._format_context_for_file()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(context_text)
        
        logger.info(f"Saved execution context to: {output_path}")
    
    def _format_context_for_file(self) -> str:
        """Format context for human-readable file.
        
        Returns:
            Formatted context text
        """
        lines = []
        
        lines.append("=" * 70)
        lines.append("CONTEXTO DE EXECUÇÃO - AI Documentation Enricher")
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"Gerado em: {self.context['timestamp']}")
        lines.append("")
        
        # API Info
        lines.append("INFORMAÇÕES DA API")
        lines.append("-" * 70)
        lines.append(f"Tipo: {self.context['api_type']}")
        if self.context['api_name']:
            lines.append(f"Nome: {self.context['api_name']}")
        if self.context['wsdl_url']:
            lines.append(f"WSDL: {self.context['wsdl_url']}")
        if self.context['base_url']:
            lines.append(f"Base URL: {self.context['base_url']}")
        lines.append("")
        
        # Namespaces (SOAP)
        if self.context['namespaces']:
            lines.append("NAMESPACES XML")
            lines.append("-" * 70)
            for ns in self.context['namespaces']:
                lines.append(f"• {ns}")
            lines.append("")
        
        # Operations
        if self.context['operations']:
            lines.append("OPERAÇÕES IDENTIFICADAS")
            lines.append("-" * 70)
            for i, op in enumerate(self.context['operations'], 1):
                lines.append(f"{i}. {op['name']}")
                if op.get('description'):
                    lines.append(f"   {op['description'][:100]}")
            lines.append(f"\nTotal: {len(self.context['operations'])} operações")
            lines.append("")
        
        # Fields
        if self.context['field_names']:
            lines.append("CAMPOS IDENTIFICADOS")
            lines.append("-" * 70)
            field_list = sorted(list(self.context['field_names']))
            for i, field in enumerate(field_list[:50], 1):
                field_type = self.context['field_types'].get(field, 'unknown')
                lines.append(f"{i}. {field} ({field_type})")
            if len(field_list) > 50:
                lines.append(f"... e mais {len(field_list) - 50} campos")
            lines.append(f"\nTotal: {len(field_list)} campos únicos")
            lines.append("")
        
        # Business Rules
        if self.context['business_rules']:
            lines.append("REGRAS DE NEGÓCIO DESCOBERTAS")
            lines.append("-" * 70)
            for i, rule in enumerate(self.context['business_rules'], 1):
                lines.append(f"{i}. {rule}")
            lines.append("")
        
        # Validation Rules
        if self.context['validation_rules']:
            lines.append("REGRAS DE VALIDAÇÃO")
            lines.append("-" * 70)
            for i, rule in enumerate(self.context['validation_rules'], 1):
                lines.append(f"{i}. {rule}")
            lines.append("")
        
        # Error Codes
        if self.context['error_codes']:
            lines.append("CÓDIGOS DE ERRO")
            lines.append("-" * 70)
            for code, desc in sorted(self.context['error_codes'].items()):
                lines.append(f"• {code}: {desc}")
            lines.append("")
        
        # Common Terms
        if self.context['common_terms']:
            lines.append("TERMOS DO DOMÍNIO")
            lines.append("-" * 70)
            lines.append(f"Termos mais relevantes: {', '.join(self.context['common_terms'][:20])}")
            lines.append("")
        
        # Footer
        lines.append("=" * 70)
        lines.append("")
        lines.append("USO DESTE CONTEXTO")
        lines.append("")
        lines.append("Este arquivo contém o conhecimento acumulado durante a análise.")
        lines.append("O contexto foi usado para:")
        lines.append("• Melhorar a precisão da análise com IA")
        lines.append("• Manter consistência entre operações")
        lines.append("• Reduzir custos usando modelos mais econômicos")
        lines.append("• Identificar padrões e regras")
        lines.append("")
        lines.append("Você pode usar este contexto para:")
        lines.append("• Entender o que foi aprendido sobre a API")
        lines.append("• Documentar o conhecimento do domínio")
        lines.append("• Treinar novos membros da equipe")
        lines.append("• Validar a análise realizada")
        lines.append("")
        lines.append("=" * 70)
        lines.append("Gerado por: AI Documentation Enricher v2.0")
        
        return "\n".join(lines)
    
    def _extract_terms(self, text: str):
        """Extract important terms from text.
        
        Args:
            text: Text to extract terms from
        """
        if not text:
            return
        
        # Simple term extraction (words with 4+ chars, not common words)
        stop_words = {
            'the', 'and', 'for', 'with', 'from', 'this', 'that',
            'para', 'com', 'uma', 'das', 'dos', 'pelo', 'pela',
            'sobre', 'entre', 'quando', 'como', 'mais', 'menos'
        }
        
        words = text.lower().split()
        for word in words:
            # Clean word
            word = ''.join(c for c in word if c.isalnum())
            
            # Count if valid
            if len(word) >= 4 and word not in stop_words:
                self.term_frequency[word] += 1
        
        # Update common terms (top 30 by frequency)
        sorted_terms = sorted(self.term_frequency.items(), key=lambda x: -x[1])
        self.context['common_terms'] = [term for term, _ in sorted_terms[:30]]
    
    def get_model_recommendation(self) -> str:
        """Get recommended model based on context complexity.
        
        Returns:
            Recommended model name
        """
        # For SOAP, might need more powerful model
        if self.context['api_type'] == 'SOAP':
            if len(self.context['operations']) > 10:
                return 'gpt-4o-mini'  # Complex SOAP
            return 'gpt-3.5-turbo'  # Simple SOAP
        
        # For REST
        if len(self.context.get('operations', [])) > 20:
            return 'gpt-4o-mini'  # Large API
        
        return 'gpt-3.5-turbo'  # Default: cheapest option

