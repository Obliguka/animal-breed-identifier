from pydantic import BaseModel
from typing import Any, Optional, List, Dict
from enum import Enum


class InputType(str, Enum):
    IMAGE = "image"  


class ContentPart(BaseModel):
    type: str
    image: str  


class RunRequest(BaseModel):
    content: List[ContentPart]  
    extra_body: Dict[str, Any] = {}


class RunResponse(BaseModel):
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class InfoResponse(BaseModel):
    input_type: InputType
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]


class Schema:
    @staticmethod
    def of(**properties) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": properties,
        }

    @staticmethod
    def string(description: str, default: Any = None, enum: List[str] = None) -> Dict[str, Any]:
        schema = {"type": "string", "description": description}
        if default is not None:
            schema["default"] = default
        if enum is not None:
            schema["enum"] = enum
        return schema

    @staticmethod
    def number(description: str, default: float = None, minimum: float = None, maximum: float = None) -> Dict[str, Any]:
        schema = {"type": "number", "description": description}
        if default is not None:
            schema["default"] = default
        if minimum is not None:
            schema["minimum"] = minimum
        if maximum is not None:
            schema["maximum"] = maximum
        return schema

    @staticmethod
    def integer(description: str, default: int = None, minimum: int = None, maximum: int = None) -> Dict[str, Any]:
        schema = {"type": "integer", "description": description}
        if default is not None:
            schema["default"] = default
        if minimum is not None:
            schema["minimum"] = minimum
        if maximum is not None:
            schema["maximum"] = maximum
        return schema

    @staticmethod
    def boolean(description: str, default: bool = None) -> Dict[str, Any]:
        schema = {"type": "boolean", "description": description}
        if default is not None:
            schema["default"] = default
        return schema

    @staticmethod
    def array(items: Dict[str, Any], description: str = None) -> Dict[str, Any]:
        schema = {"type": "array", "items": items}
        if description:
            schema["description"] = description
        return schema

    @staticmethod
    def object(description: str = None, **properties) -> Dict[str, Any]:
        schema = {"type": "object", "properties": properties}
        if description:
            schema["description"] = description
        return schema