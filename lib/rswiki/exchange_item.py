# Copyright (C) 2018 Matthew Dowdell <mdowdell244@gmail.com>

"""
"""

from datetime import datetime
from enum import Enum
import logging
import re

import mwparserfromhell

from ..exception import ExchangeTemplateMissingError, ExchangeTemplateConvertedError


__all__ = ['ExchangeCategory', 'ExchangeItem']

_FIRST_CAP_RE = re.compile('(.)([A-Z][a-z]+)')
_ALL_CAP_RE = re.compile('([a-z0-9])([A-Z])')
# the various datetime formats used
# most of these come from the exchange namespace back when people update things by hand
# the first is the correct version
# TODO: figure out how to handle timezones, e.g. EST, etc.
_DATETIME_FMTS = ['%H:%M, %B %d, %Y (UTC)',
                  '%H:%M, %d %B %Y (UTC)',
                  '%H:%M, %d %B %Y',
                  '%H:%M:%S, %d %B %Y (UTC)',
                  '%H:%M %d %B %Y (UTC)',
                  '%H:%M, %B %d, %Y (GMT)',
                  '%H:%M, %B %d, %Y',
                  '%H:%M, %d %B %Y (UTC) (UTC)',
                  '%H:%M,%d %B %Y (UTC)',
                  '%H:%M,%B %d,%Y (UTC)',
                  '%d %B %Y (UTC)']
_SQL_FMT = '%Y-%m-%d %H:%M:%S'
CATEGORY_ERRORS = ("Unexpected value for 'category': 'nil'",
                   "Unexpected value for 'category': ''")

LOGGER = logging.getLogger(__name__)


class ExchangeCategory(Enum):
    """
    The possible exchange categories.

    Jagex lists these alphabetically on the Grand Exchange Database, but the integers underneath
    seem to be static.
    """
    UNKNOWN = -1
    MISCELLANEOUS = 0
    AMMO  = 1
    ARROWS = 2
    BOLTS = 3
    CONSTRUCTION_MATERIALS = 4
    CONSTRUCTION_PRODUCTS = 5
    COOKING_INGREDIENTS = 6
    COSTUMES = 7
    CRAFTING_MATERIALS = 8
    FAMILIARS = 9
    FARMING_PRODUCE = 10
    FLETCHING_MATERIALS = 11
    FOOD_AND_DRINK = 12
    HERBLORE_MATERIALS = 13
    HUNTING_EQUIPMENT = 14
    HUNTING_PRODUCE = 15
    JEWELLERY = 16
    MAGE_ARMOUR = 17
    MAGE_WEAPONS = 18
    MELEE_ARMOUR_LOW_LEVEL = 19
    MELEE_ARMOUR_MID_LEVEL = 20
    MELEE_ARMOUR_HIGH_LEVEL = 21
    MELEE_WEAPONS_LOW_LEVEL = 22
    MELEE_WEAPONS_MID_LEVEL = 23
    MELEE_WEAPONS_HIGH_LEVEL = 24
    MINING_AND_SMITHING = 25
    POTIONS = 26
    PRAYER_ARMOUR = 27
    PRAYER_MATERIALS = 28
    RANGE_ARMOUR = 29
    RANGE_WEAPONS = 30
    RUNECRAFTING = 31
    RUNES_SPELLS_AND_TELEPORTS = 32
    SEEDS = 33
    SUMMONING_SCROLLS = 34
    TOOLS_AND_CONTAINERS = 35
    WOODCUTTING_PRODUCT = 36
    POCKET_ITEMS = 37

    def to_name(self) -> str:
        """
        """
        parts = self.name.split('_')

        if parts[0] == 'MELEE':
            parts.insert(2, '-')

        elif parts[0] == 'RUNES':
            parts[0] += ','

        for i, p in enumerate(parts):
            if i == 0:
                p = p.capitalize()
            else:
                p = p.lower()

            if p in ('drink', 'smithing', 'spells', 'teleports'):
                p = p.capitalize()

            parts[i] = p

        return ' '.join(parts)


