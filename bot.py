import logging
import os
from pathlib import Path

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)

DESIGN, QUANTITY, GROOM, BRIDE, DATE, EVENING, TIME, ADDRESS, PHONE, NAME, CONFIRM = range(11)
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "").strip()
IMAGE_DIR = Path(__file__).resolve().parent / "RASM"
DESIGNS = {
    "01": {"price": 12000, "label": "01 — 12 000 so‘m / dona"},
    "02": {"price": 15000, "label": "02 — 15 000 so‘m / dona"},
    "03": {"price": 15000, "label": "03 — 15 000 so‘m / dona"},
    "04": {"price": 30000, "label": "04 — 30 000 so‘m / dona"},
    "05": {"price": 30000, "label": "05 — 30 000 so‘m / dona"},
    "06": {"price": 40000, "label": "06 — 40 000 so‘m / dona"},
    "07": {"price": 20000, "label": "07 — 20 000 so‘m / dona"},
    "08": {"package": 50000, "label": "08 — 100 tasi 50 000 so‘m"},
    "09": {"package": 50000, "label": "09 — 100 tasi 50 000 so‘m"},
    "10": {"package": 50000, "label": "10 — 100 tasi 50 000 so‘m"},
    "11": {"price": 20000, "label": "11 — 20 000 so‘m / dona"},
    "12": {"price": 15000, "label": "12 — 15 000 so‘m / dona"},
    "13": {"price": 20000, "label": "13 — Zamish, 20 000 so‘m / dona"},
    "14": {"package": 30000, "label": "14 — 100 tasi 30 000 so‘m"},
}


def money(value: int) -> str:
    return f"{value:,}".replace(",", " ")


def answer_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([["✕ Buyurtmani bekor qilish"]], resize_keyboard=True, one_time_keyboard=True)


def calculate_total(design: str, quantity: int) -> int:
    item = DESIGNS[design]
    if "price" in item:
        return item["price"] * quantity
    if design in {"08", "09", "10"}:
        unit_price = 500 if quantity >= 100 else 650 if quantity >= 50 else 800
    else:
        unit_price = 300 if quantity >= 100 else 400 if quantity >= 50 else 500
    return unit_price * quantity


async def send_catalog(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.effective_message
    await message.reply_text(
        "✉ ZafarXatlari katalogi\n\n"
        "Sizga yoqqan xat namunasini tanlang. Har bir namuna alohida ko‘rsatilgan — rasm ostidagi tugmani bosing.\n\n"
        "▸ 08, 09, 10 va 14 uchun 100 talik narx arzonroq. 100 tadan kam buyurtmada bot narxni alohida hisoblaydi."
    )
    for number, item in DESIGNS.items():
        image_path = IMAGE_DIR / f"{number}.jpg"
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(f"✉ {number}-namunani tanlash", callback_data=f"design:{number}")]])
        if image_path.exists():
            with image_path.open("rb") as image:
                await message.reply_photo(photo=image, caption=item["label"], reply_markup=keyboard)
        else:
            await message.reply_text(f"✉ {item['label']}\nRasm topilmadi.", reply_markup=keyboard)
    return DESIGN


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    return await send_catalog(update, context)


