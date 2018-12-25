#

"""
"""

from typing import Union


__all__ = ['convert_number']


def convert_number(number: Union[int, str]) -> int:
	"""
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

