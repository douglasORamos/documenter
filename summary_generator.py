"""Generator for creating human-readable API summaries."""
import logging
from typing import List, Dict, Any, Optional
from collections import defaultdict
from models import EndpointInfo, Pattern, HTTPMethod

logger = logging.getLogger("documenter")


class APISummaryGenerator:
    """Generates human-readable summaries of API functionality."""
    
    def __init__(self):
        """Initialize the summary generator."""
        pass
    
    def generate_summary(
        self,
        endpoints: List[EndpointInfo],
        patterns: Optional[Dict[str, List[Pattern]]] = None,
        api_name: str = "API",
        api_type: str = "REST"
    ) -> str:
        """Generate a human-readable summary of the API.
        
        Args:
            endpoints: List of endpoints to summarize
            patterns: Optional discovered patterns
            api_name: Name of the API
            api_type: Type of API (REST, SOAP, etc.)
            
        Returns:
            Summary text
        """
        logger.info(f"Generating human-readable summary for {api_name} ({api_type})")
        
        summary_parts = []
        
        # Header (adapted for API type)
        summary_parts.append(self._generate_header(api_name, len(endpoints), api_type))
        
        # Overview
        summary_parts.append(self._generate_overview(endpoints, api_type))
        
        # Endpoints/Operations by category
        if api_type == "SOAP":
            summary_parts.append(self._generate_soap_operations_summary(endpoints))
        else:
            summary_parts.append(self._generate_endpoints_summary(endpoints))
        
        # Main workflows
        summary_parts.append(self._generate_workflows(endpoints, api_type))
        
        # Business rules
        if patterns:
            summary_parts.append(self._generate_business_rules(patterns))
        
        # Data structures
        summary_parts.append(self._generate_data_structures(endpoints, api_type))
        
        # Error handling
        summary_parts.append(self._generate_error_handling(endpoints, api_type))
        
        # Footer (adapted for API type)
        summary_parts.append(self._generate_footer(api_type))
        
        return "\n\n".join(summary_parts)
    
    def save(self, summary: str, output_path: str):
        """Save summary to a text file.
        
        Args:
            summary: Summary text
            output_path: Path to save the file
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        logger.info(f"Saved API summary to: {output_path}")
    
    def _generate_header(self, api_name: str, endpoint_count: int, api_type: str = "REST") -> str:
        """Generate summary header.
        
        Args:
            api_name: API name
            endpoint_count: Number of endpoints
            api_type: Type of API
            
        Returns:
            Header text
        """
        if api_type == "SOAP":
            description = "Este documento apresenta um resumo simplificado do Web Service SOAP,\nfacilitando o entendimento das operações disponíveis."
            count_label = "Total de operações SOAP:"
        else:
            description = "Este documento apresenta um resumo simplificado do funcionamento da API,\nfacilitando o entendimento das principais operações disponíveis."
            count_label = "Total de operações:"
        
        return f"""{'=' * 70}
RESUMO {'DO WEB SERVICE' if api_type == 'SOAP' else 'DA API'}: {api_name}
{'=' * 70}

{description}

