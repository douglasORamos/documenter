#!/usr/bin/env python3
"""
AI Documentation Enricher - Execução Simples

Modo de uso ultra-simples:
1. Coloque seu arquivo em input/
2. Execute: python main.py
3. Pronto!
"""

import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

# Adiciona o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import setup_logging
from config import Config
from cli import parse_documentation, auto_detect_input, auto_generate_output
from analyzer import AIAnalyzer
from tester import APITester
from patterns import PatternDetector
from generator import PostmanCollectionGenerator
from summary_generator import APISummaryGenerator
from stats_generator import StatsGenerator
from soap_generator import SOAPCollectionGenerator
from api_detector import APIDetector
from context_manager import ContextManager
from credentials_manager import CredentialsManager
from auth_detector import AuthDetector
from auth_handler import get_auth_handler
from token_manager import TokenManager
from auth_endpoint_detector import AuthEndpointDetector
from operation_classifier import OperationClassifier
from openai_logger import OpenAILogger
from api_logger import APITestLogger
from basemodel_generator import BaseModelGenerator
from models import DocumentationSource

console = Console()
logger = setup_logging()


def main():
    """Função principal - execução simplificada."""
    
    # Banner de boas-vindas
    console.print(Panel.fit(
        "[bold cyan]🚀 AI Documentation Enricher[/bold cyan]\n\n"
        "[white]Analisador e Enriquecedor de Documentação de API[/white]\n"
        "[dim]Powered by OpenAI GPT-4[/dim]",
        title="Bem-vindo",
        border_style="cyan"
    ))
    
    console.print("\n[bold]Como usar:[/bold]")
    console.print("1. ✅ Coloque seu arquivo na pasta [cyan]input/[/cyan]")
    console.print("2. ✅ Execute este programa")
    console.print("3. ✅ Pegue os resultados na pasta [green]output/[/green]\n")
    
    # Detectar arquivo de entrada
    console.print("[cyan]►[/cyan] Procurando arquivo em input/...")
    
    input_file = auto_detect_input()
    
    if not input_file:
        console.print(Panel.fit(
            "[red]❌ Nenhum arquivo encontrado![/red]\n\n"
            "[yellow]Por favor:[/yellow]\n"
            "• Coloque um arquivo de documentação na pasta [cyan]input/[/cyan]\n"
            "• Formatos aceitos: PDF, JSON, Postman, OpenAPI, TXT, Markdown\n\n"
            "[dim]Depois execute novamente: python main.py[/dim]",
            title="Erro",
            border_style="red"
        ))
        sys.exit(1)
    
    console.print(f"[green]✓[/green] Arquivo encontrado: [bold]{os.path.basename(input_file)}[/bold]")
    
    # Gerar caminho de saída
    output_file = auto_generate_output(input_file)
    console.print(f"[green]✓[/green] Saída: [bold]{os.path.basename(output_file)}[/bold]\n")
    
    # Verificar configuração da OpenAI
    try:
        Config.validate()
    except ValueError as e:
        console.print(Panel.fit(
            f"[red]❌ Erro de Configuração[/red]\n\n"
            f"{e}\n\n"
            "[yellow]Configure a OpenAI:[/yellow]\n"
            "1. Copie .env.example para .env\n"
            "2. Adicione sua OPENAI_API_KEY no arquivo .env\n"
            "3. Execute novamente",
            title="Configuração Necessária",
            border_style="red"
        ))
        sys.exit(1)
    
    # Auto-detectar se deve testar API (se credentials.json existe)
    credentials_file = 'input/credentials.json'
    test_api = os.path.exists(credentials_file)
    
    if test_api:
        console.print("[green]✓[/green] Credenciais encontradas, testará API automaticamente")
    else:
        console.print("[yellow]⊘[/yellow] Sem credenciais, apenas análise da documentação")
    
    base_url = None
    
    console.print("\n" + "="*70)
    console.print("[bold cyan]Iniciando Análise...[/bold cyan]")
    console.print("="*70 + "\n")
    
    # Initialize context manager
    context_mgr = ContextManager()
    
    # Generate collection name from input file
    collection_name = os.path.splitext(os.path.basename(input_file))[0]
    
    # Initialize loggers
    output_base = output_file.replace('.postman_collection.json', '')
    openai_logger = OpenAILogger(output_base + '_LOGS_OPENAI.txt')
    api_logger = APITestLogger(output_base + '_LOGS_API.txt', base_url or '', '')
    
    try:
        # Passo 1: Parse
        console.print("[cyan]1/8[/cyan] 📄 Lendo documentação...")
        doc_source = parse_documentation(input_file)
        console.print(f"      [green]✓[/green] Encontrados {len(doc_source.endpoints)} endpoints\n")
        
        # Passo 1.5: Detectar tipo de API
        console.print("[cyan]1.5/8[/cyan] 🔍 Detectando tipo de API...")
        detector = APIDetector()
        doc_source.api_type = detector.detect_api_type(doc_source.endpoints, doc_source.content)
        console.print(f"      [green]✓[/green] Tipo de API: [bold cyan]{doc_source.api_type}[/bold cyan]\n")
        
        # Update context
        context_mgr.add_api_info(
            api_type=doc_source.api_type,
            api_name=collection_name,
            base_url=base_url or ''
        )
        
        # Passo 2: Análise com IA
        if doc_source.api_type == "SOAP":
            console.print("[cyan]2/8[/cyan] 🤖 Analisando Web Service SOAP com IA...")
        else:
            console.print("[cyan]2/8[/cyan] 🤖 Analisando API REST com IA...")
        console.print("      [dim](Isso pode levar alguns minutos)[/dim]")
        console.print(f"      [dim]Modelo: {Config.OPENAI_MODEL}[/dim]")
        analyzer = AIAnalyzer(context_manager=context_mgr, openai_logger=openai_logger)
        doc_source = analyzer.analyze_documentation(doc_source)
        console.print(f"      [green]✓[/green] Análise de IA completa ({len(doc_source.endpoints)} operações)\n")
        
        # Extrair base URL da documentação (para testes de API)
        if test_api and not base_url:
            console.print("      [dim]Extraindo base URL da documentação...[/dim]")
            base_url = analyzer.extract_base_url(doc_source)
            if base_url:
                doc_source.base_url = base_url
                console.print(f"      [green]✓[/green] Base URL extraída: [cyan]{base_url}[/cyan]\n")
            else:
                console.print("      [yellow]⚠[/yellow] Base URL não encontrada, testes desabilitados\n")
                test_api = False
        
        # Passo 3 e 4: Testes de API (se solicitado)
        test_results = None
        patterns_by_endpoint = None
        
        if test_api and base_url:
            # Initialize TokenManager for token caching
            console.print("      [dim]Inicializando gerenciador de tokens...[/dim]")
            token_mgr = TokenManager()
            
            # Load credentials first
            console.print("      [dim]Carregando credenciais...[/dim]")
            cred_mgr = CredentialsManager()
            creds_data = cred_mgr.load_credentials()
            
            if creds_data:
                console.print(f"      [green]✓[/green] Credenciais: {cred_mgr.get_source()}")
                available_fields = list(creds_data['credentials'].keys())
                console.print(f"      [dim]Campos disponíveis: {', '.join(available_fields)}[/dim]\n")
            else:
                console.print("      [yellow]⚠[/yellow] Sem credenciais (testará sem auth)\n")
            
            # Detect authentication (AI determines how to use credentials)
            console.print("[cyan]3/8[/cyan] 🔐 Analisando autenticação da API...")
            auth_det = AuthDetector()
            available_creds = creds_data['credentials'] if creds_data else None
            detected_auth = auth_det.detect_auth_method(doc_source, doc_source.endpoints, available_creds)
            console.print(f"      [green]✓[/green] Método identificado: [bold]{detected_auth}[/bold]")
            console.print(f"      [dim]A IA determinou como usar as credenciais[/dim]\n")
            
            # Detect authentication endpoint if OAuth
            auth_endpoint_info = None
            if detected_auth == 'oauth' and creds_data:
                console.print("      [dim]Detectando endpoint de autenticação...[/dim]")
                auth_endpoint_det = AuthEndpointDetector()
                auth_endpoint = auth_endpoint_det.detect_auth_endpoint(doc_source.endpoints, doc_source)
                
                if auth_endpoint:
                    auth_info = auth_endpoint_det.extract_auth_info(auth_endpoint)
                    token_url = auth_endpoint_det.detect_token_endpoint_url(doc_source.endpoints, base_url)
                    
                    # Create auth endpoint info object
                    class AuthEndpointInfo:
                        def __init__(self, endpoint, info, token_url, base_url):
                            self.endpoint = endpoint
                            self.info = info
                            self.token_url = token_url
                            self.base_url = base_url
                    
                    auth_endpoint_info = AuthEndpointInfo(auth_endpoint, auth_info, token_url, base_url)
                    path_str = auth_endpoint.path or '(no path)'
                    console.print(f"      [green]✓[/green] Endpoint detectado: {auth_endpoint.method.value} {path_str}")
                    if token_url:
                        console.print(f"      [dim]URL do token: {token_url}[/dim]\n")
                else:
                    console.print("      [yellow]⚠[/yellow] Endpoint de autenticação não detectado automaticamente\n")
            
            # Create auth handler (uses detected method with generic credentials)
            auth_h = None
            if creds_data and detected_auth != 'none':
                auth_h = get_auth_handler(
                    detected_auth,
                    creds_data['credentials'],
                    token_manager=token_mgr,
                    auth_endpoint_info=auth_endpoint_info
                )
                
                # For OAuth, try to generate token if we have client credentials
                if detected_auth == 'oauth' and auth_endpoint_info and hasattr(auth_h, 'generate_token'):
                    console.print("      [dim]Verificando token OAuth...[/dim]")
                    # Check if we need to generate token
                    has_access_token = 'access_token' in creds_data['credentials'] and creds_data['credentials']['access_token']
                    has_client_creds = (
                        'client_id' in creds_data['credentials'] and creds_data['credentials']['client_id'] and
                        'client_secret' in creds_data['credentials'] and creds_data['credentials']['client_secret']
                    )
                    
                    if not has_access_token and has_client_creds and auth_endpoint_info.token_url:
                        console.print("      [dim]Gerando token OAuth...[/dim]")
                        token = auth_h.generate_token(token_url=auth_endpoint_info.token_url)
                        if token:
                            console.print("      [green]✓[/green] Token OAuth gerado e armazenado\n")
                        else:
                            console.print("      [yellow]⚠[/yellow] Falha ao gerar token OAuth\n")
                    elif has_access_token:
                        console.print("      [green]✓[/green] Token OAuth já disponível\n")
                    else:
                        console.print("      [yellow]⚠[/yellow] Credenciais OAuth incompletas\n")
            
            # Classify operations
            console.print("      [dim]Classificando operações...[/dim]")
            classifier = OperationClassifier(use_ai=True, openai_logger=openai_logger)
            classifications = classifier.classify_all_operations(doc_source.endpoints)
            
            prod_count = sum(1 for c in classifications.values() if c['is_production'])
            safe_count = len(classifications) - prod_count
            
            if Config.ENABLE_PRODUCTION_OPERATIONS:
                console.print(f"      [green]✓[/green] Testará TODAS ({prod_count} produção + {safe_count} seguras)\n")
            else:
                console.print(f"      [yellow]⚠[/yellow] Produção DESABILITADA: {safe_count} seguras, {prod_count} puladas\n")
            
            # Test API
            console.print("[cyan]3.5/8[/cyan] 🧪 Executando testes...")
            tester = APITester(
                base_url,
                auth_handler=auth_h,
                operation_classifier=classifier,
                enable_production_ops=Config.ENABLE_PRODUCTION_OPERATIONS,
                api_logger=api_logger
            )
            test_results = tester.test_all_endpoints(
                doc_source.endpoints,
                auth_token=None
            )
            total_tests = sum(len(results) for results in test_results.values())
            console.print(f"      [green]✓[/green] Executados {total_tests} testes\n")
            
            console.print("[cyan]4/8[/cyan] 🔍 Detectando padrões...")
            detector = PatternDetector()
            patterns_by_endpoint = {}
            
            for endpoint in doc_source.endpoints:
                path_str = endpoint.path or '(no path)'
                endpoint_key = f"{endpoint.method.value} {path_str}"
                if endpoint_key in test_results:
                    patterns = detector.analyze_test_results(
                        endpoint,
                        test_results[endpoint_key]
                    )
                    patterns_by_endpoint[endpoint_key] = patterns
            
            total_patterns = sum(len(p) for p in patterns_by_endpoint.values())
            console.print(f"      [green]✓[/green] Descobertos {total_patterns} padrões\n")
        else:
            console.print("[cyan]3/8[/cyan] ⊘ Testes de API pulados")
            console.print("[cyan]4/8[/cyan] ⊘ Detecção de padrões pulada\n")
        
        # Passo 5: Gerar Postman Collection (SOAP ou REST)
        console.print("[cyan]5/8[/cyan] 📦 Gerando Postman Collection...")
        collection_name = os.path.splitext(os.path.basename(input_file))[0]
        
        if doc_source.api_type == "SOAP" and doc_source.soap_operations:
            # Gerar SOAP Collection
            console.print("      [dim]Tipo: SOAP Web Service[/dim]")
            generator = SOAPCollectionGenerator(collection_name)
            collection = generator.generate(
                operations=doc_source.soap_operations,
                test_results=test_results,
                patterns=patterns_by_endpoint,
                wsdl_url=doc_source.soap_operations[0].wsdl_url if doc_source.soap_operations else None
            )
        else:
            # Gerar REST Collection
            console.print("      [dim]Tipo: REST API[/dim]")
            generator = PostmanCollectionGenerator(collection_name)
            collection = generator.generate(
                endpoints=doc_source.endpoints,
                test_results=test_results,
                patterns=patterns_by_endpoint,
                base_url=base_url
            )
        
        generator.save(collection, output_file)
        console.print(f"      [green]✓[/green] Collection salva\n")
        
        # Passo 6: Gerar Resumo
        console.print("[cyan]6/8[/cyan] 📄 Gerando resumo...")
        summary_generator = APISummaryGenerator()
        summary = summary_generator.generate_summary(
            endpoints=doc_source.endpoints,
            patterns=patterns_by_endpoint,
            api_name=collection_name,
            api_type=doc_source.api_type
        )
        
        summary_path = output_file.replace('.json', '_RESUMO.txt')
        if summary_path == output_file:
            summary_path = output_file + '_RESUMO.txt'
        
        summary_generator.save(summary, summary_path)
        console.print(f"      [green]✓[/green] Resumo salvo\n")
        
        # Passo 7: Gerar Estatísticas
        console.print("[cyan]7/8[/cyan] 📊 Gerando estatísticas...")
        stats_generator = StatsGenerator()
        stats = stats_generator.generate_stats(
            endpoints=doc_source.endpoints,
            test_results=test_results,
            patterns=patterns_by_endpoint,
            api_name=collection_name,
            execution_time=0.0
        )
        
        stats_path = output_file.replace('.json', '_ESTATISTICAS.txt')
        if stats_path == output_file:
            stats_path = output_file + '_ESTATISTICAS.txt'
        
        stats_generator.save(stats, stats_path)
        console.print(f"      [green]✓[/green] Estatísticas salvas\n")
        
        # Passo 8: Salvar Contexto
        console.print("[cyan]8/8[/cyan] 🧠 Salvando contexto de execução...")
        context_path = output_file.replace('.json', '_CONTEXTO.txt')
        if context_path == output_file:
            context_path = output_file + '_CONTEXTO.txt'
        
        context_mgr.save_context(context_path)
        console.print(f"      [green]✓[/green] Contexto salvo\n")
        
        # Salvar logs (sempre, mesmo vazios)
        openai_logger.save()
        api_logger.save()
        
        # Gerar e salvar BaseModels
        console.print("      [dim]Gerando basemodels...[/dim]")
        basemodel_gen = BaseModelGenerator()
        basemodels_text = basemodel_gen.generate(doc_source.endpoints)
        basemodels_path = output_file.replace('.postman_collection.json', '_BASEMODELS.txt')
        basemodel_gen.save(basemodels_text, basemodels_path)
        console.print(f"      [green]✓[/green] BaseModels salvos\n")
        
        # Mensagem de sucesso
        console.print("="*70)
        console.print(Panel.fit(
            "[bold green]✅ Análise Concluída com Sucesso![/bold green]\n\n"
            "[bold]Arquivos gerados em output/:[/bold]\n\n"
            f"📦 [cyan]{os.path.basename(output_file)}[/cyan]\n"
            "   → Postman Collection completa (para desenvolvedores)\n"
            "   → Importe no Postman para testar a API\n\n"
            f"📄 [cyan]{os.path.basename(summary_path)}[/cyan]\n"
            "   → Resumo em linguagem simples (para todos)\n"
            "   → Abra em qualquer editor de texto\n\n"
            f"📊 [cyan]{os.path.basename(stats_path)}[/cyan]\n"
            "   → Estatísticas da análise (métricas e números)\n"
            "   → Para análise quantitativa\n\n"
            f"🧠 [cyan]{os.path.basename(context_path)}[/cyan]\n"
            "   → Contexto de execução (conhecimento acumulado)\n\n"
            f"📝 [cyan]{os.path.basename(output_base + '_LOGS_OPENAI.txt')}[/cyan]\n"
            f"   → Logs OpenAI ({openai_logger.request_count} reqs, ${openai_logger.total_cost:.4f})\n\n"
            f"📝 [cyan]{os.path.basename(output_base + '_LOGS_API.txt')}[/cyan]\n"
            f"   → Logs testes API ({api_logger.test_count} tests)\n\n"
            f"📋 [cyan]{os.path.basename(basemodels_path)}[/cyan]\n"
            "   → BaseModels (schemas mínimos obrigatórios)\n\n"
            f"[bold]Total de endpoints:[/bold] {len(doc_source.endpoints)}\n"
            f"[dim]Modelo: {Config.OPENAI_MODEL} | Tokens: {openai_logger.total_tokens}[/dim]",
            title="Sucesso",
            border_style="green"
        ))
        
        console.print("\n[bold]Próximos passos:[/bold]")
        console.print("1. 📖 Leia o [cyan]_RESUMO.txt[/cyan] para entender a API")
        console.print("2. 📊 Veja as [cyan]_ESTATISTICAS.txt[/cyan] para métricas")
        console.print("3. 🧠 Confira o [cyan]_CONTEXTO.txt[/cyan] (conhecimento extraído)")
        console.print("4. 📦 Importe o [cyan].json[/cyan] no Postman")
        console.print("5. 🚀 Comece a usar a API!\n")
        
    except KeyboardInterrupt:
        console.print("\n\n[yellow]⚠ Análise cancelada pelo usuário[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(Panel.fit(
            f"[red]❌ Erro durante a análise:[/red]\n\n"
            f"{str(e)}\n\n"
            "[yellow]Verifique:[/yellow]\n"
            "• Se o arquivo não está corrompido\n"
            "• Se você tem internet\n"
            "• Se a chave da OpenAI está correta\n\n"
            "[dim]Detalhes do erro foram salvos no log[/dim]",
            title="Erro",
            border_style="red"
        ))
        logger.exception("Erro na análise")
        sys.exit(1)


if __name__ == "__main__":
    main()

