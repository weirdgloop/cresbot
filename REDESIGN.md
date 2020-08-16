## redesign

```
cresbot [-h/--help] [-V/--version]

cresbot hiscores CONFIG [-v/--verbose]
```

```python
import click


@click.group()
def main():
	"""
	"""


@main.command()
@click.argument("config")
@click.option("-v", "--verbose")
def hiscores(config: Config, verbose: int):
	"""
	"""
	setup_logging(verbose)
	# ...
```

```python
# runescape api sdk
# mediawiki api sdk
# lua module parser
```

```python

class HiscoresPager:
	"""
	"""

	def __init__(self, client, category_type: int, table: int, page: int = 1):
		"""
		"""
		self.client = client
		self.category_type = category_type
		self.table = table
		self.page = page

	def get(self, page: int) -> HiscoresPage:
		"""
		"""
		self.client.get()

	def first(self) -> HiscoresPage:
		"""
		"""
		return self.get(1)

	def last(self) -> HiscoresPage:
		"""
		"""

	def next(self, step: int = 1) -> HiscoresPage:
		self.page += step
		self.get(self.page)

	def previous(self, step: int = 1) -> HiscoresPage:
		self.page -= step
		self.get(self.page)


class HiscoresPage:
	"""
	"""

	def __init__(self, html: str):
		"""
		"""

	def is_error(self) -> bool:
		"""
		"""

	def rows(self) -> List[HiscoresRow]:
		"""
		"""

HiscoresRow = namedtuple(name, rank, level, skill)
```
