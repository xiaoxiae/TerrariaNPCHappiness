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


def round_price(number) -> int:
    """Round a number to the nearest multiple."""
    multiple = 0.05

    return round(multiple * round(number / multiple), 3)


def formatted_time(seconds: int) -> str:
    """A nicely formatted H:M:S time from seconds."""
    h = (int(seconds) // 3600) % 60
    m = (int(seconds) // 60) % 60
    s = int(seconds) % 60
    ms = int((seconds * 100) % 100)

    return f"{h:02}:{m:02}:{s:02}.{ms:02}"


def yield_groupings(l: List[Any], min_k: int, max_k: int) -> Tuple[Tuple[Any]]:
    """Yield tuples of two elements:
    1) combination from l of size from min_k to max_k (inclusive) that contain the first element of l
    2) the remaining elements"""
    assert min_k >= 1
    assert max_k >= min_k

    if len(l) == 0:
        return []

    for k in range(min_k, max_k + 1):
        for combination in combinations(l, k):
            if l[0] not in combination:
                continue

            yield (combination, tuple(i for i in l if i not in combination))

@dataclass
class Preference:
    """A class representing a preference."""

    emotion: str
    subject: Any

    @classmethod
    def from_string(cls, string: str):
        return Preference(string[: string.index(" ")], string[string.index(" ") + 1 :])


@dataclass
class NPC:
    name: str
    biome_preferences: List[Preference]
    npc_preferences: List[Preference]

    # Located in a Loved biome    ->  90%
    #              Liked biome    ->  95%
    #              Disliked biome -> 150%
    #              Hated biome    -> 110%
    # For each     Loved NPC      ->  90%
    #              Liked NPC      ->  95%
    #              Disliked NPC   -> 150%
    #              Hated NPC      -> 110%
    emotion_factors: Final[Tuple[Tuple[str, int]]] = (
        ("Loves", 0.9),
        ("Likes", 0.95),
        ("Dislikes", 1.05),
        ("Hates", 1.1),
    )

    # hard-coded from what I saw in the table
    # TODO: do this automatically?
    biomes: Final[Tuple[str]] = (
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
    max_happiness: Final[int] = 1.5

    def __init__(self, lines: List[str]):
        self.name = self.__parse_names(lines[0])[0]

        self.biome_preferences = []

        # add both biome preferences
        for i in range(1, 3):
            if not self.__strip_row(lines[i]).startswith("None"):
                self.biome_preferences.append(
                    Preference.from_string(self.__strip_row(lines[i]))
                )

        self.npc_preferences = []

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

    def get_happiness(self, biome: str, npcs: Sequence[NPC]):
        """Get the happiness of an NPC, should it be grouped with a particular set of
        NPCs in a particular biome. Note that the npc itself should be contained in the
        list of npcs

        Rules were taken from https://terraria.gamepedia.com/NPCs#Happiness."""
        happiness = 1

        # More than two other NPCs within 25 tiles (for each additional NPC): 104%
        if len(npcs) >= 4:
            happiness *= 1.04 ** (len(npcs) - 3)

        # Fewer than two other NPCs within 25 tiles: 90%
        if len(npcs) <= 3 and len(npcs) != 1:
            happiness *= 0.9

        for emotion, factor in self.emotion_factors:
            if self.__matches_preference(
                Preference(emotion, biome), self.biome_preferences
            ):
                happiness *= factor

            for npc in npcs:
                if self.__matches_preference(
                    Preference(emotion, npc.name), self.npc_preferences
                ):
                    happiness *= factor

        for restricted_group in Restrictions.npc_group_restrictions:
            if self.name in restricted_group:
                # each NPC from the group has to be in npcs
                for name in restricted_group:
                    if not self.__name_in_group(name, npcs):
                        return self.max_happiness

        for name, mandatory_biome in Restrictions.biome_restrictions:
            if self.name == name and biome != mandatory_biome:
                return self.max_happiness

        # Factors that make an NPC happy will lower its prices, down to a minimum of 75%.
        # Conversely, factors that make an NPC unhappy will raise its prices, up to a maximum of 150%.
        # The happiness rounds to 5% increments.
        # The rounding is
        happiness = min(
            max(round_price(happiness), self.min_happiness), self.max_happiness,
        )

        for npc, maximum_happiness in Restrictions.npc_happiness_restrictions:
            if self.name == npc and happiness > maximum_happiness:
                return self.max_happiness

        return happiness

    def __name_in_group(self, name: str, group: Sequence[NPC]):
        """Whether a NPC with a given name is in a group of NPCs."""
        for npc in group:
            if name == npc.name:
                return True
        return False

    @classmethod
    def get_group_happiness(self, biome: str, group: Sequence[NPC]):
        """Get the sum of how happy each of the NPC in a group is."""
        total = 0

        for npc in group:
            # ignore ignored NPCs
            if npc.name in Restrictions.ignored_npcs:
                continue

            happiness = npc.get_happiness(biome, group)

            if happiness > Restrictions.maximum_happiness_coefficient:
                return float("+inf")

            total += happiness

        return total


@dataclass
class State:
    """A given state of the algorithm. This is what's stored in Dijkstra heap.
    It contains a list of NPC groups that have already been put into a group and will
    not change, and the remaining NPCs that are yet to be put into one."""

    # a list of (biomes) : (NPCs) that each have some happiness level
    groups: List[Tuple[Tuple(str), Tuple[NPC]]]

    # the remaining NPCs that don't fit into any group (that groups will be create from)
    remaining: Tuple[NPC]

    def __post_init__(self):
        self.score = 0

        for biomes, group in self.groups:
            # take any biome from the biomes
            self.score += NPC.get_group_happiness(biomes[0], group)

        self.score = round(self.score, 3)

    def __lt__(self, other):
        """For heapq."""
        return self.score < other.score

    def contains_all_biomes(self):
        """Whether the state contains all biomes."""
        remaining_biomes = set(NPC.biomes)

        for biome, _ in self.groups:
            remaining_biomes -= set(biome)

        return len(remaining_biomes) == 0


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


npcs = parse_wiki_file(path.join(current_dir, Configuration.input_file_name))
heap = []


def add_to_heap(state: State, max_k: Optional[int] = None):
    """Add all possible groups from the remaining NPCs of a state to the heap."""
    for group, remaining in yield_groupings(
        state.remaining, Restrictions.min_group_size, max_k or len(state.groups[-1][1])
    ):
        # find the best biomes for the given group of NPCs
        best_biomes = []
        best_biomes_score = float("+inf")

        for biome in NPC.biomes:
            score = NPC.get_group_happiness(biome, group)

            if score < best_biomes_score:
                best_biomes = [biome]
                best_biomes_score = score
            elif score == best_biomes_score:
                best_biomes.append(biome)

        # only add it if the score isn't infinite
        if best_biomes_score != float("+inf"):
            new_state = State(state.groups + [(best_biomes, group)], remaining)
            heappush(heap, new_state)


add_to_heap(State([], npcs), Restrictions.max_group_size)


print("-" * Configuration.output_width)
print("Time\t\tHappiness\tQueue size")
print("-" * Configuration.output_width)

last_score = 0

found_score = None
found_file = None

while len(heap) > 0:
    state = heappop(heap)

    # quit on change of score after the optimal state has been found
    if found_score is not None and found_score != state.score:
        exit()

    # print messages on change of score
    if state.score != last_score:
        print(f"{formatted_time(time() - start_time)}\t{state.score}\t\t{len(heap)}")
        last_score = state.score

    # print the optimal state when no NPCs remain to be grouped
    if len(state.remaining) == 0:
        if not state.contains_all_biomes() and Restrictions.require_all_biomes:
            continue

        if found_score is None:
            print("-" * Configuration.output_width)
            print("Optimal layout found, writing to out.")
            print("-" * Configuration.output_width)

            found_score = state.score
            found_file = open(
                path.join(current_dir, Configuration.output_file_name), "w"
            )

            found_file.write(f"Total happiness: {found_score}\n")
            found_file.write(f"Time elapsed: {formatted_time(time() - start_time)}\n")
            found_file.write(f"-----------------{'-' * len(str(found_score))}\n\n")

        for biomes, npcs in sorted(state.groups, key=lambda e: e[0][0]):
            found_file.write(" or ".join(biomes) + ":\n")

            for npc in sorted(npcs, key=lambda npc: npc.name):
                found_file.write(
                    f"- {npc.name} ({npc.get_happiness(biomes[0], npcs)})\n"
                )

            found_file.write("\n")
        found_file.write("------------\n\n")

    add_to_heap(state)

if found_score is None:
    print("-" * Configuration.output_width)
    print(
        fill(
            "Optimal layout not found. Try to loosen restrictions in config.py",
            Configuration.output_width,
        )
    )
    print("-" * Configuration.output_width)
