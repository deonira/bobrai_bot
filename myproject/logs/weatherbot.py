from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from django.core.cache import cache
import httpx
import asyncio
import nest_asyncio
from .models import RequestLog
nest_asyncio.apply()


API_KEY = "323d4f8e54374b349cf105819241010"
BASE_URL = f"https://api.weatherapi.com/v1/current.json?key={API_KEY}&q={{city}}&lang=ru"


def get_weather(city):
    cached_weather = cache.get(city)
    if cached_weather:
        return cached_weather

    url = BASE_URL.format(city=city)
    response = httpx.get(url)

    if response.status_code != 200:
        return None

    weather_data = response.json()
    cache.set(city, weather_data, timeout=3600)
    return weather_data


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! Я бот для получения погоды. Используй команду /weather <город>.')


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

    RequestLog.objects.create(
        user_id=str(update.message.from_user.id),
        command=' '.join(context.args),
        response=weather_info
    )


async def main() -> None:
    application = Application.builder().token("7751173397:AAHGHAJVV88oNNt1Mccf4w2Plf1T9G3qXcE").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("weather", weather))

    await application.run_polling()


if __name__ == '__main__':
    asyncio.run(main())
