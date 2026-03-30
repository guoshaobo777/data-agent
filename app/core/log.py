import asyncio
import sys
from pathlib import Path

from loguru import logger

from app.agent.context import request_id_ctx_var
from app.conf.app_config import app_config

log_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<magenta> request_id - {extra[request_id]} </magenta> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)

# 注入 request_id 到日志记录中
def inject_request_id(record):
    request_id = request_id_ctx_var.get()
    record["extra"]["request_id"] = request_id

logger.remove()

# 给日志打补丁，使其支持注入 request_id
logger = logger.patch(inject_request_id)
if app_config.logging.console.enable:
    logger.add(
        sink=sys.stdout,
        level=app_config.logging.console.level,
        format=log_format
    )

if app_config.logging.file.enable:
    path = Path(app_config.logging.file.path)
    path.mkdir(parents=True, exist_ok=True)
    logger.add(
        sink=path / "app.log",
        level=app_config.logging.file.level,
        rotation=app_config.logging.file.rotation,
        retention=app_config.logging.file.retention,
        format=log_format
    )

if __name__ == '__main__':
    async def graph(request: str):
        # 打印日志
        logger.info(request)

    async def test1():
        # 接收到请求
        request_id_ctx_var.set("request-1")
        await asyncio.sleep(1)
        await graph("request-1")

    async def test2():
        # 接收到请求
        request_id_ctx_var.set("request-2")
        await asyncio.sleep(1)
        await graph("request-2")

    async def run():
        await asyncio.gather(test1(), test2())

    asyncio.run(run())