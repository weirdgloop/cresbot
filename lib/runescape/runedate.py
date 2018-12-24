# Copyright (C) 2018 Matthew Dowdell <mdowdell244@gmail.com>

"""Class for managing runedates."""

from datetime import datetime, timedelta
from typing import Union


__all__ = ['Runedate']

SECONDS_IN_DAY = 60 * 60 * 24
ISO_8601_FMT = '%Y-%m-%dT%H:%M:%SZ'


class Runedate:
    """A representation of RuneScape's Runedate.

    A Runedate is the number of days since 27 February 2002 (when RuneScape
    membership was released) rounded to 2 decimal places.
    """

    # 0 Runedate
    EPOCH = datetime(2002, 2, 27)

    def __init__(self, runedate: Union[int, float]):
        """Create a new instance of Runedate.

        :param runedate: An integer or float representation of a runedate.
        """
        self.runedate = runedate

    def __repr__(self) -> str:
        """Get a string presentation of a runedate."""
        return '{}(runedate={:.2f})'.format(self.__class__.__name__, self.runedate)

    def __str__(self) -> str:
        """Get a human-readable string representation of a runedate."""
        return '{:.2f}'.format(self.runedate)

    def __eq__(self, other):
        """Check if another object is equal to this object.

        Will convert the other object to a Runedate if it is a datetime.
        """
        # convert a datetime
        if isinstance(other, datetime):
            other = Runedate.from_datetime(other)

        if not isinstance(other, Runedate):
            raise TypeError('Expected Runedate, found: {}'.format(type(other)))

        # comparing float is inherently dodgy, so convert them to integers instead
        lhs = int(self.runedate * 100 % 1)
        rhs = int(other.runedate * 100 % 1)

        return lhs == rhs

    def __lt__(self, other):
        """Check if another object is less than this object.

        Will convert the other object to a Runedate if it is a datetime.
        """
        # convert a datetime
        if isinstance(other, datetime):
            other = Runedate.from_datetime(other)

        if not isinstance(other, Runedate):
            raise TypeError('Expected Runedate, found: {}'.format(type(other)))

        lhs = int(self.runedate * 100 % 1)
        rhs = int(other.runedate * 100 % 1)

        return lhs < rhs

    def __gt__(self, other):
        """Check if another object is greater than this object.

        Will convert the other object to a Runedate if it is a datetime.
        """
        # convert a datetime
        if isinstance(other, datetime):
            other = Runedate.from_datetime(other)

        if not isinstance(other, Runedate):
            raise TypeError('Expected Runedate, found: {}'.format(type(other)))

        lhs = int(self.runedate * 100 % 1)
        rhs = int(other.runedate * 100 % 1)

        return lhs > rhs

    def __le__(self, other):
        """Check if another object is less than or equal to this object.

        Will convert the other object to a Runedate if it is a datetime.
        """
        # convert a datetime
        if isinstance(other, datetime):
            other = Runedate.from_datetime(other)

        if not isinstance(other, Runedate):
            raise TypeError('Expected Runedate, found: {}'.format(type(other)))

        lhs = int(self.runedate * 100 % 1)
        rhs = int(other.runedate * 100 % 1)

        return lhs <= rhs

    def __ge__(self, other):
        """Check if another object is greater than or equal to this object.

        Will convert the other object to a Runedate if it is a datetime.
        """
        # convert a datetime
        if isinstance(other, datetime):
            other = Runedate.from_datetime(other)

        if not isinstance(other, Runedate):
            raise TypeError('Expected Runedate, found: {}'.format(type(other)))

        lhs = int(self.runedate * 100 % 1)
        rhs = int(other.runedate * 100 % 1)

        return lhs >= rhs

    @classmethod
    def now(cls):
        """Get the current runedate.

        :return: The current date and time as a runedate.
        """
        utcnow = datetime.utcnow()
        delta = utcnow - cls.EPOCH

        days = delta.days
        fraction = delta.seconds / _SECONDS_IN_DAY

        runedate = round(days + fraction, 2)
        return cls(runedate)

    @classmethod
    def from_datetime(cls, value: datetime):
        """Convert a datetime object to a runedate.

        :param datetime value: The datetime to convert.

        :return: The converted runedate.
        """
        diff = value - Runedate.EPOCH

        days = diff.days
        fraction = diff.seconds / _SECONDS_IN_DAY

        runedate = round(days + fraction, 2)
        return cls(runedate)

    def to_datetime(self) -> datetime:
        """Convert a runedate to a datetime object.

        :return: The converted datetime object.
        """
        delta = timedelta(days=self.runedate)
        return self.EPOCH + delta

    def to_iso8601(self) -> str:
        """Convert a runedate to a str in the ISO 8601 format.

        :return: The converted string.
        """
        return self.to_datetime().strftime(ISO_8601_FMT)
