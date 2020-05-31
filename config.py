from dataclasses import dataclass
from typing import *


@dataclass
class Configuration:
    """A dataclass for storing other program configuration."""

    # width of the terminal output
    output_width = 60

    # input and output file names
    input_file_name = "in"
    output_file_name = "out"

    # a comment that will be displayed on top of the output file
    out_comment: Optional[str] = "Pets don't decrease the happiness with the current restrictions, they can be placed pretty much wherever."


@dataclass
class Restrictions:
    """A dataclass for storing the restrictions of the search."""

    # where certain NPCs should be
    # see https://terraria.gamepedia.com/Biome-specific_items for why this is good
    # also, Truffle can only live in Mushroom
    biome_restrictions: Tuple[Tuple[str, str]] = (
        ("Witch Doctor", "Jungle"),
        ("Truffle", "Mushroom"),
    )

    # maximum happiness coefficient for the given NPC
    # if it's ever higher, the given layout will be ignored
    # example: npc_happiness_restrictions: Tuple[Tuple[str, int]] = (("Steampunker", 0.75),)
    npc_happiness_restrictions: Tuple[Tuple[str, int]] = ()

    # NPCs that must share a house
    npc_houses: Tuple[Tuple[str, str]] = (
        ("Pirate", "Angler"),
        ("Nurse", "Arms Dealer"),
        ("Clothier", "Tax Collector"),
    )

    # NPCs whos happiness can be any value
    # note that ignoring NPCs will make the program run significantly slower, since
    # it has to examine many additional layouts
    # example: ignored_npcs: Tuple[str] = ("Angler", "Guide")
    ignored_npcs: Tuple[str] = ()

    # entirely exclude certain NPCs from the search
    # useful for Santa, since he's not really around...
    excluded_npcs: Tuple[str] = ("Santa Claus",)

    # the maximum happiness coefficient an NPC can have
    # example: maximum_npc_happiness: Tuple[Tuple[str, int]] = (("Steampunker", 0.75),)
    maximum_npc_happiness: Tuple[Tuple[str, int]] = ()

    # the maximum happiness coefficient that an NPCs must have
    # any layouts with an NPC having a higher happiness coefficient will be ignored
    # set to None if you wish to disable this restriction
    maximum_happiness_coefficient: Optional[int] = 0.85

    # the minimum and maximum number of NPCs in a single house
    min_npcs_in_house: int = 2
    max_npcs_in_house: int = 2

    # whether to enable pets (cat, dog, bunny) or not
    # enabled will increase the time the program runs
    enable_pets: bool = False
