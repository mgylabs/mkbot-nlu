import pytest

from mkbot_nlu.nlu import MKBotNLU


def test_sync_parse(nlu: MKBotNLU):
    text = "안녕하세요"
    intent = nlu.sync_parse(text)
    intent.name == "chat::greet"
    intent.text == text


@pytest.mark.asyncio
async def test_parse(nlu: MKBotNLU):
    text = "안녕하세요"
    intent = await nlu.parse(text)
    intent.name == "chat::greet"
    intent.text == text
