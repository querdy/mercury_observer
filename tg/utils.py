import json
from typing import Dict

import settings
from settings import logger


def get_users_data() -> Dict[str, dict]:
    users = dict()
    try:
        open(settings.USERS_FILE_PATH, "x").close()
    except FileExistsError:
        pass
    try:
        with open(settings.USERS_FILE_PATH, "r") as f:
            users = json.load(f)
    except json.decoder.JSONDecodeError:
        logger.error("Не удалось спарсить пользователей.")
    return users

def save_user_data(user: str, **data) -> bool:
    users = get_users_data()
    try:
        users[user].update(**data)
    except KeyError:
        users.update({user: data})
    try:
        with open(settings.USERS_FILE_PATH, "w") as f:
            json.dump(users, f, indent=4)
    except json.decoder.JSONDecodeError:
        logger.error("Не удалось сохранить данные в файл")
        return False
    return True

def delete_user(user: str) -> bool:
    users = get_users_data()
    if users.pop(user):
        try:
            with open(settings.USERS_FILE_PATH, "w") as f:
                json.dump(users, f, indent=4)
        except json.decoder.JSONDecodeError:
            return False
    return True
