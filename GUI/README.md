# Chess Game GUI Version

## Overview

This project is a graphical user interface (GUI) implementation of a chess game built using Python and Tkinter. It allows two players to play chess against each other in an interactive, visually appealing environment.

The game supports all standard chess rules.

## How to Play

Players take turns interacting with the board using their mouse.

### Move Instructions

- **Regular Move:** Click on the piece you want to move, then click on the destination square.
- **Pawn Promotion:** If a pawn reaches the last row, a dialog will prompt the player to choose a promotion piece (Queen, Rook, Bishop, or Knight).
- **Castling:** Click on the king, then click two squares from the king towards the rook that you want to castle with. <br/>
  For the white player it would be two squares to the right for short castling or two squares to the left for long castling.

### Non-Chess Moves

- **Resignation:** Click the "Resign" button to forfeit the game.
- **Draw Offer:** Click the "Offer Draw" button to propose a draw.
- **Reset Game:** Click the "Reset Game" button to restart the game.

### Draw Conditions 

The program supports all standard chess draw conditions:

1. **Draw Offer Accepted**: Both players agree to a draw.
2. **Insufficient Material**: Not enough material to deliver checkmate.
3. **Stalemate**: No legal moves, and the current player is not in check.
4. **Threefold Repetition**: The same board position occurs three times. Two positions are by definition "the same" if the same types of pieces occupy the same squares, the same player has the move, the remaining castling rights are the same and the possibility to capture en passant is the same.
5. **50-Move Rule**: 50 consecutive moves are made without a pawn move or a capture.


## Project Structure

```
GUI Chess Game
├── main.py         # Entry point for the game execution
├── gui.py          # GUI logic and user interaction handling
├── game.py         # Game logic and rule enforcement
├── pieces/         # Contaians individual piece classes (Pawn, Rook, Knight, etc.)
└── images/         # Images for chess pieces
```

## Instructions to Run

1. Clone the repository from GitHub.
2. Ensure you have Python installed (preferably version 3.7 or higher).
3. Install the required libraries using:
   ```bash
   pip install Pillow
   ```
4. Run the game using the following command:
   ```bash
   python main.py
   ```

## Game Flow

1. The game starts with white making the first move.
2. Players alternate turns by interacting with the board.
3. For any invalid move a relevant message will be displayed and the player will be able to try and play a legal move instead.
4. The game continues until checkmate, draw, or resignation.
5. The GUI will display messages for game-ending conditions.

## Design and Class Structure

### Classes

- **Game:** Manages the game state, including the board matrix, move history, and rules enforcement.
- **Piece Classes:** Each chess piece (Pawn, Rook, Knight, Bishop, Queen, King) has its own class with specific movement rules.
- **ChessGUI:** Handles the graphical interface, board display, and user interactions.

## Key Features

- **Interactive GUI:** Click-based gameplay for intuitive moves.
- **Standard Chess Rules:** Supports all legal chess moves.
- **Dynamic Board Updates:** Real-time updates to the board state.
- **Game Condition Handling:** Checkmate, stalemate, threefold repetition, 50-move rule, and insufficient material detection.

## Example Usage

### Starting a New Game

Simply run the following command to launch the GUI chess game:

```bash
python main.py
```

Enjoy playing chess with a friend in this fully interactive GUI version!
