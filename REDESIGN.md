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
