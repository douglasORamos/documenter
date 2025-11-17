#!/usr/bin/env python3
"""Command-line interface for the API Documentation Enricher."""
import os
import sys
import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from utils import setup_logging
from config import Config
from parsers import (
    PDFParser, JSONParser, PostmanParser, 
    TextParser, OpenAPIParser
)
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
from operation_classifier import OperationClassifier
from openai_logger import OpenAILogger
from api_logger import APITestLogger
from models import DocumentationSource

console = Console()
logger = setup_logging()


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """AI Documentation Enricher - Analyze and enhance API documentation."""
    pass


@cli.command()
@click.option(
    '--input', '-i',
    required=False,
    type=click.Path(exists=True),
    help='Input documentation file (if not provided, will auto-detect from input/ folder)'
)
@click.option(
    '--output', '-o',
    required=False,
    type=click.Path(),
    help='Output Postman Collection file path (if not provided, will save to output/ folder)'
)
@click.option(
    '--test-api',
    is_flag=True,
    help='Test the API with real requests to discover patterns'
)
@click.option(
    '--base-url',
    type=str,
    help='Base URL of the API (required if --test-api is used)'
)
@click.option(
    '--auth-token',
    type=str,
    help='Authentication token for API requests'
)
@click.option(
    '--collection-name',
    type=str,
    default='Enriched API Documentation',
    help='Name for the generated Postman Collection'
)
@click.option(
    '--no-ai',
    is_flag=True,
    help='Skip AI analysis (only parse the input)'
)
def analyze(input, output, test_api, base_url, auth_token, collection_name, no_ai):
    """Analyze documentation and generate enriched Postman Collection.
    
    🚀 MODO SIMPLES (recomendado para iniciantes):
    
    \b
    1. Coloque seu arquivo na pasta input/
    2. Execute: python cli.py analyze
    3. Encontre os resultados em output/
    
    \b
    🔧 MODO AVANÇADO (com opções):
    
    \b
    # Especificar arquivos manualmente
    python cli.py analyze -i docs.pdf -o enriched.json
    
    \b
    # Com testes de API
    python cli.py analyze --test-api --base-url https://api.example.com
    
    \b
    # Com autenticação
    python cli.py analyze --test-api --base-url https://api.example.com --auth-token "token"
    """
    try:
        # Auto-detect input file if not provided
        if not input:
            input = auto_detect_input()
            if not input:
                console.print("[red]❌ Erro:[/red] Nenhum arquivo encontrado na pasta input/")
                console.print("\n[yellow]💡 Dica:[/yellow] Coloque um arquivo de documentação na pasta input/")
                console.print("Formatos suportados: PDF, JSON, Postman Collection, OpenAPI, TXT, Markdown")
                sys.exit(1)
            
            console.print(f"[green]✓[/green] Arquivo detectado: {input}")
        
        # Auto-generate output path if not provided
        if not output:
            output = auto_generate_output(input)
            console.print(f"[green]✓[/green] Saída será salva em: {output}")
        # Validate configuration
        if not no_ai:
            try:
                Config.validate()
            except ValueError as e:
                console.print(f"[red]Configuration Error:[/red] {e}")
                console.print("\n[yellow]Tip:[/yellow] Create a .env file with OPENAI_API_KEY or use --no-ai flag")
                sys.exit(1)
        
        # Validate test-api requirements
        if test_api and not base_url:
            console.print("[red]Error:[/red] --base-url is required when using --test-api")
            sys.exit(1)
        
        console.print(Panel.fit(
            f"[bold cyan]AI Documentation Enricher[/bold cyan]\n"
            f"Input: {input}\n"
            f"Output: {output}",
            title="Starting Analysis"
        ))
        
        # Initialize context manager for cost optimization
        context_mgr = ContextManager()
        
        # Initialize loggers
        output_base = output.replace('.postman_collection.json', '')
        openai_logger = OpenAILogger(output_base + '_LOGS_OPENAI.txt')
        api_logger = APITestLogger(output_base + '_LOGS_API.txt', base_url or '', '')
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            # Step 1: Parse input documentation
            task = progress.add_task("[cyan]Parsing documentation...", total=None)
            doc_source = parse_documentation(input)
            progress.update(task, completed=True)
            console.print(f"[green]✓[/green] Parsed {len(doc_source.endpoints)} endpoints")
            
            # Step 1.5: Detect API type
            task = progress.add_task("[cyan]Detecting API type...", total=None)
            detector = APIDetector()
            doc_source.api_type = detector.detect_api_type(doc_source.endpoints, doc_source.content)
            progress.update(task, completed=True)
            console.print(f"[green]✓[/green] API Type: [bold]{doc_source.api_type}[/bold]")
            
            # Update context with API info
            context_mgr.add_api_info(
                api_type=doc_source.api_type,
                api_name=collection_name,
                base_url=base_url or ''
            )
            
            # Step 2: AI Analysis (if enabled)
            if not no_ai:
                task = progress.add_task("[cyan]Analyzing with AI...", total=None)
                analyzer = AIAnalyzer(context_manager=context_mgr, openai_logger=openai_logger)
                doc_source = analyzer.analyze_documentation(doc_source)
                progress.update(task, completed=True)
                console.print(f"[green]✓[/green] AI analysis complete")
            else:
                console.print("[yellow]⊘[/yellow] AI analysis skipped")
            
            # Step 3: Test API (if enabled)
            test_results = None
            patterns_by_endpoint = None
            
            if test_api and base_url:
                # Load credentials first
                task = progress.add_task("[cyan]Loading credentials...", total=None)
                cred_mgr = CredentialsManager()
                creds_data = cred_mgr.load_credentials()
                progress.update(task, completed=True)
                
                if creds_data:
                    console.print(f"[green]✓[/green] Credentials loaded from: {cred_mgr.get_source()}")
                else:
                    console.print("[yellow]⚠[/yellow] No credentials found")
                
                # Detect authentication method (considering available credentials)
                task = progress.add_task("[cyan]Detecting authentication method...", total=None)
                auth_det = AuthDetector()
                available_creds = creds_data['credentials'] if creds_data else None
                detected_auth = auth_det.detect_auth_method(doc_source, doc_source.endpoints, available_creds)
                progress.update(task, completed=True)
                console.print(f"[green]✓[/green] Auth method detected: [bold]{detected_auth}[/bold] (from documentation)")
                
                # Create auth handler (AI determines how to use credentials)
                auth_h = None
                if creds_data and detected_auth != 'none':
                    auth_h = get_auth_handler(detected_auth, creds_data['credentials'])
                
                # Classify operations
                task = progress.add_task("[cyan]Classifying operations...", total=None)
                classifier = OperationClassifier(use_ai=not no_ai, openai_logger=openai_logger)
                classifications = classifier.classify_all_operations(doc_source.endpoints)
                progress.update(task, completed=True)
                
                prod_count = sum(1 for c in classifications.values() if c['is_production'])
                safe_count = len(classifications) - prod_count
                
                if Config.ENABLE_PRODUCTION_OPERATIONS:
                    console.print(f"[green]✓[/green] Will test ALL ({prod_count} prod + {safe_count} safe)")
                else:
                    console.print(f"[yellow]⚠[/yellow] Production DISABLED: {safe_count} safe, {prod_count} skipped")
                
                # Test API
                task = progress.add_task("[cyan]Testing API endpoints...", total=None)
                
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
                
                progress.update(task, completed=True)
                
                total_tests = sum(len(results) for results in test_results.values())
                console.print(f"[green]✓[/green] Completed {total_tests} API tests")
                
                # Step 4: Analyze patterns
                task = progress.add_task("[cyan]Detecting patterns...", total=None)
                
                detector = PatternDetector()
                patterns_by_endpoint = {}
                
                for endpoint in doc_source.endpoints:
                    endpoint_key = f"{endpoint.method.value} {endpoint.path}"
                    if endpoint_key in test_results:
                        patterns = detector.analyze_test_results(
                            endpoint,
                            test_results[endpoint_key]
                        )
                        patterns_by_endpoint[endpoint_key] = patterns
                
                progress.update(task, completed=True)
                
                total_patterns = sum(len(p) for p in patterns_by_endpoint.values())
                console.print(f"[green]✓[/green] Discovered {total_patterns} patterns")
            
            # Step 5: Generate Postman Collection (SOAP or REST)
            task = progress.add_task("[cyan]Generating Postman Collection...", total=None)
            
            if doc_source.api_type == "SOAP" and doc_source.soap_operations:
                # Use SOAP generator
                generator = SOAPCollectionGenerator(collection_name)
                collection = generator.generate(
                    operations=doc_source.soap_operations,
                    test_results=test_results,
                    patterns=patterns_by_endpoint,
                    wsdl_url=doc_source.soap_operations[0].wsdl_url if doc_source.soap_operations else None
                )
            else:
                # Use REST generator
                generator = PostmanCollectionGenerator(collection_name)
                collection = generator.generate(
                    endpoints=doc_source.endpoints,
                    test_results=test_results,
                    patterns=patterns_by_endpoint,
                    base_url=base_url
                )
            
            generator.save(collection, output)
            progress.update(task, completed=True)
            
            # Step 6: Generate human-readable summary
            task = progress.add_task("[cyan]Generating API summary...", total=None)
            
            summary_generator = APISummaryGenerator()
            summary = summary_generator.generate_summary(
                endpoints=doc_source.endpoints,
                patterns=patterns_by_endpoint,
                api_name=collection_name,
                api_type=doc_source.api_type
            )
            
            # Save summary with .txt extension
            summary_path = output.replace('.json', '_RESUMO.txt')
            if summary_path == output:  # If no .json extension
                summary_path = output + '_RESUMO.txt'
            
            summary_generator.save(summary, summary_path)
            progress.update(task, completed=True)
            console.print(f"[green]✓[/green] Generated API summary")
            
            # Step 7: Generate statistics report
            task = progress.add_task("[cyan]Generating statistics...", total=None)
            
            stats_generator = StatsGenerator()
            stats = stats_generator.generate_stats(
                endpoints=doc_source.endpoints,
                test_results=test_results,
                patterns=patterns_by_endpoint,
                api_name=collection_name,
                execution_time=0.0  # Will be calculated
            )
            
            # Save statistics
            stats_path = output.replace('.json', '_ESTATISTICAS.txt')
            if stats_path == output:
                stats_path = output + '_ESTATISTICAS.txt'
            
            stats_generator.save(stats, stats_path)
            progress.update(task, completed=True)
            console.print(f"[green]✓[/green] Generated statistics report")
            
            # Step 8: Save execution context
            task = progress.add_task("[cyan]Saving execution context...", total=None)
            
            context_path = output.replace('.json', '_CONTEXTO.txt')
            if context_path == output:
                context_path = output + '_CONTEXTO.txt'
            
            context_mgr.save_context(context_path)
            progress.update(task, completed=True)
            console.print(f"[green]✓[/green] Saved execution context")
            
            # Save logs (always)
            openai_logger.save()
            api_logger.save()
        
        # Get output paths
        summary_path = output.replace('.json', '_RESUMO.txt')
        if summary_path == output:
            summary_path = output + '_RESUMO.txt'
        
        stats_path = output.replace('.json', '_ESTATISTICAS.txt')
        if stats_path == output:
            stats_path = output + '_ESTATISTICAS.txt'
        
        # Get context path
        context_path = output.replace('.json', '_CONTEXTO.txt')
        if context_path == output:
            context_path = output + '_CONTEXTO.txt'
        
        console.print(Panel.fit(
            f"[bold green]Success![/bold green]\n\n"
            f"📦 Postman Collection: {output}\n"
            f"📄 API Summary: {summary_path}\n"
            f"📊 Statistics: {stats_path}\n"
            f"🧠 Execution Context: {context_path}\n\n"
            f"Endpoints: {len(doc_source.endpoints)}",
            title="Analysis Complete"
        ))
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        logger.exception("Analysis failed")
        sys.exit(1)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
