"""
Agent Memory Module
===================

Implements a two-tier memory system for the AI agent:

1. **Conversation Memory (Short-term)**:
   - Maintains the current conversation buffer
   - Sliding window with configurable max turns
   - Summarization for long conversations

2. **Long-term Memory**:
   - Vector-based storage of important facts and interactions
   - Semantic retrieval of relevant past experiences
   - Supports memory consolidation and forgetting

The memory system provides context to the agent for more coherent
and personalized interactions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class MemoryEntry:
    """A single entry in long-term memory.

    Attributes
    ----------
    content : str
        The memory content.
    metadata : dict
        Additional context (timestamp, source, importance).
    memory_type : str
        Category of memory ('fact', 'interaction', 'preference', 'summary').
    importance : float
        Importance score (0.0 to 1.0) for retrieval prioritization.
    created_at : datetime
        When the memory was created.
    """

    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    memory_type: str = "interaction"
    importance: float = 0.5
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ConversationTurn:
    """A single turn in the conversation history.

    Attributes
    ----------
    role : str
        'user' or 'assistant'.
    content : str
        The message content.
    tool_calls : list of dict, optional
        Tools invoked during this turn.
    timestamp : datetime
        When the turn occurred.
    """

    role: str
    content: str
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


class AgentMemory:
    """Two-tier memory system for the AI agent.

    Parameters
    ----------
    max_conversation_turns : int
        Maximum turns to keep in conversation buffer before summarizing.
    enable_long_term : bool
        Whether to enable long-term vector memory.
    vector_store_config : dict, optional
        Configuration for the long-term memory vector store.
    importance_threshold : float
        Minimum importance score for storing in long-term memory.

    Examples
    --------
    >>> memory = AgentMemory(max_conversation_turns=20)
    >>> memory.add_turn(ConversationTurn(role="user", content="Hello!"))
    >>> context = memory.get_context("Tell me about AI")
    """

    def __init__(
        self,
        max_conversation_turns: int = 20,
        enable_long_term: bool = True,
        vector_store_config: Optional[Dict[str, Any]] = None,
        importance_threshold: float = 0.3,
    ) -> None:
        self.max_conversation_turns = max_conversation_turns
        self.enable_long_term = enable_long_term
        self.vector_store_config = vector_store_config or {}
        self.importance_threshold = importance_threshold
        self._conversation_buffer: Dict[str, List[ConversationTurn]] = {}
        self._long_term_store: Optional[Any] = None

    def add_turn(
        self,
        turn: ConversationTurn,
        conversation_id: str = "default",
    ) -> None:
        """Add a conversation turn to the short-term buffer.

        If the buffer exceeds max_conversation_turns, older turns are
        summarized and moved to long-term memory.

        Parameters
        ----------
        turn : ConversationTurn
            The conversation turn to add.
        conversation_id : str
            ID of the conversation.
        """
        raise NotImplementedError

    def get_conversation_history(
        self,
        conversation_id: str = "default",
        last_n: Optional[int] = None,
    ) -> List[ConversationTurn]:
        """Retrieve the conversation history.

        Parameters
        ----------
        conversation_id : str
            ID of the conversation.
        last_n : int, optional
            Only return the last N turns.

        Returns
        -------
        list of ConversationTurn
            The conversation history.
        """
        raise NotImplementedError

    def store_memory(self, entry: MemoryEntry) -> None:
        """Store an entry in long-term memory.

        Parameters
        ----------
        entry : MemoryEntry
            Memory entry to store.
        """
        raise NotImplementedError

    def search_memories(
        self,
        query: str,
        top_k: int = 5,
        memory_type: Optional[str] = None,
    ) -> List[MemoryEntry]:
        """Search long-term memory for relevant entries.

        Parameters
        ----------
        query : str
            Semantic search query.
        top_k : int
            Number of results to return.
        memory_type : str, optional
            Filter by memory type.

        Returns
        -------
        list of MemoryEntry
            Relevant memory entries sorted by relevance.
        """
        raise NotImplementedError

    def get_context(
        self,
        query: str,
        conversation_id: str = "default",
    ) -> str:
        """Build a context string combining conversation history and relevant memories.

        Parameters
        ----------
        query : str
            The current user query (for memory retrieval relevance).
        conversation_id : str
            Current conversation ID.

        Returns
        -------
        str
            Formatted context string for the agent's prompt.
        """
        raise NotImplementedError

    def summarize_conversation(
        self, conversation_id: str = "default"
    ) -> str:
        """Summarize the conversation buffer to free space.

        Generates a summary of older turns and stores it as a
        long-term memory entry.

        Parameters
        ----------
        conversation_id : str
            ID of the conversation to summarize.

        Returns
        -------
        str
            The generated summary.
        """
        raise NotImplementedError

    def clear_conversation(
        self, conversation_id: str = "default"
    ) -> None:
        """Clear the conversation buffer for a given conversation.

        Parameters
        ----------
        conversation_id : str
            ID of the conversation to clear.
        """
        self._conversation_buffer.pop(conversation_id, None)

    def forget(
        self, older_than_days: int = 90, importance_below: float = 0.2
    ) -> int:
        """Remove old, low-importance memories.

        Parameters
        ----------
        older_than_days : int
            Remove memories older than this many days.
        importance_below : float
            Remove memories with importance below this threshold.

        Returns
        -------
        int
            Number of memories removed.
        """
        raise NotImplementedError
