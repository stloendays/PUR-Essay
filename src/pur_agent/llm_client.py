from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from typing import Any, Protocol

from .mock_llm import scripted_mock_run


class ToolExecutor(Protocol):
    def tool_definitions(self) -> list[dict[str, Any]]: ...
    def execute(self, name: str, arguments: dict[str, Any]) -> Any: ...


@dataclass
class LLMResult:
    text: str
    provider: str
    model: str
    response_ids: list[str] = field(default_factory=list)
    usage: dict[str, Any] = field(default_factory=dict)
    rounds: int = 0
    fallback_used: bool = False
    seed: int | None = None


class LLMClient(Protocol):
    provider: str
    model: str

    def run(self, *, instructions: str, task: str, executor: ToolExecutor | None, seed: int | None = None) -> LLMResult: ...


def _require_api_key() -> str:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set. Export it in your shell (never write it into code or config).")
    return key


def _openai_client():
    try:
        from openai import OpenAI
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("Install the optional agent dependency: pip install -e '.[agent]'") from exc
    kwargs: dict[str, Any] = {"api_key": _require_api_key()}
    if os.getenv("OPENAI_BASE_URL"):
        kwargs["base_url"] = os.environ["OPENAI_BASE_URL"]
    return OpenAI(**kwargs)


def _add_usage(total: dict[str, Any], usage: Any) -> None:
    if usage is None:
        return
    data = usage.model_dump() if hasattr(usage, "model_dump") else dict(usage)
    for key in ("input_tokens", "output_tokens", "total_tokens", "prompt_tokens", "completion_tokens"):
        if isinstance(data.get(key), (int, float)):
            total[key] = total.get(key, 0) + data[key]
    total["calls"] = total.get("calls", 0) + 1


def _guard(executor: ToolExecutor | None, final_text: str | None = None) -> tuple[bool, str]:
    """Ask the executor whether this candidate answer may be accepted.

    V2 executors also inspect the answer text (output schema and canonical vocabulary); V1
    executors look at the trace only and ignore the argument.
    """
    guard = getattr(executor, "finalization_guard", None) if executor is not None else None
    if not callable(guard):
        return True, ""
    try:
        return guard(final_text)
    except TypeError:
        return guard()


def _json_payload(result: Any) -> str:
    return json.dumps(result, default=lambda x: x.item() if hasattr(x, "item") else str(x))


@dataclass
class OpenAIResponsesClient:
    """OpenAI Responses API with local deterministic function tools."""

    model: str
    max_rounds: int = 40
    provider: str = "openai_responses"

    def __post_init__(self) -> None:
        self.client = _openai_client()

    def _create(self, **kwargs: Any):
        return self.client.responses.create(model=self.model, store=True, **kwargs)

    def run(self, *, instructions: str, task: str, executor: ToolExecutor | None, seed: int | None = None) -> LLMResult:
        tools = executor.tool_definitions() if executor is not None else []
        common: dict[str, Any] = {"tools": tools} if tools else {}
        if tools:
            common["parallel_tool_calls"] = False
        response = self._create(instructions=instructions, input=task, **common)
        ids = [response.id]
        usage: dict[str, Any] = {}
        _add_usage(usage, getattr(response, "usage", None))
        guard_retries = 0
        for round_no in range(1, self.max_rounds + 1):
            calls = [item for item in response.output if getattr(item, "type", None) == "function_call"]
            if not calls:
                can_finalize, corrective = _guard(executor, response.output_text)
                if not can_finalize and guard_retries < 3:
                    guard_retries += 1
                    response = self._create(previous_response_id=response.id, input=corrective, **common)
                    ids.append(response.id)
                    _add_usage(usage, getattr(response, "usage", None))
                    continue
                return LLMResult(response.output_text, self.provider, self.model, ids, usage, round_no, False, seed)
            outputs = []
            for call in calls:
                args = json.loads(call.arguments or "{}")
                result = executor.execute(call.name, args)  # type: ignore[union-attr]
                outputs.append({"type": "function_call_output", "call_id": call.call_id, "output": _json_payload(result)})
            response = self._create(previous_response_id=response.id, input=outputs, **common)
            ids.append(response.id)
            _add_usage(usage, getattr(response, "usage", None))
        raise RuntimeError(f"Agent exceeded max_rounds={self.max_rounds}")


