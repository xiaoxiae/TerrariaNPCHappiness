from __future__ import annotations
from dataclasses import dataclass
from typing import *
from enum import Enum, auto
from itertools import combinations
from heapq import *

from time import time
from datetime import datetime

from random import random

start_time = time()


def round_to_multiple(number, multiple) -> int:
    """Round a number to the nearest multiple"""
    return multiple * round(number / multiple)


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

    emotion_factors = (
        ("Loves", 0.9),
        ("Likes", 0.95),
        ("Dislikes", 1.5),
        ("Hates", 1.1),
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

        # Factors that make an NPC happy will lower its prices, down to a minimum of 75%.
        # Conversely, factors that make an NPC unhappy will raise its prices, up to a maximum of 150%.
        # The happiness rounds to 5% increments.
        return round(min(max(round_to_multiple(happiness, 0.05), 0.75), 1.5), 3)

    @classmethod
    def get_group_happiness(self, biome: str, group: Sequence[NPC]):
        """Get the sum of how happy each of the NPC in a group is."""
        total = 0
        was_within_pylon = False

        for npc in group:
            happiness = npc.get_happiness(biome, group)

            if happiness <= 0.85:
                was_within_pylon = True

            if happiness >= 0.9:
                return float("+inf")

            total += happiness

        return float("inf") if not was_within_pylon else total


with open("in", "r") as f:
    lines = f.read().splitlines()

# store NPCS in a dictionary by name
npcs: List[NPC] = []
for i in range(0, len(lines), 8):
    npcs.append(NPC(lines[i : i + 7]))

# Taken from https://terraria.gamepedia.com/Pylons (since they're pretty much all that matters)
biomes = (
    "Forest",
    "Snow",
    "Desert",
    "Underground",
    "Ocean",
    "Jungle",
    "Hallow",
    "Mushroom",
)

queue = []


@dataclass
class State:
    """A given state of the algorithm."""

    # a list of pre-set biome : NPC groups that each have a happiness level
    groups: List[Tuple[str, Tuple[NPC]]]

    # the remaining NPCs
    remaining: Tuple[NPC]

    def get_total_happiness(self):
        """Return how happy all of these groups in this state are."""
        total = 0

        for biome, group in self.groups:
            total += NPC.get_group_happiness(biome, group)

        return total

    def __lt__(a, b):
        """heapq"""
        return False


def add_to_queue(state: State, max_k: Optional[int] = None):
    """..."""
    for group, remaining in yield_groupings(
        state.remaining, 2, max_k or len(state.groups[-1][1])
    ):
        best_biome = None
        best_biome_score = float("+inf")

        for biome in biomes:
            score = NPC.get_group_happiness(biome, group)

            if score < best_biome_score:
                best_biome = biome
                best_biome_score = score

        if best_biome is not None:
            new_state = State(state.groups + [(best_biome, group)], remaining)
            heappush(queue, (round(new_state.get_total_happiness(), 3), new_state))


add_to_queue(State([], npcs), 3)


print(f"Time\t\tHappiness\tQueue size")
print(f"------------------------------------------")

last_score = 0

found_score = None 
found_file = None

while len(queue) > 0:
    score, state = heappop(queue)

    if len(state.remaining) == 0:
        if found_score is None:
            found_score = score
            found_file = open("out", "w")

            found_file.write(f"Total happiness: {score}\n")
            found_file.write(f"-----------------{'-' * len(str(score))}\n\n")

        for biome, npcs in state.groups:
            found_file.write(biome + ":\n")

            for npc in npcs:
                found_file.write(f"- {npc.name} ({npc.get_happiness(biome, npcs)})\n")

            found_file.write("\n")
        found_file.write("------------\n\n")

    if found_score is not None and found_score != score:
        quit()

    if score != last_score:
        print(f"{formatted_time(time() - start_time)}\t{score}\t\t{len(queue)}")
        last_score = score

    add_to_queue(state)
