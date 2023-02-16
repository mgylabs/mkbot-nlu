# Mulgyeol MK Bot NLU
Natural Language Understanding (NLU) library for MK Bot

## Usage
```python
from mkbot_nlu.utils import Intent, register_intent

@register_intent("command::music::play", "play")
def cmd_play(intent: Intent):
    if query := intent.get_an_entity("music_query"):
        return f"play {query}"
    else:
        return "play"
```

## Development Guide
### Building from source
To install dependencies, execute:
```sh
poetry install -E full
```

### Running the Tests
```sh
poetry run pytest
```
