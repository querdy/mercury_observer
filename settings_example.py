import sys
from loguru import logger
from pathlib import Path

# main
API_TOKEN_TG = 'TG_TOKEN'

BASE_DIR = Path(__file__).resolve().parent
USERS_FILE_PATH = str(BASE_DIR / "parser/login/users.json")

EXECUTE = True

ENTERPRISE_PATTERNS = ('ООО "Рога и копыта"',)

VERIFIED_PRODUCTS = ["молоко сырое коровье", ]

VERIFIED_TRANSACTION_TYPE = "охлажденные"

SCHEDULE_EVERY_TIME = 5

AUTOS = ['А555АА111', ]

TRAILERS = ['АА000011RUS', ]

TRUCK = AUTOS + TRAILERS

logger.remove()
logger.add(sys.stdout, level='INFO')
