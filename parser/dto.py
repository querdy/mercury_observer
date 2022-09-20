import re
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List
from settings import VERIFIED_PRODUCTS, VERIFIED_TRANSACTION_TYPE
from parser.utils import date_str_to_datetime


CAR_NUMBER_REGEX = r"(?i)^[АВЕКМНОРСТУХ] ?\d{3}(?<!000) ?[АВЕКМНОРСТУХ]{2} ?\d{2,3} ?[R][U][S]$"
TRAILERS_NUMBER_REGEX = r"(?i)^[АВЕКМНОРСТУХ]{2} ?\d{4}(?<!0000) ?\d{2} ?[R][U][S]$"


@dataclass(frozen=True)
class User:
    login: str
    password: str


@dataclass
class TransportNumberData:
    value: str
    is_verified: bool = False


@dataclass
class TransctionTypeData:
    value: str
    is_verified: bool = False


@dataclass
class BillOfLadingDateData:
    value: str
    is_verified: bool = False


@dataclass
class ProductNameData:
    value: str
    is_verified: bool = False


@dataclass
class TransactionData:
    rq_transaction_pk: str = None
    tr_transaction_pk: str = None
    recipient_enterprise: str = None
    recipient_company: str = None
    bill_of_lading: str = None
    waybillid: str = None
    version: str = None
    tuid: str = None
    is_confirm: bool = False
    _date_from: datetime = None
    _date_to: datetime = None
    _bill_of_lading_date: BillOfLadingDateData = None
    _product: ProductNameData = None
    _transaction_type: TransctionTypeData = None
    _car_number: TransportNumberData = None
    _trailer_number: TransportNumberData = None

    def is_valid(self):
        return (self._transaction_type.is_verified and
                self._car_number.is_verified and
                self._transaction_type.is_verified and
                self._product.is_verified and
                (self._trailer_number is None or self._trailer_number.is_verified))

    def is_expiration(self):
        expiration = (self._date_to - self._date_from).total_seconds()
        return expiration == 129600

    @property
    def date_from(self):
        return self._date_from

    @date_from.setter
    def date_from(self, value: str):
        self._date_from = date_str_to_datetime(value)

    @property
    def date_to(self):
        return self._date_to

    @date_to.setter
    def date_to(self, value: str):
        self._date_to = date_str_to_datetime(value)

    @property
    def product(self):
        return self._product

    @product.setter
    def product(self, value):
        if any([product.lower() in value.lower() for product in VERIFIED_PRODUCTS]):
            self._product = ProductNameData(value=value, is_verified=True)
        else:
            self._product = ProductNameData(value=value, is_verified=False)

    @property
    def bill_of_lading_date(self):
        return self._bill_of_lading_date

    @bill_of_lading_date.setter
    def bill_of_lading_date(self, value):
        if value != '':
            now_date = datetime.strptime(datetime.now().strftime('%d.%m.%Y'), '%d.%m.%Y')
            date = datetime.strptime(value, '%d.%m.%Y')
            if now_date - date <= timedelta(days=1):
                self._bill_of_lading_date = BillOfLadingDateData(value=value, is_verified=True)
            else:
                self._bill_of_lading_date = BillOfLadingDateData(value=value, is_verified=False)
        else:
            self._bill_of_lading_date = BillOfLadingDateData(value=value, is_verified=False)

    @property
    def transaction_type(self):
        return self._transaction_type

    @transaction_type.setter
    def transaction_type(self, value):
        if value == VERIFIED_TRANSACTION_TYPE:
            self._transaction_type = TransctionTypeData(value=value, is_verified=True)
        else:
            self._transaction_type = TransctionTypeData(value=value, is_verified=False)

    @property
    def car_number(self):
        return self._car_number

    @property
    def trailer_number(self):
        return self._trailer_number

    @car_number.setter
    def car_number(self, value):
        numbers = [number.strip() for number in value.split("/")]

        if re.search(CAR_NUMBER_REGEX, numbers[0]):
            self._car_number = TransportNumberData(value=numbers[0], is_verified=True)
        else:
            self._car_number = TransportNumberData(value=numbers[0], is_verified=False)
        
        if len(numbers) > 1:
            if re.search(TRAILERS_NUMBER_REGEX, numbers[1]):
                self._trailer_number = TransportNumberData(value=numbers[1], is_verified=True)
            else:
                self._trailer_number = TransportNumberData(value=numbers[1], is_verified=False)


@dataclass
class EnterpriseData:
    href: str = None
    numbers_of_requests: str = None
    enterprise_pk: str = None
    enterprise_name: str = None
    transactions_data: List[TransactionData] = field(default_factory=lambda: [])
