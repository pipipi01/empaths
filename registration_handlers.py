# registration_handlers.py

import os
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from database import add_user, get_user_by_username, reset_user_game_state, clear_game_set, get_all_users
import logging
from constants import HANDLE_PASSWORD, GET_USERNAME
from game_set_handlers import set_up_game
from player_manager import (
    player_registration_notice,
    player_start_game_notice
)
import re

from utils import escape_html


MODERATOR_PASSWORD = os.getenv("MODERATOR_PASSWORD")
if not MODERATOR_PASSWORD:
    raise ValueError("Переменная окружения MODERATOR_PASSWORD не установлена.")

logger = logging.getLogger(__name__)

def extract_user_info(user) -> tuple:
    """
    Извлекает username и user id из объекта пользователя Telegram.
    """
    username = user.username or user.first_name or "Unknown"
    userid = user.id
    return username, userid

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обработчик команды /start.
    """
    context.user_data.clear()

    user = update.effective_user
    username, userid = extract_user_info(user)

    # Сохраняем пользователя в базе данных и получаем флаг is_new_user
    is_new_user = add_user(username, userid)
    context.user_data['is_new_user'] = is_new_user
    clear_game_set()

    await update.message.reply_text(
            f"Привет, {escape_html(username)}! Это 'Кровь на часовой башне'\n"
            f"В этом сценарии все синие жетоны - эмпаты, а красные жетоны блефуют эмпатами, "
            "давая ложную информацию о своих красных соседях\n"
            f"Ты успешно зарегистрирован.\n"
            "Введи пароль, чтобы стать модератором партии\n\n"
            "/skip чтобы продолжить как игрок",
            parse_mode='HTML'
        )

    return HANDLE_PASSWORD

async def handle_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Проверяет введённый пароль и продолжает диалог при успешном вводе.
    """
    password = update.message.text
    user = update.effective_user
    username, userid = extract_user_info(user)

    if password == MODERATOR_PASSWORD:
        add_user(username, userid, moderator=True)

        # Получаем список пользователей из базы данных
        users = get_all_users()
        users_list = "\n".join([f"@{user['username']} (ID: {user['id']})" for user in users])

        await update.message.reply_text(
            "Теперь ты модератор!\n\n"
            "Введи имя пользователя, с которым собираешься играть (например @username):\n\n"
            "ВНИМАНИЕ: перед вводом имени надо чтобы этот пользователь начал использовать бота\n\n"
            "Список зарегистрированных пользователей:\n"
            f"{users_list}",
            parse_mode='HTML'
        )

        return GET_USERNAME
    else:
        await update.message.reply_text(
            "Пароль модератора неверный. Введите пароль ещё раз или введите /skip, чтобы продолжить как игрок."
        )
        return HANDLE_PASSWORD


async def get_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обрабатывает ввод имени пользователя для игры и передаёт управление в set_up_game.
    """
    player_username_input = update.message.text.strip()
    player_username = player_username_input.lstrip('@')
    
    if not player_username:
        await update.message.reply_text("Имя пользователя не может быть пустым. Пожалуйста, введите имя пользователя:")
        return GET_USERNAME
    
    # Проверяем, что имя пользователя содержит только буквы, цифры, "-" и "_"
    if not re.match(r'^[\w-]+$', player_username):
        await update.message.reply_text("Имя пользователя должно содержать только буквы, цифры, '-' и '_'. Пожалуйста, введите корректное имя пользователя:")
        return GET_USERNAME
    
    game_set = context.user_data.setdefault('game_set', {})
    game_set['player_username'] = player_username
    logger.info(f"Получено имя пользователя для игры: {player_username}")
    await update.message.reply_text(
        "Имя пользователя сохранено. Теперь настрой игру.\n\n"
        "Общее игроков должно быть от 7 до 16 включительно\n\n"
        "Количество красных от 1 до 4 включительно\n\n"
        "Пока что бот не проверяет соотношение синих и красных игроков\n"
        "поэтому выбор чисел зависит от модератора\n\n"
        "После выбора количества игроков тебе будет предложено\n"
        "выбрать количество красных соседей для красных жетонов\n"
        "это информация эмпатов\n"
        "Нужно будет ввести 0, 1 или 2",
        parse_mode='HTML'
    )
    
    player = get_user_by_username(player_username)
    player_id = player['id']

    await context.bot.send_message(
        chat_id=player_id,
        text=(f"Модератор @{update.effective_user.username} выбрал тебя для игры.")
    )
    reset_user_game_state(player_id)
    reset_user_game_state(update.effective_user.id)
    return await set_up_game(update, context)

async def skip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обрабатывает команду /skip, позволяя пользователю пропустить ввод пароля модератора.
    """
    user = update.effective_user
    username, userid = extract_user_info(user)
    is_new_user = context.user_data.get('is_new_user', False)

    await update.message.reply_text("Ты зарегистрирован как игрок. Модератор настроит игру и пригласит тебя.")

    if is_new_user:
        await player_registration_notice(context, username, userid)
        await player_start_game_notice(context, username, userid)
    else:
        await player_start_game_notice(context, username, userid)
        logger.info(f"Пользователь @{username} ({userid}) нажал кнопку старта и ожидает начало игры.")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обрабатывает команду /cancel, отменяя процесс регистрации.
    """
    await update.message.reply_text("Регистрация отменена.")
    return ConversationHandler.END
