from dataclasses import dataclass
from typing import *


@dataclass
class Configuration:
    """A dataclass for storing other program configuration."""

    # width of the terminal output
    output_width = 50

    # input and output file names
    input_file_name = "in"
    output_file_name = "out"


@dataclass
class Restrictions:
    """A dataclass for storing the restrictions of the search."""

    # where certain NPCs should be
    # see https://terraria.gamepedia.com/Biome-specific_items for why this is good
    # also, Truffle can only live in Mushroom
    biome_restrictions: Tuple[Tuple[str, str]] = (
        ("Witch Doctor", "Jungle"),
        ("Truffle", "Mushroom"),
        ("Santa Claus", "Snow"),
    )

    # maximum happiness coefficient for the given NPC
    # if it's ever higher, the given layout will be ignored
    # example: npc_happiness_restrictions: Tuple[Tuple[str, int]] = (("Steampunker", 0.75),)
    npc_happiness_restrictions: Tuple[Tuple[str, int]] = ()

    # NPCs that must share a house
    npc_houses: Tuple[Tuple[str, str]] = (
        ("Nurse", "Arms Dealer"),
    )

    # NPCs whos happiness can be any value
    # note: ignoring NPCs will make the program run significantly slower (it has to examine many additional layouts)
    # example: ignored_npcs: Tuple[str] = ("Angler", "Guide")
    ignored_npcs: Tuple[str] = ()

    # entirely exclude certain NPCs from the search
    # currently useful for Santa, since he's not really around...
    excluded_npcs: Tuple[str] = ("Santa Claus",)

    # the maximum happiness coefficient that an NPCs must have
    # any layouts with an NPC having a higher happiness coefficient will be ignored
    maximum_happiness_coefficient = 0.85

    # the minimum and maximum number of NPCs in a single group (inclusive)
    min_group_size = 1
    max_group_size = 3
