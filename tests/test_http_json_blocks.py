from dataclasses import dataclass

from cicada.adapters.mock_telegram import MockTelegramAdapter
from cicada.executor import Executor
from cicada.parser import Parser


@dataclass
class FakeResponse:
    text: str


class FakeHttp:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def get(self, url, *, headers=None, timeout=30):
        self.calls.append(("GET", url, headers, timeout))
        return FakeResponse(self.responses.pop(0))


def message(text: str = "go", chat_id: int = 1):
    return {
        "message": {
            "message_id": 1,
            "chat": {"id": chat_id, "type": "private"},
            "from": {"id": chat_id, "first_name": "Tester"},
            "text": text,
        }
    }


def outbound_texts(tg):
    return [e["text"] for e in tg.outbound if e["type"] == "send_message"]


def test_fetch_json_block_returns_value_to_handler():
    src = '''бот "TOKEN"
блок погода:
    fetch_json "https://api.example.com/weather?q={город}" → данные
    вернуть данные["current"]["temp_c"]

при тексте:
    пусть город = "Moscow"
    вызвать "погода" → температура
    ответ "Температура: {температура}"
'''
    program = Parser(src).parse()
    tg = MockTelegramAdapter()
    http = FakeHttp(['{"current": {"temp_c": 7}}'])
    ex = Executor(program, tg, http=http)

    ex.handle(message())

    assert http.calls == [("GET", "https://api.example.com/weather?q=Moscow", {}, 30)]
    assert outbound_texts(tg) == ["Температура: 7"]


def test_fetch_raw_then_parse_json_can_feed_later_block():
    src = '''бот "TOKEN"
блок заголовок:
    ответ "Новость: {новости['articles'][0]['title']}"

при тексте:
    fetch "https://api.example.com/news" → ответ_api
    разобрать_json ответ_api → новости
    использовать заголовок
'''
    program = Parser(src).parse()
    tg = MockTelegramAdapter()
    http = FakeHttp(['{"articles": [{"title": "Cicada ships fetch blocks"}]}'])
    ex = Executor(program, tg, http=http)

    ex.handle(message())

    assert http.calls == [("GET", "https://api.example.com/news", {}, 30)]
    assert outbound_texts(tg) == ["Новость: Cicada ships fetch blocks"]
