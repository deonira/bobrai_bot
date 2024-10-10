from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from django.core.cache import cache
import httpx
import asyncio
import nest_asyncio
from .models import RequestLog, UserSettings
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
nest_asyncio.apply()

User = get_user_model()

API_KEY = "323d4f8e54374b349cf105819241010"
BASE_URL = f"https://api.weatherapi.com/v1/current.json?key={API_KEY}&q={{city}}&lang=ru"


def get_weather(city):
    cache_key = f"weather_{city.lower()}"

    cached_weather = cache.get(cache_key)
    if cached_weather:
        print(f"Данные о погоде для {city} извлечены из кэша.")
        return cached_weather

    try:
        url = BASE_URL.format(city=city)
        response = httpx.get(url)

        if response.status_code != 200:
            print(f"Ошибка при запросе к API: {response.status_code} для города {city}")
            return None

        weather_data = response.json()

        cache.set(cache_key, weather_data, timeout=3600)
        return weather_data
    except httpx.RequestError as e:
        print(f"Ошибка при запросе к API: {e}")
        return None
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! Я бот для получения погоды. Используй команду /weather, чтобы получить погоду в другом городе. Используй /my_weather, чтобы получить погоду в установленном городе. Используй /set_city, чтобы установить город по умолчанию.')


async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) == 0:
        await update.message.reply_text('Пожалуйста, укажите город в формате /weather <город>.')
        return

    city = ' '.join(context.args)
    weather_data = get_weather(city)

    if weather_data is None or "current" not in weather_data:
        await update.message.reply_text(f'Не удалось получить погоду для города {city}. Проверьте название города.')
        return

    temperature = weather_data["current"]["temp_c"]
    feels_like = weather_data["current"]["feelslike_c"]
    description = weather_data["current"]["condition"]["text"]
    humidity = weather_data["current"]["humidity"]
    wind_speed = weather_data["current"]["wind_kph"]

    weather_info = (
        f"Погода в городе {city}:\n"
        f"Температура: {temperature}°C\n"
        f"Ощущается как: {feels_like}°C\n"
        f"Описание: {description.capitalize()}\n"
        f"Влажность: {humidity}%\n"
        f"Скорость ветра: {wind_speed} км/ч"
    )

    await update.message.reply_text(weather_info)

    try:
        await sync_to_async(RequestLog.objects.create)(user_id=str(update.message.from_user.id), command='weather',
                                                       response=weather_info)
    except Exception as e:
        print(f"Ошибка при логировании: {e}")

async def my_weather(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_settings = await sync_to_async(UserSettings.objects.filter(user_id=user_id).first)()

    if user_settings and user_settings.preferred_city:
        city = user_settings.preferred_city
        weather_data = get_weather(city)
        if weather_data is None or "current" not in weather_data:
            await update.message.reply_text(f'Не удалось получить погоду для города {city}.')
            return

        temperature = weather_data["current"]["temp_c"]
        feels_like = weather_data["current"]["feelslike_c"]
        description = weather_data["current"]["condition"]["text"]
        humidity = weather_data["current"]["humidity"]
        wind_speed = weather_data["current"]["wind_kph"]

        weather_info = (
            f"Погода в городе {city}:\n"
            f"Температура: {temperature}°C\n"
            f"Ощущается как: {feels_like}°C\n"
            f"Описание: {description.capitalize()}\n"
            f"Влажность: {humidity}%\n"
            f"Скорость ветра: {wind_speed} км/ч"
        )

        await update.message.reply_text(weather_info)
    else:
        await update.message.reply_text("Сначала выберите город с помощью команды /set_city.")

async def set_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Введите название города для установки:')
    return

async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    city = update.message.text
    user_id = update.message.from_user.id

    if get_weather(city):
        user, created = await sync_to_async(User.objects.get_or_create)(id=user_id, defaults={'username': str(user_id)})

        await sync_to_async(UserSettings.objects.update_or_create)(user=user, defaults={'preferred_city': city})
        await update.message.reply_text(f"Город {city} установлен. Теперь я буду запрашивать погоду для этого города.")
    else:
        await update.message.reply_text("Город не найден. Пожалуйста, попробуйте еще раз.")

async def main() -> None:
    application = Application.builder().token("7751173397:AAHGHAJVV88oNNt1Mccf4w2Plf1T9G3qXcE").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("weather", weather))
    application.add_handler(CommandHandler("my_weather", my_weather))
    application.add_handler(CommandHandler("set_city", set_city))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_city))

    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())