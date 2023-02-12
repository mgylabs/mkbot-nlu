from functools import wraps
from typing import Union


class Intent:
    def __init__(self, parse_result: dict) -> None:
        self.name = parse_result["intent"]["name"]
        self.entities = {}

        self.parse_entities(parse_result["entities"])

    def get_an_entity(self, name):
        if name in self.entities:
            return self.entities[name][0]
        else:
            return None

    def parse_entities(self, entities: list):
        for entity in entities:
            self.entities.setdefault(entity["entity"], []).append(entity["value"])


def register_intent(name: str):
    def deco(func):
        CommandConnector.intent2method[name] = func

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return deco


class CommandConnector:
    intent2method = {}

    @classmethod
    def Run(cls, intent: Intent) -> Union[str, None]:
        if intent.name in cls.intent2method:
            return cls.intent2method[intent.name]()
        else:
            return None
