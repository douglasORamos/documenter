"""AI Documentation Enricher - Analyze and enhance API documentation using AI."""

__version__ = "1.0.0"
__author__ = "AI Documentation Enricher Team"
__description__ = "Analyze and enrich API documentation using AI"

from .analyzer import AIAnalyzer
from .tester import APITester
from .patterns import PatternDetector
from .generator import PostmanCollectionGenerator
from .summary_generator import APISummaryGenerator
from .models import (
    DocumentationSource,
    EndpointInfo,
    FieldInfo,
    TestResult,
    Pattern,
    HTTPMethod
)

__all__ = [
    'AIAnalyzer',
    'APITester',
    'PatternDetector',
    'PostmanCollectionGenerator',
    'APISummaryGenerator',
    'DocumentationSource',
    'EndpointInfo',
    'FieldInfo',
    'TestResult',
    'Pattern',
    'HTTPMethod',
]

