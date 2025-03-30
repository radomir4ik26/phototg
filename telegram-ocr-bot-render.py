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

# Отримуємо токен бота з змінних середовища (для безпечного розгортання)
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

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
        # Налаштовуємо шлях до tesseract, якщо потрібно
        if os.environ.get("TESSERACT_PATH"):
            pytesseract.pytesseract.tesseract_cmd = os.environ.get("TESSERACT_PATH")
            
        text = pytesseract.image_to_string(img, lang='ukr+eng')
        
        # Перевіряємо, чи вдалося розпізнати текст
        if text.strip():
            await update.message.reply_text(f"Розпізнаний текст:\n\n{text}")
        else:
            await update.message.reply_text("Не вдалося розпізнати текст на зображенні.")
    
    except Exception as e:
        await update.message.reply_text(f"Помилка при обробці зображення: {str(e)}")

# Функція для вебхука (Render працює через вебхуки)
async def webhook(request):
    return web.Response(text="OK")

def main() -> None:
    # Створюємо додаток
    application = Application.builder().token(TOKEN).build()

    # Додаємо обробники команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # Додаємо обробник для фотографій
    application.add_handler(MessageHandler(filters.PHOTO, process_photo))

    # Налаштовуємо вебхук для Render
    PORT = int(os.environ.get("PORT", 8080))
    
    # Використовуємо змінну середовища для визначення режиму запуску
    # На Render встановіть змінну WEBHOOK_MODE=True
    if os.environ.get("WEBHOOK_MODE", "False").lower() == "true":
        # Отримуємо URL вебхука з змінних середовища
        WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=WEBHOOK_URL
        )
    else:
        # Для локального тестування використовуємо polling
        application.run_polling()

if __name__ == "__main__":
    main()
