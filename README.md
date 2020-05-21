# Terraria NPC Happiness
The 1.4 Terraria update, released on 20. 5. 2020, made it so that [NPCs have preferences](https://terraria.gamepedia.com/Happiness#Happiness) regarding their location, who they are near, etc. This script simulates the happiness of various groups of NPCs and finds the best possible layout for where they all should live. It internally uses [Dijkstra](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm) (and some smaller optimizations) to find the optimum.

## Restrictions
You can add certain biome and NPC restrictions by modifying the
`NPC.biome_restrictions` and `NPC.npc_restrictions` variables (although this might provide less optimal of a solution!).

## Contents
The `in` file is [this table](https://terraria.gamepedia.com/index.php?title=NPCs&action=edit&section=11) from Terraria's Wiki -- this is where preferences are parsed from.

The `out` file contains all of the resulting optimal layouts.
