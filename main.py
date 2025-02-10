import tkinter as tk
from game import game
from gui import ChessGUI

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Chess Game")
    chess_game = game()
    app = ChessGUI(root, chess_game)
    root.mainloop()
