from datetime import datetime
import json


def date_str_to_datetime(date):
    dateformats = ['%d.%m.%Y:%H', '%d.%m.%Y']
    for dateformat in dateformats:
        try:
            return datetime.strptime(date, dateformat)
        except ValueError:
            continue
    return None


def get_login_and_password(user: str):
    with open("parser/login/users.json", "r") as f:
        user_data = json.load(f).get(user)
        return user_data['login'], user_data['password']