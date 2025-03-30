import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import pytesseract
from PIL import Image
import requests
from io import BytesIO

# Налаштування логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Використовуємо безпосередньо ваш токен
TOKEN = "7763692205:AAFfyNOcS0TCFIg1jxR_nciOT52pMWJ09IM"

# Функція для обробки команди /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Привіт! Я бот для розпізнавання тексту з фотографій. "
        "Просто відправте мені фото, і я спробую розпізнати текст на ньому."
    )

# Функція для обробки команди /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Для використання бота просто відправте фотографію з текстом, "
        "і я спробую розпізнати його."
    )

# Функція для обробки фотографій та розпізнавання тексту
async def process_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Отримуємо фото з найвищою якістю
    photo = update.message.photo[-1]
    
    # Відправляємо повідомлення про початок обробки
    await update.message.reply_text("Обробляю зображення...")
    
    # Отримуємо файл
    file = await context.bot.get_file(photo.file_id)
    file_url = file.file_path
    
    try:
        # Завантажуємо зображення
        response = requests.get(file_url)
        img = Image.open(BytesIO(response.content))
        
        # Розпізнаємо текст
        # Для українського тексту додаємо параметр lang='ukr'
        # Якщо потрібна підтримка різних мов, можна використати lang='ukr+eng+rus'
        text = pytesseract.image_to_string(img, lang='ukr+eng')
        
        # Перевіряємо, чи вдалося розпізнати текст
        if text.strip():
            await update.message.reply_text(f"Розпізнаний текст:\n\n{text}")
        else:
            await update.message.reply_text("Не вдалося розпізнати текст на зображенні.")
    
    except Exception as e:
        await update.message.reply_text(f"Помилка при обробці зображення: {str(e)}")

def main() -> None:
    print(f"Використовую токен: {TOKEN}")
    
    # Створюємо додаток
    application = Application.builder().token(TOKEN).build()

    # Додаємо обробники команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # Додаємо обробник для фотографій
    application.add_handler(MessageHandler(filters.PHOTO, process_photo))

    # Запускаємо бота
    print("Бот запущений!")
    
    # Визначаємо, чи використовувати вебхук на основі змінної середовища
    webhook_mode = os.environ.get("WEBHOOK_MODE", "False").lower() == "true"
    
    if webhook_mode:
        # Отримуємо URL вебхука з змінних середовища
        webhook_url = os.environ.get("WEBHOOK_URL")
        port = int(os.environ.get("PORT", 8080))
        
        print(f"Запускаємо в режимі вебхука на порту {port}")
        print(f"Використовуємо вебхук URL: {webhook_url}")
        
        application.run_webhook(
            listen="0.0.0.0",
            port=port,
            webhook_url=webhook_url
        )
    else:
        # Використовуємо polling для локального запуску
        print("Запускаємо в режимі polling")
        application.run_polling()

if __name__ == "__main__":
    main()