class ExchangeItem:
    """
    A representation of an item and it's data as stored in an exchange module or page.
    """

    _ATTRS = ('item_id', 'price', 'last', 'date', 'last_date', 'volume', 'volume_date', 'item',
              'value', 'limit', 'members', 'category', 'alchable', 'examine', 'usage')
    # TODO: low_alch and high_alch seem to have been there before we had value
    #       so we should derive value from them
    # score looks to be incrrect spelling for store
    _IGNORED_ATTRS = ('icon', 'view', 'low_alch', 'high_alch', 'store', 'abs_min_price',
                      'abs_max_price', 'direction', 'street', 'score', 'obj')

    def __init__(self, allow_category_nil: bool = False, **kwargs):
        """
        Create a new instance of ``ExchangeItem``.

        :param **kwargs: Key-value arguments for the object attributes. The following attributes
            are valid:

            * item_id
            * price
            * last
            * date
            * last_date
            * volume
            * volume_date
            * item
            * value
            * limit
            * members
            * category
            * alchable
            * examine
            * usage

            The following attributes are considered valid but are ignored as they are from previous
            version of exchange module or page formats:

            * icon
            * view
            * low_alch
            * high_alch
            * abs_min_price
            * abs_max_price
            * direction
            * street
            * score (mispelt version of store)
            * obj (duplication of item_id)

        :raises AttributeError: If an unrecognised attribute is found.
        :raises ValueError: If an invalid value for a valid attribute is found.
        """
        for k, v in kwargs.items():
            if k in self._ATTRS:
                if k == 'category' and allow_category_nil:
                    try:
                        self.category = v
                    except ValueError as exc:
                        if str(exc).endswith(CATEGORY_ERRORS):
                            self.category = ExchangeCategory.UNKNOWN
                else:
                    setattr(self, k, v)

            elif k in self._IGNORED_ATTRS:
                pass

            else:
                msg = 'Unknown attribute found: name={!s}, value={!r}'.format(k, v)
                raise AttributeError(msg)

        if 'alchable' not in kwargs:
            self.alchable = False

    def __repr__(self) -> str:
        """
        """
        name = self.__class__.__name__
        values = []

        for attr in self._ATTRS:
            val = getattr(self, attr)

            if isinstance(val, datetime):
                val = val.strftime(_DATETIME_FMTS[0])

            elif isinstance(val, ExchangeCategory):
                val = val.to_name()

            values.append('{}={!r}'.format(attr, val))

        return '{}({})'.format(name, ', '.join(values))

    def to_module() -> str:
        """
        Convert the instance to a Lua table to be used for an exchange module.

        :rtype: str
        """
        values = []

        for attr in self._ATTRS:
            key = snakecase_to_camelcase(attr)

            if attr == 'usage':
                usage = [' ' * 8 + repr(u) for u in self.usage]
                val = ',\n'.join(usage)

                values.append('    {!s} = {\n{!s}\n    }'.format(key, val))

            else:
                val = getattr(self, attr)

                if isinstance(val, datetime):
                    val = val.strftime(_DATETIME_FMT)

                elif isinstance(val, ExchangeCategory):
                    val = val.to_name

                if val is None:
                    values.append('    {!s} = nil'.format(key))
                else:
                    values.append('    {!s} = {!r}'.format(key, val))

        return 'return {\n' + ',\n'.join(values) + '\n}\n'

    @classmethod
    def from_module(cls, text: str, allow_category_nil: bool = False):
        """
        Create an instance of ``ExchangeItem`` from the content of an exchange module,
        e.g. ``Module:Exchange/Fire rune``.

        :param str text: The content of the module.

        :return ExchangeItem: An instance of ExchangeItem containing the data found in ``text``.
        """
        # strip_any_whitespace
        text = text.strip()
        # remove_initial_return
        text = re.sub(r'\Areturn {', '', text)
        # remove_closing_brace
        text = re.sub(r'}\Z', '', text)
        # strip_any_whitespace_again
        text = text.strip()

        attrs = {}
        lines = text.split('\n')
        in_usage = False

        for line in lines:
            line = line.strip()

            if not line:
                # skip blank lines
                continue

            if line.startswith('--'):
                # ignore comments
                continue

            if line.startswith('usage'):
                key = 'usage'
                value = []
                in_usage = True
                continue

            if in_usage:
                if line.strip() == '}':
                    in_usage = False
                else:
                    line = line.strip().replace(',', '')[1:-1]
                    value.append(line)
                    continue

            else:
                parts = line.split('=', maxsplit=2)
                key = parts[0].strip()
                value = parts[1].strip()

                # convert to snake case
                key = camelcase_to_snakecase(key)

                # trim_trailing_comma
                if value.endswith(','):
                    value = value[:-1]

                # trim_quotes_on_string_values
                if (
                    (value.startswith('\'') and value.endswith('\'')) or
                    (value.startswith('"') and value.endswith('"'))
                ):
                    value = value[1:-1]

            attrs[key] = value

        return cls(allow_category_nil=allow_category_nil, **attrs)

    @classmethod
    def from_page(cls, text: str):
        """
        Create an instance of ``ExchangeItem`` from the content of an exchange page,
        e.g. ``Exchange:Fire rune``.

        :param str text: The content of the module.

        :return ExchangeItem: An instance of ExchangeItem containing the data found in ``text``.

        :raises ExchangeTemplateMissingError:
        """
        # strip_any_whitespace
        text = text.strip()

        # remove noincludes
        text = re.sub(r'<noinclude>[\s\S]*?</noinclude>', '', text, flags=re.MULTILINE)
        # remove categories
        text = re.sub(r'\[\[Category:.+?\]\]', '', text)
        # remove default sort
        text = re.sub(r'\{\{DEFAULTSORT:.+?\}\}', '', text)
        # remove comments
        text = re.sub(r'<!--[\s\S]*?-->', '', text, flags=re.MULTILINE)
        # strip_any_whitespace_again
        text = text.strip()

        attrs = {}

        wikicode = mwparserfromhell.parse(text)
        templates = wikicode.filter_templates()

        for template in templates:
            if template.name.strip() == 'ExchangeItem':
                break
        else:
            raise ExchangeTemplateMissingError()

        for param in template.params:
            name = str(param.name).strip()

            if name.isdigit():
                continue

            name = camelcase_to_snakecase(str(param.name).strip())
            attrs[name] = str(param.value).strip()

        return cls(allow_category_nil=True, **attrs)

    @property
    def item_id(self) -> int:
        """
        Getter for the ``item_id`` attribute.

        :rtype: int
        """
        return self._item_id

    @item_id.setter
    def item_id(self, value):
        """
        Setter for the ``item_id`` attribute.

        :param value: The value to set ``item_id`` to.

        :raises ValueError: If ``value`` is invalid.
        """
        self._item_id = convert_to_int('item_id', value, 1)

    @property
    def price(self) -> int:
        """
        Getter for the ``price`` attribute.

        :rtype: int
        """
        return self._price

    @price.setter
    def price(self, value):
        """
        Setter for the ``price`` attribute.

        :param value: The value to set ``price`` to.

        :raises ValueError: If ``value`` is invalid.
        """
        self._price = convert_to_int('price', value, 0)

    @property
    def last(self) -> int:
        """
        Getter for the last attribute.

        :rtype: int
        """
        return self._last

    @last.setter
    def last(self, value):
        """
        Setter for the ``last`` attribute.

        :param value: The value to set ``last`` to.

        :raises ValueError: If ``value`` is invalid.
        """
        self._last = convert_to_int('last', value, 0)

    @property
    def date(self) -> datetime:
        """
        Getter for the ``date`` attribute.

        :rtype: datetime.
        """
        return self._date

    @property
    def date_sql(self) -> str:
        """
        Get ``date`` in a format accepted by MySQL's datetime field.

        :rtype: str
        """
        return self._date.strftime(_SQL_FMT)

    @date.setter
    def date(self, value):
        """
        Setter for the ``date`` attribute.

        :param value: The value to set ``date`` to.

        :raises ValueError: If ``value`` is invalid.
        """
        self._date = convert_to_datetime('date', value)

    @property
    def last_date(self) -> datetime:
        """
        Getter for the ``last_date`` attribute.

        :rtype: datetime.
        """
        return self._last_date

    @property
    def last_date_sql(self) -> str:
        """
        Get ``last_date`` in a format accepted by MySQL's datetime field.

        :rtype: str
        """
        return self._date.strftime(_SQL_FMT)

    @last_date.setter
    def last_date(self, value):
        """
        Setter for the ``last_date`` attribute.

        :param value: The value to set ``last_date`` to.

        :raises ValueError: If ``value`` is invalid.
        """
        self._last_date = convert_to_datetime('last_date', value)

    @property
    def volume(self):
        """
        Getter for the volume attribute.

        :rtype: int
        """
        return self._volume

    @volume.setter
    def volume(self, value):
        """
        Setter for the ``volume`` attribute.

        :param value: The value to set ``volume`` to.

        :raises ValueError: If ``value`` is invalid.
        """
        self._volume = convert_to_float('volume', value, 0.0)

    @property
    def volume_date(self) -> datetime:
        """
        Getter for the ``volume_date`` attribute.

        :rtype: datetime.
        """
        return self._volume_date

    @property
    def volume_date_sql(self) -> str:
        """
        Get ``volume_date`` in a format accepted by MySQL's datetime field.

        :rtype: str
        """
        return self._volume_date.strftime(_SQL_FMT)

    @volume_date.setter
    def volume_date(self, value):
        """
        Setter for the ``volume_date`` attribute.

        :param value: The value to set ``volume_date`` to.

        :raises ValueError: If ``value`` is invalid.
        """
        self._volume_date = convert_to_datetime('volume_date', value)

    @property
    def item(self) -> str:
        """
        Getter for the ``item`` attribute.

        :rtype: str.
        """
        return self._item

    @item.setter
    def item(self, value):
        """
        Setter for the ``item`` attribute.

        :param value: The value to set ``item`` to.
        """
        self._item = value

    @property
    def value(self) -> int:
        """
        Getter for the ``value`` attribute.

        :rtype: int.
        """
        return self._value

    @value.setter
    def value(self, value):
        """
        Setter for the ``value`` attribute.

        :param value: The value to set ``value`` to.

        :raises ValueError: If ``value`` is invalid.
        """
        # cook says it's valid for values to be 0
        self._value = convert_to_int('value', value, 0)

    @property
    def limit(self) -> int:
        """
        Getter for the ``limit`` attribute.

        :rtype: int.
        """
        return self._limit

    @limit.setter
    def limit(self, value):
        """
        Setter for the ``limit`` attribute.

        :param value: The value to set ``limit`` to.

        :raises ValueError: If ``value`` is invalid.
        """
        self._limit = convert_to_int('limit', value, 0)

    @property
    def members(self) -> bool:
        """
        Getter for the ``members`` attribute.

        :rtype: bool.
        """
        return self._members

    @members.setter
    def members(self, value):
        """
        Setter for the ``members`` attribute.

        :param value: The value to set ``members`` to.

        :raises ValueError: If ``value`` is invalid.
        """
        self._members = convert_to_bool('members', value)

    @property
    def category(self) -> ExchangeCategory:
        """
        Getter for the ``category`` attribute.

        :rtype: ExchangeCategory.
        """
        return self._category

    @category.setter
    def category(self, value):
        """
        Setter for the ``category`` attribute.

        :param value: The value to set ``category`` to.

        :raises ValueError: If ``value`` is invalid.
        """
        if isinstance(value, ExchangeCategory):
            self._category = value
        else:
            new_value = value \
                .replace(' - ', '_') \
                .replace(',', '') \
                .replace(' ', '_') \
                .upper()

            try:
                self._category = getattr(ExchangeCategory, new_value)
            except AttributeError as exc:
                if new_value.startswith('JEWEL'):
                    # handle quirky spellings of jewellery
                    self._category = ExchangeCategory.JEWELLERY
                    LOGGER.warning('%s category was correct from %r to %r',
                                   self.item, value, new_value)

                elif new_value.startswith('HERBS'):
                    # a couple of odd instances of this
                    self._category = ExchangeCategory.HERBLORE_MATERIALS
                    LOGGER.warning('%s category was correct from %r to %r',
                                   self.item, value, new_value)

                elif new_value == 'FLATPACKS':
                    # old name for construction products
                    self._category = ExchangeCategory.CONSTRUCTION_PRODUCTS

                else:
                    msg = 'Unexpected value for {!r}: {!r}'.format('category', value)
                    raise ValueError(msg)

    @property
    def alchable(self) -> bool:
        """
        Getter for the ``alchable`` attribute.

        :rtype: bool.
        """
        return self._alchable

    @alchable.setter
    def alchable(self, value):
        """
        Setter for the ``alchable`` attribute.

        :param value: The value to set ``alchable`` to.

        :raises ValueError: If ``value`` is invalid.
        """
        self._alchable = convert_to_bool('alchable', value)


