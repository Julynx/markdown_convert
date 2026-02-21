"""
Autoinstall chromium headless browser for playwright.
"""

import os

from install_playwright import install
from playwright.sync_api import sync_playwright

from .constants import GREEN, RED
from .utils import color


def ensure_chromium(loud=True):
    """
    Ensures the chromium playwright browser is installed.
    If not, tries to install it.
    """
    with sync_playwright() as playwright:
        if is_browser_installed(playwright.chromium):
            return True

        if loud:
            print(
                "The Playwright Chromium browser was not found."
                " Attempting to install it, please wait..."
            )

        try:
            result = install([playwright.chromium])
            if not result:
                result = install([playwright.chromium], with_deps=True)

            if loud:
                if result:
                    msg = color(
                        GREEN,
                        "The Playwright Chromium browser was successfully installed.\n",
                    )
                    print(msg)
                else:
                    msg = color(
                        RED,
                        "ERROR: The Playwright Chromium browser could not be"
                        " automatically installed."
                        "\nPlease manually run 'playwright install' and try again.\n",
                    )
                    print(msg)

            return result

        except Exception as exc:
            msg = color(
                RED,
                "ERROR: There was an exception while trying to install the"
                f" Playwright Chromium browser:\n{exc}",
            )
            print(msg)
            return False


def is_browser_installed(browser):
    """
    Checks if a specific browser is installed by verifying its executable path.
    Browser type can be 'chromium', 'firefox', or 'webkit'.
    """
    try:
        return os.path.exists(browser.executable_path)
    except Exception:
        return False
