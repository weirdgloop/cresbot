#

"""
"""

import pytest


@pytest.mark.parametrize('name, expected', [
	('Ammo', ExchangeCategory.X),
	('Arrows', ExchangeCategory.X),
	('Bolts', ExchangeCategory.X),
	('Construction materials', ExchangeCategory.X),
	('Construction products', ExchangeCategory.X),
	('Cooking ingredients', ExchangeCategory.X),
	('Costumes', ExchangeCategory.X),
	('Crafting materials', ExchangeCategory.X),
	('Familiars', ExchangeCategory.X),
	('Farming produce', ExchangeCategory.X),
	('Fletching materials', ExchangeCategory.X),
	('Food and Drink', ExchangeCategory.X),
	('Herblore materials', ExchangeCategory.X),
	('Hunting equipment', ExchangeCategory.X),
	('Hunting Produce', ExchangeCategory.X),
	('Jewellery', ExchangeCategory.X),
	('Mage armour', ExchangeCategory.X),
	('Mage weapons', ExchangeCategory.X),
	('Melee armour - high level', ExchangeCategory.X),
	('Melee armour - low level', ExchangeCategory.X),
	('Melee armour - mid level', ExchangeCategory.X),
	('Melee weapons - high level', ExchangeCategory.X),
	('Melee weapons - low level', ExchangeCategory.X),
	('Melee weapons - mid level', ExchangeCategory.X),
	('Mining and Smithing', ExchangeCategory.X),
	('Miscellaneous', ExchangeCategory.X),
	('Pocket items', ExchangeCategory.X),
	('Potions', ExchangeCategory.X),
	('Prayer armour', ExchangeCategory.X),
	('Prayer materials', ExchangeCategory.X),
	('Range armour', ExchangeCategory.X),
	('Range weapons', ExchangeCategory.X),
	('Runecrafting', ExchangeCategory.X),
	('Runes, Spells and Teleports', ExchangeCategory.X),
	('Seeds', ExchangeCategory.X),
	('Summoning scrolls', ExchangeCategory.X),
	('Tools and containers', ExchangeCategory.X),
	('Woodcutting product', ExchangeCategory.X),
])
def test_from_name(name: str, expected: ExchangeCategory):
	"""Test that the canonical category names are mapped to the correct
	category.
	"""
	assert ExchangeCategory.from_name(name) == expected

# TODO: check what weird and wonderful values the wiki was throwing back at us for this
@pytest.mark.parametrize('name, expected', [
	# various spellings of jewellery
	('Jewellry', ExchangeCategory.X),
	# variants of herblore materials
	('Herbs', ExchangeCategory.HERBLORE_MATERIALS),
	# old names that have been replaced
	('Flatpacks', ExchangeCategory.CONSTRUCTION_PRODUCTS),
])
def test_from_name_wiki(name: str, expected: ExchangeCategory):
	"""Test that the various category names used on the wiki map to the correct
	category.
	"""
	assert ExchangeCategory.from_name(name) == expected
