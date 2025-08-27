import asyncio
import contextlib
import logging
import os
import random
import sys
from typing import NoReturn

from aiogram.exceptions import TelegramRetryAfter
from aiogram.types import Update


logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


async def _watch_connectivity(bot) -> None:
    while True:
        try:
            await asyncio.wait_for(bot.get_me(), timeout=10)
        except Exception as exc:  # noqa: BLE001
            logging.error("Connectivity check failed: %s", exc)
            sys.exit(1)
        await asyncio.sleep(15)


async def _backfill_pending_updates(bot, dp) -> None:
    should_backfill = os.getenv("BOT_BACKFILL_ON_START", "false").strip().lower() in {"1", "true", "yes"}
    if not should_backfill:
        return
    logging.info("Backfilling pending updates before starting polling...")
    # Ensure webhook is removed without dropping pending updates so getUpdates backlog remains
    with contextlib.suppress(Exception):
        await bot.delete_webhook(drop_pending_updates=False)

    offset: int | None = None
    limit = 100
    handled = 0
    while True:
        updates: list[Update] = await bot.get_updates(offset=offset, limit=limit, timeout=0)
        if not updates:
            break
        for upd in updates:
            try:
                await dp.feed_update(bot, upd)
            except Exception as exc:  # noqa: BLE001
                logging.error("Failed to handle backfill update %s: %s", getattr(upd, "update_id", "?"), exc)
            finally:
                offset = upd.update_id + 1
                handled += 1
    if handled:
        logging.info("Backfill complete. Handled %s pending updates.", handled)
    else:
        logging.info("No pending updates to backfill.")


async def start_polling_once(exit_on_disconnect: bool) -> None:
    from aiogram import Bot, Dispatcher

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logging.warning("TELEGRAM_BOT_TOKEN is not set. Sleeping instead of polling...")
        if exit_on_disconnect:
            sys.exit(1)
        while True:
            await asyncio.sleep(3600)

    bot = Bot(token=token)
    from src.core.dispatcher import build_dispatcher

    dp = build_dispatcher()

    logging.info("Starting aiogram polling...")
    watcher_task: asyncio.Task | None = None
    if exit_on_disconnect:
        watcher_task = asyncio.create_task(_watch_connectivity(bot))
    try:
        # Start matching loop in background
        try:
            from src.services.matching import run_matching_loop  # type: ignore
            asyncio.create_task(run_matching_loop(bot))
        except Exception:
            pass
        await _backfill_pending_updates(bot, dp)
        await dp.start_polling(bot)
    finally:
        if watcher_task is not None:
            watcher_task.cancel()
            with contextlib.suppress(Exception):
                await watcher_task
        await bot.session.close()


async def run_polling_forever() -> NoReturn:
    exit_on_disconnect = os.getenv("BOT_EXIT_ON_DISCONNECT", "false").strip().lower() in {"1", "true", "yes"}
    min_backoff_seconds = 1
    max_backoff_seconds = 60
    backoff_seconds = min_backoff_seconds

    while True:
        try:
            await start_polling_once(exit_on_disconnect)
            backoff_seconds = min_backoff_seconds
        except TelegramRetryAfter as exc:
            delay = int(exc.retry_after) + random.randint(0, 3)
            logging.warning("Rate limited. Retrying in %s seconds...", delay)
            await asyncio.sleep(delay)
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001
            logging.error("Polling error: %s", exc)
            if exit_on_disconnect:
                logging.error("Exiting due to BOT_EXIT_ON_DISCONNECT=true")
                sys.exit(1)
            await asyncio.sleep(backoff_seconds)
            backoff_seconds = min(backoff_seconds * 2, max_backoff_seconds)


def main() -> None:
    asyncio.run(run_polling_forever())


if __name__ == "__main__":
    main()


