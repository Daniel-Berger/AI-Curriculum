"""
Agent Service using LangGraph.

Orchestrates tools (retrieval, calculation, search) to answer user questions.
"""

import logging
from typing import AsyncGenerator, Dict, List, Optional
import json
import re

from app.models import ChatResponse
from app.rag_service import RAGService
from app.llm_client import LLMClient

logger = logging.getLogger(__name__)


class AgentService:
    """LangGraph-based agent for multi-tool orchestration.

    Responsibilities:
    - Route queries to appropriate tools
    - Call tools in sequence if needed
    - Generate final response
    - Handle fallbacks
    """

    def __init__(self, llm_client: LLMClient, rag_service: RAGService):
        """Initialize agent.

        Args:
            llm_client: LLM client for generation
            rag_service: RAG service for document retrieval
        """
        self.llm_client = llm_client
        self.rag_service = rag_service

        # Define available tools
        self.tools = self._initialize_tools()

    def _initialize_tools(self) -> Dict:
        """Initialize available tools."""
        return {
            "retrieval": {
                "description": "Retrieve relevant documents",
                "fn": self._tool_retrieval
            },
            "calculator": {
                "description": "Evaluate mathematical expressions",
                "fn": self._tool_calculator
            },
            "web_search": {
                "description": "Search the web (mock)",
                "fn": self._tool_web_search
            }
        }

    async def process_message(
        self,
        message: str,
        chat_id: str,
        temperature: float = 0.7
    ) -> ChatResponse:
        """Process user message and generate response.

        Args:
            message: User input
            chat_id: Conversation identifier
            temperature: Sampling temperature

        Returns:
            ChatResponse with message and sources
        """
        try:
            logger.info(f"Processing message for {chat_id}: {message[:50]}")

            # Decide which tool to use
            tool_decision = await self._decide_tool(message)
            logger.info(f"Tool decision: {tool_decision['tool']}")

            # Execute tool
            tool_result = await self._execute_tool(
                tool_decision["tool"],
                tool_decision["input"]
            )

            # Generate response using LLM
            response_text = await self.llm_client.generate_response(
                user_message=message,
                context=tool_result.get("context", ""),
                temperature=temperature
            )

            # Extract sources from retrieval result
            sources = tool_result.get("sources", [])

            return ChatResponse(
                message=response_text,
                sources=sources,
                tokens_used=tool_result.get("tokens", 0)
            )

        except Exception as e:
            logger.error(f"Message processing error: {e}")
            raise

    async def stream_message(
        self,
        message: str,
        chat_id: str,
        temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        """Stream response for user message.

        Args:
            message: User input
            chat_id: Conversation identifier
            temperature: Sampling temperature

        Yields:
            Response text chunks
        """
        try:
            # Decide tool
            tool_decision = await self._decide_tool(message)

            # Execute tool
            tool_result = await self._execute_tool(
                tool_decision["tool"],
                tool_decision["input"]
            )

            # Stream response from LLM
            async for chunk in self.llm_client.stream_response(
                user_message=message,
                context=tool_result.get("context", ""),
                temperature=temperature
            ):
                yield chunk

        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield f"Error: {str(e)}"

    async def _decide_tool(self, message: str) -> Dict:
        """Decide which tool to use for user message.

        Args:
            message: User input

        Returns:
            Dict with tool name and input
        """
        # Simple heuristic-based routing
        message_lower = message.lower()

        if any(word in message_lower for word in ["calculate", "math", "eval", "="]):
            return {"tool": "calculator", "input": message}

        elif any(word in message_lower for word in ["search", "google", "web", "find"]):
            return {"tool": "web_search", "input": message}

        else:
            # Default to retrieval for most questions
            return {"tool": "retrieval", "input": message}

    async def _execute_tool(self, tool_name: str, tool_input: str) -> Dict:
        """Execute selected tool.

        Args:
            tool_name: Name of tool to execute
            tool_input: Input for tool

        Returns:
            Tool result with context and metadata
        """
        if tool_name == "retrieval":
            return await self._tool_retrieval(tool_input)
        elif tool_name == "calculator":
            return await self._tool_calculator(tool_input)
        elif tool_name == "web_search":
            return await self._tool_web_search(tool_input)
        else:
            return {"context": "", "sources": [], "tokens": 0}

    async def _tool_retrieval(self, query: str) -> Dict:
        """Retrieval tool: fetch relevant documents.

        Args:
            query: User question

        Returns:
            Context and sources
        """
        try:
            # Retrieve relevant chunks
            chunks = self.rag_service.retrieve_relevant_chunks(query, top_k=3)

            # Build context
            context = self.rag_service.build_context(chunks)

            # Format sources
            sources = [
                {
                    "document": chunk["document_name"],
                    "snippet": chunk["content"][:100]
                }
                for chunk in chunks
            ]

            return {
                "context": context,
                "sources": sources,
                "tokens": len(chunks) * 50  # Estimate
            }

        except Exception as e:
            logger.error(f"Retrieval tool error: {e}")
            return {"context": "", "sources": [], "tokens": 0}

    async def _tool_calculator(self, expression: str) -> Dict:
        """Calculator tool: evaluate math expressions.

        Args:
            expression: Mathematical expression

        Returns:
            Result and context
        """
        try:
            # Extract math expression
            # Simple regex: find "= 5" or "2 + 3" patterns
            match = re.search(r'(\d+[\s\+\-\*/]\d+)', expression)

            if match:
                expr = match.group(1).replace(" ", "")
                try:
                    result = eval(expr)  # In production, use safer evaluator
                    context = f"Calculation result: {expr} = {result}"
                    return {
                        "context": context,
                        "sources": [],
                        "tokens": 10
                    }
                except:
                    pass

            return {"context": "", "sources": [], "tokens": 0}

        except Exception as e:
            logger.error(f"Calculator tool error: {e}")
            return {"context": "", "sources": [], "tokens": 0}

    async def _tool_web_search(self, query: str) -> Dict:
        """Web search tool (mock).

        Args:
            query: Search query

        Returns:
            Mock search results
        """
        try:
            # In production: call Brave Search API, SerpAPI, etc.
            # For now, return mock results
            context = f"Web search results for '{query}': Mock results would appear here."

            return {
                "context": context,
                "sources": [{"source": "web", "url": "https://example.com"}],
                "tokens": 20
            }

        except Exception as e:
            logger.error(f"Web search tool error: {e}")
            return {"context": "", "sources": [], "tokens": 0}
