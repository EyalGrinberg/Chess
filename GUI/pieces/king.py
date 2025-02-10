
class king:
    def __init__(self, color, position, has_not_moved=True, has_castled=False):
        """ 
        Initializes a king object.
        Args:
            color (str): the color of the king, either 'white' or 'black'.
            position (str): the position of the king on the board, a string of length 2.
            has_not_moved (bool): a flag to indicate if the king hasn't moved (a condition for castling).
            has_castled (bool): a flag to indicate if the king has castled (used for the testing function).
        """
        self.color = color
        self.position = position
        self.has_not_moved = has_not_moved
        self.has_castled = has_castled
        self.reachable_squares = [] # including threatened squares
        self.is_checked = False

    def __repr__(self) -> str:
        if self.color == 'white':
            return 'K'
        else:
            return 'k'


    def move(self, new_position, game=None):
        """ 
        Checks if the move is legal and updates the king's position if it is.
        Args:
            new_position (str): the new position of the king on the board, a string of length 2.
            game (game, optional): an instance of a game class. This function uses a method of the game class, instead of inheritance because a king 'is-not-a' game.
        """
        if abs(ord(new_position[0]) - ord(self.position[0])) > 1 or abs(int(new_position[1]) - int(self.position[1])) > 1:
            raise Exception("Kings can only move one square in any direction")
        if game.sqaure_conversion_to_indices(new_position) not in self.reachable_squares:
            raise Exception("This square is threatened, you can't move your king to this square.")
        self.position = new_position
        self.has_not_moved = False    
        
    def squares_threat_test(self, board, squares, king_square):       
        """
        Checks if the squares in the list are threatened by the opponent pieces.
        Args:
            board (list): a 2D list representing the board.
            squares (list): a list of tuples representing the squares to check.
            king_square (tuple): a tuple representing the king's position on the board.
        Returns:
            A tuple containing the squares that are not threatened by the opponent pieces and the piece threatening the king (if the king is threatened).
        """
        self.is_checked = False
        unthreatened_inboard_squares = squares.copy()
        king_threatening_piece = None
        for tested_square in squares:             
            for row in board:
                for square in row:
                    if square is not None and square.color != self.color: 
                        # check if the opponent piece located in square is threatening the tested square 
                        if tested_square in square.reachable_squares: 
                            if tested_square in unthreatened_inboard_squares:
                                unthreatened_inboard_squares.remove(tested_square)
                        if king_square in square.reachable_squares:
                            self.is_checked = True
                            king_threatening_piece = square
        return unthreatened_inboard_squares, king_threatening_piece

    def update_reachable_squares(self, board):
        """ 
        Updates the reachable squares of the king.
        Args:
            board (list): a 2D list representing the board.
        """
        self.reachable_squares = []
        piece_col = ord(self.position[0]) - 97 # 0,1,...,7
        piece_row = int(self.position[1]) - 1 # 0,1,...,7
        # the king's reachable squares are the 8 squares around it.
        eight_squares = [(piece_row + 1, piece_col), (piece_row - 1, piece_col), (piece_row, piece_col + 1), (piece_row, piece_col - 1),
                         (piece_row + 1, piece_col + 1), (piece_row + 1, piece_col - 1), (piece_row - 1, piece_col + 1), (piece_row - 1, piece_col - 1)]
        # remove the squares that are not on the board
        in_board_squares = [(row, col) for row, col in eight_squares if 0 <= row <= 7 and 0 <= col <= 7]
        in_board_squares_copy = in_board_squares.copy()
        for square in in_board_squares_copy:
            square_piece = board[square[0]][square[1]]
            if square_piece is not None and square_piece.color == self.color:
                # remove the square if it's occupied by a piece of the same color
                in_board_squares.remove(square)
        # remove the squares that are threatened by the opponent pieces
        self.reachable_squares = self.squares_threat_test(board, in_board_squares, (piece_row, piece_col))[0]  
        
    def get_tup_repr(self):
        """ 
        Returns a tuple representation of the required attributes of the king object to be used in the 3-fold repetition rule.
        """
        return (self.__class__, self.color, self.has_castled)