{count_label} {endpoint_count}
Tipo: {api_type}"""
    
    def _generate_soap_operations_summary(self, endpoints: List[EndpointInfo]) -> str:
        """Generate SOAP operations summary.
        
        Args:
            endpoints: List of endpoints (converted from SOAP operations)
            
        Returns:
            SOAP operations summary text
        """
        summary = "OPERAÇÕES SOAP DISPONÍVEIS\n" + ("-" * 70)
        
        if not endpoints:
            return summary + "\n\nNenhuma operação SOAP foi identificada."
        
        summary += f"\n\nTotal: {len(endpoints)} operações SOAP\n"
        
        for i, endpoint in enumerate(endpoints, 1):
            # Extract operation name from path
            if endpoint.path and '/' in endpoint.path:
                op_name = endpoint.path.split('/')[-1]
            else:
                op_name = endpoint.description or f"Operation {i}"
            
            summary += f"\n{i}. {op_name}"
            
            # Add description
            if endpoint.description:
                desc = self._simplify_description(endpoint.description)
                summary += f"\n   {desc}"
            
            # Input parameters (request fields)
            if endpoint.request_fields:
                required = [f.name for f in endpoint.request_fields if f.required]
                optional = [f.name for f in endpoint.request_fields if not f.required and f.required is not None]
                
                params_summary = []
                if required:
                    params_summary.append(f"obrigatórios: {', '.join(required[:5])}")
                if optional and len(required) < 3:
                    params_summary.append(f"opcionais: {', '.join(optional[:3])}")
                
                if params_summary:
                    summary += f"\n   Parâmetros XML: {'; '.join(params_summary)}"
                    if len(endpoint.request_fields) > 8:
                        summary += f" (+ {len(endpoint.request_fields) - 8} outros)"
            
            # Output parameters (response fields)
            if endpoint.response_fields:
                output_names = [f.name for f in endpoint.response_fields[:5]]
                summary += f"\n   Retorna (XML): {', '.join(output_names)}"
                if len(endpoint.response_fields) > 5:
                    summary += f" (+ {len(endpoint.response_fields) - 5} outros)"
        
        summary += "\n\n💡 NOTA: Esta é uma API SOAP. As requisições devem usar:"
        summary += "\n   • Método HTTP: POST"
        summary += "\n   • Content-Type: text/xml; charset=utf-8"
        summary += "\n   • Body: XML com SOAP Envelope"
        
        return summary
    
    def _generate_overview(self, endpoints: List[EndpointInfo], api_type: str = "REST") -> str:
        """Generate API overview.
        
        Args:
            endpoints: List of endpoints
            
        Returns:
            Overview text
        """
        # Group by resource
        resources = self._group_by_resource(endpoints)
        
        if api_type == "SOAP":
            overview = "VISÃO GERAL DO WEB SERVICE\n" + ("-" * 70)
            overview += "\n\nEste Web Service SOAP oferece as seguintes operações:\n"
        else:
            overview = "VISÃO GERAL\n" + ("-" * 70)
            overview += "\n\nEsta API permite trabalhar com os seguintes recursos:\n"
        
        for resource, eps in resources.items():
            operations = self._describe_operations(eps)
            overview += f"\n• {resource.upper()}: {operations}"
        
        return overview
    
    def _generate_endpoints_summary(self, endpoints: List[EndpointInfo]) -> str:
        """Generate summary of all endpoints.
        
        Args:
            endpoints: List of endpoints
            
        Returns:
            Endpoints summary text
        """
        summary = "OPERAÇÕES DISPONÍVEIS\n" + ("-" * 70)
        
        # Group by resource
        resources = self._group_by_resource(endpoints)
        
        for resource, eps in sorted(resources.items()):
            summary += f"\n\n📦 {resource.upper()}\n"
            
            for i, endpoint in enumerate(eps, 1):
                path_str = endpoint.path or '(no path)'
                summary += f"\n{i}. {endpoint.method.value} {path_str}\n"
                
                # Add description if available
                if endpoint.description:
                    desc = self._simplify_description(endpoint.description)
                    summary += f"   {desc}\n"
                
                # DETAILED request fields
                if endpoint.request_fields:
                    summary += "\n   📥 PARÂMETROS QUE VOCÊ PRECISA ENVIAR:\n"
                    for field in endpoint.request_fields:
                        field_line = f"   • {field.name}"
                        
                        # Type
                        if field.field_type:
                            field_line += f" ({self._simplify_type(field.field_type)})"
                        
                        # Required
                        if field.required:
                            field_line += " - OBRIGATÓRIO"
                        elif field.required is False:
                            field_line += " - opcional"
                        
                        summary += field_line + "\n"
                        
                        # Description
                        if field.description:
                            summary += f"     {field.description}\n"
                        
                        # Possible values
                        if field.possible_values:
                            values_str = ', '.join(str(v) for v in field.possible_values[:5])
                            summary += f"     Valores possíveis: {values_str}\n"
                        
                        # Constraints
                        if field.constraints:
                            for constraint_key, constraint_val in field.constraints.items():
                                summary += f"     {constraint_key}: {constraint_val}\n"
                    
                    summary += "\n"
                
                # DETAILED response fields
                if endpoint.response_fields:
                    summary += "   📤 O QUE VOCÊ VAI RECEBER:\n"
                    for field in endpoint.response_fields:
                        field_line = f"   • {field.name}"
                        
                        # Type
                        if field.field_type:
                            field_line += f" ({self._simplify_type(field.field_type)})"
                        
                        summary += field_line
                        
                        # Description
                        if field.description:
                            summary += f": {field.description}"
                        
                        summary += "\n"
                    
                    summary += "\n"
        
        return summary
    
    def _generate_workflows(self, endpoints: List[EndpointInfo], api_type: str = "REST") -> str:
        """Generate main workflows description.
        
        Args:
            endpoints: List of endpoints
            
        Returns:
            Workflows text
        """
        workflows = "FLUXOS PRINCIPAIS\n" + ("-" * 70)
        
        # Identify common workflows
        has_create = any(ep.method == HTTPMethod.POST for ep in endpoints)
        has_read = any(ep.method == HTTPMethod.GET for ep in endpoints)
        has_update = any(ep.method in [HTTPMethod.PUT, HTTPMethod.PATCH] for ep in endpoints)
        has_delete = any(ep.method == HTTPMethod.DELETE for ep in endpoints)
        
        workflows += "\n\nFluxos típicos de uso:\n"
        
        if has_create and has_read:
            workflows += "\n1. CRIAR E CONSULTAR"
            workflows += "\n   → Primeiro, crie um novo registro usando a operação de criação"
            workflows += "\n   → Em seguida, consulte os detalhes usando a operação de consulta"
            workflows += "\n   → Você receberá um identificador (ID) ao criar, use-o para consultar"
        
        if has_update:
            workflows += "\n\n2. ATUALIZAR INFORMAÇÕES"
            workflows += "\n   → Consulte o registro atual para ver os dados atuais"
            workflows += "\n   → Envie os novos dados usando a operação de atualização"
            workflows += "\n   → Você pode atualizar apenas os campos que deseja mudar"
        
        if has_delete:
            workflows += "\n\n3. REMOVER REGISTROS"
            workflows += "\n   → Use o identificador (ID) do registro que deseja remover"
            workflows += "\n   → Após remover, o registro não estará mais disponível"
        
        if has_read and any((ep.path and 'list' in ep.path.lower()) or (ep.method == HTTPMethod.GET and ep.path and not '{' in ep.path) for ep in endpoints):
            workflows += "\n\n4. LISTAR E FILTRAR"
            workflows += "\n   → Use a operação de listagem para ver todos os registros"
            workflows += "\n   → Você pode usar filtros para encontrar registros específicos"
            workflows += "\n   → Os resultados geralmente vêm em páginas para facilitar a navegação"
        
        return workflows
    
    def _generate_business_rules(self, patterns: Dict[str, List[Pattern]]) -> str:
        """Generate business rules section.
        
        Args:
            patterns: Discovered patterns by endpoint
            
        Returns:
            Business rules text
        """
        rules_text = "REGRAS E COMPORTAMENTOS\n" + ("-" * 70)
        rules_text += "\n\nRegras importantes descobertas:\n"
        
        rule_count = 0
        seen_rules = set()
        
        for endpoint_key, endpoint_patterns in patterns.items():
            for pattern in endpoint_patterns:
                # Simplify pattern description
                simple_desc = self._simplify_pattern(pattern)
                
                # Avoid duplicates
                if simple_desc and simple_desc not in seen_rules:
                    rule_count += 1
                    rules_text += f"\n{rule_count}. {simple_desc}"
                    seen_rules.add(simple_desc)
        
        if rule_count == 0:
            rules_text += "\nNenhuma regra adicional foi descoberta na análise."
        
        return rules_text
    
    def _generate_data_structures(self, endpoints: List[EndpointInfo], api_type: str = "REST") -> str:
        """Generate data structures overview.
        
        Args:
            endpoints: List of endpoints
            
        Returns:
            Data structures text
        """
        if api_type == "SOAP":
            data_text = "PARÂMETROS XML COMUNS\n" + ("-" * 70)
        else:
            data_text = "ESTRUTURA DOS DADOS\n" + ("-" * 70)
        
        # Collect all unique field names and their types
        field_info = defaultdict(set)
        
        for endpoint in endpoints:
            for field in endpoint.request_fields + endpoint.response_fields:
                if '.' not in field.name:  # Only top-level fields
                    field_type = self._simplify_type(field.field_type)
                    field_desc = field.description or "Sem descrição"
                    field_info[field.name].add((field_type, field_desc[:50]))
        
        if field_info:
            data_text += "\n\nCampos comuns utilizados:\n"
            
            for field_name, info_set in sorted(field_info.items())[:10]:  # Top 10
                field_type, field_desc = list(info_set)[0]
                data_text += f"\n• {field_name}: {field_desc}"
                if field_type and field_type != "desconhecido":
                    data_text += f" (tipo: {field_type})"
        else:
            data_text += "\n\nA estrutura dos dados será definida conforme você utiliza a API."
        
        return data_text
    
    def _generate_error_handling(self, endpoints: List[EndpointInfo], api_type: str = "REST") -> str:
        """Generate error handling section.
        
        Args:
            endpoints: List of endpoints
            
        Returns:
            Error handling text
        """
        if api_type == "SOAP":
            error_text = "TRATAMENTO DE ERROS SOAP\n" + ("-" * 70)
        else:
            error_text = "TRATAMENTO DE ERROS\n" + ("-" * 70)
        
        # Collect all error codes
        all_errors = {}
        for endpoint in endpoints:
            for code, desc in endpoint.error_codes.items():
                if code not in all_errors:
                    all_errors[code] = desc
        
        if all_errors:
            error_text += "\n\nPossíveis situações de erro:\n"
            
            for code in sorted(all_errors.keys()):
                desc = all_errors[code]
                simple_desc = self._simplify_error(code, desc)
                error_text += f"\n• {simple_desc}"
        else:
            if api_type == "SOAP":
                error_text += "\n\nEm caso de erro, o Web Service retorna uma SOAP Fault:"
                error_text += "\n\n• SOAP Fault: Indica que houve um erro no processamento"
                error_text += "\n  - <faultcode>: Código do erro"
                error_text += "\n  - <faultstring>: Descrição do erro"
                error_text += "\n  - <detail>: Detalhes adicionais"
                error_text += "\n\n💡 Dica: Sempre verifique se a resposta contém <soap:Fault>"
            else:
                error_text += "\n\nA API retornará mensagens de erro quando algo não funcionar como esperado."
                error_text += "\nVerifique sempre o código de retorno: 200-299 indica sucesso, 400+ indica erro."
        
        return error_text
    
    def _generate_footer(self, api_type: str = "REST") -> str:
        """Generate summary footer.
        
        Args:
            api_type: Type of API
            
        Returns:
            Footer text
        """
        if api_type == "SOAP":
            usage_text = """COMO USAR ESTE RESUMO

