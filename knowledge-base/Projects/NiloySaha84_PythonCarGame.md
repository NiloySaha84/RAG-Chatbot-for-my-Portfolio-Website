# Pygame Car Racing Game

This project is a simple 2D car racing game built using Python and the Pygame library. The player controls a car and navigates through lanes, avoiding collisions with other vehicles while trying to achieve a high score. The game gets progressively harder as the speed of the vehicles increases.

## Features

- **Player-controlled car**: Move the car left or right between lanes using the arrow keys.
- **Enemy cars**: Other vehicles spawn randomly in the lanes and move downwards. Avoid collisions with them.
- **Increasing difficulty**: As the player progresses, the speed of the enemy cars increases.
- **Score system**: The player earns points for successfully avoiding enemy cars, and the score is displayed in-game.
- **Game over animation**: If the player collides with another vehicle, a crash explosion image is displayed and the game ends.

## Controls

- **Left arrow** (`←`) - Move the car left to the next lane.
- **Right arrow** (`→`) - Move the car right to the next lane.
- **Escape** (`ESC`) - Quit the game.

## Setup and Requirements

### Prerequisites

Make sure you have Python installed on your system. You also need to install the Pygame library.

To install Pygame, run:
```bash
pip install pygame
