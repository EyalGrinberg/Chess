# Chess Game cmd version

## Overview

This project is a chess game implemented in Python. <br/>
The game allows two players to play against each other through the command line. <br/>
It supports all standard chess rules.

---

## How to Play

Players take turns inputting their moves via the command line. <br/>
Below are the supported legal input types:

1. **Regular Move**: Input of 4 characters.

   - The first two characters represent the origin square.
   - The last two characters represent the target square.
   - The first character of each square is a letter in `a`-`h`, representing the column (from left to right).
   - The second character is an integer in `1`-`8`, representing the row (from bottom to top of the board).
   - Example: `e2e4` moves a piece from e2 to e4.

2. **Promotion Move**: Input of 5 characters.

   - The first four characters are the same as a regular move.
   - The fifth character specifies the promotion piece:
     - `Q` for Queen
     - `R` for Rook
     - `B` for Bishop
     - `N` for Knight
   - Example: `e7e8Q` promotes a pawn to a queen.

3. **Castling**:

   - Short castling: `O-O`
   - Long castling: `O-O-O`

4. **Non-Chess Moves**:

   - **Resignation**: Input `resign` to forfeit the game.
   - **Draw Offer**:
     - Input `draw?` to offer a draw.
     - Opponent responds with `Y` (yes) or `N` (no).
     - If rejected, the player must input another move.
   - **Exit Game**: Input `exit` to end the program.

---

## General Design

- **Classes**:

  - Each chess piece (e.g., `Pawn`, `Rook`, `King`) has its own class with specific attributes and methods.
  - The `Game` class manages the game state, including the board matrix, move history, rules enforcement etc.

- **Game Flow**:

  - The board state is printed each turn, showing white pieces at the bottom and black pieces at the top when the game is in the starting position.
  - If an invalid input is provided, a suitable exception is raised, and the player can retry.
  - When the game concludes (win, draw, or resignation), a relevant message is printed before exiting the program.

---

## Draw Conditions

The program supports all standard chess draw conditions:

1. **Draw Offer Accepted**: Both players agree to a draw.
2. **Insufficient Material**: Not enough material to deliver checkmate.
3. **Stalemate**: No legal moves, and the current player is not in check.
4. **Threefold Repetition**: The same board position occurs three times. Two positions are by definition "the same" if the same types of pieces occupy the same squares, the same player has the move, the remaining castling rights are the same and the possibility to capture en passant is the same.
5. **50-Move Rule**: 50 consecutive moves are made without a pawn move or a capture.

---

## Playing Options

The game provides two ways to play:

1. **Regular Game**:

   - Start from the initial chess position.
   - Call the `play_game()` function without arguments.

2. **Custom Game Position**:

   - Play from a specific position (useful for testing).
   - Call `play_game()` with the following arguments:
     - `chess_game`: An instance of the `Game` class.
     - `pieces`: A set of `Piece` objects (e.g., pawns, knights) placed in desired positions.
     - `testing_specific_position`: Set to `True`.

---

## Example Usage

1. **Starting a New Game**:

```python
from chess_game import play_game

play_game()
```

2. **Starting from a Specific Position**:

```python
from chess_game import game, rook, king, pawn, play_game

# create a game instance. possible to initialize certain attributes as desired.
chess_game = game()

# Define custom pieces
pieces = {
    king('white', 'e1', has_castled=True),
    king('black', 'e8'),
    pawn('white', 'e2'),
    rook('black', 'a8')
}

# Play from custom position
play_game(chess_game=chess_game, pieces=pieces, testing_specific_position=True)
```



---

Enjoy playing!