Este documento foi criado para facilitar o entendimento do Web Service SOAP.
Para informações técnicas detalhadas, consulte a documentação completa
ou a Postman Collection gerada.

PRÓXIMOS PASSOS

1. Identifique qual operação SOAP você precisa usar
2. Veja quais parâmetros XML são necessários
3. Monte o XML com SOAP Envelope
4. Envie via POST com Content-Type: text/xml
5. Processe a resposta XML recebida

DICAS SOAP

• Use sempre método POST para chamadas SOAP
• O Content-Type deve ser text/xml ou application/soap+xml
• Todos os parâmetros devem estar dentro de <soap:Body>
• Verifique se não há <soap:Fault> na resposta
• Use ferramentas como SoapUI ou Postman para testar
• Mantenha o namespace correto nas requisições"""
        else:
            usage_text = """COMO USAR ESTE RESUMO

Este documento foi criado para facilitar o entendimento da API.
Para informações técnicas detalhadas, consulte a documentação completa
ou a Postman Collection gerada.

PRÓXIMOS PASSOS

1. Identifique qual operação você precisa usar
2. Veja quais dados são necessários
3. Prepare os dados no formato correto
4. Faça a chamada para a API
5. Verifique a resposta recebida

DICAS

• Sempre verifique o código de resposta (200 = sucesso)
• Guarde os identificadores (IDs) retornados para uso futuro
• Em caso de erro, leia a mensagem de erro para entender o problema
• Comece testando operações simples de consulta antes de criar dados"""
        
        return f"""{'=' * 70}

