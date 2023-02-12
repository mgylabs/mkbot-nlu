import asyncio
import os
import shutil
import tarfile

import aiohttp

from mkbot_nlu.paths import MODULE_ROOT_PATH
from mkbot_nlu.utils import CommandConnector, Intent

DEFAULT_MODEL_DIR = os.path.join(MODULE_ROOT_PATH, "models")


class MKBotNLU:
    def __init__(
        self, model_path: str = f"{DEFAULT_MODEL_DIR}/nlu-20230210-225717.tar.gz"
    ) -> None:
        from rasa.core.agent import Agent

        self.agent = Agent.load(model_path)

    @classmethod
    async def download_ko_wiki_model(cls):
        download_dir_name = "mkbot-nlu"
        download_dir_path = os.getenv("TEMP") + f"/{download_dir_name}"
        tar_dir_name = "ko_wiki_model-0.0.0"
        package_name = "ko_wiki_model"

        download_file_name = f"{download_dir_path}/{tar_dir_name}.tar.gz"

        os.makedirs(download_dir_path, exist_ok=True)

        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.get(
                "https://github.com/mgylabs/spacy_ko_wiki_model/releases/download/v0.0.0/ko_wiki_model-0.0.0.tar.gz",
            ) as r:
                with open(download_file_name, "wb") as f:
                    async for chunk in r.content.iter_chunked(1024 * 1024):
                        f.write(chunk)

        tar = tarfile.open(download_file_name)
        tar.extractall(download_dir_path)
        tar.close()

        shutil.move(
            f"{download_dir_path}/{tar_dir_name}/{package_name}", f"./{package_name}"
        )
        shutil.move(
            f"{download_dir_path}/{tar_dir_name}/{package_name}.egg-info",
            f"./{package_name}.egg-info",
        )

    def sync_parse(self, message: str) -> str:
        message = message.strip()
        result = asyncio.run(self.agent.parse_message(message))
        intent = Intent(result)
        intent.cmd = CommandConnector.Run(intent)
        return intent

    async def parse(self, message: str):
        message = message.strip()
        result = await self.agent.parse_message(message)
        intent = Intent(result)
        intent.cmd = CommandConnector.Run(intent)
        return intent
