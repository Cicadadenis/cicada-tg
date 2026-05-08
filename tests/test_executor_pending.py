from cicada.adapters.mock_telegram import MockTelegramAdapter
from cicada.executor import Executor
from cicada.parser import Parser


def make_executor(source: str):
    program = Parser(source).parse()
    telegram = MockTelegramAdapter()
    return Executor(program, telegram), telegram


def message(text: str, chat_id: int = 1):
    return {
        "message": {
            "message_id": 1,
            "chat": {"id": chat_id, "type": "private"},
            "from": {"id": chat_id, "first_name": "Tester"},
            "text": text,
        }
    }


def callback(data: str, chat_id: int = 1):
    return {
        "callback_query": {
            "id": "cb-1",
            "from": {"id": chat_id, "first_name": "Tester"},
            "message": {"message_id": 1, "chat": {"id": chat_id, "type": "private"}},
            "data": data,
        }
    }


def sent_texts(telegram: MockTelegramAdapter):
    return [event["text"] for event in telegram.outbound if event["type"] == "send_message"]


def test_pending_statements_resume_after_text_answer_outside_scenario():
    executor, telegram = make_executor(
        '''бот "TOKEN"
при тексте:
    спросить "Как вас зовут?" -> имя
    ответ "Привет, {имя}!"
'''
    )

    executor.handle(message("начать"))
    assert sent_texts(telegram) == ["Как вас зовут?"]

    telegram.clear_outbound()
    executor.handle(message("Алиса"))

    assert sent_texts(telegram) == ["Привет, Алиса!"]


def test_pending_statements_resume_after_callback_answer_outside_scenario():
    executor, telegram = make_executor(
        '''бот "TOKEN"
при тексте:
    спросить "Выберите вариант" -> выбор
    ответ "Вы выбрали: {выбор}"
'''
    )

    executor.handle(message("начать"))
    telegram.clear_outbound()
    executor.handle(callback("Да"))

    assert sent_texts(telegram) == ["Вы выбрали: Да"]


def test_duplicate_ask_nodes_resume_after_current_instruction():
    executor, telegram = make_executor(
        '''бот "TOKEN"
при тексте:
    спросить "Повторите ввод" -> первый
    спросить "Повторите ввод" -> второй
    ответ "{первый}/{второй}"
'''
    )

    executor.handle(message("начать"))
    assert sent_texts(telegram) == ["Повторите ввод"]

    telegram.clear_outbound()
    executor.handle(message("один"))
    assert sent_texts(telegram) == ["Повторите ввод"]

    telegram.clear_outbound()
    executor.handle(message("два"))
    assert sent_texts(telegram) == ["один/два"]
