# Terraria NPC Happiness

[2020/05/25]: the code, at the moment, does not produce accurate numbers, due to the fact that Terraria's source code doesn't seem to correspond with what the NPC's Wikipedia page says. I'll try to remedy this in the upcomming days -- sorry!

[2020/05/27]: all should be fixed now. The output looks a little different -- it is separated into a list of 'villages' in certain biomes, that contain 'houses' of NPCs.

---

The 1.4 Terraria update made it so that [NPCs have preferences](https://terraria.gamepedia.com/Happiness#Happiness) regarding their location, who they are near, etc. This script simulates the happiness of various groups of NPCs and finds the best possible layout for where they all should live (given the provided restrictions). It internally uses [Dijkstra](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm) (and some smaller optimizations) to find the optimum.

## Running the program
Download the repository (Clone or download) and run `python3 npc.py` (you need to have [Python 3](https://www.python.org/) installed!).

## Custom restrictions
You can add certain restrictions on NPC happiness, their biomes and some other things by changing [`config.py`](config.py).

## Contents
- [`in`](in) -- contains [this table](https://terraria.gamepedia.com/index.php?title=NPCs&action=edit&section=11) from Terraria's Wiki -- this is where preferences are parsed from. Will be updated should something on the website change.
- [`out`](out) -- contains all of the resulting optimal layouts the program produced (currently contains best layouts, given whatever config specifies).
- [`npc.py`](npc.py) -- main program logic.
- [`config.py`](config.py) -- configuration file. **Look here if you're interested in what the results look like.**
