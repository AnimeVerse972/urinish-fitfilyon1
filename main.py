import os
import logging
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode, ChatMemberStatus
from aiogram.types import (
    Message, 
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton
)
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart
from aiogram.utils.markdown import hbold
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiohttp import web

# Token va sozlamalar
API_TOKEN = os.getenv("BOT_TOKEN")
CHANNELS = ['@AniVerseClip', '@StudioNovaOfficial']
ADMINS = ['6486825926', '7575041003']

# Logger
logging.basicConfig(level=logging.INFO)

# Bot va Dispatcher
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

# Keep-alive uchun mini web server (Render uchun)
async def on_startup(app: web.Application):
    logging.info("Web server ishga tushdi!")

async def handle(request):
    return web.Response(text="Bot ishga tushgan!")

app = web.Application()
app.router.add_get("/", handle)
app.on_startup.append(on_startup)

# /start komandasi
@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    not_subscribed = []

    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status not in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                not_subscribed.append(channel)
        except Exception:
            not_subscribed.append(channel)

    if not_subscribed:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=f"🔔 {ch}", url=f"https://t.me/{ch.strip('@')}")] for ch in not_subscribed
            ]
        )
        await message.answer("📛 *Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling:*", reply_markup=keyboard)
        return

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📢 Reklama"), KeyboardButton(text="💼 Homiylik")]
        ],
        resize_keyboard=True
    )

    await message.answer("✅ Assalomu alaykum!\nAnime kodini yuboring (masalan: 1, 2, 3, ...)", reply_markup=keyboard)

# Kod bilan xabarni yuborish
@router.message()
async def handle_code(message: Message):
    user_id = message.from_user.id
    text = message.text.strip()

    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status not in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                await message.answer(f"⛔ Iltimos, {channel} kanaliga obuna bo‘ling va qaytadan urinib ko‘ring.")
                return
        except Exception:
            await message.answer(f"⚠️ {channel} kanal tekshiruvida xatolik.")
            return

    anime_posts = {
        "1": {"channel": "@AniVerseClip", "message_id": 10},
        "2": {"channel": "@AniVerseClip", "message_id": 23},
        # ... qolganlar
        "45": {"channel": "@AniVerseClip", "message_id": 946},
    }

    if text in anime_posts:
        channel = anime_posts[text]["channel"]
        msg_id = anime_posts[text]["message_id"]

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="TOMOSHA QILISH", url=f"https://t.me/{channel.strip('@')}/{msg_id}")]
        ])
        await bot.copy_message(chat_id=user_id, from_chat_id=channel, message_id=msg_id, reply_markup=keyboard)

    elif text == "📢 Reklama":
        await message.answer("Reklama uchun @DiyorbekPTMA ga murojat qiling. Faqat reklama bo‘yicha!")
    elif text == "💼 Homiylik":
        await message.answer("Homiylik uchun karta: 8800904257677885")
    else:
        await message.answer("❌ Bunday kod topilmadi. Iltimos, to‘g‘ri anime kodini yuboring.")

# Botni ishga tushirish
if __name__ == "__main__":
    import asyncio
    from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

    async def main():
        await bot.delete_webhook(drop_pending_updates=True)
        runner = web.AppRunner(app)
        await runner.setup()

        site = web.TCPSite(runner, "0.0.0.0", 8080)
        await site.start()

        await dp.start_polling(bot)

    asyncio.run(main())
