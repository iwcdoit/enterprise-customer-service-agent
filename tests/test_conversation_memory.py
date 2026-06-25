from __future__ import annotations

from customer_service_app.domain.schemas import ChatMessage
from customer_service_app.services.conversation_memory import ConversationMemoryCompactor


def test_memory_compactor_keeps_short_history() -> None:
    """历史不长时不需要压缩。"""

    history = [
        ChatMessage(role="user", content="你好"),
        ChatMessage(role="assistant", content="你好，有什么可以帮你？"),
    ]

    window = ConversationMemoryCompactor(max_history_messages=3).compact(history)

    assert window.messages == history
    assert window.compressed is False
    assert window.compressed_count == 0


def test_memory_compactor_summarizes_earlier_messages() -> None:
    """历史过长时，较早消息会变成一条摘要，最近消息保留原文。"""

    history = [
        ChatMessage(role="user", content=f"用户问题 {index}")
        for index in range(1, 7)
    ]

    window = ConversationMemoryCompactor(
        max_history_messages=4,
        keep_recent_messages=2,
    ).compact(history)

    assert window.compressed is True
    assert window.original_count == 6
    assert window.compressed_count == 4
    assert len(window.messages) == 3
    assert window.messages[0].role == "system"
    assert window.messages[0].metadata["memory_type"] == "history_summary"
    assert "用户问题 1" in window.messages[0].content
    assert window.messages[1:] == history[-2:]
