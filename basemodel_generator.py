"""Gerador de BaseModels - schemas mínimos dos endpoints."""
import json
import logging
from typing import List, Dict, Any
from datetime import datetime
from models import EndpointInfo, FieldInfo

logger = logging.getLogger("documenter")


class BaseModelGenerator:
    """Gera arquivo com schemas mínimos (apenas campos obrigatórios)."""
    
    def __init__(self):
        """Inicializa o gerador."""
        pass
    
    def generate(self, endpoints: List[EndpointInfo]) -> str:
        """Gera basemodels para todos os endpoints.
        
        Args:
            endpoints: Lista de endpoints
            
        Returns:
            Texto formatado com basemodels
        """
        logger.info(f"Gerando basemodels para {len(endpoints)} endpoints")
        
        lines = []
        
        # Header
        lines.append("=" * 70)
        lines.append("BASEMODELS - SCHEMAS MÍNIMOS DOS ENDPOINTS")
        lines.append("=" * 70)
        lines.append(f"Gerado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        lines.append("")
        lines.append("Este arquivo mostra o MÍNIMO OBRIGATÓRIO para cada endpoint funcionar.")
        lines.append("Use como referência rápida do que precisa enviar.")
        lines.append("")
        lines.append("=" * 70)
        
        # Gerar para cada endpoint
        for endpoint in endpoints:
            basemodel = self._generate_endpoint_basemodel(endpoint)
            if basemodel:  # Só adiciona se tiver campos obrigatórios
                lines.append("")
                lines.append(basemodel)
                lines.append("-" * 70)
        
        # Footer
        lines.append("")
        lines.append("=" * 70)
        lines.append("FIM DOS BASEMODELS")
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def save(self, basemodels_text: str, output_path: str):
        """Salva basemodels em arquivo.
        
        Args:
            basemodels_text: Texto dos basemodels
            output_path: Caminho do arquivo
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(basemodels_text)
            
            logger.info(f"Basemodels salvos em: {output_path}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar basemodels: {e}")
    
    def _generate_endpoint_basemodel(self, endpoint: EndpointInfo) -> str:
        """Gera basemodel para um endpoint.
        
        Args:
            endpoint: Endpoint
            
        Returns:
            Texto formatado do basemodel ou string vazia
        """
        # Pegar apenas campos obrigatórios
        required_fields = [f for f in endpoint.request_fields if f.required]
        
        # Se não tem campos obrigatórios, pular
        if not required_fields:
            return ""
        
        lines = []
        
        # Título
        lines.append(f"ENDPOINT: {endpoint.method.value} {endpoint.path}")
        lines.append("")
        
        # Descrição se tiver
        if endpoint.description:
            desc = endpoint.description.split('\n')[0][:100]
            lines.append(f"Descrição: {desc}")
            lines.append("")
        
        # Campos obrigatórios
        lines.append("CAMPOS OBRIGATÓRIOS:")
        
        for field in required_fields:
            # Nome e tipo
            field_line = f"• {field.name}"
            if field.field_type:
                field_line += f" ({field.field_type}"
                
                # Constraints
                if field.constraints:
                    constraints = []
                    if 'minLength' in field.constraints:
                        constraints.append(f"{field.constraints['minLength']}")
                    if 'maxLength' in field.constraints:
                        constraints.append(f"-{field.constraints['maxLength']} chars")
                    if constraints:
                        field_line += f", {' '.join(constraints)}"
                
                field_line += ")"
            
            lines.append(field_line)
            
            # Descrição
            if field.description:
                lines.append(f"  O que é: {field.description[:80]}")
            
            # Exemplo
            example_value = self._get_example_value(field)
            lines.append(f"  Exemplo: {json.dumps(example_value, ensure_ascii=False)}")
            lines.append("")
        
        # JSON mínimo
        lines.append("JSON MÍNIMO:")
        minimal_json = {}
        for field in required_fields:
            minimal_json[field.name] = self._get_example_value(field)
        
        lines.append(json.dumps(minimal_json, indent=2, ensure_ascii=False))
        
        return "\n".join(lines)
    
    def _get_example_value(self, field: FieldInfo) -> Any:
        """Obtém valor de exemplo para um campo.
        
        Args:
            field: Informações do campo
            
        Returns:
            Valor de exemplo
        """
        # Se tem valores possíveis, usa o primeiro
        if field.possible_values:
            return field.possible_values[0]
        
        # Baseado no tipo
        field_type = (field.field_type or 'string').lower()
        
        if 'string' in field_type or 'str' in field_type:
            # Casos especiais
            if 'email' in field.name.lower():
                return "usuario@email.com"
            elif 'cpf' in field.name.lower():
                return "12345678901"
            elif 'senha' in field.name.lower() or 'password' in field.name.lower():
                return "senha123"
            elif 'key' in field.name.lower() or 'chave' in field.name.lower():
                return "api-key-123"
            elif 'login' in field.name.lower() or 'user' in field.name.lower():
                return "usuario123"
            else:
                return "valor_exemplo"
        
        elif 'int' in field_type or 'number' in field_type:
            return 1
        
        elif 'bool' in field_type:
            return True
        
        elif 'array' in field_type or 'list' in field_type:
            return []
        
        elif 'object' in field_type:
            return {}
        
        else:
            return "valor"

