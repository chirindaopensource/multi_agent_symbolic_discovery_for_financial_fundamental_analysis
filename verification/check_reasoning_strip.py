"""Issue E: a thinking model's reasoning must be stripped from every role reply at the role-callable path.

Fixture strings only, no live calls: each passes through make_role_callable_task_12 with a fake transport, as a
response mapping (the engine transport's shape) and as a text response, and the answer is read back through
the Task 19 adapter every caller uses.
Usage: python verification/check_reasoning_strip.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "verification"))
from notebook_namespace import load_namespace  # noqa: E402

ns = load_namespace(ROOT)
make_role_callable = ns["make_role_callable_task_12"]
registry = ns["build_role_sampling_registry_task_12"]()
read_reply = ns["_call_distiller_task_19"]
fixtures = {
    "<think>a</think>w=0.5,0.5": ("w=0.5,0.5", len("<think>a</think>")),
    "reason…</think>\nanswer": ("answer", len("reason…</think>")),
    "answer": ("answer", 0),
    "<think>x</think>draft</think>  EXPRESSION: 1.0 * NI_ps  ": (
        "EXPRESSION: 1.0 * NI_ps", len("<think>x</think>draft</think>")
    ),
}
for raw, (answer, reasoning_chars) in fixtures.items():
    for shape in ("mapping", "text"):
        def transport(request, raw=raw, shape=shape):
            """Return the fixture as the engine transport (mapping) or a text transport would."""
            if shape == "mapping":
                return {"text": raw, "finish_reason": "stop", "prompt_tokens": 3, "completion_tokens": 5}
            return raw
        record = make_role_callable("meta", registry, transport)("prompt")
        assert read_reply(lambda prompt, record=record: record, "prompt") == answer, (raw, shape, record)
        assert record["raw_text"] == raw and record["reasoning_chars"] == reasoning_chars, (raw, shape, record)
        if shape == "mapping":
            assert record["response"]["finish_reason"] == "stop" and record["response"]["completion_tokens"] == 5
        print(f"{shape:8s} {raw!r:58} -> {answer!r}")
record = make_role_callable("meta", registry, lambda request: {"finish_reason": "stop"})("prompt")
assert record["raw_text"] is None and record["reasoning_chars"] == 0 and record["response"] == {"finish_reason": "stop"}
print("CHECK OK")
