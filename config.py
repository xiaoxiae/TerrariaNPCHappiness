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

    # with whom should certain NPCs be
    # note that this only specifies that the NPCs should be together, not that others can't join them
    npc_group_restrictions: Tuple[Tuple[str, str]] = (
        ("Angler", "Pirate"),
        ("Arms Dealer", "Nurse"),
        ("Steampunker", "Cyborg", "Goblin Tinkerer"),
    )

    # maximum happiness coefficient for the given NPC
    # if it's ever higher, the layout will be ignored
    npc_happiness_restrictions: Tuple[Tuple[str, int]] = ()

    # NPCs whos happiness can be any value
    # note: ignoring NPCs will make the program run significantly slower (it has to examine many additional layouts)
    # example: ignored_npcs: Tuple[str] = ("Angler", "Guide")
    ignored_npcs: Tuple[str] = ()

    # the maximum happiness coefficient that an NPCs must have
    # any layouts with an NPC having a higher happiness coefficient will be ignored
    maximum_happiness_coefficient = 0.85

    # whether we want the NPC groups to cover all biomes, or some can be missing
    require_all_biomes = True

    # the minimum and maximum number of NPCs in a single group (inclusive)
    min_group_size = 2
    max_group_size = 3
