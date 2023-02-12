import asyncio
import os
import tarfile

import requests
from rasa.core.agent import Agent

from mkbot_nlu.utils import CommandConnector, Intent


class MKBotNLU:
    def __init__(self, model_path: str) -> None:
        self.agent = Agent.load(model_path)
        download_dir_name = "mkbot-nlu"
        self.download_dir_path = os.getenv("TEMP") + f"\\{download_dir_name}"

    def download_ko_wiki_model(self):
        download_file_name = f"{self.download_dir_path}\\ko_wiki_model-0.0.0.tar.gz"

        os.makedirs(os.path.dirname(download_file_name), exist_ok=True)

        r = requests.get(
            "https://github.com/mgylabs/spacy_ko_wiki_model/releases/download/v0.0.0/ko_wiki_model-0.0.0.tar.gz",
            stream=True,
        )
        r.raise_for_status()

        with open(download_file_name, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                f.write(chunk)

        tar = tarfile.open(download_file_name)
        tar.extractall()
        tar.close()

    def sync_parse(self, message: str) -> str:
        message = message.strip()
        result = asyncio.run(self.agent.parse_message(message))
        return CommandConnector.Run(Intent(result))

    async def parse(self, message: str):
        message = message.strip()
        result = await self.agent.parse_message(message)
        return CommandConnector.Run(Intent(result))