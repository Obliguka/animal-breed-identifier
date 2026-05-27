from abc import ABC, abstractmethod
from typing import Optional
from schemas import RunRequest, RunResponse, InfoResponse


class ServiceBase(ABC):
    @abstractmethod
    def get_info(self) -> InfoResponse:
        pass

    @abstractmethod
    def run(self, request: RunRequest) -> RunResponse:
        pass

    def get_text(self, request: RunRequest) -> Optional[str]:
        content = request.content
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            for part in content:
                if part.type == "text":
                    return part.text
        return None

    def get_image(self, request: RunRequest) -> Optional[str]:
        content = request.content
        if isinstance(content, list):
            for part in content:
                if part.type == "image":
                    return part.image
        return None