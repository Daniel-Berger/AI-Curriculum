"""Configuration for the AI Agent.

Provides a simple dataclass-based configuration for the agent,
controlling LLM behavior, tool availability, and execution limits.

Swift parallel:
    - Dataclass config  ~  struct AgentConfig: Codable { }
    - Default values    ~  Swift memberwise initializer defaults
    - Frozen dataclass  ~  let properties (immutable after init)
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AgentConfig:
    """Immutable configuration for the AI agent.

    Attributes:
        model_name: LLM model identifier.
        temperature: Sampling temperature (0.0 = deterministic).
        max_iterations: Maximum number of agent reasoning loops.
        max_tokens: Maximum tokens in each LLM response.
        available_tools: Names of tools the agent may use.
        human_in_the_loop: Whether to pause for human approval
            before executing tool calls.
        verbose: Whether to print intermediate reasoning steps.
    """

    model_name: str = "claude-sonnet-4-20250514"
    temperature: float = 0.0
    max_iterations: int = 10
    max_tokens: int = 1024
    available_tools: tuple[str, ...] = field(
        default_factory=lambda: ("calculator", "datetime", "search")
    )
    human_in_the_loop: bool = False
    verbose: bool = False

    def with_tools(self, *tool_names: str) -> AgentConfig:
        """Return a new config with a different set of available tools.

        Since this dataclass is frozen, we must create a new instance
        rather than mutating in place -- similar to Swift value semantics.
        """
        return AgentConfig(
            model_name=self.model_name,
            temperature=self.temperature,
            max_iterations=self.max_iterations,
            max_tokens=self.max_tokens,
            available_tools=tuple(tool_names),
            human_in_the_loop=self.human_in_the_loop,
            verbose=self.verbose,
        )
