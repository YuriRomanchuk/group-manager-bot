from aiogram import Router, F, Bot
from aiogram.types import Message, ChatMemberUpdated
from config import ADMIN_IDS, WELCOME_MESSAGE, MAX_WARNINGS
from utils.db import get_warnings, add_warning, get_settings

router = Router()


@router.chat_member()
async def on_new_member(event: ChatMemberUpdated):
    if event.new_chat_member.status in ("member", "restricted"):
        settings = get_settings(event.chat.id)
        if settings.get("welcome_enabled", 1):
            user = event.new_chat_member.user
            welcome = settings.get("welcome_message", WELCOME_MESSAGE).format(
                user=user.full_name,
                username=user.username or "N/A"
            )
            await event.answer(welcome)


@router.message(F.text.lower().contains("spam"))
@router.message(F.text.lower().contains("buy"))
@router.message(F.text.lower().contains("crypto"))
@router.message(F.text.lower().contains("airdrop"))
async def anti_spam(message: Message, bot: Bot):
    settings = get_settings(message.chat.id)
    if not settings.get("antispam_enabled", 1):
        return

    user_id = message.from_user.id
    chat_id = message.chat.id

    count = add_warning(user_id, chat_id, message.text[:50])

    if count >= MAX_WARNINGS:
        try:
            await bot.ban_chat_member(chat_id, user_id)
            await message.answer(f"User {message.from_user.full_name} banned (spam)")
            from utils.db import reset_warnings
            reset_warnings(user_id, chat_id)
        except Exception:
            pass
    else:
        remaining = MAX_WARNINGS - count
        await message.answer(
            f"Warning {count}/{MAX_WARNINGS} for {message.from_user.full_name}\n"
            f"{remaining} more warnings and you'll be banned."
        )


@router.message(F.command("warn"))
async def warn_user(message: Message, bot: Bot):
    if message.from_user.id not in ADMIN_IDS:
        return

    if not message.reply_to_message:
        await message.answer("Reply to a message to warn that user")
        return

    user_id = message.reply_to_message.from_user.id
    chat_id = message.chat.id
    reason = message.text.replace("/warn", "").strip() or "No reason"

    count = add_warning(user_id, chat_id, reason)

    if count >= MAX_WARNINGS:
        try:
            await bot.ban_chat_member(chat_id, user_id)
            await message.answer(f"User banned after {MAX_WARNINGS} warnings")
            from utils.db import reset_warnings
            reset_warnings(user_id, chat_id)
        except Exception:
            pass
    else:
        await message.answer(
            f"Warning {count}/{MAX_WARNINGS} for {message.reply_to_message.from_user.full_name}\n"
            f"Reason: {reason}"
        )


@router.message(F.command("unwarn"))
async def unwarn_user(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    if not message.reply_to_message:
        await message.answer("Reply to a message to unwarn that user")
        return

    from utils.db import reset_warnings
    reset_warnings(message.reply_to_message.from_user.id, message.chat.id)
    await message.answer(f"Warnings reset for {message.reply_to_message.from_user.full_name}")


@router.message(F.command("warnings"))
async def check_warnings(message: Message):
    if not message.reply_to_message:
        await message.answer("Reply to a message to check warnings")
        return

    count = get_warnings(message.reply_to_message.from_user.id, message.chat.id)
    await message.answer(f"{message.reply_to_message.from_user.full_name} has {count}/{MAX_WARNINGS} warnings")


@router.message(F.command("mute"))
async def mute_user(message: Message, bot: Bot):
    if message.from_user.id not in ADMIN_IDS:
        return

    if not message.reply_to_message:
        await message.answer("Reply to a message to mute that user")
        return

    try:
        from aiogram.types import ChatPermissions
        permissions = ChatPermissions(can_send_messages=False)
        await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, permissions)
        await message.answer(f"Muted {message.reply_to_message.from_user.full_name}")
    except Exception:
        await message.answer("Failed to mute user")


@router.message(F.command("unmute"))
async def unmute_user(message: Message, bot: Bot):
    if message.from_user.id not in ADMIN_IDS:
        return

    if not message.reply_to_message:
        await message.answer("Reply to a message to unmute that user")
        return

    try:
        from aiogram.types import ChatPermissions
        permissions = ChatPermissions(
            can_send_messages=True,
            can_send_audios=True,
            can_send_documents=True,
            can_send_photos=True,
            can_send_videos=True,
            can_send_video_notes=True,
            can_send_voice_notes=True,
            can_send_polls=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
            can_invite_users=True,
            can_change_info=True,
            can_pin_messages=True,
            can_manage_topics=True
        )
        await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, permissions)
        await message.answer(f"Unmuted {message.reply_to_message.from_user.full_name}")
    except Exception:
        await message.answer("Failed to unmute user")
