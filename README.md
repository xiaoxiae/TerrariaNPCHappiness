# Terraria NPC Happiness
The 1.4 Terraria update, released on 20. 5. 2020, made it so that [NPCs have preferences](https://terraria.gamepedia.com/Happiness#Happiness) regarding their location, who they are near, etc...

This script aims to calculate just that: it simulates the happiness of various groups of NPCs and finds the best possible layout for where they all should live. It internally uses [Dijkstra](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm) to do so.

The `in` file contains [this table](https://terraria.gamepedia.com/index.php?title=NPCs&action=edit&section=11) from Terraria's Wiki.

The `out` file contains all of the resulting layouts.
