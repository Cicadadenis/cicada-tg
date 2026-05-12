from cicada.adapters.mock_telegram import MockTelegramAdapter
from cicada.database import Database
from cicada.executor import Executor
from cicada.parser import Parser


def make_executor(source: str, *, debug: bool = False, store=None):
    program = Parser(source).parse()
    telegram = MockTelegramAdapter()
    return Executor(program, telegram, debug=debug, store=store), telegram


def message(text: str, chat_id: int = 1):
    return {
        "message": {
            "message_id": 1,
            "chat": {"id": chat_id, "type": "private"},
            "from": {"id": chat_id, "first_name": "Tester"},
            "text": text,
        }
    }


def test_save_load_db_key_file_chat_id(tmp_path):
    store = Database(str(tmp_path / "db.json"))
    chat_id = 1144785510
    executor, _ = make_executor(
        '''бот "TOKEN"
при тексте:
    сохранить "file_{chat_id}" = "ok"
    получить "file_{chat_id}" → out
    ответ "{out}"
''',
        store=store,
    )
    executor.handle(message("hi", chat_id=chat_id))
    uid = str(chat_id)
    assert store.get(uid, "file_1144785510") == "ok"


def test_render_template_and_regex_fallback(tmp_path):
    store = Database(str(tmp_path / "db.json"))
    executor, _ = make_executor(
        'бот "TOKEN"\nпри тексте:\n    ответ "x"\n',
        store=store,
    )
    ctx = executor.runtime.user(1144785510)
    assert executor._render_template_string("file_{chat_id}", ctx) == "file_1144785510"
    assert executor._regex_fallback_db_template("pre_{chat_id}_{user_id}", ctx) == "pre_1144785510_1144785510"


def test_state_debug_logs(tmp_path, capsys):
    store = Database(str(tmp_path / "db.json"))
    chat_id = 1144785510
    executor, _ = make_executor(
        '''бот "TOKEN"
при тексте:
    сохранить "file_{chat_id}" = 1
    получить "file_{chat_id}" → out
''',
        store=store,
        debug=True,
    )
    executor.handle(message("hi", chat_id=chat_id))
    out = capsys.readouterr().out
    assert "[STATE] saving key='file_1144785510'" in out
    assert "[STATE] loading key='file_1144785510'" in out
    assert "user_id=1144785510" in out


def test_load_db_falls_back_to_global_key(tmp_path):
    store = Database(str(tmp_path / "db.json"))
    store.set_global("категории", ["Пицца", "Суши"])
    executor, telegram = make_executor(
        '''бот "TOKEN"
при старте:
    получить "категории" → категории
    ответ "{категории}"
''',
        store=store,
    )

    executor.handle(message("/start"))

    texts = [e["text"] for e in telegram.outbound if e["type"] == "send_message"]
    assert texts == ["Пицца, Суши"]