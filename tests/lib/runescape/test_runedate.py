#

"""Tests for Runedate."""

from lib.runescape.runedate import Runedate, ISO_8601_FMT


def test_epoch():
	"""Check that the Runedate Epoch is for the correct date and time.
	"""
	expected = '2002-02-27T00:00:00Z'
	epoch_str = Runedate.EPOCH.strftime(ISO_8601_FMT)

	assert epoch_str == expected

def test_new_integer():
	"""Check that an integer can be converted to the correct time."""
	expected = '2018-12-24T00:00:00Z'
	value = Runedate(6144).to_iso8601()

	assert value == expected


def test_new_float():
	"""Check that a float can be converted to the correct time."""
	expected = '2018-12-24T13:12:00Z'
	value = Runedate(6144.55).to_iso8601()

	assert value == expected


def test_str_integer():
	"""Check that the human readable representation is correct for an integer runedate."""
	expected = '6144.00'
	value = str(Runedate(6144))

	assert value == expected


def test_str_float():
	"""Check that the human readable representation is correct for a float runedate."""
	expected = '6144.55'
	value = str(Runedate(6144.55))

	assert value == expected


def test_repr_integer():
	"""Check that the string representation is correct for an integer runedate."""
	expected = 'Runedate(runedate=6144.00)'
	value = repr(Runedate(6144))

	assert value == expected


def test_repr_float():
	"""Check that the string representation is correct for a float runedate."""
	expected = 'Runedate(runedate=6144.55)'
	value = repr(Runedate(6144.55))

	assert value == expected


def test_eq():
	"""Check that equality checking works."""
	first = Runedate(6144.50)
	second = Runedate(6144.50)
	third = Runedate(6144.55)

	assert first == second
	assert first != third


def test_lt():
	"""Check that equality checking works."""
	first = Runedate(6144.50)
	second = Runedate(6144.55)

	assert first < second

def test_gt():
	"""Check that equality checking works."""
	first = Runedate(6144.55)
	second = Runedate(6144.50)

	assert first > second

def test_le():
	"""Check that equality checking works."""
	first = Runedate(6144.50)
	second = Runedate(6144.50)
	third = Runedate(6144.55)

	assert first <= second
	assert first <= third


def test_ge():
	"""Check that equality checking works."""
	first = Runedate(6144.55)
	second = Runedate(6144.55)
	third = Runedate(6144.50)

	assert first >= second
	assert first >= third
