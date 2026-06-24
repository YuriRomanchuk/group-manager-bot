from aiogram import Router, F
from aiogram.types import Message
from config import ADMIN_IDS
from utils.db import update_settings, get_settings

router = Router()


@router.message(F.command("settings"))
async def settings_panel(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("Admin only command")
        return

    settings = get_settings(message.chat.id)
    status = "ON" if settings.get("welcome_enabled", 1) else "OFF"
    antispam = "ON" if settings.get("antispam_enabled", 1) else "OFF"

    await message.answer(
        f"Bot Settings\n\n"
        f"Welcome: {status}\n"
        f"Anti-spam: {antispam}\n\n"
        f"Commands:\n"
        f"/toggle_welcome - Toggle welcome messages\n"
        f"/toggle_antispam - Toggle anti-spam\n"
        f"/set_welcome <message> - Set welcome message\n\n"
        f"Variables: {{user}}, {{username}}"
    )


@router.message(F.command("toggle_welcome"))
async def toggle_welcome(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    settings = get_settings(message.chat.id)
    new_val = 0 if settings.get("welcome_enabled", 1) else 1
    update_settings(message.chat.id, welcome_enabled=new_val)
    await message.answer(f"Welcome messages: {'ON' if new_val else 'OFF'}")


@router.message(F.command("toggle_antispam"))
async def toggle_antispam(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    settings = get_settings(message.chat.id)
    new_val = 0 if settings.get("antispam_enabled", 1) else 1
    update_settings(message.chat.id, antispam_enabled=new_val)
    await message.answer(f"Anti-spam: {'ON' if new_val else 'OFF'}")


@router.message(F.command("set_welcome"))
async def set_welcome(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    msg = message.text.replace("/set_welcome", "").strip()
    if not msg:
        await message.answer("Usage: /set_welcome Hello {user}! Welcome to our group!")
        return

    update_settings(message.chat.id, welcome_message=msg)
    await message.answer(f"Welcome message updated:\n{msg}")


@router.message(F.command("help"))
async def help_cmd(message: Message):
    await message.answer(
        "Group Manager Bot\n\n"
        "Admin Commands:\n"
        "/settings - Bot settings panel\n"
        "/warn - Warn a user (reply to message)\n"
        "/unwarn - Remove warning\n"
        "/warnings - Check user warnings\n"
        "/mute - Mute a user\n"
        "/unmute - Unmute a user\n"
        "/toggle_welcome - Toggle welcome\n"
        "/toggle_antispam - Toggle anti-spam\n"
        "/set_welcome <message> - Set welcome text\n\n"
        "Anti-spam detects: spam, buy, crypto, airdrop"
    )
