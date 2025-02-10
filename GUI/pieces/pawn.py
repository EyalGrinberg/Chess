class pawn: 
    def __init__(self, color, position):
        """ 
        Initializes a pawn object.
        Args:
            color (str): the color of the pawn, either 'white' or 'black'.
            position (str): the position of the pawn on the board, a string of length 2.    
        """
        self.color = color
        self.position = position
        self.two_squares = False # turns on only once in the game when a pawn is moving 2 squares forward and turns off the move after it.
        self.is_en_passant_capture = False # this flag indicates if a capture of the form "f5e6" is a regular capture or an en passant capture.
        self.is_capture = False # this flag indicates if the move is a capture move.
        self.can_be_captured_en_passant = False # this flag indicates if the pawn can be captured en passant. 
        # used for the 3-fold repetition rule which requires that two positions are the same iff the en passant situation is the same for all pawns.
        self.reachable_squares = [] # squares that the pawn can capture or threat (not including the forward squares).

    def __repr__(self) -> str:
        if self.color == 'white':
            return 'P'
        else:
            return 'p'
            
    def move(self, new_position, game):
        """
        Checks if the move is legal and updates the pawn's position if it is.
        Args:
            new_position (str): the new position of the pawn on the board, a string of length 2.
            game (game, optional): an instance of a game class. This function uses methods and attributes of the game class, instead of inheritance because a pawn 'is-not-a' game.
        """
        self.is_en_passant_capture = False # turn the en passant flag off
        self.is_capture = False # turn the capture flag off
        self.two_squares = False
        # check if it's a capture move
        if abs(ord(new_position[0]) - ord(self.position[0])) == 1:
            if int(new_position[1]) - int(self.position[1]) == 1 and game.player_turn == 0 or \
                int(new_position[1]) - int(self.position[1]) == -1 and game.player_turn == 1:
                    self.is_capture = True
                    self.capture(new_position, game)
            else:
                raise Exception("Pawns cannot move that way.")
        # regular move
        if new_position[0] != self.position[0] or self.color == 'white' and int(self.position[1]) > int(new_position[1]) or self.color == 'black' and int(self.position[1]) < int(new_position[1]):
            raise Exception("Pawns can only move forward.")
        if abs(int(new_position[1]) - int(self.position[1])) > 2:
            raise Exception("Pawns can't move more than 2 squares.")
        if abs(int(new_position[1]) - int(self.position[1])) == 2:
            if self.position[1] != '2' and self.color == 'white' or self.position[1] != '7' and self.color == 'black':
                raise Exception("Pawns can move 2 squares only from their opening position")
        new_position_as_tup = game.sqaure_conversion_to_indices(new_position)
        # check if the pawn is blocked by another piece
        pawn_forward_reachable = game.get_pawn_forward_reachable_squares(self)
        if new_position_as_tup not in pawn_forward_reachable and self.position[0] == new_position[0] and not self.is_capture:
            raise Exception("That pawn is blocked by another piece.")   
        # check if it's a 2 squares move
        if self.color == 'white' and self.position[1] == '2' and new_position[1] == '4':
            self.two_squares = True 
        if self.color == 'black' and self.position[1] == '7' and new_position[1] == '5':
            self.two_squares = True
        # update the pawn's position if the move is legal
        self.position = new_position 
        
    def capture(self, new_position, game):     
        """
        Captures a piece on the board by a pawn.
        Args:
            new_position (str): the position of the piece to capture on the board, a string of length 2.
            game (game): an instance of a game class.        
        """ 
        # check if it's an en passant move
        new_pos_col = ord(new_position[0]) - 97
        for tup in ((0, 4, '6'), (1, 3, '3')):
            if game.player_turn == tup[0]: # white takes black's pawn en passant
                piece_to_capture = game.board[tup[1]][new_pos_col]
                if piece_to_capture is not None:
                    if int(self.position[1]) == tup[1] + 1 and piece_to_capture.__class__ == pawn and piece_to_capture.two_squares == True \
                        and game.last_piece_moved == piece_to_capture and new_position[0] == piece_to_capture.position[0] and new_position[1] == tup[2]:
                            self.is_en_passant_capture = True
                            self.en_passant(new_position, game)                        
        # if it is not an en passant capture it's a regular capture
        if self.is_en_passant_capture == False:
            target_square_indices = game.sqaure_conversion_to_indices(new_position) 
            target_sqaure_piece = game.board[target_square_indices[0]][target_square_indices[1]]
            if target_sqaure_piece is None:
                raise Exception("There is no piece to capture at this square.")
        # update the position of the pawn after the capture
        self.position = new_position          

    def en_passant(self, new_position, game):
        """ 
        Update the board after the en passant move, the 'move_piece' method updates everything except the opponent's pawn being taken.
        Args:
            new_position (str): the position of the piece to capture on the board, a string of length 2.
            game (game): an instance of a game class.
        """
        new_pos_col = ord(new_position[0]) - 97
        if game.player_turn == 0:
            game.board[4][new_pos_col] = None
        else:
            game.board[3][new_pos_col] = None
        
    def update_reachable_squares(self, board):
        """ 
        Updates the reachable squares of the pawn. 
        By reachable squares I mean the squares that the pawn can capture or threat (not including the forward squares).
        Args:
            board (list): a 2D list representing the board.
        """
        self.reachable_squares = []
        piece_col = ord(self.position[0]) - 97 # 0,1,...,7
        piece_row = int(self.position[1]) - 1 # 0,1,...,7
        if self.color == 'white':
            if piece_row < 7:
                if piece_col > 0:
                    # check if there is a piece to capture to the left
                    if board[piece_row + 1][piece_col - 1] is not None and board[piece_row + 1][piece_col - 1].color == 'black':
                        self.reachable_squares.append((piece_row + 1, piece_col - 1))
                if piece_col < 7:
                    # check if there is a piece to capture to the right
                    if board[piece_row + 1][piece_col + 1] is not None and board[piece_row + 1][piece_col + 1].color == 'black':
                        self.reachable_squares.append((piece_row + 1, piece_col + 1))
        else:
            if piece_row > 0:
                if piece_col > 0:
                    if board[piece_row - 1][piece_col - 1] is not None and board[piece_row - 1][piece_col - 1].color == 'white':
                        self.reachable_squares.append((piece_row - 1, piece_col - 1))
                if piece_col < 7:
                    if board[piece_row - 1][piece_col + 1] is not None and board[piece_row - 1][piece_col + 1].color == 'white':
                        self.reachable_squares.append((piece_row - 1, piece_col + 1))

    def get_tup_repr(self):
        """ 
        Returns a tuple representation of the required attributes of the pawn object to be used in the 3-fold repetition rule.
        """
        return (self.__class__, self.color, self.can_be_captured_en_passant)
