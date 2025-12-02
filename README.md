# Weather Bot — Telegram Bot для прогноза погоды

Профессиональная реализация Telegram бота с интеграцией OpenWeatherMap API.

## Возможности

✅ Быстрый прогноз погоды для любого города  
✅ Кнопки с популярными городами  
✅ История запросов пользователя  
✅ Логирование всех действий  
✅ Обработка ошибок  
✅ Docker контейнеризация  

## Требования

- Docker и Docker Compose
- Аккаунты:
  - Telegram Bot Token (от @BotFather)
  - OpenWeatherMap API Key (от https://openweathermap.org/api)

## Быстрый старт (локально)

### 1. Клонировать репозиторий

```bash
git clone <your-repo-url>
cd weather_bot
```

### 2. Создать .env файл

```bash
cp .env.example .env
```

Отредактировать `.env`:

```
TELEGRAM_TOKEN=your_bot_token_here
OPENWEATHER_API_KEY=your_api_key_here
```

### 3. Собрать и запустить с Docker Compose

```bash
docker-compose up -d
```

### 4. Проверить логи

```bash
docker-compose logs -f weather_bot
```

### 5. Остановить бота

```bash
docker-compose down
```

---

## Деплой на VPS

### Требования к серверу

- Linux (Ubuntu 20.04+ рекомендуется)
- Docker установлен
- Docker Compose установлен

### Инструкция деплоя

#### 1. Подключиться к серверу

```bash
ssh root@your_server_ip
```

#### 2. Установить Docker (если не установлен)

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

#### 3. Установить Docker Compose

```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 4. Загрузить проект на сервер

```bash
# Локально:
git push origin main

# На сервере:
git clone <your-repo-url>
cd weather_bot
```

#### 5. Создать .env файл

```bash
nano .env
```

Вставить:

```
TELEGRAM_TOKEN=your_token
OPENWEATHER_API_KEY=your_key
```

Сохранить: `Ctrl+X` → `Y` → `Enter`

#### 6. Запустить бота

```bash
docker-compose up -d
```

#### 7. Проверить статус

```bash
docker-compose ps
docker-compose logs -f weather_bot
```

---

## Структура проекта

```
weather_bot/
├── weather_bot_prod.py      # Основной код с логированием
├── requirements.txt          # Зависимости Python
├── Dockerfile               # Конфигурация контейнера
├── docker-compose.yml       # Запуск контейнера
├── .dockerignore            # Что игнорировать при сборке
├── .env                     # Переменные окружения (не коммитить!)
├── .gitignore              # Что игнорировать в Git
├── logs/                   # Логи приложения (создаются автоматически)
└── README.md               # Этот файл
```

---

## Логирование

Логи сохраняются в `logs/bot.log` и выводятся в консоль.

Просмотр логов в Docker контейнере:

```bash
# Real-time логи
docker-compose logs -f weather_bot

# Последние 100 строк
docker-compose logs --tail=100 weather_bot
```

---

## Команды бота

| Команда | Описание |
|---------|---------|
| `/start` | Начало работы, показать кнопки |
| `/help` | Справка по командам |
| `/history` | Показать последние 5 запросов |
| `/clear_history` | Очистить историю |

---

## Обновление бота

```bash
# Загрузить новый код
git pull origin main

# Пересобрать и перезапустить контейнер
docker-compose up -d --build
```

---

## Проблемы и решения

### Контейнер не запускается

```bash
docker-compose logs weather_bot
```

Проверить наличие `TELEGRAM_TOKEN` и `OPENWEATHER_API_KEY` в `.env`.

### Бот не отвечает

1. Проверить токены в `.env`
2. Проверить интернет соединение на сервере
3. Посмотреть логи: `docker-compose logs weather_bot`

### Как перезагрузить бота

```bash
docker-compose restart weather_bot
```

---

## Лицензия

MIT License

---

## Автор

Created for learning Telegram Bot Development

**По вопросам**: создайте issue в репозитории