def camelcase_to_snakecase(value: str) -> str:
    """
    Converts a string in camel case to the equivalent name in snake case.

    :param str value: The string to convert.

    :return str: The converted string
    """
    # based on <https://stackoverflow.com/a/1176023>
    s1 = _FIRST_CAP_RE.sub(r'\1_\2', value)
    return _ALL_CAP_RE.sub(r'\1_\2', s1).lower()


def snakecase_to_camelcase(value: str) -> str:
    """
    """
    parts = value.split('_')

    for i, p in enumerate(parts):
        if i == 0:
            continue

        parts[i] = p.capitalize()

    return ''.join(parts)


def convert_to_bool(name: str, value) -> bool:
    """
    Convert a vaue to it's ``bool`` equivalent.

    Converts the following strings to ``True``:

    * yes
    * true

    Converts the following strings to ``False``:

    * no
    * false

    Both sets of strings are case insensitive.

    :param str name: The name of the attribute being converted. Used in error messages.
    :param value: The value to convert.

    :return bool: The converted value.

    :raises ValueError: If ``value`` could not be converted to a ``bool``.
    """
    if isinstance(value, bool):
        return value

    value = value.strip().lower()

    if value in ('true', 'yes'):
        return True

    if value in ('false', 'no'):
        return False

    msg = 'Unable to convert {!r} to boolean: {!r}'.format(name, value)
    raise ValueError(msg)


