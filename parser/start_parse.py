from typing import List
from bs4 import BeautifulSoup as BSoup
from datetime import datetime
import settings
from settings import logger
from parser.document_parser import request_document_parser
from parser.document_parser import transaction_document_parser
from parser.login.base_session import BaseSession
from parser.login.mercury_login import check_cookies
from parser.fix_transaction import fix_transport_number
from parser import dto


def start_parse():
    url = 'https://mercury.vetrf.ru/gve/operatorui?_action=changeServicedEnterprise'
    sess = check_cookies('cookies.json')
    page = sess.get(url)
    soup = BSoup(page.content, 'html5lib')

    enterprises = _get_enterprises_data(soup)
    _validate_enterprises(sess=sess, enterprises=enterprises)
    if settings.EXECUTE:
        _tr_execution(sess=sess, enterprises=enterprises)
    return enterprises


def _tr_execution(sess: BaseSession, enterprises: List[dto.EnterpriseData]):
    for enterprise in enterprises:
        for transaction in enterprise.transactions_data:
            logger.info(f"tr: {transaction.rq_transaction_pk} timedelta: {(transaction.date_from - datetime.now()).total_seconds()}")
            if (transaction.date_from - datetime.now()).total_seconds() < 0:
                logger.info(f"Срок годности 36ч: {transaction.is_expiration()}")
                if transaction.is_expiration():
                    _accept_transaction(sess, enterprise.enterprise_pk, transaction)
                    if not transaction.car_number.is_verified or (transaction.trailer_number is not None and not transaction.trailer_number.is_verified):
                        is_correction = True
                        fix_transport_number(sess=sess, enterprise=enterprise.enterprise_pk, transaction=transaction)
                    transaction_document_parser(sess, enterprise.enterprise_pk, transaction)
                    logger.info((transaction.date_from - datetime.now()).total_seconds())
                    if transaction.is_valid():
                        _confirm_transaction(sess, enterprise.enterprise_pk, transaction)
                    logger.info("Оформлено" if transaction.is_confirm else "Не оформлено")
                else:
                    logger.info("Не оформлено")


def _confirm_transaction(sess: BaseSession,
                         enterprise: dto.EnterpriseData.enterprise_pk,
                         transaction: dto.TransactionData):
    url = 'https://mercury.vetrf.ru/gve/operatorui'
    confirm_tr_params = {
        'waybillId': transaction.waybillid,
        '_action': 'formTransaction',
        'pageList': '1',
        'transactionPk': transaction.tr_transaction_pk,
        'request': 'false',
        'input': '',
        'waybill': '',
        'vetDocument': '',
        'version': transaction.version,
        'cancelAction': 'listTransaction',
        'skipCheck': 'true',
        'templateWaybillSeries': '',
        'templateWaybillNumber': '',
        'templateWaybillDate': '',
        'templateWaybillType': '',
        'templateWaybillAbsent': '',
        'forwardedMessage': '',
        'tuid': transaction.tuid
    }
    page = sess.fetch(url, data=confirm_tr_params)
    transaction.is_confirm = True


def _accept_transaction(sess: BaseSession, enterprise_pk: str, transaction: dto.TransactionData):
    url = "https://mercury.vetrf.ru/gve/operatorui"
    sess.fetch(url, params={'enterprisePk': enterprise_pk,
                            '_action': 'chooseServicedEnterprise'
                            }
               )
    page = sess.fetch(url, params={'_action': 'listTransactionAjax',
                                   'formed': 'false',
                                   'status': '4',
                                   'pageList': '1',
                                   'all': 'true',
                                   'request': 'true',
                                   'template': 'false',
                                   }
                      )

    soup = BSoup(page.text, 'html5lib')

    tr_params = {'_action': 'showTransactionForm',
                 'transactionPk': transaction.rq_transaction_pk,
                 'pageList': '1',
                 'cancelAction': 'listTransaction',
                 'anchor': '',
                 }
    sess.fetch(url, params=tr_params)

    accept_params = {'_action': 'transactionAcceptForm',
                     'pageList': '1',
                     'transactionPk': transaction.rq_transaction_pk,
                     'request': 'true',
                     'version': '3',
                     'skipCheck': 'true',
                     }
    page = sess.fetch(url, params=accept_params)
    soup = BSoup(page.content, 'html5lib')
    transaction.tr_transaction_pk = soup.find("input", {"name": "transactionPk"}).get_attribute_list('value')[-1]


def _get_enterprises_data(soup) -> List[dto.EnterpriseData]:
    enterprises = []
    all_tr_requests = _get_all_tr_requests(soup)
    for tr_request in all_tr_requests:
        enterprise_data = dto.EnterpriseData()
        enterprise_tag = tr_request.find_previous("td")

        enterprise_data.enterprise_pk = enterprise_tag.find_parent("tr").find("td").find("input").get("value")
        if len(enterprise_tag.find_all("a")) == 2:
            enterprise_tag.a.decompose()  # если есть входящие всд, убрать тег с ними из дерева bs
        enterprise_data.href = enterprise_tag.find("a").get("href")
        enterprise_data.numbers_of_requests = enterprise_tag.find("a").get_text().strip()
        enterprise_tag.a.decompose()  # убрать тег с заявками из дерева bs
        enterprise_data.enterprise_name = enterprise_tag.get_text().strip()
        enterprises.append(enterprise_data)

    return enterprises


def _validate_enterprises(sess: BaseSession,
                          enterprises: List[dto.EnterpriseData]):
    for enterprise in enterprises[:]:
        for pattern in settings.ENTERPRISE_PATTERNS:
            if enterprise not in enterprises:
                continue
            if enterprise.enterprise_name.find(pattern) != -1:
                enterprise.transactions_data = request_document_parser(sess, enterprise.enterprise_pk)
        if not enterprise.transactions_data:
            enterprises.remove(enterprise)


def _get_all_tr_requests(soup: BSoup) -> List[BSoup]:
    all_tr_requests = soup.find_all("a", title=["Входящие заявки от ХС. ", "Входящие заявки от ХС. Есть новые."])
    return all_tr_requests
