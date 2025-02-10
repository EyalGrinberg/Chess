class rook:
    def __init__(self, color, position, has_not_moved=True, has_castled=False):
        """ 
        Initializes a rook object.
        Args:
            color (str): the color of the rook, either 'white' or 'black'.
            position (str): the position of the rook on the board, a string of length 2.
            has_not_moved (bool): a flag to indicate if the rook has moved (a condition for castling).
            has_castled (bool): a flag to indicate if the rook has castled.
        """
        self.color = color
        self.position = position
        self.has_not_moved = has_not_moved 
        self.has_castled = has_castled
        self.reachable_squares = []

    def __repr__(self) -> str:
        if self.color == 'white':
            return 'R'
        else:
            return 'r'

    def move(self, new_position, game=None):
        """ 
        Checks if the move is legal and updates the rook's position if it is.
        Args:
            new_position (str): the new position of the rook on the board, a string of length 2.
            game (game, optional): not used in this method, but it's here to keep the same method signature as the other pieces.
        """
        if new_position[0] != self.position[0] and new_position[1] != self.position[1]:
            raise Exception("Rooks can only move in straight lines")
        self.position = new_position 
        self.has_not_moved = False # the rook can't castle anymore after it moved

    def reachable_squares_per_direction(self, board, squares_range, row, col, iterate_cols):
        """ 
        Iterates over the squares in a certain direction and updates the reachable squares of the rook.
        Args:
            board (list): a 2D list representing the board.
            squares_range (range): a range object representing the squares to iterate over.
            row (int): the row index of the rook on the board.
            col (int): the column index of the rook on the board.
            iterate_cols (bool): a flag to indicate if the iteration is over the columns or the rows.
        """
        for i in squares_range:
            if iterate_cols:
                square = board[row][i]
            else:
                square = board[i][col]
            # check if there's a piece of the same color in the way
            if square is not None:
                if square.color == self.color:
                    break
                else: # add the last square that can be reached if the Rook captures a piece of the opposite color
                    if iterate_cols:
                        self.reachable_squares.append((row, i))
                    else:
                        self.reachable_squares.append((i, col))
                    break
            else: # add the square if it's empty
                if iterate_cols:
                    self.reachable_squares.append((row, i))
                else:
                    self.reachable_squares.append((i, col))
    
    def update_reachable_squares(self, board):
        """ 
        Updates the reachable squares of the rook.
        Args:
            board (list): a 2D list representing the board.
        Returns:
            The reachable squares of the rook (used for the queen reachable squares calculation).
        """
        self.reachable_squares = []
        piece_col = ord(self.position[0]) - 97 # 0,1,...,7
        piece_row = int(self.position[1]) - 1 # 0,1,...,7
        # check the squares to the right
        if piece_col < 7:
            self.reachable_squares_per_direction(board, range(piece_col + 1, 8), piece_row, piece_col, True)
        # check the squares to the left
        if piece_col > 0:
            self.reachable_squares_per_direction(board, range(piece_col - 1, -1, -1), piece_row, piece_col, True)
        # check the squares below
        if piece_row < 7:
            self.reachable_squares_per_direction(board, range(piece_row + 1, 8), piece_row, piece_col, False)
        # check the squares above
        if piece_row > 0:
            self.reachable_squares_per_direction(board, range(piece_row - 1, -1, -1), piece_row, piece_col, False)         
        # usually there's no need to return the reachable_squares, except for the rook and bishop since the queen inherits from them.   
        return self.reachable_squares         
    
    def get_tup_repr(self):
        """ 
        Returns a tuple representation of the required attributes of the rook object to be used in the 3-fold repetition rule.
        """
        return (self.__class__, self.color, self.has_castled)                              
 