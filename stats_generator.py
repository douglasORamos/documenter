"""Statistics generator for API analysis."""
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from models import EndpointInfo, TestResult, Pattern

logger = logging.getLogger("documenter")


class StatsGenerator:
    """Generates statistics report for API analysis."""
    
    def __init__(self):
        """Initialize the statistics generator."""
        self.start_time = datetime.now()
    
    def generate_stats(
        self,
        endpoints: List[EndpointInfo],
        test_results: Optional[Dict[str, List[TestResult]]] = None,
        patterns: Optional[Dict[str, List[Pattern]]] = None,
        api_name: str = "API",
        execution_time: float = 0.0
    ) -> str:
        """Generate statistics report.
        
        Args:
            endpoints: List of endpoints analyzed
            test_results: Optional test results
            patterns: Optional discovered patterns
            api_name: Name of the API
            execution_time: Time taken for analysis
            
        Returns:
            Statistics report as string
        """
        logger.info(f"Generating statistics report for {api_name}")
        
        stats_parts = []
        
        # Header
        stats_parts.append(self._generate_header(api_name))
        
        # Summary
        stats_parts.append(self._generate_summary(
            endpoints, test_results, patterns, execution_time
        ))
        
        # Endpoints breakdown
        stats_parts.append(self._generate_endpoints_breakdown(endpoints))
        
        # Testing statistics
        if test_results:
            stats_parts.append(self._generate_testing_stats(test_results))
        
        # Pattern statistics
        if patterns:
            stats_parts.append(self._generate_pattern_stats(patterns))
        
        # Field analysis
        stats_parts.append(self._generate_field_stats(endpoints))
        
        # Footer
        stats_parts.append(self._generate_footer())
        
        return "\n\n".join(stats_parts)
    
    def save(self, stats: str, output_path: str):
        """Save statistics to a text file.
        
        Args:
            stats: Statistics text
            output_path: Path to save the file
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(stats)
        
        logger.info(f"Saved statistics report to: {output_path}")
    
    def _generate_header(self, api_name: str) -> str:
        """Generate header.
        
        Args:
            api_name: API name
            
        Returns:
            Header text
        """
        return f"""{'=' * 70}
ESTATÍSTICAS DA ANÁLISE: {api_name}
{'=' * 70}

