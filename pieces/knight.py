      
class knight:
    def __init__(self, color, position):
        """ 
        Initializes a knight object.
        Args:
            color (str): the color of the knight, either 'white' or 'black'.
            position (str): the position of the knight on the board, a string of length 2.
        """
        self.color = color
        self.position = position
        self.reachable_squares = []

    def __repr__(self) -> str:
        if self.color == 'white':
            return 'N'
        else:
            return 'n'

    def move(self, new_position, game=None):
        """ 
        Checks if the move is legal and updates the knight's position if it is.
        Args:
            new_position (str): the new position of the knight on the board, a string of length 2.
            game (game, optional): not used in this method, but it's here to keep the same method signature as the other pieces.
        """
        if abs(ord(new_position[0]) - ord(self.position[0])) == 2 and abs(ord(new_position[1]) - ord(self.position[1])) == 1:
            self.position = new_position
        elif abs(ord(new_position[0]) - ord(self.position[0])) == 1 and abs(ord(new_position[1]) - ord(self.position[1])) == 2:
            self.position = new_position
        else:
            raise Exception("Knights move in an L shape")
        
    def update_reachable_squares(self, board):
        """ 
        Updates the reachable squares of the knight.
        Args:
            board (list): a 2D list representing the board.
        """
        self.reachable_squares = []
        piece_col = ord(self.position[0]) - 97 # 0,1,...,7
        piece_row = int(self.position[1]) - 1 # 0,1,...,7
        eight_squares = [(piece_row + 2, piece_col + 1), (piece_row + 2, piece_col - 1), (piece_row - 2, piece_col + 1), (piece_row - 2, piece_col - 1), 
                         (piece_row + 1, piece_col + 2), (piece_row + 1, piece_col - 2), (piece_row - 1, piece_col + 2), (piece_row - 1, piece_col - 2)]
        for square in eight_squares:
            if 0 <= square[0] <= 7 and 0 <= square[1] <= 7:
                square_piece = board[square[0]][square[1]]
                if square_piece is None or square_piece.color != self.color:
                    self.reachable_squares.append(square)
                    
    def get_tup_repr(self):
        """ 
        Returns a tuple representation of the required attributes of the knight object to be used in the 3-fold repetition rule.
        """
        return (self.__class__, self.color)
 