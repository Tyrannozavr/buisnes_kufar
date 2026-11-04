"""Celery / fire-and-forget enqueue for auth SMTP emails.

На request-path предпочитаем asyncio.create_task: иначе kombu.delay при
недоступном брокере может тормозить register/reset на несколько секунд.
Celery — для sync-контекста и retry в воркере.
"""
from __future__ import annotations

import asyncio
from typing import Literal, Optional

from app.celery_app import celery_app
from app_logging.logger import logger

AuthEmailKind = Literal[
    "verification",
    "password_reset",
    "password_recovery",
    "email_change_code",
]


def enqueue_auth_email(
    kind: AuthEmailKind,
    email: str,
    *,
    url: Optional[str] = None,
    code: Optional[str] = None,
) -> None:
    """Fire-and-forget; never block the HTTP request on SMTP/broker."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        loop.create_task(_send_auth_email_async(kind, email, url=url, code=code))
        return

    try:
        send_auth_email.delay(kind, email, url, code)
        return
    except Exception as exc:
        logger.warning("Celery enqueue auth email failed, running inline: %s", exc)

    asyncio.run(_send_auth_email_async(kind, email, url=url, code=code))


def _run_coro_sync(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        return asyncio.ensure_future(coro, loop=loop)
    return asyncio.run(coro)


@celery_app.task(name="auth.send_email", bind=True, max_retries=3, default_retry_delay=30)
def send_auth_email(
    self,
    kind: str,
    email: str,
    url: Optional[str] = None,
    code: Optional[str] = None,
) -> None:
    try:
        ok = _run_coro_sync(_send_auth_email_async(kind, email, url=url, code=code))
    except Exception as exc:
        logger.exception("Auth email task failed kind=%s email=%s", kind, email)
        raise self.retry(exc=exc)
    if ok is False:
        raise self.retry(exc=RuntimeError(f"SMTP send failed kind={kind} email={email}"))


async def _send_auth_email_async(
    kind: str,
    email: str,
    *,
    url: Optional[str] = None,
    code: Optional[str] = None,
) -> bool:
    from app.core.email_utils import (
        send_email_change_code,
        send_password_recovery_code,
        send_password_reset_email,
        send_verification_email,
    )

    ok = False
    if kind == "verification":
        if not url:
            logger.error("Auth email verification missing url for %s", email)
            return False
        ok = await send_verification_email(email, url)
        if not ok:
            logger.error("VERIFICATION LINK FOR DEVELOPMENT: %s", url)
    elif kind == "password_reset":
        if not url:
            logger.error("Auth email password_reset missing url for %s", email)
            return False
        ok = await send_password_reset_email(email, url)
    elif kind == "password_recovery":
        if not code:
            logger.error("Auth email password_recovery missing code for %s", email)
            return False
        ok = await send_password_recovery_code(email, code)
        if not ok:
            logger.error("RECOVERY CODE FOR DEVELOPMENT: %s", code)
    elif kind == "email_change_code":
        if not code:
            logger.error("Auth email email_change_code missing code for %s", email)
            return False
        ok = await send_email_change_code(email, code)
    else:
        logger.error("Unknown auth email kind=%s email=%s", kind, email)
        return False

    return bool(ok)