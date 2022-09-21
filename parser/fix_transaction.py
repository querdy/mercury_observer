import re
from bs4 import BeautifulSoup as BSoup
from settings import logger
from parser import dto
from parser.login.base_session import BaseSession

autos = ['К114АР159RUS', 'К154ВО159RUS', 'М272ЕН159RUS', 'Н841АС159RUS', 'А833УЕ159RUS', 'А259ТТ159RUS',
         'М259ОУ159RUS', 'М915РР159RUS', 'Е251МН159RUS', 'Т002РМ159RUS', 'М240ОУ159RUS', 'М283ЕН159RUS',
         'А475НО159RUS', 'А260ТТ159RUS', 'К444ВВ159RUS',
         ]

trailers = ['АО411059RUS', 'АР579559RUS', 'АС541159RUS', 'АТ484359RUS', 'АР551159RUS', 'АС683259RUS',
            'АТ490059RUS', 'АС541259RUS', 'АС683159RUS',
            ]

truck = autos + trailers


def fix_transport_number(sess: BaseSession, enterprise: dto.EnterpriseData.enterprise_pk, transaction: dto.TransactionData):
    url = 'https://mercury.vetrf.ru/gve/operatorui'
    sess.fetch(url, params={'enterprisePk': enterprise,
                            '_action': 'chooseServicedEnterprise'
                            }
               )
    transaction_params = {'_action': 'showTransactionForm',
                          'transactionPk': transaction.tr_transaction_pk,
                          'pageList': '1',
                          'cancelAction': 'listTransaction',
                          'anchor': '',
                          }
    sess.fetch(url, params=transaction_params)
    edit_page_params = {
        '_action': 'modifyTransactionForm',
        'pageList': '1',
        'transactionPk': transaction.tr_transaction_pk,
        'request': 'false',
    }
    page = sess.fetch(url, data=edit_page_params)
    soup = BSoup(page.content, 'html5lib')
    version_id = soup.find("input", {"name": "version"}).get_attribute_list('value')[0]
    waybillFirm = soup.find("input", {"name": "waybillFirm"}).get_attribute_list('value')[0]
    waybillCommonHSNumber = soup.find("input", {"name": "waybillCommonHSNumber"}).get_attribute_list('value')[0]

    car_number = _find_correct_number(transaction.car_number.value)
    if not car_number:
        return False
    if transaction.trailer_number:
        trailer_number = _find_correct_number(transaction.trailer_number.value)
    else:
        trailer_number = ' '

    confirm_params = {
        'transactionType': '1',
        'incomplete': 'false',
        'waybillFirm': waybillFirm,
        'waybillCommonHSNumber': waybillCommonHSNumber,
        'transportType': '1',
        'transportAuto': car_number,
        'trailer': trailer_number,
        'storageType': 2,
        'waybill.pk': '',
        'waybill.version': '',
        '_action': 'modifyTransaction',
        'pk': transaction.tr_transaction_pk,
        'request': 'false',
        'pageList': '1',
        'version': version_id,
    }

    page = sess.fetch(url, data=confirm_params)
    if car_number in page.text:
        logger.info("Номер машины изменен")
        return True


def _find_correct_number(vehicle_number: str, vehicles_numbers: list = truck):
    logger.info(vehicle_number)
    vehicle_number = _vehicle_number_fix(vehicle_number)
    if vehicle_number:
        for number in vehicles_numbers:
            if vehicle_number.upper() in number.upper():
                return number
    return False


def _vehicle_number_fix(vehicle_number: str):
    veh_number = None
    if regex_car := re.search(r"(?<!\d)(\d{3})(?!\d)", vehicle_number):
        start = regex_car.start()
        end = regex_car.end()
        veh_number = vehicle_number[start - 1: end + 2]
    elif regex_trailer := re.search(r"(?<!\d)(\d{4})(!\d)*", vehicle_number):
        start = regex_trailer.start()
        end = regex_trailer.end()
        veh_number = vehicle_number[start - 2: end]

    if veh_number is not None and len(veh_number) >= 6:
        return veh_number
    else:
        return None