{usage_text}

{'=' * 70}

Documento gerado automaticamente pelo AI Documentation Enricher"""
    
    def _group_by_resource(self, endpoints: List[EndpointInfo]) -> Dict[str, List[EndpointInfo]]:
        """Group endpoints by resource.
        
        Args:
            endpoints: List of endpoints
            
        Returns:
            Dictionary mapping resource names to endpoints
        """
        resources = defaultdict(list)
        
        for endpoint in endpoints:
            # Extract resource from path (first segment)
            parts = endpoint.path.strip('/').split('/') if endpoint.path else []
            resource = parts[0] if parts else 'geral'
            resources[resource].append(endpoint)
        
        return dict(resources)
    
    def _describe_operations(self, endpoints: List[EndpointInfo]) -> str:
        """Describe what operations are available.
        
        Args:
            endpoints: List of endpoints for a resource
            
        Returns:
            Description text
        """
        operations = []
        
        if any(ep.method == HTTPMethod.POST for ep in endpoints):
            operations.append("criar")
        if any(ep.method == HTTPMethod.GET for ep in endpoints):
            operations.append("consultar")
        if any(ep.method in [HTTPMethod.PUT, HTTPMethod.PATCH] for ep in endpoints):
            operations.append("atualizar")
        if any(ep.method == HTTPMethod.DELETE for ep in endpoints):
            operations.append("remover")
        
        if operations:
            return ", ".join(operations)
        return "operações diversas"
    
    def _describe_endpoint_simple(self, endpoint: EndpointInfo) -> str:
        """Create a simple description of an endpoint.
        
        Args:
            endpoint: Endpoint to describe
            
        Returns:
            Simple description
        """
        method_descriptions = {
            HTTPMethod.GET: "Consultar",
            HTTPMethod.POST: "Criar",
            HTTPMethod.PUT: "Atualizar completamente",
            HTTPMethod.PATCH: "Atualizar parcialmente",
            HTTPMethod.DELETE: "Remover"
        }
        
        action = method_descriptions.get(endpoint.method, endpoint.method.value)
        
        # Simplify path
        path = endpoint.path or ''
        if path and ('{id}' in path or '{' in path):
            resource = path.split('/')[1] if len(path.split('/')) > 1 else "recurso"
            return f"{action} um {resource} específico"
        else:
            resource = path.split('/')[-1] if path and path.split('/') else "recursos"
            if endpoint.method == HTTPMethod.GET:
                return f"{action} {resource}"
            return f"{action} novo {resource}"
    
    def _simplify_description(self, description: str) -> str:
        """Simplify a technical description.
        
        Args:
            description: Original description
            
        Returns:
            Simplified description
        """
        # Take first sentence or first 100 chars
        desc = description.split('\n')[0].split('.')[0]
        if len(desc) > 100:
            desc = desc[:97] + "..."
        
        # Remove technical jargon
        desc = desc.replace('endpoint', 'operação')
        desc = desc.replace('API', 'sistema')
        desc = desc.replace('request', 'requisição')
        desc = desc.replace('response', 'resposta')
        
        return desc
    
    def _summarize_fields(self, fields: List) -> str:
        """Summarize request fields in simple terms.
        
        Args:
            fields: List of field info
            
        Returns:
            Summary text
        """
        if not fields:
            return ""
        
        required = [f.name for f in fields if f.required]
        optional = [f.name for f in fields if not f.required and f.required is not None]
        
        parts = []
        if required:
            parts.append(", ".join(required[:3]))
        if optional and len(required) < 3:
            parts.append(f"(opcional: {', '.join(optional[:2])})")
        
        result = " ".join(parts)
        if len(fields) > 5:
            result += " e outros campos"
        
        return result
    
    def _summarize_response(self, fields: List) -> str:
        """Summarize response fields.
        
        Args:
            fields: List of field info
            
        Returns:
            Summary text
        """
        if not fields:
            return "confirmação da operação"
        
        field_names = [f.name for f in fields[:4] if '.' not in f.name]
        
        if field_names:
            return ", ".join(field_names)
        return "dados do recurso"
    
    def _simplify_type(self, field_type: Optional[str]) -> str:
        """Simplify field type description.
        
        Args:
            field_type: Original type
            
        Returns:
            Simplified type
        """
        if not field_type:
            return "desconhecido"
        
        type_map = {
            'string': 'texto',
            'integer': 'número inteiro',
            'number': 'número',
            'boolean': 'verdadeiro/falso',
            'array': 'lista',
            'object': 'objeto'
        }
        
        return type_map.get(field_type.lower(), field_type)
    
    def _simplify_pattern(self, pattern: Pattern) -> str:
        """Simplify pattern description.
        
        Args:
            pattern: Pattern object
            
        Returns:
            Simplified description
        """
        # Remove technical terms and make it more readable
        desc = pattern.description
        
        # Simplify common technical terms
        desc = desc.replace('field', 'campo')
        desc = desc.replace('validation rule', 'regra de validação')
        desc = desc.replace('HTTP', '')
        desc = desc.replace('endpoint', 'operação')
        
        # Add context based on type
        if pattern.pattern_type == 'validation':
            desc = "Validação: " + desc
        elif pattern.pattern_type == 'error':
            desc = "Erro: " + desc
        elif pattern.pattern_type == 'dependency':
            desc = "Dependência: " + desc
        
        return desc[:150]  # Limit length
    
    def _simplify_error(self, code: int, description: str) -> str:
        """Simplify error description.
        
        Args:
            code: Error code
            description: Error description
            
        Returns:
            Simplified error text
        """
        error_map = {
            400: "Dados inválidos ou incorretos",
            401: "Autenticação necessária ou inválida",
            403: "Sem permissão para esta operação",
            404: "Recurso não encontrado",
            409: "Conflito (ex: recurso já existe)",
            422: "Dados não processáveis",
            500: "Erro interno do sistema"
        }
        
        simple = error_map.get(code, description)
        
        return f"Código {code}: {simple}"

