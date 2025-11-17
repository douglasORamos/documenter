"""Logger for OpenAI API requests and responses."""
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger("documenter")


class OpenAILogger:
    """Logs all OpenAI API requests and responses for audit and debugging."""
    
    def __init__(self, output_path: str):
        """Initialize the OpenAI logger.
        
        Args:
            output_path: Path to save the log file
        """
        self.output_path = output_path
        self.logs = []
        self.request_count = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        self.start_time = datetime.now()
    
    def log_request(
        self,
        purpose: str,
        prompt: str,
        response: str,
        tokens: Dict[str, int],
        duration: float,
        model: str = "gpt-5-nano"
    ):
        """Log an OpenAI request.
        
        Args:
            purpose: Purpose of the request (e.g., "Analyze endpoint POST /users")
            prompt: Prompt sent to OpenAI
            response: Response received
            tokens: Token usage dict with 'prompt_tokens', 'completion_tokens', 'total_tokens'
            duration: Request duration in seconds
            model: Model used
        """
        self.request_count += 1
        
        # Calculate cost (approximate for gpt-5-nano)
        # Assuming similar to gpt-4o-mini: $0.15/1M input, $0.60/1M output
        input_tokens = tokens.get('prompt_tokens', 0)
        output_tokens = tokens.get('completion_tokens', 0)
        total_tokens = tokens.get('total_tokens', input_tokens + output_tokens)
        
        cost = (input_tokens * 0.00000015) + (output_tokens * 0.0000006)
        
        self.total_tokens += total_tokens
        self.total_cost += cost
        
        log_entry = {
            'number': self.request_count,
            'timestamp': datetime.now(),
            'purpose': purpose,
            'model': model,
            'prompt': prompt,
            'response': response,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'total_tokens': total_tokens,
            'cost': cost,
            'duration': duration
        }
        
        self.logs.append(log_entry)
        
        logger.debug(f"OpenAI request logged: #{self.request_count}, tokens: {total_tokens}, cost: ${cost:.4f}")
    
    def save(self):
        """Save logs to file (always creates file, even if empty)."""
        try:
            with open(self.output_path, 'w', encoding='utf-8') as f:
                if not self.logs:
                    f.write(self._format_empty_logs())
                    logger.info(f"Saved empty OpenAI logs to: {self.output_path}")
                else:
                    f.write(self._format_logs())
                    logger.info(f"Saved OpenAI logs to: {self.output_path}")
                    logger.info(f"Total: {self.request_count} requests, {self.total_tokens} tokens, ${self.total_cost:.4f}")
            
        except Exception as e:
            logger.error(f"Error saving OpenAI logs: {e}")
    
    def _format_logs(self) -> str:
        """Format logs as human-readable text.
        
        Returns:
            Formatted log text
        """
        lines = []
        
        # Header
        lines.append("=" * 70)
        lines.append("LOGS DE REQUISIÇÕES OPENAI")
        lines.append("=" * 70)
        lines.append(f"Data: {self.start_time.strftime('%d/%m/%Y %H:%M:%S')}")
        lines.append(f"Modelo: {self.logs[0]['model'] if self.logs else 'gpt-5-nano'}")
        lines.append("")
        lines.append(f"Total de Requisições: {self.request_count}")
        lines.append(f"Total de Tokens: {self.total_tokens:,}")
        lines.append(f"Custo Total Estimado: ${self.total_cost:.4f}")
        lines.append("")
        
        # Each request
        for log in self.logs:
            lines.append("-" * 70)
            lines.append(f"REQUISIÇÃO #{log['number']} - {log['timestamp'].strftime('%H:%M:%S')}")
            lines.append("-" * 70)
            lines.append(f"Propósito: {log['purpose']}")
            lines.append(f"Modelo: {log['model']}")
            lines.append(f"Duração: {log['duration']:.2f}s")
            lines.append("")
            
            lines.append("PROMPT ENVIADO:")
            # Truncate very long prompts
            prompt = log['prompt']
            if len(prompt) > 1500:
                prompt = prompt[:1500] + "\n... (truncado)"
            lines.append(prompt)
            lines.append("")
            
            lines.append("RESPOSTA RECEBIDA:")
            response = log['response']
            if len(response) > 1000:
                response = response[:1000] + "\n... (truncado)"
            lines.append(response)
            lines.append("")
            
            lines.append(f"Tokens: {log['total_tokens']} (input: {log['input_tokens']}, output: {log['output_tokens']})")
            lines.append(f"Custo: ${log['cost']:.4f}")
            lines.append("")
        
        # Footer
        lines.append("=" * 70)
        lines.append("FIM DOS LOGS")
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def _format_empty_logs(self) -> str:
        """Format empty log file.
        
        Returns:
            Empty log text
        """
        return f"""{'=' * 70}
LOGS DE REQUISIÇÕES OPENAI
{'=' * 70}
Data: {self.start_time.strftime('%d/%m/%Y %H:%M:%S')}
Modelo: gpt-5-nano

Nenhuma requisição OpenAI foi realizada nesta execução.

Possíveis motivos:
- Análise foi executada com --no-ai
- Endpoints foram extraídos do parse direto (sem necessidade de IA)
- Erro impediu chamadas OpenAI

{'=' * 70}
"""

