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


def test_pereslat_document_alias_resends_current_document():
    src = """бот "TOKEN"
при документе:
    переслать документ
"""
    program = Parser(src).parse()
    tg = MockTelegramAdapter()
    ex = Executor(program, tg)
    ex.handle({
        "message": {
            "message_id": 1,
            "chat": {"id": 1, "type": "private"},
            "from": {"id": 1, "first_name": "T"},
            "document": {"file_id": "DOC_FILE_ID", "file_name": "a.pdf"},
        }
    })

    docs = [e for e in tg.outbound if e["type"] == "document"]
    assert len(docs) == 1
    assert docs[0]["path"] == "DOC_FILE_ID"


def test_pereslat_voice_alias_resends_current_voice():
    src = """бот "TOKEN"
при голосовом:
    переслать голосовое
"""
    program = Parser(src).parse()
    tg = MockTelegramAdapter()
    ex = Executor(program, tg)
    ex.handle({
        "message": {
            "message_id": 1,
            "chat": {"id": 1, "type": "private"},
            "from": {"id": 1, "first_name": "T"},
            "voice": {"file_id": "VOICE_FILE_ID"},
        }
    })

    voices = [e for e in tg.outbound if e["type"] == "voice"]
    assert len(voices) == 1
    assert voices[0]["path"] == "VOICE_FILE_ID"


def test_pereslat_sticker_alias_resends_current_sticker():
    src = """бот "TOKEN"
при стикере:
    переслать стикер
"""
    program = Parser(src).parse()
    tg = MockTelegramAdapter()
    ex = Executor(program, tg)
    ex.handle({
        "message": {
            "message_id": 1,
            "chat": {"id": 1, "type": "private"},
            "from": {"id": 1, "first_name": "T"},
            "sticker": {"file_id": "STICKER_FILE_ID", "emoji": "🙂"},
        }
    })

    stickers = [e for e in tg.outbound if e["type"] == "sticker"]
    assert len(stickers) == 1
    assert stickers[0]["file_id"] == "STICKER_FILE_ID"
