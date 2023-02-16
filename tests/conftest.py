import pytest

from mkbot_nlu.nlu import MKBotNLU


@pytest.fixture(scope="session")
def nlu():
    nlu = MKBotNLU()
    nlu.start()
    return nlu
