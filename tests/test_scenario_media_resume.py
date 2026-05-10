"""Продолжение сценария после спросить при приходе документа/медиа."""

from cicada.adapters.mock_telegram import MockTelegramAdapter
from cicada.core import MediaEvent, TelegramUpdateNormalizer
from cicada.database import Database
from cicada.executor import Executor
from cicada.parser import Parser


def make_executor(source: str, *, store=None):
    program = Parser(source).parse()
    telegram = MockTelegramAdapter()
    return Executor(program, telegram, store=store), telegram


def message(text: str, chat_id: int = 1):
    return {
        "message": {
            "message_id": 1,
            "chat": {"id": chat_id, "type": "private"},
            "from": {"id": chat_id, "first_name": "Tester"},
            "text": text,
        }
    }


def document_update(file_id: str = "DOC_FILE_ID", chat_id: int = 1, message_id: int = 2):
    return {
        "message": {
            "message_id": message_id,
            "chat": {"id": chat_id, "type": "private"},
            "from": {"id": chat_id, "first_name": "Tester"},
            "document": {"file_id": file_id, "file_name": "a.pdf"},
        }
    }


def sent_texts(telegram: MockTelegramAdapter):
    return [e["text"] for e in telegram.outbound if e["type"] == "send_message"]


def test_scenario_continues_after_document_after_ask(tmp_path):
    store = Database(str(tmp_path / "db.json"))
    src = """бот "TOKEN"
при тексте:
    запустить загрузка

сценарий загрузка:
    шаг загрузка_файла:
        спросить "Отправьте файл" -> файл
        ответ "Файл загружен!"
"""
    ex, tg = make_executor(src, store=store)
    ex.handle(message("go"))
    assert "Отправьте файл" in sent_texts(tg)[-1]

    tg.clear_outbound()
    ex.handle(document_update())
    assert sent_texts(tg) == ["Файл загружен!"]


def test_scenario_recovers_pending_when_cleared_before_document(tmp_path):
    store = Database(str(tmp_path / "db.json"))
    src = """бот "TOKEN"
при тексте:
    запустить загрузка

сценарий загрузка:
    шаг загрузка_файла:
        спросить "Отправьте файл" -> файл
        ответ "Файл загружен!"
"""
    ex, tg = make_executor(src, store=store)
    ex.handle(message("go"))
    ctx = ex.runtime.user(1)
    ctx._pending_stmts = []

    tg.clear_outbound()
    ex.handle(document_update())
    assert sent_texts(tg) == ["Файл загружен!"]


def test_normalizer_document_before_text():
    msg = {
        "message_id": 1,
        "chat": {"id": 1, "type": "private"},
        "from": {"id": 1, "first_name": "x"},
        "text": "strange",
        "document": {"file_id": "fid123", "file_name": "a.bin"},
    }
    ev = TelegramUpdateNormalizer.from_message(msg)
    assert isinstance(ev, MediaEvent)
    assert ev.media_type == "документ"
    assert ev.file_id == "fid123"
