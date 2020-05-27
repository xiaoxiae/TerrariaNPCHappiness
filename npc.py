from __future__ import annotations
from dataclasses import dataclass
from typing import *
from itertools import combinations
from heapq import *

from time import time
from datetime import datetime
from textwrap import fill
from os import path
from sys import exit

from config import Restrictions, Configuration

start_time = time()
current_dir = path.dirname(path.abspath(__file__))

Biome = NewType("Biome", str)


def round_price(number: float) -> int:
    """Round a number to the nearest multiple of 0.05."""
    # special case for infinities
    if number == float("inf"):
        return number

    multiple = 0.05

    return round(multiple * round(number / multiple), 3)


def rounded_sum(*args):
    return round_price(sum(*args))


def formatted_time(seconds: int) -> str:
    """A nicely formatted H:M:S.MS time from seconds."""
    h = (int(seconds) // 3600) % 60
    m = (int(seconds) // 60) % 60
    s = int(seconds) % 60
    ms = int((seconds * 100) % 100)

    return f"{h:02}:{m:02}:{s:02}.{ms:02}"


def yield_groupings(
    l: Sequence[Any], a: int, b: int
) -> Iterator[Tuple[Tuple[Any], Tuple[Any]]]:
    """Yield tuples of two elements:
    1) combination from l of size from a to b (inclusive) that contain the
       first element of l
    2) the remaining elements"""

    assert a >= 1
    assert b >= a

    if len(l) == 0:
        return []

    for k in range(a, b + 1):
        for combination in combinations(l, k):
            if l[0] not in combination:
                continue

            yield (combination, tuple(i for i in l if i not in combination))


@dataclass
class Preference:
    """A class representing a preference."""

    emotion: str
    subject: str

    @classmethod
    def from_string(cls, string: str):
        """Parse a preference from string like 'Likes Clothier'."""
        return Preference(string[: string.index(" ")], string[string.index(" ") + 1 :])


@dataclass
class NPC:
    """A class representing a single NPC."""

    name: str
    biome_preferences: List[Preference]
    npc_preferences: List[Preference]

    emotion_factors: Final[Tuple[Tuple[str, int]]] = (
        ("Loves", 0.9),
        ("Likes", 0.95),
        ("Dislikes", 1.05),
        ("Hates", 1.1),
    )

    # TODO: do this automatically (currently hard-coded from the table)?
    biomes: Final[Tuple[Biome]] = (
        "Forest",
        "Snow",
        "Desert",
        "Underground",
        "Ocean",
        "Jungle",
        "Hallow",
        "Mushroom",
    )

    min_happiness: Final[int] = 0.75
    default_happiness: Final[int] = 1
    max_happiness: Final[int] = 1.5

    def __str__(self):
        return self.name

    __repr__ = __str__

    def __init__(self, lines: List[str]):
        self.name = self.__parse_names(lines[0])[0]

        self.biome_preferences = []

        # add biome preferences (the next 3 lines of the file)
        for i in range(1, 3):
            if not self.__strip_row(lines[i]).startswith("None"):
                self.biome_preferences.append(
                    Preference.from_string(self.__strip_row(lines[i]))
                )

        self.npc_preferences = []

        # add NPC preferences (next 4 lines in the file)
        self.__add_npc_preference("Loves", lines[3])
        self.__add_npc_preference("Likes", lines[4])
        self.__add_npc_preference("Dislikes", lines[5])
        self.__add_npc_preference("Hates", lines[6])

    def __parse_names(self, name: str) -> Optional[List[str]]:
        """Turns |<small>{{item|Painter|class=mirror}}{{item|Zoologist|class=mirror}}</small>
        Into ["Painter", "Zoologist"]."""

        names = []
        name = self.__strip_row(name)

        if name == "None":
            return None

        while "{{" in name:
            names.append(name[: name.index("}}") + 2][7:-15])
            name = name[name.index("}}") + 2 :].strip()

        return names

    def __add_npc_preference(self, emotion: str, names: str):
        """Adds a preference to the given NPC from its string."""
        for name in self.__parse_names(names) or []:
            self.npc_preferences.append(Preference(emotion, name))

    def __strip_row(self, string):
        """|<small>Dislikes Underground</small> -> Dislikes Underground"""
        return string.strip()[8:-8]

    def __matches_preference(self, p: Preference, preferences: List[Preference]):
        """Return True if the preference matches any in the list."""
        return any(
            (p.emotion == p2.emotion and p.subject == p2.subject) for p2 in preferences
        )

    def get_happiness(self, village: Village, biome: Biome, check_restrictions=True):
        """Get the happiness of an NPC, should it be a part of a particular village.
        Since the function will return infinity if some restrictions are not met, an
        option is provided to disable them."""

        happiness = self.default_happiness

        # find the house the NPC is staying in
        for h in village:
            if self in h:
                house = h

        if len(house) >= 3:
            happiness *= 1.04 ** (len(house) - 3)

        if len(house) <= 2 and len(village) <= 4:
            happiness *= 0.9

        # preferences
        for emotion, factor in self.emotion_factors:
            if self.__matches_preference(
                Preference(emotion, biome), self.biome_preferences
            ):
                happiness *= factor

            for npc in house:
                if self.__matches_preference(
                    Preference(emotion, npc.name), self.npc_preferences
                ):
                    happiness *= factor

        happiness = min(
            max(round_price(happiness), self.min_happiness), self.max_happiness,
        )

        # possibly check for some restrictions
        if check_restrictions:
            # correct biome
            for name, mandatory_biome in Restrictions.biome_restrictions:
                if self.name == name and biome != mandatory_biome:
                    return float("inf")

            # max. happiness for a specific npc
            for npc, maximum_happiness in Restrictions.npc_happiness_restrictions:
                if self.name == npc and happiness > maximum_happiness:
                    return float("inf")

            # max. happiness for all npcs
            if happiness > Restrictions.maximum_happiness_coefficient:
                return float("inf")

            for group in Restrictions.npc_houses:
                if self.name in group:
                    # check, if all other NPCs from the group are also in the house
                    for other in group:
                        if other not in house:
                            return float("inf")

        return happiness


@dataclass
class House:
    """A class representing a single NPC house."""

    npcs: List[NPC]

    def __str__(self):
        return f"({', '.join([str(npc) for npc in self])})"

    __repr__ = __str__

    def __getitem__(self, i: int) -> NPC:
        """Get the i-th NPC in the house."""
        return self.npcs[i]

    def __len__(self) -> int:
        """Get the number of NPCs in the house."""
        return len(self.npcs)

    def __contains__(self, npc_or_name: Union[NPC, str]) -> bool:
        """Return True if an NPC is in this house (either the object or by name), else
        False."""

        if isinstance(npc_or_name, NPC):
            return npc_or_name in self.npcs
        else:
            for npc in self:
                if npc.name == npc_or_name:
                    return True
            return False

    def get_happiness(self, village: Village, biome: Biome) -> int:
        """Get the happiness of the entire house in a given village."""
        return rounded_sum([npc.get_happiness(village, biome) for npc in self])


@dataclass
class Village:
    """A class representing a village of houses in a particular biome."""

    houses: List[House]

    def __post_init__(self):
        self.update_biomes()

    def __str__(self):
        return f"[{', '.join([str(house) for house in self])}]"

    __repr__ = __str__

    def __getitem__(self, i: int) -> House:
        """Get the i-th house in the village."""
        return self.houses[i]

    def __len__(self) -> int:
        """Get the number of houses in the village."""
        return len(self.houses)

    def npcs(self) -> Iterator[NPC]:
        """Yield all NPCs of the village."""
        for house in self:
            for npc in house:
                yield npc

    def get_happiness(self, biome: Optional[Biome] = None):
        """Get the happiness of the entire village, either in the given biome, or in
        the best one (calculated by calling this function with various biomes...)."""
        return rounded_sum(
            [house.get_happiness(self, biome or self.biomes[0]) for house in self]
        )

    def update_biomes(self):
        """Calculate the best biomes for the village (lowest happiness) and store them
        in a list. The individual NPC happiness may differ, but the sum will be the
        same."""

        best_biomes = []
        best_biomes_happiness = float("+inf")

        for biome in NPC.biomes:
            happiness = self.get_happiness(biome)

            if happiness < best_biomes_happiness:
                best_biomes = [biome]
                best_biomes_happiness = happiness

            elif happiness == best_biomes_happiness:
                best_biomes.append(biome)

        self.biomes = best_biomes


@dataclass
class State:
    """A given state of the algorithm. This is what's stored in Dijkstra heap.
    It contains a list of villages, and the remaining NPCs that currently aren't in
    one."""

    villages: List[Village]
    remaining: Tuple[NPC]

    def __post_init__(self):
        """Store the happiness so it doesn't need to be re-calculated repeatedly."""
        self.happiness = rounded_sum(
            [village.get_happiness() for village in self.villages]
        )

    def __lt__(self, other):
        """For being compared in the heapq."""
        return self.happiness < other.happiness

    def __getitem__(self, i: int) -> House:
        """Get the i-th village in the state."""
        return self.villages[i]

    def __len__(self) -> int:
        """Get the number of villages in the state."""
        return len(self.villages)


def parse_wiki_file(path: str) -> List[str]:
    """Read the table from the 'in' file."""
    with open(path, "r") as f:
        lines = f.read().strip().splitlines()

        # skip lines till the actual NPC rows
        lines = lines[13:]

        # connect malformed lines (so they all start with a |)
        i = 0
        while i < len(lines):
            if not lines[i].startswith("|"):
                lines[i - 1] = lines.pop(i)
            else:
                i += 1

        # disconnect on ||
        i = 0
        while i < len(lines):
            if "||" in lines[i]:
                lines.insert(i + 1, lines[i][lines[i].index("||") + 1 :])
                lines[i] = lines[i][: lines[i].index("||")]
            else:
                i += 1

    npcs: List[NPC] = []
    for i in range(0, len(lines), 8):
        npcs.append(NPC(lines[i : i + 7]))

    return npcs


def add_to_heap(state: State, max_k: Optional[int] = None):
    """Add all possible groups from the remaining NPCs of a state to the heap."""
    for group, remaining in yield_groupings(
        state.remaining,
        Restrictions.min_group_size,
        max_k or len(state.villages[-1][-1]),
    ):
        # previously added village
        previous_village = None if len(state.villages) == 0 else state.villages[-1]

        # attempt to add a new house to the village
        if previous_village is not None:
            new_village = Village(previous_village.houses + [House(group)])

            # if the happiness is fine enough, create a new state
            if new_village.get_happiness() != float("inf"):
                new_state = State(state.villages[:-1] + [new_village], remaining)
                heappush(heap, new_state)

        # else simply make a village out of the new house
        new_village = Village([House(group)])

        if new_village.get_happiness() != float("inf"):
            new_state = State(state.villages + [new_village], remaining)
            heappush(heap, new_state)


npcs = parse_wiki_file(path.join(current_dir, Configuration.input_file_name))
heap: List[State] = []

# exclude NPCs
npcs = [npc for npc in npcs if npc.name not in Restrictions.excluded_npcs]


add_to_heap(State([], npcs), Restrictions.max_group_size)

print("-" * Configuration.output_width)
print("Time\t\tHappiness\tQueue size")
print("-" * Configuration.output_width)

last_happiness = 0
found_happiness = None
found_file = None

while len(heap) > 0:
    state = heappop(heap)

    # quit on change of happiness after the optimal state has been found
    if found_happiness is not None and found_happiness != state.happiness:
        exit()

    # print messages on change of happiness
    if state.happiness != last_happiness:
        print(
            f"{formatted_time(time() - start_time)}\t{state.happiness}\t\t{len(heap)}"
        )
        last_happiness = state.happiness

    # print the optimal state when no NPCs remain to be grouped
    if len(state.remaining) == 0:
        # first time finding an optimal state
        if found_happiness is None:
            print("-" * Configuration.output_width)
            print("Optimal layout found, writing to out.")
            print("-" * Configuration.output_width)

            # save it
            found_happiness = state.happiness

            # open file
            found_file = open(
                path.join(current_dir, Configuration.output_file_name), "w"
            )

            found_file.write(f"Total happiness: {found_happiness}\n")
            found_file.write(f"Time elapsed: {formatted_time(time() - start_time)}\n")
            found_file.write(f"-----------------{'-' * len(str(found_happiness))}\n\n")

        for i, village in enumerate(state):
            found_file.write(f"Village {i + 1}: ({' / '.join(village.biomes)})\n")

            for i, house in enumerate(village):
                found_file.write(f"  House {i + 1}:\n")

                for npc in house:
                    found_file.write(
                        f"    {npc.name}"
                        f" ({' / '.join([str(npc.get_happiness(village, biome, False)) for biome in village.biomes])})\n"
                    )

            found_file.write("\n")
        found_file.write("------------\n\n")

    add_to_heap(state)

if found_happiness is None:
    print("-" * Configuration.output_width)
    print(
        fill(
            "Optimal layout not found. Try to loosen restrictions in config.py",
            Configuration.output_width,
        )
    )
    print("-" * Configuration.output_width)