def convert_to_int(name: str, value, min_value: int = None) -> int:
    """
    Converts a value to an integer.

    :param str name: The name of the attribute being converted. Used in error messages.
    :param value: The value to convert.

    :return int: The converted value.

    :raises ValueError: If ``value`` could not be converted to an ``int``.
    """
    if not isinstance(value, int):
        if value == 'nil' or value == '' or value is None:
            return None

        # strip commas
        value = value.replace(',', '')
        # rm trailing gp
        value = value.lower().replace('gp', '')
        # rm any leftover whitespace
        value = value.strip()

        # TODO: handle modifiers, e.g. 100k, 1.1m(il)?, etc.

        try:
            value = int(value)
        except ValueError as exc:
            msg = '{!r} could not be converted to an integer: {!r}.'.format(name, value)
            raise ValueError(msg) from exc

    if min_value is not None and value < min_value:
        msg = '{!r} must be greater than {!r}: {!r}.'.format(name, min_value, value)
        raise ValueError(msg)

    return value


def convert_to_float(name: str, value, min_value: float = None) -> float:
    """
    Converts a value to an integer.

    :param str name: The name of the attribute being converted. Used in error messages.
    :param value: The value to convert.

    :return float: The converted value.

    :raises ValueError: If ``value`` could not be converted to a ``float``.
    """
    if not isinstance(value, float):
        try:
            # strip commas
            value = value.replace(',', '')
            value = float(value)
        except ValueError as exc:
            msg = '{!r} could not be converted to a float: {!r}.'.format(name, value)
            raise ValueError(msg) from exc

    if min_value is not None and value < min_value:
        msg = '{!r} must be greater than {!r}: {!r}.'.format(name, min_value, value)
        raise ValueError(msg)

    return value


def convert_to_datetime(name: str, value) -> datetime:
    """
    Converts a value to a datetime object.

    :param str name: The name of the attribute being converted. Used in error messages.
    :param value: The value to convert.

    :return bool: The converted value.

    :raises ValueError: If ``value`` could not be converted to a ``datetime``.
    """
    if isinstance(value, datetime):
        return value

    if value == '' or value is None:
        return None

    # handle cases where someone used ~~~~ instead of ~~~~~
    # when manually setting a date
    value = re.sub(r'\[\[.*?\]\]', '', value)
    value = re.sub(r'\{\{.*?\}\}', '', value)

    # strip any leftover whitespace that creeps in
    value = value.strip()

    for fmt in _DATETIME_FMTS:
        try:
            value = datetime.strptime(value, fmt)
            break
        except ValueError:
            pass
    else:
        msg = '{!r} could not be converted to a datetime: {!r}.'.format(name, value)
        raise ValueError(msg)

    return value
