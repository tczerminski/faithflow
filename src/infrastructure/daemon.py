import asyncio
from asyncio import CancelledError
from datetime import timedelta

import structlog
from structlog.contextvars import bound_contextvars

from src.infrastructure.skew import skew


def daemon(
    interval: timedelta, func, logging_context: dict | None = None
) -> asyncio.Task:
    async def background():
        seconds = interval.total_seconds()
        if seconds <= 0:
            raise ValueError("Interval must be greater than zero.")
        context = logging_context or {}
        logger = structlog.get_logger().bind(
            logger=func.__name__,
        )
        with bound_contextvars(**context):
            await logger.ainfo("starting daemon")
            try:
                while True:
                    delay = skew(seconds)
                    await logger.adebug(
                        "waiting till daemon execution",
                        delay=delay,
                    )
                    await asyncio.sleep(delay)
                    await logger.adebug("executing daemon")
                    # noinspection PyBroadException
                    try:
                        await func()
                    except Exception:
                        await logger.aexception("exception caught")
                    finally:
                        continue
            except CancelledError:
                await logger.ainfo("stopping daemon")
                await func()

    return asyncio.create_task(background())
