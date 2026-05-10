"""кодировать_url — пробелы и кириллица в query string."""

from cicada.adapters.mock_telegram import MockTelegramAdapter
from cicada.executor import Executor
from cicada.parser import Parser


def test_qr_reply_encodes_multiline_query_value():
    src = r'''бот "TOKEN"
при тексте:
    запомни qr_text = "привет всем"
    ответ "https://api.example.com/?data={кодировать_url(qr_text)}"
'''
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
    texts = [e["text"] for e in tg.outbound if e["type"] == "send_message"]
    assert len(texts) == 1
    assert "привет%20всем" in texts[0] or "%D0%BF%D1%80%D0%B8%D0%B2%D0%B5%D1%82%20%D0%B2%D1%81%D0%B5%D0%BC" in texts[0]


def test_kodirovat_url_builtin():
    from cicada.executor import _call_builtin
    assert _call_builtin("кодировать_url", ["a b"]) == "a%20b"