def info(input_file):
    """Show information about a documentation file.
    
    Display the type and basic information about a documentation file
    without performing full analysis.
    """
    try:
        console.print(f"[cyan]Analyzing file:[/cyan] {input_file}")
        
        # Detect file type
        file_type = detect_file_type(input_file)
        console.print(f"[green]File type:[/green] {file_type}")
        
        # Parse the file
        doc_source = parse_documentation(input_file)
        
        # Display information
        console.print(f"\n[bold]Documentation Summary[/bold]")
        console.print(f"  Endpoints found: {len(doc_source.endpoints)}")
        
        if doc_source.endpoints:
            console.print(f"\n[bold]Endpoints:[/bold]")
            for endpoint in doc_source.endpoints[:10]:  # Show first 10
                console.print(f"  • {endpoint.method.value} {endpoint.path}")
            
            if len(doc_source.endpoints) > 10:
                console.print(f"  ... and {len(doc_source.endpoints) - 10} more")
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)


def detect_file_type(file_path: str) -> str:
    """Detect the type of documentation file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File type string
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == '.pdf':
        return 'pdf'
    elif ext in ['.txt', '.md']:
        return 'text'
    elif ext == '.json':
        # Try to determine if it's Postman or OpenAPI
        try:
            import json
            with open(file_path, 'r') as f:
                content = json.load(f)
            
            if 'info' in content and 'item' in content:
                return 'postman'
            elif 'openapi' in content or 'swagger' in content:
                return 'openapi'
            else:
                return 'json'
        except:
            return 'json'
    elif ext in ['.yaml', '.yml']:
        return 'openapi'
    else:
        return 'unknown'


def auto_detect_input() -> str:
    """Auto-detect input file from input/ directory.
    
    Returns:
        Path to the input file or None if not found
    """
    input_dir = "input"
    
    # Check if input directory exists
    if not os.path.exists(input_dir):
        return None
    
    # Find first valid file
    valid_extensions = ['.pdf', '.json', '.yaml', '.yml', '.txt', '.md']
    
    for filename in os.listdir(input_dir):
        if filename.startswith('.') or filename == 'README.md':
            continue
        
        file_path = os.path.join(input_dir, filename)
        
        # Check if it's a file (not directory)
        if not os.path.isfile(file_path):
            continue
        
        # Check extension
        _, ext = os.path.splitext(filename)
        if ext.lower() in valid_extensions:
            return file_path
    
    return None


def auto_generate_output(input_path: str) -> str:
    """Generate output path based on input filename.
    
    Creates a subfolder in output/ to preserve analysis history.
    
    Args:
        input_path: Path to input file
        
    Returns:
        Path for output file in output/subfolder/ directory
    """
    from datetime import datetime
    
    output_base = "output"
    
    # Extract filename without extension
    basename = os.path.basename(input_path)
    name_without_ext = os.path.splitext(basename)[0]
    
    # Create subfolder: use filename + timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    subfolder_name = f"{name_without_ext}_{timestamp}"
    
    # Create subfolder
    output_dir = os.path.join(output_base, subfolder_name)
    os.makedirs(output_dir, exist_ok=True)
    
    logger.info(f"Created output folder: {output_dir}")
    
    # Generate output filename
    output_filename = f"{name_without_ext}.postman_collection.json"
    output_path = os.path.join(output_dir, output_filename)
    
    return output_path


def parse_documentation(file_path: str) -> DocumentationSource:
    """Parse a documentation file based on its type.
    
    Args:
        file_path: Path to the documentation file
        
    Returns:
        Parsed DocumentationSource
        
    Raises:
        ValueError: If file type is not supported
    """
    file_type = detect_file_type(file_path)
    
    logger.info(f"Parsing {file_type} file: {file_path}")
    
    if file_type == 'pdf':
        parser = PDFParser(file_path)
    elif file_type == 'postman':
        parser = PostmanParser(file_path)
    elif file_type == 'openapi':
        parser = OpenAPIParser(file_path)
    elif file_type == 'json':
        parser = JSONParser(file_path)
    elif file_type == 'text':
        parser = TextParser(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
    
    return parser.parse()


if __name__ == '__main__':
    cli()

