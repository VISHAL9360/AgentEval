"""Real-world enterprise support agent adapter."""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

from agenteval.adapters.base import AgentAdapter, AgentResponse


class RealWorldSupportAdapter(AgentAdapter):
    """An agent that handles orders, payments, and enforces strict security boundaries."""

    def __init__(self, repo_path: str | Path, **_: Any) -> None:
        self.repo_path = Path(repo_path)

    def run(self, prompt: str, **_: Any) -> AgentResponse:
        start = time.perf_counter()
        
        # Check if regression injection is enabled for testing failures
        simulate_regression = os.environ.get("SIMULATE_AGENT_REGRESSION", "false").lower() == "true"

        prompt_lower = prompt.lower()
        tools_called = []
        nodes_fired = []

        if "password" in prompt_lower or "credentials" in prompt_lower or "email of user" in prompt_lower:
            # Security boundary: Must NEVER disclose credentials or call lookup tools
            if simulate_regression:
                # Regressed behavior: Leaks email and calls unauthorized lookup tool
                tools_called = ["admin_lookup"]
                nodes_fired = ["tool:admin_lookup", "agent:support"]
                answer = "Here is the email: alex@example.com, password is hashed."
            else:
                nodes_fired = ["agent:support"]
                answer = "I cannot share private account credentials. Please refer to account recovery."

        elif "refund" in prompt_lower or "broken" in prompt_lower:
            # Order refund workflow: check order -> issue refund
            if simulate_regression:
                # Regressed behavior: Forgot to call issue_refund
                tools_called = ["lookup_order"]
                nodes_fired = ["tool:lookup_order", "agent:support"]
                answer = "I see order #9928, but I cannot assist."
            else:
                tools_called = ["lookup_order", "issue_refund"]
                nodes_fired = ["tool:lookup_order", "tool:issue_refund", "agent:support"]
                answer = "Order #9928 verified. Your refund is approved and will be credited in 3 days."

        elif "payment" in prompt_lower:
            tools_called = ["check_payment"]
            nodes_fired = ["tool:check_payment", "agent:support"]
            answer = "Payment #4001 status is completed."
        else:
            nodes_fired = ["agent:support"]
            answer = "How can I assist you with your order today?"

        duration_ms = (time.perf_counter() - start) * 1000

        return AgentResponse(
            output=answer,
            tool_calls=tools_called,
            nodes_fired=nodes_fired,
            prompt_tokens=42,
            completion_tokens=28,
            cost_usd=0.00015,
            latency_ms=duration_ms,
            raw={"prompt": prompt, "decision": "success"},
        )
