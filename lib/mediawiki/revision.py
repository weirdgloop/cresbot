#

"""
"""

class Revision:
	"""
	"""

	_ATTRS = ('a', 'b')

	def __init__(self, api=None, **kwargs):
		"""
		"""
		for k, v in kwargs.items():
			if k not in self._ATTRS:
				msg = 'Unknown attribute given for Revision: {} (value: {})'.format(k, v)
				raise AttributeError(msg)

			setattr(self, k, v)
