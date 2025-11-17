"""Logger for API test requests and responses."""
import logging
import json
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger("documenter")


class APITestLogger:
    """Logs all API test requests and responses."""
    
    def __init__(self, output_path: str, base_url: str = "", auth_type: str = ""):
        """Initialize the API test logger.
        
        Args:
            output_path: Path to save the log file
            base_url: Base URL of the API being tested
            auth_type: Authentication type being used
        """
        self.output_path = output_path
        self.base_url = base_url
        self.auth_type = auth_type
        self.logs = []
        self.test_count = 0
        self.start_time = datetime.now()
    
    def log_test(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        body: Any,
        response_status: int,
        response_headers: Dict[str, str],
        response_body: Any,
        duration: float,
        test_name: str = ""
    ):
        """Log an API test.
        
        Args:
            method: HTTP method
            url: Full URL
            headers: Request headers
            body: Request body
            response_status: Response status code
            response_headers: Response headers
            response_body: Response body
            duration: Request duration
            test_name: Description of the test
        """
        self.test_count += 1
        
        log_entry = {
            'number': self.test_count,
            'timestamp': datetime.now(),
            'test_name': test_name,
            'method': method,
            'url': url,
            'request_headers': dict(headers),
            'request_body': body,
            'response_status': response_status,
            'response_headers': dict(response_headers),
            'response_body': response_body,
            'duration': duration
        }
        
        self.logs.append(log_entry)
        
        logger.debug(f"API test logged: #{self.test_count}, {method} {url}, status: {response_status}")
    
    def save(self):
        """Save logs to file (always creates file, even if empty)."""
        try:
            with open(self.output_path, 'w', encoding='utf-8') as f:
                if not self.logs:
                    f.write(self._format_empty_logs())
                    logger.info(f"Saved empty API logs to: {self.output_path}")
                else:
                    f.write(self._format_logs())
                    logger.info(f"Saved API test logs to: {self.output_path}")
                    logger.info(f"Total: {self.test_count} tests executed")
            
        except Exception as e:
            logger.error(f"Error saving API logs: {e}")
    
    def _format_logs(self) -> str:
        """Format logs as human-readable text.
        
        Returns:
            Formatted log text
        """
        lines = []
        
        # Header
        lines.append("=" * 70)
        lines.append("LOGS DE TESTES DA API")
        lines.append("=" * 70)
        lines.append(f"Data: {self.start_time.strftime('%d/%m/%Y %H:%M:%S')}")
        if self.base_url:
            lines.append(f"Base URL: {self.base_url}")
        if self.auth_type:
            lines.append(f"Autenticação: {self.auth_type}")
        lines.append("")
        lines.append(f"Total de Testes: {self.test_count}")
        lines.append("")
        
        # Each test
        for log in self.logs:
            lines.append("-" * 70)
            lines.append(f"TESTE #{log['number']} - {log['timestamp'].strftime('%H:%M:%S')}")
            lines.append("-" * 70)
            
            if log['test_name']:
                lines.append(f"Teste: {log['test_name']}")
            
            lines.append(f"Endpoint: {log['method']} {log['url']}")
            lines.append(f"Duração: {log['duration']:.2f}s")
            lines.append("")
            
            # Request headers
            lines.append("REQUEST HEADERS:")
            for key, value in log['request_headers'].items():
                # Mask sensitive headers
                if key.lower() in ['authorization', 'api-key', 'x-api-key']:
                    value = self._mask_sensitive(str(value))
                lines.append(f"  {key}: {value}")
            lines.append("")
            
            # Request body
            if log['request_body']:
                lines.append("REQUEST BODY:")
                body_str = self._format_body(log['request_body'])
                lines.append(body_str)
                lines.append("")
            
            # Response
            lines.append("RESPONSE:")
            lines.append(f"Status: {log['response_status']} {self._get_status_text(log['response_status'])}")
            lines.append("")
            
            # Response headers (principais)
            lines.append("Response Headers:")
            for key in ['content-type', 'content-length']:
                value = log['response_headers'].get(key, log['response_headers'].get(key.title()))
                if value:
                    lines.append(f"  {key}: {value}")
            lines.append("")
            
            # Response body
            if log['response_body']:
                lines.append("Response Body:")
                body_str = self._format_body(log['response_body'])
                # Limit response body size
                if len(body_str) > 1000:
                    body_str = body_str[:1000] + "\n... (truncado)"
                lines.append(body_str)
                lines.append("")
        
        # Footer
        lines.append("=" * 70)
        lines.append("FIM DOS LOGS")
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def _mask_sensitive(self, value: str) -> str:
        """Mask sensitive information.
        
        Args:
            value: Original value
            
        Returns:
            Masked value
        """
        if len(value) > 20:
            return value[:8] + "..." + value[-4:]
        elif len(value) > 10:
                return value[:4] + "..." + value[-2:]
        else:
            return "***"
    
    def _format_empty_logs(self) -> str:
        """Format empty log file.
        
        Returns:
            Empty log text
        """
        lines = []
        lines.append("=" * 70)
        lines.append("LOGS DE TESTES DA API")
        lines.append("=" * 70)
        lines.append(f"Data: {self.start_time.strftime('%d/%m/%Y %H:%M:%S')}")
        if self.base_url:
            lines.append(f"Base URL: {self.base_url}")
        if self.auth_type:
            lines.append(f"Autenticação: {self.auth_type}")
        lines.append("")
        lines.append("Nenhum teste de API foi executado nesta execução.")
        lines.append("")
        lines.append("Possíveis motivos:")
        lines.append("- Não foi solicitado testar API")
        lines.append("- Base URL não foi fornecida ou extraída")
        lines.append("- Credenciais não disponíveis")
        lines.append("- Apenas análise da documentação")
        lines.append("")
        lines.append("=" * 70)
        return "\n".join(lines)
    
    def _format_body(self, body: Any) -> str:
        """Format body for display.
        
        Args:
            body: Request or response body
            
        Returns:
            Formatted body string
        """
        if isinstance(body, dict):
            return json.dumps(body, indent=2, ensure_ascii=False)
        elif isinstance(body, str):
            try:
                # Try to parse and pretty-print JSON
                parsed = json.loads(body)
                return json.dumps(parsed, indent=2, ensure_ascii=False)
            except:
                return body
        else:
            return str(body)
    
    def _get_status_text(self, status: int) -> str:
        """Get status text for status code.
        
        Args:
            status: HTTP status code
            
        Returns:
            Status text
        """
        status_texts = {
            200: "OK",
            201: "Created",
            204: "No Content",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            409: "Conflict",
            422: "Unprocessable Entity",
            500: "Internal Server Error"
        }
        return status_texts.get(status, "")

