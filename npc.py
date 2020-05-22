from __future__ import annotations
from dataclasses import dataclass
from typing import *
from itertools import combinations
from heapq import *

from time import time
from datetime import datetime
from textwrap import fill

start_time = time()


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
    """Return a tuple of two elements:
    1) combinations of l of size (min_k, max_k) that contain the first element of l
    2) the remaining elements"""
    if len(l) == 0:
        return []

    for k in range(min_k, max_k + 1):
        for c1 in combinations(l, k):
            if l[0] not in c1:
                continue

            yield (c1, tuple(i for i in l if i not in c1))


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

    EMOTION_FACTORS = (
        ("Loves", 0.9),
        ("Likes", 0.95),
        ("Dislikes", 1.05),
        ("Hates", 1.1),
    )

    MIN_HAPPINESS = 0.75
    MAX_HAPPINESS = 1.5

    # restrictions on where certain NPCs should be
    # see https://terraria.gamepedia.com/Biome-specific_items
    biome_restrictions = (
        ("Witch Doctor", "Jungle"),
        ("Truffle", "Mushroom"),
        ("Santa Claus", "Snow"),
    )

    # restrictions on with whom should certain NPCs be
    npc_group_restrictions = (
        ("Angler", "Pirate"),
        ("Arms Dealer", "Nurse"),
        ("Steampunker", "Cyborg", "Goblin Tinkerer"),
    )

    # restrictions on minimum level of happiness for the given NPC
    npc_happiness_restrictions = (
        ("Steampunker", 0.8),
    )

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
        """|<small>{{item|Painter|class=mirror}}{{item|Zoologist|class=mirror}}</small> -> ["Painter", "Zoologist"]"""

        names = []
        name = self.__strip_row(name)

        if name == "None":
            return None

        while "{{" in name:
            names.append(name[: name.index("}}") + 2][7:-15])
            name = name[name.index("}}") + 2 :].strip()

        return names

    def __add_npc_preference(self, emotion: str, names: str):
        """Adds a preference to the given"""
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

        # Located in a Loved biome    ->  90%
        #              Liked biome    ->  95%
        #              Disliked biome -> 150%
        #              Hated biome    -> 110%
        # For each     Loved NPC      ->  90%
        #              Liked NPC      ->  95%
        #              Disliked NPC   -> 150%
        #              Hated NPC      -> 110%
        for emotion, factor in self.EMOTION_FACTORS:
            if self.__matches_preference(
                Preference(emotion, biome), self.biome_preferences
            ):
                happiness *= factor

            for npc in npcs:
                if self.__matches_preference(
                    Preference(emotion, npc.name), self.npc_preferences
                ):
                    happiness *= factor

        # apply restrictions
        for group in self.npc_group_restrictions:
            if self.name in group:
                # each NPC from the group has to be in npcs
                for npc in group:
                    if not self.__npc_in_group(npc, npcs):
                        return self.MAX_HAPPINESS

        for name, mandatory_biome in self.biome_restrictions:
            if self.name == name and biome != mandatory_biome:
                return self.MAX_HAPPINESS

        # Factors that make an NPC happy will lower its prices, down to a minimum of 75%.
        # Conversely, factors that make an NPC unhappy will raise its prices, up to a maximum of 150%.
        # The happiness rounds to 5% increments.
        # The rounding is
        happiness = min(
            max(round_price(happiness), self.MIN_HAPPINESS), self.MAX_HAPPINESS,
        )

        for npc, maximum_happiness in self.npc_happiness_restrictions:
            if self.name == npc and happiness > maximum_happiness:
                return self.MAX_HAPPINESS

        return happiness

    def __npc_in_group(self, n1: str, group: Sequence[NPC]):
        """Whet"""
        for n2 in group:
            if n1 == n2.name:
                return True
        return False

    @classmethod
    def get_group_happiness(self, biome: str, group: Sequence[NPC]):
        """Get the sum of how happy each of the NPC in a group is."""
        total = 0

        for npc in group:
            happiness = npc.get_happiness(biome, group)

            # restrict only to groups of happiness <= 0.85 to speed up computation
            # if no solution is found, increase (or somehow change) this limit to also
            # include solutions that are not as good
            #
            # note that it is good to include one .85 NPC in each biome so they can
            # sell the Pylon for that biome -- that's why the .85 solution
            if happiness > 0.85:
                return float("+inf")

            total += happiness

        return total


def read_lines() -> List[str]:
    """Read the table from the 'in' file."""
    with open("in", "r") as f:
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

    return lines


lines = read_lines()

# store NPCS in a dictionary by name
npcs: List[NPC] = []
for i in range(0, len(lines), 8):
    npcs.append(NPC(lines[i : i + 7]))

# Taken from https://terraria.gamepedia.com/Pylons
biomes = (
    "Forest",
    "Snow",
    "Desert",
    "Underground",  # not Cave since Happiness table says 'Underground'
    "Ocean",
    "Jungle",
    "Hallow",
    "Mushroom",
)

heap = []


@dataclass
class State:
    """A given state of the algorithm."""

    # a list of pre-set (list of biomes) : (NPC groups) that each have a happiness level
    # the biomes are equally good for the NPCs, that's why it's better to write 'em all
    groups: List[Tuple[Tuple(str), Tuple[NPC]]]

    # the remaining NPCs
    remaining: Tuple[NPC]

    def __post_init__(self):
        self.score = 0

        for biomes, group in self.groups:
            # take any biome from the biomes
            self.score += NPC.get_group_happiness(biomes[0], group)

        self.score = round(self.score, 3)

    def __lt__(a, b):
        """For heapq."""
        return a.score < b.score


def add_to_heap(state: State, max_k: Optional[int] = None):
    """Add all possible groups from the remaining NPCs of a state to the heap."""
    for group, remaining in yield_groupings(
        state.remaining, 2, max_k or len(state.groups[-1][1])
    ):
        # find the best biomes for the given group of NPCs
        best_biomes = []
        best_biomes_score = float("+inf")

        for biome in biomes:
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


add_to_heap(State([], npcs), 4)


print(f"------------------------------------------")
print(f"Time\t\tHappiness\tQueue size")
print(f"------------------------------------------")

last_score = 0

found_score = None
found_file = None

while len(heap) > 0:
    state = heappop(heap)

    # quit on change of score after the optimal state has been found
    if found_score is not None and found_score != state.score:
        quit()

    # print messages on change of score
    if state.score != last_score:
        print(f"{formatted_time(time() - start_time)}\t{state.score}\t\t{len(heap)}")
        last_score = state.score

    # print the optimal state when no NPCs remain to be grouped
    if len(state.remaining) == 0:
        if found_score is None:
            print(f"------------------------------------------")
            print("Optimal layout found, writing to out.")
            print(f"------------------------------------------")

            found_score = state.score
            found_file = open("out", "w")

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
    print(f"------------------------------------------")
    print(
        fill(
            "Optimal layout not found. Please, loosen the restrictions the in NPC class (the *_restrictions variables and the conditions in the get_happiness method).",
            42,
        )
    )
    print(f"------------------------------------------")
