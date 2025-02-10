       
class bishop:
    def __init__(self, color, position):
        """ 
        Initializes a bishop object.
        Args:
            color (str): the color of the bishop, either 'white' or 'black'.
            position (str): the position of the bishop on the board, a string of length 2.
        """
        self.color = color
        self.position = position
        self.reachable_squares = []

    def __repr__(self) -> str:
        if self.color == 'white':
            return 'B'
        else:
            return 'b'

    def move(self, new_position, game=None):
        """ 
        Checks if the move is legal and updates the bishop's position if it is.
        Args:
            new_position (str): the new position of the bishop on the board, a string of length 2.
            game (game, optional): not used in this method, but it's here to keep the same method signature as the other pieces.
        """
        if abs(ord(new_position[0]) - ord(self.position[0])) != abs(int(new_position[1]) - int(self.position[1])):
            raise Exception("Bishops move diagonally")
        self.position = new_position
    
    def reachable_squares_per_direction_b(self, board, squares_range, row, col, iterate_up, iterate_right):
        """ 
        Iterates over the squares in a certain direction and updates the reachable squares of the bishop.
        Args:
            board (list): a 2D list representing the board.
            squares_range (range): a range object representing the squares to iterate over.
            row (int): the row index of the bishop on the board.
            col (int): the column index of the bishop on the board.
            iterate_up (bool): a flag to indicate if the iteration is up or down.
            iterate_right (bool): a flag to indicate if the iteration is right or left.
        """
        for i in squares_range:
            if iterate_up and iterate_right: # up and right
                square = board[row + i][col + i]
            elif iterate_up and not iterate_right: # up and left
                square = board[row + i][col - i]
            elif not iterate_up and iterate_right: # down and right
                square = board[row - i][col + i]
            else: # down and left
                square = board[row - i][col - i]
            # check if there's a piece of the same color in the way
            if square is not None:
                if square.color == self.color:
                    break
                else: # add the capturing square 
                    if iterate_up and iterate_right:
                        self.reachable_squares.append((row + i, col + i))
                    elif iterate_up and not iterate_right:
                        self.reachable_squares.append((row + i, col - i))
                    elif not iterate_up and iterate_right:
                        self.reachable_squares.append((row - i, col + i))
                    else:
                        self.reachable_squares.append((row - i, col - i))
                    break
            else: # add the empty square
                if iterate_up and iterate_right:
                    self.reachable_squares.append((row + i, col + i))
                elif iterate_up and not iterate_right:
                    self.reachable_squares.append((row + i, col - i))
                elif not iterate_up and iterate_right:
                    self.reachable_squares.append((row - i, col + i))
                else:
                    self.reachable_squares.append((row - i, col - i))
    
    def update_reachable_squares(self, board):
        """ 
        Updates the reachable squares of the bishop.
        Args:
            board (list): a 2D list representing the board.
        Returns:
            The reachable squares of the bishop (used for the queen reachable squares calculation).
        """
        self.reachable_squares = []
        piece_col = ord(self.position[0]) - 97 # 0,1,...,7
        piece_row = int(self.position[1]) - 1 # 0,1,...,7
        if piece_col < 7 and piece_row < 7:
            # check the squares to the right and up
            self.reachable_squares_per_direction_b(board, range(1, min(8 - piece_row, 8 - piece_col)), piece_row, piece_col, True, True)
        if piece_col > 0 and piece_row < 7:
            # check the squares to the left and up
            self.reachable_squares_per_direction_b(board, range(1, min(8 - piece_row, piece_col + 1)), piece_row, piece_col, True, False)
        if piece_col < 7 and piece_row > 0:
            # check the squares to the right and down
            self.reachable_squares_per_direction_b(board, range(1, min(piece_row + 1, 8 - piece_col)), piece_row, piece_col, False, True)
        if piece_col > 0 and piece_row > 0:
            # check the squares to the left and down
            self.reachable_squares_per_direction_b(board, range(1, min(piece_row + 1, piece_col + 1)), piece_row, piece_col, False, False)
        return self.reachable_squares                   
        
    def get_tup_repr(self):
        """ 
        Returns a tuple representation of the required attributes of the bishop object to be used in the 3-fold repetition rule.
        """
        return (self.__class__, self.color)
