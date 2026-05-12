from cicada.adapters.mock_telegram import MockTelegramAdapter
<<<<<<< HEAD
=======
from cicada.database import Database
>>>>>>> 8838bf7 (Add dynamic inline keyboards, HTTP JSON blocks and catalog modules)
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


<<<<<<< HEAD
=======
def callback(data: str, chat_id: int = 1):
    return {
        "callback_query": {
            "id": "cb1",
            "from": {"id": chat_id, "first_name": "Tester"},
            "message": {
                "message_id": 2,
                "chat": {"id": chat_id, "type": "private"},
            },
            "data": data,
        }
    }


>>>>>>> 8838bf7 (Add dynamic inline keyboards, HTTP JSON blocks and catalog modules)
def test_inline_keyboard_dynamic_from_list_with_back_button():
    src = '''бот "TOKEN"
при тексте:
    пусть товары = ["Яблоко", "Банан"]
    inline-кнопки: из товары по name/id callback=товар_ columns=2 append_back=true
'''
    program = Parser(src).parse()
    tg = MockTelegramAdapter()
    ex = Executor(program, tg)

    ex.handle(message("каталог"))

    inline = [e for e in tg.outbound if e["type"] == "inline_keyboard"]
    assert len(inline) == 1
    keyboard = inline[0]["keyboard"]
    assert keyboard[0][0]["text"] == "Яблоко"
    assert keyboard[0][0]["callback_data"] == "товар_Яблоко"
    assert keyboard[0][1]["text"] == "Банан"
    assert keyboard[0][1]["callback_data"] == "товар_Банан"
    assert keyboard[1][0]["text"] == "🔙 Назад"
    assert keyboard[1][0]["callback_data"] == "back"
<<<<<<< HEAD
=======


def test_inline_keyboard_from_db_alias_with_back_button(tmp_path):
    store = Database(str(tmp_path / "db.json"))
    store.set("1", "категории", ["Одежда", "Обувь"])
    src = '''бот "TOKEN"
при тексте:
    ответ "Выберите категорию:"
    inline из бд "категории" callback "category:" columns=2 назад "⬅️ Назад" → "назад"
'''
    program = Parser(src).parse()
    tg = MockTelegramAdapter()
    ex = Executor(program, tg, store=store)

    ex.handle(message("каталог"))

    inline = [e for e in tg.outbound if e["type"] == "inline_keyboard"]
    assert len(inline) == 1
    keyboard = inline[0]["keyboard"]
    assert keyboard[0][0]["text"] == "Одежда"
    assert keyboard[0][0]["callback_data"] == "category:Одежда"
    assert keyboard[0][1]["text"] == "Обувь"
    assert keyboard[0][1]["callback_data"] == "category:Обувь"
    assert keyboard[1][0]["text"] == "⬅️ Назад"
    assert keyboard[1][0]["callback_data"] == "назад"


def test_inline_keyboard_from_db_alias_reads_global_db(tmp_path):
    store = Database(str(tmp_path / "db.json"))
    src = '''бот "TOKEN"
глобально категории = ["Пицца", "Суши", "Напитки"]
при старте:
    сохранить_глобально "категории" = категории
    ответ "Выберите категорию:"
    inline из бд "категории" callback "category:" назад "⬅️ Назад" → "назад"
'''
    program = Parser(src).parse()
    tg = MockTelegramAdapter()
    ex = Executor(program, tg, store=store)

    ex.handle({
        "message": {
            "message_id": 1,
            "chat": {"id": 1, "type": "private"},
            "from": {"id": 1, "first_name": "Tester"},
            "text": "/start",
        }
    })

    keyboard = [e for e in tg.outbound if e["type"] == "inline_keyboard"][0]["keyboard"]
    assert keyboard[0][0]["text"] == "Пицца"
    assert keyboard[0][0]["callback_data"] == "category:Пицца"
    assert keyboard[3][0]["callback_data"] == "назад"


def test_inline_keyboard_from_db_alias_supports_json_object_globals(tmp_path):
    store = Database(str(tmp_path / "db.json"))
    src = '''бот "TOKEN"
глобально категории = [{"id":"pizza","name":"Пицца"}, {"id":"sushi","name":"Суши"}]
при старте:
    сохранить_глобально "категории" = категории
    ответ "Выберите категорию:"
    inline из бд "категории" текст "name" id "id" callback "category:" назад "⬅️ Назад" → "назад"
'''
    program = Parser(src).parse()
    tg = MockTelegramAdapter()
    ex = Executor(program, tg, store=store)

    ex.handle({
        "message": {
            "message_id": 1,
            "chat": {"id": 1, "type": "private"},
            "from": {"id": 1, "first_name": "Tester"},
            "text": "/start",
        }
    })

    keyboard = [e for e in tg.outbound if e["type"] == "inline_keyboard"][0]["keyboard"]
    assert keyboard[0][0]["text"] == "Пицца"
    assert keyboard[0][0]["callback_data"] == "category:pizza"
    assert keyboard[1][0]["text"] == "Суши"
    assert keyboard[1][0]["callback_data"] == "category:sushi"


def test_exact_callback_handler_wins_over_generic_router():
    src = '''бот "TOKEN"
при нажатии:
    если начинается_с(кнопка, "category:"):
        ответ "category"
        вернуть

при нажатии "назад":
    ответ "Главное меню"
'''
    program = Parser(src).parse()
    tg = MockTelegramAdapter()
    ex = Executor(program, tg)

    ex.handle(callback("назад"))

    texts = [e["text"] for e in tg.outbound if e["type"] == "send_message"]
    assert texts == ["Главное меню"]
>>>>>>> 8838bf7 (Add dynamic inline keyboards, HTTP JSON blocks and catalog modules)
