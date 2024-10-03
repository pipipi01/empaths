# Игра "Кровь на часовой башне с эмпатами"

В этом сценарии все синие жетоны - эмпаты, а красные жетоны блефуют эмпатами, 
давая ложную информацию о своих красных соседях

## Оглавление
- [Требования](#требования)
- [Установка и настройка](#установка-и-настройка)
- [Использование](#использование)
- [Команды](#команды)
- [Запуск игры в Docker](#запуск-игры-в-docker)


## Требования
- Python 3.11+
- Docker и Docker Compose
- Telegram Bot Token (для работы бота)

## Установка и настройка

### 1. Клонируйте репозиторий:
```sh
git clone <URL вашего репозитория>
cd 123
```

### 2. Создайте виртуальное окружение и активируйте его (опционально):
```sh
python3 -m venv venv
source venv/bin/activate
```

### 3. Установите зависимости:
```sh
pip install -r requirements.txt
```

### 4. Создайте файл `.env` и добавьте Telegram Bot Token:
```
TELEGRAM_BOT_TOKEN=ваш_токен_бота
```

### 5. Инициализация базы данных:
```sh
python -c "from database import init_db; init_db()"
```

## Использование
Запустите бота локально:
```sh
python bot.py
```

## Команды
### Команды для игроков и модераторов:
- `/start` - Начало игры.
- `/skip` - Пропуск регистрации как модератора и продолжение как игрок.
- `/enter_neighbors` - Ввод количества соседей для красных жетонов.
- `/kill_token` - Убийство жетона модератором.
- `/execute_token` - Казнь жетона игроком.
- `/skip_enter_neighbors` - Пропустить этап выбора соседей.

## Запуск в Docker
Для запуска бота с использованием Docker:

### 1. Постройте Docker образ и запустите контейнер:
```sh
docker-compose up -d
```

### 2. Проверка логов:
```sh
docker-compose logs -f
```

### 3. Makefile команды:

- Сборка контейнера: 
  ```sh
  make build
  ```
- Запуск контейнера:
  ```sh
  make up
  ```
- Остановка контейнера:
  ```sh
  make down
  ```
- Просмотр логов:
  ```sh
  make logs
  ```


---

Этот README поможет пользователям быстро разобраться в игре и запустить бота. Вы можете обновить его по мере изменения функционала или добавления новых возможностей.