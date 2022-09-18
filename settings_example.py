import sys
from loguru import logger


# main
API_TOKEN_TG = 'your api token'

EXECUTE = True

ENTERPRISE_PATTERNS = (
    'ООО "Русь", ЖК Российский', 'ООО "Русь", Осенцовская племенная ферма', 'ООО "Русь", ферма Лобаново', 'ИП ЧОГОВАДЗЕ КОБА СУЛИКОЕВИЧ',
)

VERIFIED_PRODUCTS = ["молоко сырое коровье", "минтай бг мороженый"]

VERIFIED_TRANSACTION_TYPE = "охлажденные"

logger.remove()
logger.add(sys.stdout, level='INFO')
