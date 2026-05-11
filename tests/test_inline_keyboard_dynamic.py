from cicada.adapters.mock_telegram import MockTelegramAdapter
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
