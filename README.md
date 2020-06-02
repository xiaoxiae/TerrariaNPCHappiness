# Terraria NPC Happiness
The 1.4 Terraria update made it so that [NPCs have preferences](https://terraria.gamepedia.com/Happiness#Happiness) regarding their location, who they are near, etc. This script simulates the happiness of various groups of NPCs and finds the best possible layout for where they all should live (given the provided restrictions). It internally uses [Dijkstra](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm) (and some smaller optimizations) to find the optimum.

## Running the program
Download the repository (Clone or download) and run `python3 npc.py` (you need to have [Python 3](https://www.python.org/) installed!).

## Custom restrictions
You can add certain restrictions on NPC happiness, biomes, specific NPC groups, pets and many other things by changing [`config.py`](config.py).

## Contents
- [`in`](in) -- contains [this table](https://terraria.gamepedia.com/index.php?title=NPCs&action=edit&section=11) from Terraria's Wiki -- this is where preferences are parsed from. Will be updated should something on the website change.
- [`out`](out) -- contains all of the resulting optimal layouts the program produced (currently contains best layouts, given whatever config specifies).
- [`npc.py`](npc.py) -- main program logic.
- [`config.py`](config.py) -- configuration file.

## Sample output (the best one, IMHO)
```
Village 1: (Forest)
  House 1:
    Guide (0.85)
    Merchant (0.85)

Village 2: (Forest)
  House 1:
    Zoologist (0.8)
    Golfer (0.8)

Village 3: (Desert / Hallow)
  House 1:
    Nurse (0.8 / 0.75)
    Arms Dealer (0.75 / 0.8)

Village 4: (Underground / Hallow)
  House 1:
    Tavernkeep (0.8 / 0.75)
    Demolitionist (0.75 / 0.8)

Village 5: (Hallow)
  House 1:
    Party Girl (0.75)
    Wizard (0.85)

Village 6: (Snow)
  House 1:
    Goblin Tinkerer (0.8)
    Mechanic (0.75)
  House 2:
    Clothier (0.85)
    Tax Collector (0.85)

Village 7: (Desert)
  House 1:
    Dye Trader (0.85)
    Stylist (0.8)
  House 2:
    Steampunker (0.75)
    Cyborg (0.85)

Village 8: (Mushroom)
  House 1:
    Dryad (0.85)
    Truffle (0.85)

Village 9: (Jungle)
  House 1:
    Painter (0.85)
    Witch Doctor (0.85)

Village 10: (Ocean)
  House 1:
    Angler (0.85)
    Pirate (0.75)
```

## Resources
I used the [decompiled Terraria 1.4 source code](https://github.com/Pryaxis/Sources) to check how the happiness is actually implemented, since the Wiki was(/is) a little vague on the details.
