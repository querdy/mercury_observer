from datetime import datetime


def date_str_to_datetime(date):
    dateformats = ['%d.%m.%Y:%H', '%d.%m.%Y']
    for dateformat in dateformats:
        try:
            return datetime.strptime(date, dateformat)
        except ValueError:
            continue
    return None
