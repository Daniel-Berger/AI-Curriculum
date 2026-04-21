"""
AI Agent with Tool Use

A working agent that uses Claude API with tool calling to solve complex tasks.
Implements the ReAct pattern (Reason + Act).
"""

from config import CONFIG, TOOLS
from tools import TOOL_REGISTRY
import anthropic


def extract_text_response(content_blocks: list) -> str:
    """Extract text response from content blocks."""
    for block in content_blocks:
        if hasattr(block, 'type') and block.type == 'text':
            return block.text
    return ""


def execute_tools(content_blocks: list) -> list[dict]:
    """Execute all tool_use blocks in response."""
    tool_results = []

    for block in content_blocks:
        if hasattr(block, 'type') and block.type == 'tool_use':
            tool_name = block.name
            tool_input = block.input
            tool_id = block.id

            # Execute the tool
            if tool_name in TOOL_REGISTRY:
                try:
                    result = TOOL_REGISTRY[tool_name](**tool_input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_id,
                        "content": str(result),
                        "is_error": False
                    })
                except Exception as e:
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_id,
                        "content": f"Error: {str(e)}",
                        "is_error": True
                    })
            else:
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_id,
                    "content": f"Tool '{tool_name}' not found",
                    "is_error": True
                })

    return tool_results


def run_agent(
    query: str,
    max_iterations: int = 5,
    verbose: bool = False,
) -> str:
    """
    Run the AI agent to process a query using tools.

    Args:
        query: User query
        max_iterations: Maximum agent iterations
        verbose: Print debug information

    Returns:
        Final answer as string
    """
    client = anthropic.Anthropic()

    messages = [{"role": "user", "content": query}]

    if verbose:
        print(f"[User] {query}\n")

    for iteration in range(max_iterations):
        if verbose:
            print(f"[Iteration {iteration + 1}/{max_iterations}]")

        # Call Claude with tools
        response = client.messages.create(
            model=CONFIG['model'],
            max_tokens=1024,
            tools=TOOLS,
            messages=messages
        )

        if verbose:
            print(f"Stop reason: {response.stop_reason}")

        # Check if model used tools
        has_tool_use = any(
            hasattr(block, 'type') and block.type == 'tool_use'
            for block in response.content
        )

        if not has_tool_use:
            # Final answer
            answer = extract_text_response(response.content)
            if verbose:
                print(f"\n[Agent] {answer}")
            return answer

        # Add assistant response to messages
        messages.append({"role": "assistant", "content": response.content})

        # Execute tools
        if verbose:
            for block in response.content:
                if hasattr(block, 'type') and block.type == 'tool_use':
                    print(f"  → Calling {block.name}({block.input})")

        tool_results = execute_tools(response.content)

        # Add tool results to messages
        messages.append({"role": "user", "content": tool_results})

        if verbose:
            for result in tool_results:
                content = result['content'][:100]
                print(f"  ← Result: {content}...")

    return "Maximum iterations reached without final answer"


def main():
    """Example usage of the agent."""
    queries = [
        "What is 100 + 50?",
        "Calculate 25 * 4 and then add 10",
        "What's the current date and time?",
    ]

    for query in queries:
        print("=" * 60)
        answer = run_agent(query, verbose=True)
        print(f"\nFinal Answer: {answer}")
        print()


if __name__ == "__main__":
    main()
