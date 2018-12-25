#

"""
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List

from .exchange_category import ExchangeCategory
from .util import convert_number


__all__ = [
    'Trend',
    'ExchangeCatalogueCategoryAlpha',
    'ExchangeCatalogueCategory',
    'ExchangeCatalogueItemPriceChange',
    'ExchangeCatalogueItem',
    'ExchangeCatalogueItemList',
    'ExchangeCataloguePercentChange',
    'ExchangeCatalogueDetailItem',
    'ExchangeCatalogueDetail',
]

# bools are returned as strings from the exchange database api
# so this is used to convert them to the correct type
_BOOL_MAP = {
    'true': True,
    'false': False,
}


class Trend(Enum):
    """
    """
    POSITIVE = 'positive'
    NEUTRAL = 'neutral'
    NEGATIVE = 'negative'


@dataclass
class ExchangeCatalogueCategoryAlpha:
    """
    """
    letter: str
    items: int


@dataclass
class ExchangeCatalogueCategory:
    """
    """
    types: List[str]
    alpha: List[ExchangeCatalogueCategoryAlpha]

    def __post_init__(self):
        """
        """
        self.alpha = [ExchangeCatalogueCategoryAlpha(**alpha) for alpha in self.alpha]


@dataclass
class ExchangeCataloguePriceChange:
    """
    """
    trend: str
    price: int

    def __post_init__(self):
        """
        """
        self.trend = Trend(self.trend)
        self.price = convert_number(self.price)

@dataclass
class ExchangeCatalogueItem:
    """
    """
    icon: str
    icon_large: str
    id: int
    category: str
    category_icon: str
    name: str
    description: str
    current: ExchangeCataloguePriceChange
    today: ExchangeCataloguePriceChange
    members: bool

    def __post_init__(self):
        """
        """
        self.category = ExchangeCategory.from_name(self.category)
        self.current = ExchangeCataloguePriceChange(**self.current)
        self.today = ExchangeCataloguePriceChange(**self.today)
        self.members = _BOOL_MAP[self.members]


@dataclass
class ExchangeCatalogueItemList:
    """
    """
    total: int
    items: List[ExchangeCatalogueItem]

    def __post_init__(self):
        """
        """
        items = []

        for item in self.items:
            # rename type to category
            item['category'] = item.pop('type', '')
            item['category_icon'] = item.pop('typeIcon', '')
            items.append(ExchangeCatalogueItem(**item))

        self.items = items


@dataclass
class ExchangeCataloguePercentChange:
    """
    """
    trend: str
    change: str

    def __post_init__(self):
        """
        """
        self.trend = Trend(self.trend)

@dataclass
class ExchangeCatalogueDetailItem:
    """
    """
    icon: str
    icon_large: str
    id: int
    category: ExchangeCategory
    category_icon: str
    name: str
    description: str
    current: ExchangeCataloguePriceChange
    today: ExchangeCataloguePriceChange
    members: bool
    day30: ExchangeCataloguePercentChange
    day90: ExchangeCataloguePercentChange
    day180: ExchangeCataloguePercentChange

    def __post_init__(self):
        """
        """
        self.category = ExchangeCategory.from_name(self.category)
        self.current = ExchangeCataloguePriceChange(**self.current)
        self.today = ExchangeCataloguePriceChange(**self.today)
        self.members = _BOOL_MAP[self.members]
        self.day30 = ExchangeCataloguePercentChange(**self.day30)
        self.day90 = ExchangeCataloguePercentChange(**self.day90)
        self.day180 = ExchangeCataloguePercentChange(**self.day180)


@dataclass
class ExchangeCatalogueDetail:
    """
    """
    item: ExchangeCatalogueDetailItem

    def __post_init__(self):
        """
        """
        # rename type to category
        self.item['category'] = self.item.pop('type', '')
        self.item['category_icon'] = self.item.pop('typeIcon', '')

        self.item = ExchangeCatalogueDetailItem(**self.item)


@dataclass
class ExchangeGraphPoint:
    """
    """
    time: datetime
    price: int

    def __post_init__(self):
        """
        """
        time = int(self.time) // 1000
        self.time = datetime.utcfromtimestamp(time)


class ExchangeGraphList(list):
    """
    """

    def before_date(self, before: datetime):
        """
        """
        ret = ExchangeGraphList()

        for point in self:
            if point.time < before:
                ret.append(point)

            break

        return ret

    def after_date(self, after: datetime):
        """
        """
        ret = ExchangeGraphList()

        for point in self:
            if point.time > after:
                ret.append(point)

        return ret

    def between_dates(self, start: datetime, end: datetime):
        """
        """
        ret = ExchangeGraphList()

        for point in self:
            if point.time > start:
                if point.time < end:
                    ret.append(point)

                break

        return ret

@dataclass
class ExchangeGraph:
    """
    """
    daily: ExchangeGraphList
    average: ExchangeGraphList

    def __post_init__(self):
        """
        """
        daily = ExchangeGraphList()
        average = ExchangeGraphList()

        for k, v in self.daily.items():
            point = ExchangeGraphPoint(time=k, price=v)
            daily.append(point)

        for k, v in self.average.items():
            point = ExchangeGraphPoint(time=k, price=v)
            average.append(point)

        daily.sort(key=lambda x: x.time)
        average.sort(key=lambda x: x.time)

        self.daily = daily
        self.average = average


@dataclass
class ExchangeMostTradedRow:
    """
    """
    id: int
    name: str
    members: bool
    min: int
    max: int
    median: int
    total: int

    def __post_init__(self):
        """
        """
        self.min = convert_number(self.min)
        self.max = convert_number(self.max)
        self.median = convert_number(self.median)
        self.total = convert_number(self.total)
