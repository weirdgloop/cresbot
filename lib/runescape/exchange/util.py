#

"""
"""

from typing import Union


__all__ = ['convert_number']


def convert_number(number: Union[int, str]) -> int:
	"""Convert a number with optional units to an integer.

	If the number is an integer, then it will be returned immediately. If the number is a string,
	then it will be converted to a number. A numeric string may have optional units appended, e.g.
	1k, 1m, etc. The permitted units are k, m, and b which represent 10**3, 10**6 and 10**9
	respectively. These units are case insensitive.

	For example::

	    >>> convert_number(1000)
	    1000
	    >>> convert_number('1k')
	    1000

	:param Union[int, str] number: The number to convert.

	:return: The converted number as an integer.
	"""
	# nothing to do
	if isinstance(number, int):
		return number

	# force to lower case
	number = number.lower()

	# trim leading + if present
	if number.startswith('+'):
		number = number[1:]

	if number.endswith('k'):
		multiplier = 1_000
	elif number.endswith('m'):
		multiplier = 1_000_000
	elif number.endswith('b'):
		multiplier = 1_000_000_000
	else:
		multiplier = 1

	if multiplier > 1:
		number = number[:-1]

	number = float(number)
	number *= multiplier
	number = int(number)

	return number

