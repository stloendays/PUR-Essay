from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Protocol


class ToolExecutor(Protocol):
    def tool_definitions(self) -> list[dict[str, Any]]: ...
    def execute(self, name: str, arguments: dict[str, Any]) -> Any: ...


@dataclass
class OpenAIResponsesClient:
    """OpenAI Responses API adapter using local deterministic function tools."""

    model: str
    max_rounds: int = 24

    def __post_init__(self) -> None:
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is not set")
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Install the optional agent dependency: pip install -e '.[agent]'") from exc
        kwargs: dict[str, Any] = {"api_key": os.environ["OPENAI_API_KEY"]}
        if os.getenv("OPENAI_BASE_URL"):
            kwargs["base_url"] = os.environ["OPENAI_BASE_URL"]
        self.client = OpenAI(**kwargs)

    def run(self, *, instructions: str, task: str, executor: ToolExecutor) -> tuple[str, dict[str, Any]]:
        response = self.client.responses.create(
            model=self.model,
            instructions=instructions,
            input=task,
            tools=executor.tool_definitions(),
            parallel_tool_calls=False,
            store=True,
        )
        trace: list[dict[str, Any]] = []
        for _ in range(self.max_rounds):
            calls = [item for item in response.output if getattr(item, "type", None) == "function_call"]
            if not calls:
                guard = getattr(executor, "finalization_guard", None)
                if callable(guard):
                    can_finalize, corrective = guard()
                    if not can_finalize:
                        response = self.client.responses.create(
                            model=self.model,
                            previous_response_id=response.id,
                            input=corrective,
                            tools=executor.tool_definitions(),
                            parallel_tool_calls=False,
                            store=True,
                        )
                        continue
                usage = response.usage.model_dump() if getattr(response, "usage", None) else None
                return response.output_text, {"response_id": response.id, "trace": trace, "usage": usage}
            outputs = []
            for call in calls:
                args = json.loads(call.arguments or "{}")
                result = executor.execute(call.name, args)
                trace.append({"tool": call.name, "arguments": args, "output": result})
                payload = json.dumps(result, default=lambda x: x.item() if hasattr(x, "item") else str(x))
                outputs.append({"type": "function_call_output", "call_id": call.call_id, "output": payload})
            response = self.client.responses.create(
                model=self.model,
                previous_response_id=response.id,
                input=outputs,
                tools=executor.tool_definitions(),
                parallel_tool_calls=False,
                store=True,
            )
        raise RuntimeError(f"Agent exceeded max_rounds={self.max_rounds}")