async def choose_design(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    design = query.data.split(":", 1)[1]
    context.user_data["design"] = design
    await query.message.reply_text(
        f"✓ {DESIGNS[design]['label']} tanlandi.\n\nNechta xat kerak? Faqat son yozing.",
        reply_markup=answer_keyboard(),
    )
    return QUANTITY


async def save_text(update: Update, context: ContextTypes.DEFAULT_TYPE, key: str, next_text: str, next_state: int) -> int:
    if update.message.text.lower() in {"bekor qilish", "✕ buyurtmani bekor qilish", "/cancel"}:
        return await cancel(update, context)
    context.user_data[key] = update.message.text.strip()
    await update.message.reply_text(next_text, reply_markup=answer_keyboard())
    return next_state


async def groom(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await save_text(update, context, "groom", "💍 Kuyov ismi qabul qilindi.\n\nKelinning ismi nima?", BRIDE)


async def bride(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await save_text(update, context, "bride", "💍 Kelin ismi qabul qilindi.\n\nTo‘y sanasi qaysi kun?\nMasalan: 25.09.2026", DATE)


async def wedding_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await save_text(update, context, "date", "📅 Sana saqlandi.\n\nTo‘y kechasi qaysi kuni yoki qanday tadbir?", EVENING)


async def evening(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await save_text(update, context, "evening", "🌙 Tadbir ma’lumoti saqlandi.\n\nSoat nechida yetkazamiz?\nMasalan: 18:30", TIME)


async def delivery_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await save_text(update, context, "time", "⏰ Vaqt saqlandi.\n\nManzil va mo‘ljalni yozing.", ADDRESS)


async def address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await save_text(update, context, "address", "📍 Manzil saqlandi.\n\nBuyurtmachi telefon raqamini yozing yoki Telegramdagi raqamni yuboring.", PHONE)


async def quantity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        count = int(update.message.text.strip())
        if count < 1 or count > 100:
            raise ValueError
    except ValueError:
        await update.message.reply_text("⚠ Iltimos, 1 dan 100 gacha bo‘lgan son kiriting.", reply_markup=answer_keyboard())
        return QUANTITY
    context.user_data["quantity"] = count
    design = context.user_data["design"]
    total = calculate_total(design, count)
    await update.message.reply_text(f"✓ {count} ta xat uchun taxminiy jami: {money(total)} so‘m.\n\nKuyovning ismi nima?", reply_markup=answer_keyboard())
    return GROOM


async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await save_text(update, context, "phone", "☎ Telefon raqami saqlandi.\n\nBuyurtmachi ismini yozing.", NAME)


async def name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["name"] = update.message.text.strip()
    data = context.user_data
    total = calculate_total(data["design"], data["quantity"])
    summary = (
        "✉ BUYURTMA XULOSASI\n\n"
        f"Kuyov: {data['groom']}\nKelin: {data['bride']}\nTo‘y sanasi: {data['date']}\n"
        f"Kechasi/tadbir: {data['evening']}\nSoat: {data['time']}\nManzil: {data['address']}\n"
        f"Namuna: {data['design']} ({DESIGNS[data['design']]['label']})\nXatlar soni: {data['quantity']} ta\nTelefon: {data['phone']}\nIsm: {data['name']}\n\n"
        f"Jami: {money(total)} so‘m\n\nMa’lumotlar to‘g‘rimi? Tasdiqlash tugmasini bosing."
    )
    await update.message.reply_text(summary, reply_markup=ReplyKeyboardMarkup([["✓ Tasdiqlash", "↻ Qayta boshlash"]], resize_keyboard=True))
    return CONFIRM


async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text in {"Qayta boshlash", "↻ Qayta boshlash"}:
        return await start(update, context)
    if update.message.text not in {"Tasdiqlash", "✓ Tasdiqlash"}:
        await update.message.reply_text("Iltimos, ✓ Tasdiqlash yoki ↻ Qayta boshlash tugmasidan birini tanlang.")
        return CONFIRM
    data = context.user_data
    total = calculate_total(data["design"], data["quantity"])
    user = update.effective_user
    order = (
        "✉ YANGI ZAFARXATLARI BUYURTMASI\n━━━━━━━━━━━━━━\n\n"
        f"Kuyov: {data['groom']}\nKelin: {data['bride']}\nTo‘y sanasi: {data['date']}\n"
        f"Kechasi/tadbir: {data['evening']}\nSoat: {data['time']}\nManzil/mo‘ljal: {data['address']}\n"
        f"Namuna: {data['design']} ({DESIGNS[data['design']]['label']})\nXatlar soni: {data['quantity']} ta\nTelefon: {data['phone']}\nIsm: {data['name']}\n"
        f"Jami: {money(total)} so‘m\n\nTelegram: @{user.username or 'username yo‘q'}\nUser ID: {user.id}"
    )
    if not ADMIN_CHAT_ID:
        await update.message.reply_text("Buyurtma saqlandi, ammo ADMIN_CHAT_ID sozlanmagan. Administrator bot sozlamasini to‘ldirishi kerak.", reply_markup=ReplyKeyboardRemove())
        logging.warning("Order from %s could not be forwarded: ADMIN_CHAT_ID is empty", user.id)
    else:
        await context.bot.send_message(chat_id=int(ADMIN_CHAT_ID), text=order)
        await update.message.reply_text("✓ Buyurtmangiz qabul qilindi!\n\nXatingizni mehr bilan tayyorlaymiz. Tez orada siz bilan bog‘lanamiz.", reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text("Buyurtma bekor qilindi.\n\nQayta boshlash uchun /start bosing.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


async def bot_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"Sizning chat ID raqamingiz: {update.effective_chat.id}")


def build_application() -> Application:
    application = Application.builder().token(os.environ["BOT_TOKEN"]).build()
    conversation = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={DESIGN: [CallbackQueryHandler(choose_design, pattern=r"^design:\d{2}$")], GROOM: [MessageHandler(filters.TEXT & ~filters.COMMAND, groom)], BRIDE: [MessageHandler(filters.TEXT & ~filters.COMMAND, bride)], DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, wedding_date)], EVENING: [MessageHandler(filters.TEXT & ~filters.COMMAND, evening)], TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, delivery_time)], ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, address)], QUANTITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, quantity)], PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone)], NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)], CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm)]},
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(CommandHandler("id", bot_id))
    application.add_handler(conversation)
    return application


if __name__ == "__main__":
    build_application().run_polling(allowed_updates=Update.ALL_TYPES)