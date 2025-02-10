from pieces.rook import rook
from pieces.bishop import bishop

class queen(bishop, rook):
    # a queen is a combination of a bishop and a rook
    def __init__(self, color, position):
        """ 
        Initializes a queen object.
        Args:
            color (str): the color of the queen, either 'white' or 'black'.
            position (str): the position of the queen on the board, a string of length 2.
        """
        self.color = color
        self.position = position
        self.reachable_squares = []

    def __repr__(self) -> str:
        if self.color == 'white':
            return 'Q'
        else:
            return 'q'

    def move(self, new_position, game=None):
        """ 
        Checks if the move is legal and updates the queen's position if it is.
        Args:
            new_position (str): the new position of the queen on the board, a string of length 2.
            game (game, optional): not used in this method, but it's here to keep the same method signature as the other pieces.
        """
        if new_position[0] != self.position[0] and new_position[1] != self.position[1] \
            and abs(ord(new_position[0]) - ord(self.position[0])) != abs(int(new_position[1]) - int(self.position[1])):
            raise Exception("Queens can move in straight lines and diagonally")
        self.position = new_position
        
    def update_reachable_squares(self, board):
        """ 
        Updates the reachable squares of the queen using the bishop and rook methods.
        Args:
            board (list): a 2D list representing the board.
        """
        self.reachable_squares = []
        diag_squares = bishop.update_reachable_squares(self, board)
        non_diag_squares = rook.update_reachable_squares(self, board)
        self.reachable_squares = diag_squares + non_diag_squares     

    def get_tup_repr(self):
        """ 
        Returns a tuple representation of the required attributes of the queen object to be used in the 3-fold repetition rule.
        """
        return (self.__class__, self.color)        

