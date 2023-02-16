import asyncio
import logging
import multiprocessing
import os
import shutil
import tarfile
from multiprocessing.managers import SyncManager

import aiohttp

from mkbot_nlu.paths import MODULE_ROOT_PATH
from mkbot_nlu.utils import CommandConnector, Intent

log = logging.getLogger(__name__)

DEFAULT_MODEL_DIR = os.path.join(MODULE_ROOT_PATH, "models")


class NluTask:
    manager: SyncManager = None

    def __init__(self, text: str) -> None:
        self.event = self.manager.Event()
        self.namespace = self.manager.Namespace()
        self.text = text
        self.intent = None

    @property
    def text(self):
        return self.namespace.text

    @text.setter
    def text(self, text: str):
        self.namespace.text = text

    @property
    def intent(self):
        self.event.wait()
        return self.namespace.intent

    @intent.setter
    def intent(self, intent: Intent):
        self.namespace.intent = intent


class Loader(multiprocessing.Process):
    def __init__(
        self,
        model_path: str,
        task_queue: multiprocessing.Queue,
    ) -> None:
        super().__init__(daemon=True)

        self.model_path = model_path
        self.task_queue = task_queue

    async def _nlu_parse(self, agent, message: str):
        message = message.strip()
        result = await agent.parse_message(message)
        intent = Intent(result)

        return intent

    async def _nlu_main(self):
        log.info("NLU Model Loading...")

        from rasa.core.agent import Agent

        agent = Agent.load(self.model_path)

        log.info("NLU Model Loaded")

        while True:
            task: NluTask = self.task_queue.get()

            intent = await self._nlu_parse(agent, task.text)
            task.intent = intent

            task.event.set()

    def run(self):
        proc_name = self.name
        log.info(f"Start process: {proc_name}")

        asyncio.run(self._nlu_main())

        log.info(f"End of process: {proc_name}")


class MKBotNLU:
    def __init__(
        self, model_path: str = f"{DEFAULT_MODEL_DIR}/nlu-20230213-231000.tar.gz"
    ) -> None:
        self.model_path = model_path
        self.manager = multiprocessing.Manager()
        NluTask.manager = self.manager

    def start(self):
        self.tasks = self.manager.Queue()
        self.loader = Loader(self.model_path, self.tasks)
        self.loader.start()

    def join(self):
        self.loader.join()

    def terminate(self):
        self.loader.terminate()

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
            f"{download_dir_path}/{tar_dir_name}/{package_name}",
            f"{target_dir_path}/{package_name}",
        )
        shutil.move(
            f"{download_dir_path}/{tar_dir_name}/{package_name}.egg-info",
            f"{target_dir_path}/{package_name}.egg-info",
        )

    def _request_nlu(self, message: str):
        task = NluTask(message)
        self.tasks.put(task)

        intent = task.intent
        intent.response = CommandConnector.Run(intent)

        return intent

    def sync_parse(self, message: str):
        return self._request_nlu(message)

    async def parse(self, message: str) -> Intent:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._request_nlu, message)
