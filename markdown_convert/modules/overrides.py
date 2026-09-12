"""
Module providing runtime overrides and patches.
"""

import asyncio
from typing import Any

from playwright.sync_api._context_manager import PlaywrightContextManager


def apply_playwright_context_cleanup_patch() -> None:
    """
    Patches PlaywrightContextManager exit handler to await cancelled tasks.

    Playwright's default synchronous context manager cancels internal connection
    tasks and immediately closes the event loop without running cancellation
    callbacks. Awaiting task completion prevents unretrieved exception warnings
    during interpreter shutdown.
    """

    def _safe_playwright_context_exit(
        self: PlaywrightContextManager, *args: Any
    ) -> None:
        if self._exit_was_called:
            return
        self._exit_was_called = True
        self._connection.stop_sync()
        if self._watcher:
            self._watcher.close()
        if self._own_loop:
            pending_tasks = [
                task for task in asyncio.all_tasks(self._loop) if not task.done()
            ]
            for pending_task in pending_tasks:
                pending_task.cancel()
            if pending_tasks:
                self._loop.run_until_complete(
                    asyncio.gather(*pending_tasks, return_exceptions=True)
                )
            self._loop.run_until_complete(self._loop.shutdown_asyncgens())
            self._loop.close()

    PlaywrightContextManager.__exit__ = _safe_playwright_context_exit


apply_playwright_context_cleanup_patch()
