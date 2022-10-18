import sys
from loguru import logger
from pathlib import Path

# main
API_TOKEN_TG = 'TOKEN'

BASE_DIR = Path(__file__).resolve().parent
USERS_FILE_PATH = str(BASE_DIR / "parser/login/users.json")

EXECUTE = True

ENTERPRISE_PATTERNS = (
    'ООО "Русь", ЖК Российский', 'ООО "Русь", Осенцовская племенная ферма', 'ООО "Русь", ферма Лобаново',
)

VERIFIED_PRODUCTS = ["молоко сырое коровье",]

VERIFIED_TRANSACTION_TYPE = "охлажденные"

logger.remove()
logger.add(sys.stdout, level='INFO')
