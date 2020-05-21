# Terraria NPC Happiness
The 1.4 Terraria update, released on 20. 5. 2020, made it so that [NPCs have preferences](https://terraria.gamepedia.com/Happiness#Happiness) regarding their location, who they are near, etc. This script simulates the happiness of various groups of NPCs and finds the best possible layout for where they all should live. It internally uses [Dijkstra](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm) (and some smaller optimizations) to find the optimum.

## Restrictions
You can add certain biome and NPC restrictions by modifying the
`NPC.biome_restrictions` and `NPC.npc_restrictions` variables (although this might provide less optimal of a solution!).

## Contents
The `in` file is [this table](https://terraria.gamepedia.com/index.php?title=NPCs&action=edit&section=11) from Terraria's Wiki -- this is where preferences are parsed from.

The `out` file contains all of the resulting optimal layouts.

One layout could look like this:
```
Forest:
- Golfer (0.8)
- Guide (0.85)
- Zoologist (0.8)

Forest:
- Arms Dealer (0.8)
- Merchant (0.85)
- Nurse (0.8)

Jungle:
- Demolitionist (0.8)
- Tavernkeep (0.8)
- Witch Doctor (0.85)

Hallow:
- Painter (0.85)
- Party Girl (0.75)
- Wizard (0.85)

Snow:
- Goblin Tinkerer (0.8)
- Mechanic (0.75)
- Santa Claus (0.8)

Snow:
- Clothier (0.85)
- Tax Collector (0.85)

Desert:
- Dye Trader (0.85)
- Stylist (0.8)

Snow or Desert:
- Cyborg (0.8)
- Steampunker (0.8)

Mushroom:
- Dryad (0.85)
- Truffle (0.85)

Ocean:
- Angler (0.85)
- Pirate (0.75)
```
