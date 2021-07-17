from enum import Enum
from mongoengine import *


class Status(Enum):
    NONE = 'none'
    BUY = 'buy'
    SELL = 'sell'


# Is not used.
class Period(Enum):
    DAY = 1
    WEEK = 2
    MONTH = 3


class Sample(EmbeddedDocument):
    date = DateTimeField()
    open = DecimalField()
    high = DecimalField()
    low = DecimalField()
    close = DecimalField()


class BackTest(EmbeddedDocument):
    name = StringField()
    profit = DecimalField()


class Stock(Document):
    symbol = StringField(required=True)
    name = StringField()
    full_name = StringField()
    country = StringField()
    isin = StringField()
    currency = StringField()
    date = DateTimeField()
    close = DecimalField()
    status = EnumField(Status, default=Status.NONE)
    history = EmbeddedDocumentListField(Sample)
    back_test = EmbeddedDocumentListField(BackTest)
