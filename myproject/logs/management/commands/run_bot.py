from django.core.management.base import BaseCommand
import asyncio
from logs.weatherbot import main

class Command(BaseCommand):
    help = 'Запуск Telegram Weather-Bot'

    def handle(self, *args, **kwargs):
        asyncio.run(main())