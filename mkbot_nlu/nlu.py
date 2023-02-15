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
        self, model_path: str = f"{DEFAULT_MODEL_DIR}/nlu-20230213-231000.tar.gz"
    ) -> None:
        from rasa.core.agent import Agent

        self.agent = Agent.load(model_path)

    @classmethod
    async def download_ko_model(cls, target_dir_path: str):
        download_dir_name = "mkbot-nlu"
        download_dir_path = os.getenv("TEMP") + f"/{download_dir_name}"
        tar_dir_name = "ko_news_md-0.1.0"
        package_name = "ko_news_md"

        download_file_name = f"{download_dir_path}/{tar_dir_name}.tar.gz"

        os.makedirs(download_dir_path, exist_ok=True)

        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.get(
                "https://github.com/mgylabs/spacy_ko_model/releases/download/ko_news_md-0.1.0/ko_news_md-0.1.0.tar.gz",
            ) as r:
                with open(download_file_name, "wb") as f:
                    async for chunk in r.content.iter_chunked(1024 * 1024):
                        f.write(chunk)

        tar = tarfile.open(download_file_name)
        tar.extractall(download_dir_path)
        tar.close()

        os.makedirs(target_dir_path, exist_ok=True)

        shutil.move(
            f"{download_dir_path}/{tar_dir_name}/{package_name}", f"{target_dir_path}/{package_name}"
        )
        shutil.move(
            f"{download_dir_path}/{tar_dir_name}/{package_name}.egg-info",
            f"{target_dir_path}/{package_name}.egg-info",
        )

    def sync_parse(self, message: str) -> Intent:
        message = message.strip()
        result = asyncio.run(self.agent.parse_message(message))
        intent = Intent(result)
        intent.response = CommandConnector.Run(intent)
        return intent

    async def parse(self, message: str) -> Intent:
        message = message.strip()
        result = await self.agent.parse_message(message)
        intent = Intent(result)
        intent.response = CommandConnector.Run(intent)
        return intent
