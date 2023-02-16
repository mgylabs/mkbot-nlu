import pytest

from mkbot_nlu.nlu import MKBotNLU


@pytest.mark.asyncio
async def test_parse(nlu: MKBotNLU):
    text = "안녕하세요"
    intent = await nlu.parse(text)
    assert intent.name == "chat::greet"
    assert intent.text == text


@pytest.mark.asyncio
async def test_get_an_entity(nlu: MKBotNLU):
    text = "메시지 4개 삭제"
    intent = await nlu.parse(text)
    assert intent.name == "command::delete"
    assert intent.text == text

    amount = intent.get_an_entity("amount")

    assert amount == "4"
