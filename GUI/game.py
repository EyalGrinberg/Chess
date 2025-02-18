import copy
from pieces.pawn import pawn
from pieces.rook import rook
from pieces.knight import knight
from pieces.bishop import bishop
from pieces.queen import queen
from pieces.king import king

class game:

    def __init__(self, player_turn=0, move_cnt=0, move_cnt_50=0, is_mate=False):
        """
        Initializes the board and other attributes for an initial position of a chess game.
        Args:
            player_turn (int): 0 for white, 1 for black. Default is 0.
            move_cnt (int): the number of moves that have been played so far. Default is 0.
            move_cnt_50 (int): the number of moves played since the last capture or pawn move. Default is 0.
        """
        self.player_turn = player_turn # 0 for white, 1 for black
        self.move_cnt = move_cnt
        self.move_cnt_50 = move_cnt_50 # counts the number of moves played since the last capture or pawn move - used for the 50 moves draw.
        self.pieces_lst = [] # relevant only for insufficient material draw. 
        # will remain empty until move_cnt=30 since this type of draw is relevant only after 30 moves.
        self.last_piece_moved = None # used for checking the en passant case
        self.piece_moved_two_turns_ago = None # used for turning off the two_squares flag in the pawn class only after the opponent's move.
        self.kings_positions = [(0, 4), (7, 4)] # kings' positions, white is first and black is second
        # board initialzation
        self.board = [[None for _ in range(8)] for _ in range(8)]
        # pieces
        for tup in ((0, 'white'), (7, 'black')):
            self.board[tup[0]][0] = rook(tup[1], 'a' + str(tup[0] + 1))
            self.board[tup[0]][1] = knight(tup[1], 'b' + str(tup[0] + 1))
            self.board[tup[0]][2] = bishop(tup[1], 'c' + str(tup[0] + 1))
            self.board[tup[0]][3] = queen(tup[1], 'd' + str(tup[0] + 1))
            self.board[tup[0]][4] = king(tup[1], 'e' + str(tup[0] + 1))
            self.board[tup[0]][5] = bishop(tup[1], 'f' + str(tup[0] + 1))
            self.board[tup[0]][6] = knight(tup[1], 'g' + str(tup[0] + 1))
            self.board[tup[0]][7] = rook(tup[1], 'h' + str(tup[0] + 1))
        # pawns
        for col in range(8):
            # white 
            self.board[1][col] = pawn('white', chr(col + 97) + '2')
            # black 
            self.board[6][col] = pawn('black', chr(col + 97) + '7')
        self.positions_dict = {} # counts occurances of all the positions during a game, used for the 3-fold repetition draw
        # initialize the positions_dict with the initial position
        board_of_tups = copy.deepcopy(self.board)
        for i in range(8):
            for j in range(8):
                if board_of_tups[i][j] is not None:
                    board_of_tups[i][j] = board_of_tups[i][j].get_tup_repr()
        board_as_tup = tuple(tuple(row) for row in board_of_tups)
        self.positions_dict[(board_as_tup, self.player_turn)] = 1
        self.is_mate = is_mate # for GUI purposes
        
    """
    board visualization
[
        [a b c d e f g h]
        
    [8   R N B Q K B N R]]
    [7   P P P P P P P P]]     
    [6                   ]
    [5                   ]
    [4                   ]
    [3                   ]
    [2   P P P P P P P P]]
    [1   R N B Q K B N R]]
                            ]
    """ 
    
    def __repr__(self): 
        """The game is represented by the board matrix which contains the pieces."""
        # for simplicity the board matrix upper left corner is (0,0) and the bottom right corner is (7,7), but when printed it should be reverted.
        return "\n".join([str(row) for row in self.board][::-1])
    
    def sqaure_conversion_to_indices(self, square):
        """
        Converts a square given as a letter and a number to indices in the board matrix,
        also validates the square input.
        Args:
            square (str): a string of length 2, with the first character should be a letter between 'a' and 'h'
            and the second character should be a number between '1' and '8'.
        Returns:
            (int, int): a tuple of two integers representing the indices of the square in the board matrix.
        """
        if len(square) != 2:
            raise Exception("The square should be a string of length 2.")
        conversion_dict = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
        if square[0] not in conversion_dict:
            raise Exception("The first character of the provided square should be a letter between 'a' and 'h'.")
        if square[1] not in '12345678':
            raise Exception("The second character of the provided square should be a number between '1' and '8'.")
        return (int(square[1]) - 1, conversion_dict[square[0]])
    
    def square_conversion_from_indices_to_str(self, square):
        """ 
        Converts a square given as a tuple of indices to a string of length 2.
        The function assumes a legal input (since it's already taken care of and the function isn't used by the user).
        Args:
            square ((int, int)): a tuple of the indices of the square in the board matrix.
        Returns:
            str: a string of length 2 representing the square.
        """
        conversion_dict = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'}
        return conversion_dict[square[1]] + str(square[0] + 1)
    
    def update_reachable_squares_for_all_pieces(self):
        """
        Updates the reachable squares of all the pieces after moving a piece.
        The kings are getting updated last to deal with cases of checks or a mate.
        The function also updates the kings_positions attribute.
        """
        kings = [None] * 2
        for row in self.board:
            for square in row:
                if square is not None and square.__class__ == king:
                    if square.color == 'white':
                        kings[0] = square
                    else:
                        kings[1] = square
                    continue
                elif square is not None:
                    square.update_reachable_squares(self.board)
        # update kings_positions at the end to deal with cases of checks.
        kings[0].update_reachable_squares(self.board)
        kings[1].update_reachable_squares(self.board)
        # update kings_positions
        self.kings_positions = []
        for i in (0, 1):
            self.kings_positions.append(self.sqaure_conversion_to_indices(kings[i].position))
    
    def get_pawn_forward_reachable_squares(self, pawn):
        """
        Computes the forward reachable squares of a pawn.
        Args:
            pawn (pawn): a pawn object
        Returns:
            list of tuples: the pawn's forward reachable squares.
        """
        pawn_col = ord(pawn.position[0]) - 97 # 0,1,...,7
        pawn_row = int(pawn.position[1]) - 1 # 0,1,...,7
        if pawn.color == 'white':
            if pawn_row == 7:
                return [] 
            if pawn_row == 1: # starting position
                if self.board[pawn_row + 1][pawn_col] is None:
                    if self.board[pawn_row + 2][pawn_col] is None: 
                        # the pawn can move 2 squares forward
                        return [(pawn_row + 1, pawn_col), (pawn_row + 2, pawn_col)]
                    # the pawn can move 2 squares forward
                    return [(pawn_row + 1, pawn_col)]
            else: # the pawn moved from it's starting position during the game
                if self.board[pawn_row + 1][pawn_col] is None:
                    return [(pawn_row + 1, pawn_col)]
        else: # black
            if pawn_row == 0:
                return []
            if pawn_row == 6:
                if self.board[pawn_row - 1][pawn_col] is None:
                    if self.board[pawn_row - 2][pawn_col] is None: 
                        return [(pawn_row - 1, pawn_col), (pawn_row - 2, pawn_col)]
                    return [(pawn_row - 1, pawn_col)]
            else:
                if self.board[pawn_row - 1][pawn_col] is None:
                    return [(pawn_row - 1, pawn_col)]
        # the pawn is blocked by another piece and can't move forward
        return [] 
    
    def move_simulation(self, game, cmd): 
        """
        Simulates a move in a given game.
        Args:
            game (game): an instance of a game to simulate a move for.
            cmd (str): a string of length 4 for a regular move or length 5 for a promotion move.
        Returns:
            1 if cmd is a valid move, 0 otherwise
        """
        sim_game = copy.deepcopy(game) # copy the game to not make unwanted updates in case of an invalid move
        try:
            sim_game = sim_game.move_piece(cmd)
            return 1
        except Exception as e:
            return 0 
    
    def test_mate(self, game, threatened_king, king_position):
        """
        Checks if the game provided has a mate position.
        The function is called only twice (once for each color) via the check_king_threat 
        method if the king is being checked after the opponent played a move.
        Args:
            game (game): an instance of game class to check if it is in a mate position. 
                The game is the new_game from the check_king_threat method.
            threatened_king (king): the checked king.
            king_position ((int, int)): the threatened king's position as tuple.
        Returns:
            1 if its a mate and 0 if the check is avoidable.
        """
        # the implementation of the reachable squares updates adds to the king's reachable_squares squares that contain
        # an opponent's pieces that are protected. it is not ideal but I deal with it by simulating what happens if the
        # king captures those pieces, and in that way I know to ignore those so called reachable squares.
        if len(threatened_king.reachable_squares) > 0: # might be legal and also illegal reachable squares, need to ignore the illegal ones.
            for candidate_square in threatened_king.reachable_squares:
                cmd = threatened_king.position + self.square_conversion_from_indices_to_str(candidate_square)
                if self.move_simulation(game, cmd):
                    # if the simulation worked properly, there exists a reachable square that the king can escape to
                    return 0
        # by now we know the king is checked and it can't escape the check, 
        # need to check if there is a piece that can block the check or capture the threatening piece.
        threatening_piece = threatened_king.squares_threat_test(game.board, [king_position], king_position)[1]
        threatening_piece_pos = self.sqaure_conversion_to_indices(threatening_piece.position)
        # if the threatening piece is a pawn or a knight there is no blocking option, only capturing.
        # if it's a queen, bishop or a rook then there is a blocking option in addition to capturing.
        capturing_square = [threatening_piece_pos]
        # blocking_squares are the squares between the threatening piece and the king.
        blocking_squares = []
        if threatening_piece.__class__ in (rook, queen):
            piece_reachable = threatening_piece.reachable_squares
            for i in (0, 1): # 0 for the same row and 1 for the same column.
                if king_position[i] == threatening_piece_pos[i]: 
                    squares = [x for x in piece_reachable if x[i] == king_position[i]]
                    if king_position[1 - i] > threatening_piece_pos[1 - i]: 
                        # need to keep only square to the right of the rook/queen (between the rook/queen and the king)
                        blocking_squares = [x for x in squares if x[1 - i] > threatening_piece_pos[1 - i]]
                    else: # need to keep only square to the left of the rook/queen (between the rook/queen and the king)
                        blocking_squares = [x for x in squares if x[1 - i] < threatening_piece_pos[1 - i]]
        # if the threatening piece is diagonally to the king, blocking squares still won't be initialized.
        if threatening_piece.__class__ in (bishop, queen):
            piece_reachable = threatening_piece.reachable_squares
            if king_position[0] < threatening_piece_pos[0] and king_position[1] < threatening_piece_pos[1]: # king is bottom-left to the piece
                blocking_squares = [x for x in piece_reachable if x[0] < threatening_piece_pos[0] and x[1] < threatening_piece_pos[1]]
            if king_position[0] > threatening_piece_pos[0] and king_position[1] < threatening_piece_pos[1]: # king is upper-left to the piece
                blocking_squares = [x for x in piece_reachable if x[0] > threatening_piece_pos[0] and x[1] < threatening_piece_pos[1]]
            if king_position[0] > threatening_piece_pos[0] and king_position[1] > threatening_piece_pos[1]: # king is upper-right to the piece
                blocking_squares = [x for x in piece_reachable if x[0] > threatening_piece_pos[0] and x[1] > threatening_piece_pos[1]]
            if king_position[0] < threatening_piece_pos[0] and king_position[1] > threatening_piece_pos[1]: # king is bottom-right to the piece
                blocking_squares = [x for x in piece_reachable if x[0] < threatening_piece_pos[0] and x[1] > threatening_piece_pos[1]]
        blocking_squares += capturing_square
        if king_position in blocking_squares:
            blocking_squares.remove(king_position)
        # now need to check if there's a piece of the king's side that can block the check or capture the threatening piece.
        # start with an en passant capture of the threatening piece.
        if threatening_piece.__class__ == pawn:
            en_passant_candidates = []
            for tup in (('white', 3, 'black'), ('black', 4, 'white')):
                if threatening_piece.color == tup[0] and threatening_piece_pos[0] == tup[1] and threatening_piece.two_squares: 
                    # check if there is a pawn that can capture the threatening pawn en passant
                    if threatening_piece_pos[1] > 0:
                        left_square = game.board[threatening_piece_pos[0]][threatening_piece_pos[1] - 1]
                        if left_square is not None and left_square.__class__ == pawn and left_square.color == tup[2]:
                            # append the position as string of length 2 since it will be used to build the cmd for move_simulation
                            en_passant_candidates.append(left_square.position) 
                    if threatening_piece_pos[1] < 7:
                        right_square = game.board[threatening_piece_pos[0]][threatening_piece_pos[1] + 1]
                        if right_square is not None and right_square.__class__ == pawn and right_square.color == tup[2]:
                            en_passant_candidates.append(right_square.position)
            # need to simulate the en passant capture of the threatening pawn since the capturing pawn might be pinned 
            for candidate_square in en_passant_candidates:
                cmd = candidate_square + threatening_piece.position[0]
                if threatening_piece.color == 'white':
                    cmd += '3'
                else:
                    cmd += '6'
                if self.move_simulation(game, cmd):
                    return 0
        # blocking the check
        for row in game.board:
            for square in row:
                if square is not None and square.color == threatened_king.color and square.__class__ != king:
                    # if it's a pawn need to consider both the reachable squares (its capturing options) and the forward squares. 
                    reachable_lst = square.reachable_squares
                    if square.__class__ == pawn:
                        pawn_forward_reachable = game.get_pawn_forward_reachable_squares(square)
                        reachable_lst += pawn_forward_reachable
                    # if square is not a pawn need to consider the reachable squares only.
                    # again, need to simulate the block in case the blocking piece is pinned.
                    for block in blocking_squares:
                        if block in reachable_lst:
                            cmd = square.position + self.square_conversion_from_indices_to_str(block)
                            if self.move_simulation(game, cmd):
                                return 0                         
        # there is no escaping, capturing or blocking option - it's a mate.
        return 1 
                        
    def check_king_threat(self, cmd_input, promotion=False): 
        """
        Performs the move in cases of regular and promotion moves (non castle moves) including verification of the user's input.
        It also checks cases of illegal moves related to the king, mates and pins. 
        And also keeps maintaining the game's and pieces' attributes.
        Args:
            cmd_input (str): the user's input for the move.
            promotion (bool): a flag to indicate that it's a promotion move.
        Returns:
            The game after the move was played if it was a legal move (no exception was raised).
            If it is a mate move it prints the winner's identity and exits the program.
        """
        # general checks
        old_position = cmd_input[:2]
        new_position = cmd_input[2:4]
        old_position_indices = self.sqaure_conversion_to_indices(old_position)
        new_position_indices = self.sqaure_conversion_to_indices(new_position)
        piece = self.board[old_position_indices[0]][old_position_indices[1]]
        if piece is None:
            raise Exception("There is no piece at the input square.")
        if (self.player_turn == 0 and piece.color == 'black') or (self.player_turn == 1 and piece.color == 'white'):
            raise Exception("The chosen piece is not yours.")
        if old_position == new_position:
            raise Exception("The piece is already at the target square.")
        # need to check if the target square is already occupied by another piece,
        # but need to call the 'move' method of the piece first to prevent cases of 'd1f2' for example. 
        target_square = self.board[new_position_indices[0]][new_position_indices[1]] 
        # simulate the move and check its validity, if the move is legal - return the new game after the move was played.
        new_game = copy.deepcopy(self)
        piece = new_game.board[old_position_indices[0]][old_position_indices[1]] # its ok to override the piece since its the same piece anyway.
        if promotion:
            if piece.__class__ != pawn:
                raise Exception("Only pawns can be promoted.")
            promotion_piece = cmd_input[-1]
            if promotion_piece not in ['Q', 'R', 'B', 'N']:
                raise Exception("The promotion piece is not valid.")
            # promotions are only at the last rank of the board.
            if piece.color == 'white' and new_position_indices[0] != 7 or piece.color == 'black' and new_position_indices[0] != 0:
                raise Exception("The pawn can't be promoted at this position.")
            piece.move(new_position, new_game)            
            if target_square is not None and target_square.color == piece.color:
                raise Exception("The target square is already occupied.")
            # create an instance of the promotion piece in the target square
            if promotion_piece == 'Q':
                new_game.board[new_position_indices[0]][new_position_indices[1]] = queen(piece.color, new_position)
            elif promotion_piece == 'R': 
                new_game.board[new_position_indices[0]][new_position_indices[1]] = rook(piece.color, new_position)
            elif promotion_piece == 'B':
                new_game.board[new_position_indices[0]][new_position_indices[1]] = bishop(piece.color, new_position)
            else: # 'N'
                new_game.board[new_position_indices[0]][new_position_indices[1]] = knight(piece.color, new_position)
        else: # regular move
            piece.move(new_position, new_game)
            if target_square is not None and target_square.color == piece.color:
                raise Exception("The target square is already occupied.") 
            # check if there is another piece in the way
            if piece.__class__ != pawn:
                if new_position_indices not in piece.reachable_squares and piece.__class__ != king:
                    raise Exception("There is another piece in the way.")
            new_game.board[new_position_indices[0]][new_position_indices[1]] = piece   
        # these lines should be executed for both promotion and regular move
        new_game.board[old_position_indices[0]][old_position_indices[1]] = None 
        if new_game.last_piece_moved is not None:
            new_game.piece_moved_two_turns_ago = new_game.last_piece_moved   
        new_game.last_piece_moved = piece
        new_game.player_turn = 1 - new_game.player_turn
        new_game.move_cnt += 1
        new_game.update_reachable_squares_for_all_pieces()
        # king safety cases
        white_king_self = self.board[self.kings_positions[0][0]][self.kings_positions[0][1]]
        white_king_new = new_game.board[new_game.kings_positions[0][0]][new_game.kings_positions[0][1]]
        black_king_self = self.board[self.kings_positions[1][0]][self.kings_positions[1][1]]
        black_king_new = new_game.board[new_game.kings_positions[1][0]][new_game.kings_positions[1][1]]
        # check if the player playing is not avoiding being checked
        if white_king_self.is_checked and white_king_new.is_checked or black_king_self.is_checked and black_king_new.is_checked:
            raise Exception("Your king is being checked, you cannot play this move.")
        # check if the moved piece is pinned
        if self.player_turn == 0:
            if white_king_new.is_checked and new_game.last_piece_moved.__class__ != king:
                raise Exception("The chosen piece is pinned.")
        else:
            if black_king_new.is_checked and new_game.last_piece_moved.__class__ != king:
                raise Exception("The chosen piece is pinned.")     
        # check if it's a king move to a threatened square
        if self.player_turn == 0:
            if not white_king_self.is_checked and white_king_new.is_checked and new_game.last_piece_moved.__class__ == king:
                raise Exception("The king can't move to a threatened square.")
        else:
            if not black_king_self.is_checked and black_king_new.is_checked and new_game.last_piece_moved.__class__ == king:
                raise Exception("The king can't move to a threatened square.")
        # if the king is checked, check if its a mate
        if new_game.player_turn == 0 and white_king_new.is_checked:
            # black played a move and checked the white king, need to see if its a mate 
            if self.test_mate(new_game, white_king_new, new_game.kings_positions[0]):
                new_game.is_mate = True
                print(new_game)
                print("Black wins!")
                # exit() for GUI purposes
        if new_game.player_turn == 1 and black_king_new.is_checked:
            if self.test_mate(new_game, black_king_new, new_game.kings_positions[1]):    
                new_game.is_mate = True
                print(new_game)
                print("White wins!")
                # exit() for GUI purposes
        # reset the move_cnt_50 if there was a capture or a pawn move
        if piece.__class__ == pawn or target_square is not None: # by now the target square is not the same color as the piece
            new_game.move_cnt_50 = 0
        else:
            new_game.move_cnt_50 += 1        
        # it's a legal move that doesn't end with a mate - return the updated game   
        return new_game
                                      
    def move_piece(self, cmd_input):
        """
        Performs a move according to the user's input.
        If it's a castle move (short or long) - it performs the castle (if it's legal).
        If it's a regular or promotion move - it calls the check_king_threat function which performs the move (if it's legal)
        If the input is non of the above options, it raises an exception.
        Args:
            cmd_input (str): the user's input for the move.
        Returns:
            for castle moves - the updated game after the castle was played.
            for regular and promotion moves - the result of the check_king_threat method
        """
        # first need to turn off the two_squares flag in case there was a pawn that moved 2 squares in the previous move.
        if self.piece_moved_two_turns_ago is not None and self.piece_moved_two_turns_ago.__class__ == pawn and self.piece_moved_two_turns_ago.two_squares:
            self.piece_moved_two_turns_ago.two_squares = False
        # second need to turn off the can_be_captured_en_passant in case there was a pawn that could be captured en passant in the previous move and wasn't captured.
        if self.piece_moved_two_turns_ago is not None and self.piece_moved_two_turns_ago.__class__ == pawn and self.piece_moved_two_turns_ago.can_be_captured_en_passant:
            self.piece_moved_two_turns_ago.can_be_captured_en_passant = False
        # short castle case
        if cmd_input == 'O-O':
            if self.player_turn == 0: # white player
                row = 0
            else: # black player
                row = 7
            if self.board[row][5] is not None or self.board[row][6] is not None:
                raise Exception("The squares between the king and the rook should be empty.")
            castled_king = self.board[row][4]
            castled_rook = self.board[row][7]
            if not castled_king.has_not_moved or not castled_rook.has_not_moved:
                raise Exception("The king or the rook has moved already.")
            # check if the squares that the king will pass through are threatened
            if castled_king.squares_threat_test(board=self.board, squares=[(row, 4), (row, 5), (row, 6)], king_square=(row, 4))[0] \
                == [(row, 4), (row, 5), (row, 6)]:       
                # perform the castle itself
                self.board[row][6] = castled_king
                self.board[row][5] = castled_rook
                # there is no call for a move method of any piece so need to update positions 'manually'
                castled_king.position = 'g' + str(row + 1)
                castled_rook.position = 'f' + str(row + 1)
                self.board[row][4] = None
                self.board[row][7] = None
            else:
                raise Exception("The squares that the king will pass through are threatened.")
        # long castle case
        elif cmd_input == 'O-O-O':
            if self.player_turn == 0: # white player
                row = 0
            else:
                row = 7
            if self.board[row][1] is not None or self.board[row][2] is not None or self.board[row][3] is not None:
                raise Exception("The squares between the king and the rook should be empty.")
            castled_king = self.board[row][4]
            castled_rook = self.board[row][0]
            if not castled_king.has_not_moved or not castled_rook.has_not_moved:
                raise Exception("The king or the rook has moved already.")
            if castled_king.squares_threat_test(self.board, [(row, 4), (row, 3), (row, 2)], (row, 4))[0] == [(row, 4), (row, 3), (row, 2)]:
                self.board[row][2] = castled_king
                self.board[row][3] = castled_rook
                castled_king.position = 'c' + str(row + 1)
                castled_rook.position = 'd' + str(row + 1)
                self.board[row][4] = None
                self.board[row][0] = None
            else:
                raise Exception("The squares that the king will pass through are threatened.")
        # return value
        ret_game = None
        if cmd_input in ('O-O', 'O-O-O'):
            # regular end of move updates
            castled_king.has_castled = True
            castled_rook.has_castled = True
            if self.last_piece_moved is not None:
                self.piece_moved_two_turns_ago = self.last_piece_moved
            self.last_piece_moved = None # it doesn't really matter in castle case
            self.player_turn = 1 - self.player_turn
            self.update_reachable_squares_for_all_pieces()
            self.move_cnt_50 += 1 # no captures or pawn moves in castle moves
            self.move_cnt += 1
            ret_game = self
        else: 
            if len(cmd_input) == 4: # normal case
                ret_game = self.check_king_threat(cmd_input)
            elif len(cmd_input) == 5: # promotion case
                ret_game = self.check_king_threat(cmd_input, True)         
            else: # if the input length is not 4, and neither a promotion nor a 
                # castle move ('e7e8', 'O-O', 'O-O-O') - it means it's an invalid move.     
                raise Exception("Invalid move") 
        # for castle cases return the updated game after the castle was played, for regular and promotion moves return the result of the check_king_threat method
        return ret_game         

    def check_insufficient_material_draw(self):
        """
        Checks if the game is in an insufficient material draw position.
        Returns:
            1 if the game is in an insufficient material draw position, 0 otherwise.
        """
        # insufficient material draw - relevant only when there are 3 pieces or less on the board. 
        # (move_cnt should be at least 29 since there are 32 pieces in chess).
        if self.move_cnt > 29:
            self.pieces_lst = []
            # need to check which pieces are left on the board, insufficient material draw cases are:
            # king vs king, king & knight vs king, king & bishop vs king (colors are not relevant)
            for row in self.board:
                for square in row:
                    if square is not None:
                        self.pieces_lst.append(square)
                    if len(self.pieces_lst) > 3: # there is a sufficient material for deciding the game.
                        break
            if len(self.pieces_lst) == 2: # king vs king
                return 1
            elif len(self.pieces_lst) == 3: # king & knight vs king or king & bishop vs king
                for piece in self.pieces_lst:
                    if piece.__class__ == king:
                        continue
                    if piece.__class__ in (bishop, knight):
                        return 1
        # if the function reaches this line, there is a sufficient material for deciding the game.  
        return 0
    
    def check_stalemate_draw(self, stalemated_king):
        """ 
        Checks if the game is in a stalemate position.
        Args:
            stalemated_king (king): the king that is potentially stalemated.
        Returns:
            1 if the game is in a stalemate position, 0 otherwise.
        """
        break_cond = False
        ret = 1
        if stalemated_king.is_checked:
            ret = 0
        # at this point we know the king is not checked.
        if len(stalemated_king.reachable_squares) > 0:
            for candidate_square in stalemated_king.reachable_squares:
                cmd = stalemated_king.position + self.square_conversion_from_indices_to_str(candidate_square)
                if self.move_simulation(self, cmd):
                    ret = 0 # the king can move
                    break
        # at this point we know the king is not checked and it can't move.
        # need to check if there is a piece of the king color that can move (legally)
        # starting with the en passant option since it's a lot different and could save the for loops that come afterwards.
        if self.last_piece_moved.__class__ == pawn and self.last_piece_moved.color != stalemated_king.color and \
            self.last_piece_moved.two_squares: # there is a pawn that potentially can be captured en passant
            en_passant_candidate_pos = self.sqaure_conversion_to_indices(self.last_piece_moved.position)
            en_passant_candidates = []
            if en_passant_candidate_pos[1] > 0: # need to check left
                left_square = self.board[en_passant_candidate_pos[0]][en_passant_candidate_pos[1] - 1]
                if left_square is not None and left_square.__class__ == pawn and left_square.color == stalemated_king.color:
                    # there is a pawn to the left of the candidate that can capture en passant, need to check that it's not pinned
                    en_passant_candidates.append(left_square.position)
            if en_passant_candidate_pos[1] < 7: # need to check right
                right_square = self.board[en_passant_candidate_pos[0]][en_passant_candidate_pos[1] + 1]
                if right_square is not None and right_square.__class__ == pawn and right_square.color == stalemated_king.color:
                    # there is a pawn to the right of the candidate that can capture en passant, need to check that it's not pinned
                    en_passant_candidates.append(right_square.position) 
            for candidate_square in en_passant_candidates:
                cmd = candidate_square + self.last_piece_moved.position[0]
                if self.last_piece_moved.color == 'white':
                    cmd += '3'
                else:
                    cmd += '6'
                if  self.move_simulation(self, cmd):
                    ret = 0
                    # the last moved piece is a pawn that can be captured en passant
                    self.last_piece_moved.can_be_captured_en_passant = True 
                    break
        # checking all the pieces' reachable squares
        for row in self.board:
            for square in row:
                if square is not None and square.color == stalemated_king.color and square.__class__ != king:
                    # if it's a pawn need to consider both the reachable squares (it's capturing options) and the forward squares. 
                    reachable_lst = square.reachable_squares
                    if square.__class__ == pawn:
                        pawn_forward_reachable = self.get_pawn_forward_reachable_squares(square)
                        reachable_lst += pawn_forward_reachable
                    # if square is not a pawn need to consider the reachable squares only.
                    if len(reachable_lst) > 0:
                        for reach_square in reachable_lst:
                            cmd = square.position + self.square_conversion_from_indices_to_str(reach_square)
                            if self.move_simulation(self, cmd):
                                ret = 0
                                break_cond = True
                                break
                if break_cond:
                    break
            if break_cond:
                break
        # at this point we know the king is not checked, it can't move and there are no pieces that can move - it's a stalemate.
        return ret
    
    def check_three_fold_repetition_draw(self):
        """
        Checks if the game is in a three-fold repetition draw position.
        Returns:
            1 if the game is in a three-fold repetition draw position, 0 otherwise.
        """
        board_of_tups = copy.deepcopy(self.board)
        for i in range(8):
            for j in range(8):
                if board_of_tups[i][j] is not None:
                    board_of_tups[i][j] = board_of_tups[i][j].get_tup_repr()
        board_as_tup = tuple(tuple(row) for row in board_of_tups)
        if (board_as_tup, self.player_turn) in self.positions_dict:
            self.positions_dict[(board_as_tup, self.player_turn)] += 1
            if self.positions_dict[(board_as_tup, self.player_turn)] == 3:
                return 1
        else:
            self.positions_dict[(board_as_tup, self.player_turn)] = 1
        return 0
