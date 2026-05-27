import base64
from schemas import InfoResponse, InputType, RunRequest, RunResponse, Schema
from service_base import ServiceBase
from llm_client import trace_vision_call


class AnimalIdentifierService(ServiceBase):
    
    def get_info(self) -> InfoResponse:
        return InfoResponse(
            input_type=InputType.IMAGE,
            input_schema=Schema.of(),
            output_schema=Schema.of(
                animal=Schema.string("Вид животного"),
                breed=Schema.string("Порода"),
            ),
        )
    
    def run(self, request: RunRequest) -> RunResponse:
        try:
            image_b64 = self.get_image(request)
            if image_b64 is None:
                return RunResponse(
                    status="error",
                    error="Картинка не передана"
                )
            
            with open("prompts/prompt_photo.txt", "r", encoding="utf-8") as f:
                prompt = f.read()
            
            # Вызываем функцию для распознавания
            result = trace_vision_call(
                prompt=prompt,
                image_base64=image_b64,
                metadata={},
            )
            
            return RunResponse(
                status="success",
                result={
                    "animal": result.get("animal", "unknown"),
                    "breed": result.get("breed", "unknown"),
                }
            )
            
        except Exception as e:
            return RunResponse(status="error", error=str(e))


_service_instance = None

def get_service() -> ServiceBase:
    global _service_instance
    if _service_instance is None:
        _service_instance = AnimalIdentifierService()
    return _service_instance