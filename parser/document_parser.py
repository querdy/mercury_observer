from typing import List

from bs4 import BeautifulSoup as BSoup

from parser.login.base_session import BaseSession
from parser import dto
from settings import logger
from parser.utils import date_str_to_datetime


def _base_get(sess: BaseSession, enterprise_pk: str) -> (BaseSession, str):
    url = "https://mercury.vetrf.ru/gve/operatorui"
    sess.fetch(
        url,
        params={"enterprisePk": enterprise_pk, "_action": "chooseServicedEnterprise"},
    )

    return sess, url


def request_document_parser(
    sess: BaseSession, enterprise_pk: str
) -> List[dto.TransactionData] | None:
    sess, url = _base_get(sess, enterprise_pk)
    page = sess.fetch(
        url,
        params={
            "_action": "listTransactionAjax",
            "formed": "false",
            "status": "4",
            "pageList": "1",
            "all": "true",
            "request": "true",
            "template": "false",
        },
    )

    soup = BSoup(page.text, "html5lib")

    transactions_pk = [
        request.find_previous_sibling().getText()
        for request in soup.find_all("a", title="просмотр сведений")
    ]
    if not transactions_pk:
        logger.info(
            "Не удалось получить TransactionsPk. "
            "Вероятно, меркурию снова плохо и он не отображает заявки. "
            "Следующая попытка через несколько минут. (request_document_parser)"
        )
        return None

    rq_transactions_data = []
    for transaction_pk in transactions_pk:
        transaction_params = {
            "_action": "showTransactionForm",
            "transactionPk": transaction_pk,
            "pageList": "1",
            "cancelAction": "listTransaction",
            "anchor": "",
        }
        page = sess.fetch(url, params=transaction_params)
        soup = BSoup(page.content, "html5lib")

        transaction_data = dto.TransactionData()
        transaction_data.rq_transaction_pk = transaction_pk
        _upgrade_enterprise_data(soup, transaction_data=transaction_data)
        rq_transactions_data.append(transaction_data)

    return rq_transactions_data


def transaction_document_parser(
    sess: BaseSession, enterprise_pk: str, transaction: dto.TransactionData
):
    sess, url = _base_get(sess, enterprise_pk)
    transaction_params = {
        "_action": "showTransactionForm",
        "transactionPk": transaction.tr_transaction_pk,
        "pageList": "1",
        "cancelAction": "listTransaction",
        "anchor": "",
    }

    page = sess.fetch(url, params=transaction_params)
    soup = BSoup(page.content, "html5lib")

    _upgrade_enterprise_data(soup, transaction)
    transaction.waybillid = soup.find("input", {"name": "waybillId"}).get_attribute_list("value")[0]
    transaction.version = soup.find("input", {"name": "version"}).get_attribute_list("value")[0]
    transaction.tuid = soup.find("input", {"name": "tuid"}).get_attribute_list("value")[0]

    vet_document = soup.find('a', class_='operation-link blue').get('href').split('&')[1].split('=')[-1]
    page = sess.fetch(url, params={'_action': 'showVetDocumentAjaxForm',
                                   'vetDocument': vet_document})
    soup = BSoup(page.text, 'html5lib')
    transaction.date_from = soup.find_all('td', class_='value')[8].getText()
    transaction.date_to = soup.find_all('td', class_='value')[9].getText()


def _upgrade_enterprise_data(soup: BSoup, transaction_data: dto.TransactionData):
    transaction_data.recipient_enterprise = (
        soup.find_all("table", {"class": "innerFormWide"})[1]
        .find_all("tr")[1]
        .find_all("td")[1]
        .find("a")
        .get_text()
        .strip()
    )
    transaction_data.recipient_company = (
        soup.find_all("table", {"class": "innerFormWide"})[1]
        .find_all("tr")[1]
        .find_all("td")[0]
        .find("a")
        .get_text()
        .strip()
    )
    transaction_data.bill_of_lading = (
        soup.find_all("table", {"class": "innerFormWide"})[1]
        .find_all("tr")[1]
        .find_all("td")[2]
        .get_text()
        .strip()
    )
    transaction_data.bill_of_lading_date = (
        soup.find_all("table", {"class": "innerFormWide"})[1]
        .find_all("tr")[1]
        .find_all("td")[3]
        .get_text()
        .strip()
    )
    transaction_data.product = (
        soup.find_all("table", {"class": "innerFormWide"})[1]
        .find("a", title="просмотр сведений")
        .get_text()
        .strip()
    )
    transaction_data.car_number = (
        soup.find_all("table", {"class": "innerForm"})[2]
        .find_all("tr")[-2]
        .find("td", {"class": "value"})
        .get_text()
        .strip()
        .replace(" ", "")
    )
    transaction_data.transaction_type = (
        soup.find_all("table", {"class": "innerForm"})[2]
        .find_all("tr")[-1]
        .find("td", {"class": "value"})
        .get_text()
        .strip()
    )
