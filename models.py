"""Data models for the documentation enricher."""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class HTTPMethod(Enum):
    """HTTP methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"


@dataclass
class FieldInfo:
    """Information about a field in a request or response."""
    name: str
    field_type: Optional[str] = None
    required: Optional[bool] = None
    description: Optional[str] = None
    possible_values: List[Any] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    nested_fields: List['FieldInfo'] = field(default_factory=list)


@dataclass
class EndpointInfo:
    """Information about an API endpoint."""
    path: str
    method: HTTPMethod
    description: Optional[str] = None
    request_fields: List[FieldInfo] = field(default_factory=list)
    response_fields: List[FieldInfo] = field(default_factory=list)
    headers: Dict[str, str] = field(default_factory=dict)
    query_params: Dict[str, Any] = field(default_factory=dict)
    examples: List[Dict[str, Any]] = field(default_factory=list)
    error_codes: Dict[int, str] = field(default_factory=dict)


@dataclass
class TestResult:
    """Result of an API test."""
    endpoint: EndpointInfo
    request_payload: Dict[str, Any]
    response_status: int
    response_body: Any
    response_headers: Dict[str, str]
    execution_time: float
    error: Optional[str] = None


@dataclass
class Pattern:
    """A discovered pattern in the API behavior."""
    pattern_type: str  # 'input_output', 'validation', 'error', 'dependency'
    description: str
    conditions: List[str] = field(default_factory=list)
    examples: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 1.0


@dataclass
class SOAPParameter:
    """SOAP parameter information."""
    name: str
    xml_type: str  # XSD type (string, int, boolean, etc.)
    required: bool = False
    namespace: Optional[str] = None
    description: Optional[str] = None
    example_value: Optional[str] = None


@dataclass
class SOAPOperation:
    """SOAP operation information."""
    name: str
    namespace: str
    soap_action: str
    wsdl_url: str
    description: Optional[str] = None
    input_params: List[SOAPParameter] = field(default_factory=list)
    output_params: List[SOAPParameter] = field(default_factory=list)
    
    def to_endpoint_info(self) -> EndpointInfo:
        """Convert to EndpointInfo for compatibility."""
        from models import HTTPMethod, FieldInfo
        
        # Convert input params to request fields
        request_fields = []
        for param in self.input_params:
            field = FieldInfo(
                name=param.name,
                field_type=param.xml_type,
                required=param.required,
                description=param.description
            )
            if param.example_value:
                field.possible_values = [param.example_value]
            request_fields.append(field)
        
        # Convert output params to response fields
        response_fields = []
        for param in self.output_params:
            field = FieldInfo(
                name=param.name,
                field_type=param.xml_type,
                description=param.description
            )
            response_fields.append(field)
        
        return EndpointInfo(
            path=self.wsdl_url,
            method=HTTPMethod.POST,  # SOAP always uses POST
            description=self.description,
            request_fields=request_fields,
            response_fields=response_fields
        )


@dataclass
class DocumentationSource:
    """Source documentation to be analyzed."""
    file_path: str
    file_type: str  # 'pdf', 'json', 'postman', 'txt', 'openapi'
    content: Any = None
    endpoints: List[EndpointInfo] = field(default_factory=list)
    api_type: str = "REST"  # 'REST', 'SOAP', 'GRAPHQL', 'UNKNOWN'
    soap_operations: List[SOAPOperation] = field(default_factory=list)
    base_url: Optional[str] = None  # Extracted base URL from documentation
    environment: str = "production"  # production, staging, dev

