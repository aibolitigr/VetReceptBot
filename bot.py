import logging
import asyncio
import datetime
import os
from aiogram import Bot, Dispatcher, types, Router
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from aiogram.enums import ParseMode
from aiogram.enums import ParseMode
from aiogram.filters import Command
from docx import Document

# 🔹 Вставь свой токен бота
TOKEN = "7759754415:AAE2UWgC_B9lx-DV4TG-57JsyZS4qES9LjY"

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
router = Router()

# 🔹 Клавиатура с кнопкой
menu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📝 Новый рецепт")]],
    resize_keyboard=True
)

user_data = {}

@router.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer("Привет! Я бот для заполнения рецептов.\n\nНажми '📝 Новый рецепт' или введи /new_recipe", reply_markup=menu)

@router.message(lambda message: message.text == "📝 Новый рецепт" or message.text == "/new_recipe")
async def ask_instance_number(message: types.Message):
    user_data[message.chat.id] = {}
    await message.answer("Введите номер экземпляра рецепта:")

@router.message(lambda message: message.chat.id in user_data and "instance_number" not in user_data[message.chat.id])
async def ask_recipe_number(message: types.Message):
    user_data[message.chat.id]["instance_number"] = message.text
    await message.answer("Введите номер рецепта:")

@router.message(lambda message: message.chat.id in user_data and "recipe_number" not in user_data[message.chat.id])
async def ask_owner(message: types.Message):
    user_data[message.chat.id]["recipe_number"] = message.text
    user_data[message.chat.id]["date"] = datetime.datetime.now().strftime("%d.%m.%Y")
    await message.answer("Введите ФИО владельца и адрес:")

@router.message(lambda message: message.chat.id in user_data and "owner_name" not in user_data[message.chat.id])
async def ask_pet_info(message: types.Message):
    user_data[message.chat.id]["owner_name"] = message.text
    await message.answer("Введите вид, пол, возраст, кличку или идентификационный номер животного:")

@router.message(lambda message: message.chat.id in user_data and "pet_info" not in user_data[message.chat.id])
async def ask_medicine(message: types.Message):
    user_data[message.chat.id]["pet_info"] = message.text
    await message.answer("Введите название препарата и регистрационный номер (если есть):")

@router.message(lambda message: message.chat.id in user_data and "medicine" not in user_data[message.chat.id])
async def ask_dosage(message: types.Message):
    user_data[message.chat.id]["medicine"] = message.text
    await message.answer("Введите общую дозу препарата:")

@router.message(lambda message: message.chat.id in user_data and "dosage" not in user_data[message.chat.id])
async def ask_single_dose(message: types.Message):
    user_data[message.chat.id]["dosage"] = message.text
    await message.answer("Введите разовую дозу препарата:")

@router.message(lambda message: message.chat.id in user_data and "single_dose" not in user_data[message.chat.id])
async def ask_frequency(message: types.Message):
    user_data[message.chat.id]["single_dose"] = message.text
    await message.answer("Введите частоту приёма препарата:")

@router.message(lambda message: message.chat.id in user_data and "frequency" not in user_data[message.chat.id])
async def ask_time_of_day(message: types.Message):
    user_data[message.chat.id]["frequency"] = message.text
    await message.answer("Введите время приёма (утром, днём, вечером и т. д.):")

@router.message(lambda message: message.chat.id in user_data and "time_of_day" not in user_data[message.chat.id])
async def ask_duration(message: types.Message):
    user_data[message.chat.id]["time_of_day"] = message.text
    await message.answer("Введите длительность приёма:")

@router.message(lambda message: message.chat.id in user_data and "duration" not in user_data[message.chat.id])
async def ask_method(message: types.Message):
    user_data[message.chat.id]["duration"] = message.text
    await message.answer("Введите способ введения (перорально, внутримышечно и т. д.):")

@router.message(lambda message: message.chat.id in user_data and "method" not in user_data[message.chat.id])
async def ask_feeding_time(message: types.Message):
    user_data[message.chat.id]["method"] = message.text
    await message.answer("Препарат принимается до, во время или после еды?")

@router.message(lambda message: message.chat.id in user_data and "feeding_time" not in user_data[message.chat.id])
async def ask_vet_name(message: types.Message):
    user_data[message.chat.id]["feeding_time"] = message.text
    await message.answer("Введите ФИО ветеринарного врача:")

@router.message(lambda message: message.chat.id in user_data and "vet_name" not in user_data[message.chat.id])
async def ask_expiry_date(message: types.Message):
    user_data[message.chat.id]["vet_name"] = message.text
    await message.answer("Введите срок действия рецепта (ДД.ММ.ГГГГ):")

@router.message(lambda message: message.chat.id in user_data and "expiry_date" not in user_data[message.chat.id])
async def finalize_recipe(message: types.Message):
    user_data[message.chat.id]["expiry_date"] = message.text
    template_path = "Бланк рецепта для бота телеграмм.docx"
    
    try:
        doc = Document(template_path)
        for paragraph in doc.paragraphs:
            for key, value in user_data[message.chat.id].items():
                if f"{{{key}}}" in paragraph.text:
                    paragraph.text = paragraph.text.replace(f"{{{key}}}", value)

        def sanitize_filename(filename):
            invalid_chars = '<>:"/\\|?*'
            for char in invalid_chars:
                filename = filename.replace(char, "_")
            return filename

        filename = sanitize_filename(
    f"Рецепт_{user_data[message.chat.id]['recipe_number']}_"
    f"{user_data[message.chat.id]['owner_name']}.docx"
)

        doc.save(filename)
        
        file = FSInputFile(filename)
        await message.answer_document(file)

        del user_data[message.chat.id]
    except Exception as e:
        await message.answer(f"❌ Ошибка при создании рецепта: {e}")

async def main():
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
