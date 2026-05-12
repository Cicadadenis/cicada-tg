from cicada.adapters.mock_telegram import MockTelegramAdapter
from cicada.adapters.telegram import TelegramAdapter
from cicada.executor import Executor
from cicada.parser import Parser


def message(text: str, chat_id: int = 1):
    return {
        "message": {
            "message_id": 1,
            "chat": {"id": chat_id, "type": "private"},
            "from": {"id": chat_id, "first_name": "Tester"},
            "text": text,
        }
    }


def test_formatted_replies_emit_separate_preview_events():
    src = '''бот "TOKEN"
при тексте:
    пусть name = "Alice"
    ответ_md "*{name}*"
    ответ_html "<b>{name}</b>"
    ответ_md2 "__{name}__"
    ответ_markdown_v2 "`{name}`"
'''
    program = Parser(src).parse()
    tg = MockTelegramAdapter()
    ex = Executor(program, tg)

    ex.handle(message("format"))

    formatted = [
        (event["type"], event["text"])
        for event in tg.outbound
        if event["type"] in {"markdown", "html", "markdown_v2"}
    ]
    assert formatted == [
        ("markdown", "*Alice*"),
        ("html", "<b>Alice</b>"),
        ("markdown_v2", "__Alice__"),
        ("markdown_v2", "`Alice`"),
    ]


def test_telegram_adapter_uses_expected_parse_modes():
    class RecordingTelegramAdapter(TelegramAdapter):
        def __init__(self):
            self.calls = []

        def call(self, method: str, data: dict = None) -> dict:
            self.calls.append((method, data))
            return {"ok": True, "result": {}}

    tg = RecordingTelegramAdapter()

    tg.send_markdown(1, "*bold*")
    tg.send_html(1, "<b>bold</b>")
    tg.send_markdown_v2(1, "*bold*")

    assert tg.calls == [
        ("sendMessage", {"chat_id": 1, "text": "*bold*", "parse_mode": "Markdown"}),
        ("sendMessage", {"chat_id": 1, "text": "<b>bold</b>", "parse_mode": "HTML"}),
        ("sendMessage", {"chat_id": 1, "text": "*bold*", "parse_mode": "MarkdownV2"}),
    ]
