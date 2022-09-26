import sys
from loguru import logger


# main
API_TOKEN_TG = 'API TOKEN'

EXECUTE = True

users_file_path = "parser/login/users.json"

ENTERPRISE_PATTERNS = (
    'ООО "Русь", ЖК Российский', 'ООО "Русь", Осенцовская племенная ферма', 'ООО "Русь", ферма Лобаново',
)

VERIFIED_PRODUCTS = ["молоко сырое коровье",]

VERIFIED_TRANSACTION_TYPE = "охлажденные"

logger.remove()
logger.add(sys.stdout, level='INFO')