Relatório gerado automaticamente pelo AI Documentation Enricher
Data/Hora: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}"""
    
    def _generate_summary(
        self,
        endpoints: List[EndpointInfo],
        test_results: Optional[Dict[str, List[TestResult]]],
        patterns: Optional[Dict[str, List[Pattern]]],
        execution_time: float
    ) -> str:
        """Generate summary section.
        
        Args:
            endpoints: List of endpoints
            test_results: Test results
            patterns: Patterns discovered
            execution_time: Execution time
            
        Returns:
            Summary text
        """
        summary = "RESUMO GERAL\n" + ("-" * 70)
        
        # Endpoints
        summary += f"\n\n📊 Total de Endpoints Analisados: {len(endpoints)}"
        
        # Methods breakdown
        methods_count = {}
        for ep in endpoints:
            method = ep.method.value
            methods_count[method] = methods_count.get(method, 0) + 1
        
        if methods_count:
            summary += "\n\nMétodos HTTP:"
            for method, count in sorted(methods_count.items()):
                summary += f"\n  • {method}: {count} endpoint(s)"
        
        # Fields statistics
        total_request_fields = sum(len(ep.request_fields) for ep in endpoints)
        total_response_fields = sum(len(ep.response_fields) for ep in endpoints)
        
        summary += f"\n\n📝 Campos Identificados:"
        summary += f"\n  • Request: {total_request_fields} campos"
        summary += f"\n  • Response: {total_response_fields} campos"
        summary += f"\n  • Total: {total_request_fields + total_response_fields} campos"
        
        # Testing stats
        if test_results:
            total_tests = sum(len(results) for results in test_results.values())
            summary += f"\n\n🧪 Testes de API Executados: {total_tests}"
        
        # Patterns
        if patterns:
            total_patterns = sum(len(p) for p in patterns.values())
            summary += f"\n\n🔍 Padrões Descobertos: {total_patterns}"
        
        # Execution time
        if execution_time > 0:
            minutes = int(execution_time // 60)
            seconds = int(execution_time % 60)
            if minutes > 0:
                time_str = f"{minutes}m {seconds}s"
            else:
                time_str = f"{seconds}s"
            summary += f"\n\n⏱️  Tempo de Execução: {time_str}"
        
        return summary
    
    def _generate_endpoints_breakdown(self, endpoints: List[EndpointInfo]) -> str:
        """Generate endpoints breakdown.
        
        Args:
            endpoints: List of endpoints
            
        Returns:
            Breakdown text
        """
        breakdown = "DETALHAMENTO DOS ENDPOINTS\n" + ("-" * 70)
        
        if not endpoints:
            breakdown += "\n\nNenhum endpoint foi identificado."
            return breakdown
        
        breakdown += f"\n\nTotal: {len(endpoints)} endpoints\n"
        
        for i, endpoint in enumerate(endpoints, 1):
            breakdown += f"\n{i}. {endpoint.method.value} {endpoint.path}"
            
            # Request fields
            req_count = len(endpoint.request_fields)
            req_required = len([f for f in endpoint.request_fields if f.required])
            if req_count > 0:
                breakdown += f"\n   Request: {req_count} campos ({req_required} obrigatórios)"
            
            # Response fields
            resp_count = len(endpoint.response_fields)
            if resp_count > 0:
                breakdown += f"\n   Response: {resp_count} campos"
            
            # Error codes
            if endpoint.error_codes:
                breakdown += f"\n   Códigos de erro: {len(endpoint.error_codes)}"
        
        return breakdown
    
    def _generate_testing_stats(self, test_results: Dict[str, List[TestResult]]) -> str:
        """Generate testing statistics.
        
        Args:
            test_results: Test results
            
        Returns:
            Testing stats text
        """
        stats = "ESTATÍSTICAS DE TESTES\n" + ("-" * 70)
        
        total_tests = sum(len(results) for results in test_results.values())
        stats += f"\n\nTotal de Testes Executados: {total_tests}"
        
        # Status codes breakdown
        status_counts = {}
        success_count = 0
        error_count = 0
        
        for results in test_results.values():
            for result in results:
                status = result.response_status
                status_counts[status] = status_counts.get(status, 0) + 1
                
                if 200 <= status < 300:
                    success_count += 1
                elif status >= 400:
                    error_count += 1
        
        stats += f"\n\nResultados:"
        stats += f"\n  ✓ Sucesso (2xx): {success_count}"
        stats += f"\n  ✗ Erros (4xx/5xx): {error_count}"
        
        if status_counts:
            stats += "\n\nCódigos de Status Encontrados:"
            for status, count in sorted(status_counts.items()):
                stats += f"\n  • {status}: {count} vez(es)"
        
        # Average response time
        all_times = []
        for results in test_results.values():
            all_times.extend([r.execution_time for r in results if r.execution_time > 0])
        
        if all_times:
            avg_time = sum(all_times) / len(all_times)
            min_time = min(all_times)
            max_time = max(all_times)
            
            stats += f"\n\nTempo de Resposta:"
            stats += f"\n  • Médio: {avg_time:.2f}s"
            stats += f"\n  • Mínimo: {min_time:.2f}s"
            stats += f"\n  • Máximo: {max_time:.2f}s"
        
        return stats
    
    def _generate_pattern_stats(self, patterns: Dict[str, List[Pattern]]) -> str:
        """Generate pattern statistics.
        
        Args:
            patterns: Discovered patterns
            
        Returns:
            Pattern stats text
        """
        stats = "PADRÕES DESCOBERTOS\n" + ("-" * 70)
        
        total_patterns = sum(len(p) for p in patterns.values())
        stats += f"\n\nTotal de Padrões: {total_patterns}"
        
        # Pattern types breakdown
        pattern_types = {}
        for endpoint_patterns in patterns.values():
            for pattern in endpoint_patterns:
                ptype = pattern.pattern_type
                pattern_types[ptype] = pattern_types.get(ptype, 0) + 1
        
        if pattern_types:
            stats += "\n\nTipos de Padrões:"
            for ptype, count in sorted(pattern_types.items()):
                stats += f"\n  • {ptype}: {count}"
        
        # Average confidence
        all_confidences = []
        for endpoint_patterns in patterns.values():
            all_confidences.extend([p.confidence for p in endpoint_patterns])
        
        if all_confidences:
            avg_confidence = sum(all_confidences) / len(all_confidences)
            stats += f"\n\nConfiança Média dos Padrões: {avg_confidence:.0%}"
        
        return stats
    
    def _generate_field_stats(self, endpoints: List[EndpointInfo]) -> str:
        """Generate field statistics.
        
        Args:
            endpoints: List of endpoints
            
        Returns:
            Field stats text
        """
        stats = "ANÁLISE DE CAMPOS\n" + ("-" * 70)
        
        # Collect field types
        field_types_count = {}
        required_count = 0
        optional_count = 0
        
        for endpoint in endpoints:
            for field in endpoint.request_fields + endpoint.response_fields:
                # Count types
                ftype = field.field_type or 'unknown'
                field_types_count[ftype] = field_types_count.get(ftype, 0) + 1
                
                # Count required/optional
                if field.required:
                    required_count += 1
                elif field.required is False:
                    optional_count += 1
        
        total_fields = sum(field_types_count.values())
        stats += f"\n\nTotal de Campos: {total_fields}"
        
        if required_count > 0 or optional_count > 0:
            stats += f"\n\nObrigatoriedade:"
            stats += f"\n  • Obrigatórios: {required_count}"
            stats += f"\n  • Opcionais: {optional_count}"
            stats += f"\n  • Não especificado: {total_fields - required_count - optional_count}"
        
        if field_types_count:
            stats += "\n\nTipos de Dados:"
            for ftype, count in sorted(field_types_count.items(), key=lambda x: -x[1]):
                percentage = (count / total_fields) * 100
                stats += f"\n  • {ftype}: {count} ({percentage:.1f}%)"
        
        # Find most common field names
        field_names_count = {}
        for endpoint in endpoints:
            for field in endpoint.request_fields + endpoint.response_fields:
                name = field.name.split('.')[-1]  # Get last part for nested fields
                field_names_count[name] = field_names_count.get(name, 0) + 1
        
        if field_names_count:
            # Top 10 most common
            top_fields = sorted(field_names_count.items(), key=lambda x: -x[1])[:10]
            stats += "\n\nCampos Mais Comuns:"
            for name, count in top_fields:
                stats += f"\n  • {name}: {count} ocorrência(s)"
        
        return stats
    
    def _generate_footer(self) -> str:
        """Generate footer.
        
        Returns:
            Footer text
        """
        return f"""{'=' * 70}

COMO USAR ESTAS ESTATÍSTICAS

Este relatório fornece uma visão quantitativa da análise realizada.
Use estas informações para:

• Entender a complexidade da API
• Identificar padrões de design
• Avaliar a cobertura da documentação
• Planejar testes e integrações

ARQUIVOS RELACIONADOS

• Postman Collection: Para testar os endpoints
• Resumo em Texto: Para entender a API em linguagem simples
• Estatísticas: Para análise quantitativa (este arquivo)

{'=' * 70}

Gerado por: AI Documentation Enricher v2.0
Powered by OpenAI GPT-4"""

