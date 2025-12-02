# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем requirements.txt
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код приложения
COPY weather_bot_prod.py .

# Создаём директорию для логов
RUN mkdir -p logs

# Запускаем бота
CMD ["python", "weather_bot_prod.py"]
