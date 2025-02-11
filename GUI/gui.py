import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk  # For handling images
from game import game  # Assuming the `game` module is already defined and imported

class ChessGUI:
    def __init__(self, root, chess_game):
        self.root = root
        self.game = chess_game
        self.color_dict = {0: 'White', 1: 'Black'}
        self.piece_images = self.load_piece_images()
        self.emptyimage = self.load_empty_image()  # Initialize an empty list to store image references
        self.selected_square = None
        self.create_widgets()

    def load_empty_image(self):
        emptyimage = Image.open('./images/empty.png')
        emptyimage = emptyimage.resize((32, 32), Image.LANCZOS)  # Resize to fit buttons
        image = ImageTk.PhotoImage(emptyimage)
        return image  
        
    def load_piece_images(self):
        piece_map = {
            "K": "white-king.png", "Q": "white-queen.png", "R": "white-rook.png", "B": "white-bishop.png",
            "N": "white-knight.png", "P": "white-pawn.png", "k": "black-king.png", "q": "black-queen.png",
            "r": "black-rook.png", "b": "black-bishop.png", "n": "black-knight.png", "p": "black-pawn.png"
        }
        images = {}
        for piece, file_name in piece_map.items():
            try:
                image = Image.open(f'./images/{file_name}')
                image = image.resize((32, 32), Image.LANCZOS)
                images[piece] = ImageTk.PhotoImage(image)
            except FileNotFoundError:
                print(f"Image file not found: {file_name}")
                images[piece] = None
        return images

    def create_widgets(self):
        self.board_frame = tk.Frame(self.root)
        self.board_frame.grid(row=0, column=0, padx=10, pady=10)

        self.board_squares = []
        for row in range(8):
            row_squares = []
            for col in range(8):
                color = "#D2B48C" if (row + col) % 2 == 0 else "#8B4513"
                button = tk.Button(
                    self.board_frame, bg=color, width=1, height=1,
                    command=lambda r=row, c=col: self.handle_click(r, c)
                )
                button.grid(row=7-row, column=col)  # Reverse row for correct visualization
                row_squares.append(button)
            self.board_squares.append(row_squares)

        self.info_label = tk.Label(self.root, text="White's turn", font=("Arial", 14))
        self.info_label.grid(row=1, column=0, pady=5)

        self.controls_frame = tk.Frame(self.root)
        self.controls_frame.grid(row=2, column=0, pady=10)

        self.reset_button = tk.Button(self.controls_frame, text="Reset Game", command=self.reset_game)
        self.reset_button.grid(row=0, column=0, padx=5)

        self.resign_button = tk.Button(self.controls_frame, text="Resign", command=self.resign_game)
        self.resign_button.grid(row=0, column=1, padx=5)

        self.draw_button = tk.Button(self.controls_frame, text="Offer Draw", command=self.offer_draw)
        self.draw_button.grid(row=0, column=2, padx=5)

        self.update_board()

    def update_board(self):
        for row in range(8):
            for col in range(8):
                piece = self.game.board[row][col]
                if piece:
                    image = self.piece_images.get(str(piece), None)
                    self.board_squares[row][col].config(image=image, compound="center", width=32, height=32)
                else:
                    self.board_squares[row][col].config(image=self.emptyimage, text="", compound="center", width=32, height=32)

    def handle_click(self, row, col):
        if not self.selected_square:
            self.selected_square = (row, col)
        else:
            from_square = self.selected_square
            to_square = (row, col)
            move = self.game.square_conversion_from_indices_to_str(from_square) + \
                   self.game.square_conversion_from_indices_to_str(to_square)
            self.selected_square = None

            # Handle castling move detection
            if self.is_castling_move(from_square, to_square):
                move = self.get_castling_command(from_square, to_square)

            # Handle promotion after the move if detected
            if self.detect_promotion(from_square, to_square):
                move = self.handle_promotion(from_square, to_square)

            self.game.update_reachable_squares_for_all_pieces()  # Update reachable squares before making a move
            try:
                self.game = self.game.move_piece(move)
                self.update_board()

                # it's important to check for the threefold repetition draw before checking for checkmate because the game state will change in case of a mate
                if self.game.check_three_fold_repetition_draw():
                    messagebox.showinfo("Game Over", "Draw by threefold repetition!")
                    self.reset_game()

                if self.game.is_mate:
                    messagebox.showinfo("Game Over", f"Checkmate! {self.color_dict[1 - self.game.player_turn]} wins!")
                    self.reset_game()
                else:
                    self.info_label.config(text=f"{self.color_dict[self.game.player_turn]}'s turn")

                # Check for draw conditions
                if self.game.check_stalemate_draw(self.get_stalemated_king()):
                    messagebox.showinfo("Game Over", "Draw by stalemate!")
                    self.reset_game()
                
                elif self.game.check_insufficient_material_draw():
                    messagebox.showinfo("Game Over", "Draw by insufficient material!")
                    self.reset_game()

                elif self.game.move_cnt_50 == 100:
                    messagebox.showinfo("Game Over", "Draw by the 50-move rule!")
                    self.reset_game()

            except Exception as e:
                messagebox.showerror("Invalid Move", str(e))

    def is_castling_move(self, from_square, to_square):
        king_row, king_col = from_square
        if self.game.player_turn == 0 and king_row == 7 or self.game.player_turn == 1 and king_row == 0:
            return False
        to_row, to_col = to_square
        if self.game.board[king_row][king_col].__class__.__name__ == 'king' and abs(king_col - to_col) == 2 and king_row == to_row:
            return True
        return False

    def get_castling_command(self, from_square, to_square):
        king_row, king_col = from_square
        to_col = to_square[1]
        if to_col == king_col + 2:
            return 'O-O'
        elif to_col == king_col - 2:
            return 'O-O-O'

    def get_stalemated_king(self):
        if self.game.player_turn == 0:
            return self.game.board[self.game.kings_positions[0][0]][self.game.kings_positions[0][1]]
        return self.game.board[self.game.kings_positions[1][0]][self.game.kings_positions[1][1]]

    def reset_game(self):
        self.game = game()
        self.update_board()
        self.info_label.config(text="White's turn")

    def resign_game(self):
        winner = self.color_dict[1 - self.game.player_turn]
        messagebox.showinfo("Game Over", f"{winner} wins by resignation!")
        self.reset_game()

    def offer_draw(self):
        response = messagebox.askyesno("Draw Offer", f"{self.color_dict[1 - self.game.player_turn]}: Accept draw?")
        if response:
            messagebox.showinfo("Game Over", "Game drawn by agreement!")
            self.reset_game()

    def show_promotion_dialog(self):
        promotion_piece = simpledialog.askstring("Pawn Promotion", "Choose promotion piece (Q/R/B/N):", parent=self.root)
        if promotion_piece not in ['Q', 'R', 'B', 'N']:
            messagebox.showerror("Invalid Choice", "Please choose a valid promotion piece (Q, R, B, N).")
            return self.show_promotion_dialog()
        return promotion_piece

    def handle_promotion(self, from_square, to_square):
        promotion_piece = self.show_promotion_dialog()
        move_base = self.game.square_conversion_from_indices_to_str(from_square) + \
                    self.game.square_conversion_from_indices_to_str(to_square) + promotion_piece
        return move_base

    def detect_promotion(self, from_square, to_square):
        to_row = to_square[0]
        pawn = self.game.board[from_square[0]][from_square[1]]  # Get the pawn piece
        if pawn and pawn.__class__.__name__ == 'pawn':
            if (pawn.color == 'white' and to_row == 7) or (pawn.color == 'black' and to_row == 0):
                return True
        return False