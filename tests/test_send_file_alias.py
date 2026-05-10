"""Алиас «отправить файл» должен давать ту же семантику, что «документ»."""

from cicada.adapters.mock_telegram import MockTelegramAdapter
from cicada.executor import Executor
from cicada.parser import Parser


def test_otpravit_file_alias_triggers_send_document():
    src = """бот "TOKEN"
при тексте:
    ответ "📥 Отправляю..."
    отправить файл "https://example.com/file.pdf"
    ответ "✅ Готово"
"""
    program = Parser(src).parse()
    tg = MockTelegramAdapter()
    ex = Executor(program, tg)
    ex.handle({
        "message": {
            "message_id": 1,
            "chat": {"id": 1, "type": "private"},
            "from": {"id": 1, "first_name": "T"},
            "text": "go",
        }
    })
    docs = [e for e in tg.outbound if e["type"] == "document"]
    assert len(docs) == 1
    assert docs[0]["path"] == "https://example.com/file.pdf"


def test_pri_dokument_handler_registered():
    src = """бот "TOKEN"
при документ:
    ответ "got doc"
"""
    program = Parser(src).parse()
    kinds = [h.kind for h in program.handlers]
    assert "document_received" in kinds