@dataclass
class OpenAICompatibleClient:
    """Chat Completions fallback for OpenAI-compatible providers without the Responses API.

    Same prompts, same tool definitions, same executor; only the transport differs.
    """

    model: str
    max_rounds: int = 40
    provider: str = "openai_compatible_chat"

    def __post_init__(self) -> None:
        self.client = _openai_client()

    @staticmethod
    def _chat_tools(defs: list[dict[str, Any]]) -> list[dict[str, Any]]:
        out = []
        for d in defs:
            out.append({"type": "function", "function": {"name": d["name"], "description": d.get("description", ""), "parameters": d["parameters"]}})
        return out

    def run(self, *, instructions: str, task: str, executor: ToolExecutor | None, seed: int | None = None) -> LLMResult:
        defs = executor.tool_definitions() if executor is not None else []
        tools = self._chat_tools(defs)
        messages: list[dict[str, Any]] = [{"role": "system", "content": instructions}, {"role": "user", "content": task}]
        ids: list[str] = []
        usage: dict[str, Any] = {}
        guard_retries = 0
        for round_no in range(1, self.max_rounds + 1):
            kwargs: dict[str, Any] = {"model": self.model, "messages": messages}
            if tools:
                kwargs["tools"] = tools
                kwargs["parallel_tool_calls"] = False
            if seed is not None:
                kwargs["seed"] = seed
            resp = self.client.chat.completions.create(**kwargs)
            ids.append(getattr(resp, "id", "") or "")
            _add_usage(usage, getattr(resp, "usage", None))
            msg = resp.choices[0].message
            calls = list(getattr(msg, "tool_calls", None) or [])
            if not calls:
                text = msg.content or ""
                can_finalize, corrective = _guard(executor, text)
                if not can_finalize and guard_retries < 3:
                    guard_retries += 1
                    messages.append({"role": "assistant", "content": text})
                    messages.append({"role": "user", "content": corrective})
                    continue
                return LLMResult(text, self.provider, self.model, ids, usage, round_no, False, seed)
            messages.append({"role": "assistant", "content": msg.content or "", "tool_calls": [
                {"id": c.id, "type": "function", "function": {"name": c.function.name, "arguments": c.function.arguments or "{}"}} for c in calls
            ]})
            for c in calls:
                args = json.loads(c.function.arguments or "{}")
                result = executor.execute(c.function.name, args)  # type: ignore[union-attr]
                messages.append({"role": "tool", "tool_call_id": c.id, "content": _json_payload(result)})
        raise RuntimeError(f"Agent exceeded max_rounds={self.max_rounds}")


@dataclass
class AutoClient:
    """Try the Responses API first; fall back to Chat Completions if the provider does not serve it."""

    model: str
    max_rounds: int = 40
    provider: str = "auto"

    def run(self, *, instructions: str, task: str, executor: ToolExecutor | None, seed: int | None = None) -> LLMResult:
        try:
            from openai import APIStatusError, NotFoundError  # type: ignore
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("Install the optional agent dependency: pip install -e '.[agent]'") from exc
        try:
            return OpenAIResponsesClient(self.model, self.max_rounds).run(instructions=instructions, task=task, executor=executor, seed=seed)
        except NotFoundError:
            pass
        except APIStatusError as exc:
            if getattr(exc, "status_code", None) not in (400, 404, 405, 501):
                raise
        result = OpenAICompatibleClient(self.model, self.max_rounds).run(instructions=instructions, task=task, executor=executor, seed=seed)
        result.fallback_used = True
        return result


@dataclass
class MockLLMClient:
    """Offline stand-in for CI and dry runs. Never contacts a network.

    With tools it follows the recovery strategy literally and assembles the final JSON from
    tool outputs (a deterministic 'perfect tool follower'). Without tools it abstains, because
    a mock has no reasoning; this makes the direct-LLM baseline an honest negative in dry runs.
    """

    model: str = "mock"
    max_rounds: int = 40
    provider: str = "mock"

    def run(self, *, instructions: str, task: str, executor: ToolExecutor | None, seed: int | None = None) -> LLMResult:
        t0 = time.perf_counter()
        text, rounds = scripted_mock_run(executor)
        # Submit the answer to the finalization guard exactly as a real transport would, so
        # dry runs exercise the gate instead of bypassing it. The mock is deterministic, so it
        # does not retry; a refusal is recorded and reported rather than silently retried away.
        _guard(executor, text)
        _ = t0
        return LLMResult(text, self.provider, self.model, [f"mock-{i}" for i in range(rounds)], {"input_tokens": 0, "output_tokens": 0, "calls": rounds}, rounds, False, seed)


def make_client(provider: str, model: str, *, max_rounds: int = 40) -> LLMClient:
    provider = (provider or "auto").lower()
    if provider == "mock":
        return MockLLMClient(model or "mock", max_rounds)
    if not model:
        raise RuntimeError("Set OPENAI_MODEL or pass --model")
    if provider in ("responses", "openai_responses"):
        return OpenAIResponsesClient(model, max_rounds)
    if provider in ("chat", "openai_compatible", "compat"):
        return OpenAICompatibleClient(model, max_rounds)
    if provider == "auto":
        return AutoClient(model, max_rounds)
    raise ValueError(f"Unknown provider {provider!r}; use mock|auto|responses|chat")
