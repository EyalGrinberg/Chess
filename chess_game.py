# 1. work on the error messages, some cases are not really possible to get. 
# 2. complex draws: (later treat cases of more advanced draws: 3 times repetiton and 50 moves without capturing)



import copy # used for copying instances of class game and simulating moves.

class game:
    def __init__(self, player_turn=0, move_cnt=0):
        """
        Initializes the board and other attributes for an initial position of a chess game.
        Args:
            player_turn (int): 0 for white, 1 for black. Default is 0.
            move_cnt (int): the number of moves that have been played so far. Default is 0.
        """
        self.player_turn = player_turn # 0 for white, 1 for black
        self.move_cnt = move_cnt
        self.pieces_lst = [] # relevant only for insufficient material draw. 
        # will remain empty until move_cnt=30 since this type of draw is relevant only after 30 moves.
        self.last_piece_moved = None # used for checking the en passant case
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
        This function converts a square given as a tuple of indices to a string of length 2.
        The function assumes a legal input (since it's already taken care of).
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
            # it doesn't really matter which exceptions are raised but it should be one of these two, it's mainly for readability
            Exception("Your king is being checked, you cannot play this move.") 
            Exception("The chosen piece is pinned.")
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
                else: # otherwise it's not a legal escape from the check
                    continue
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
        # start with an en passnt capture of the threatening piece.
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
                else:
                    continue
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
                            else:
                                continue                          
        # there is no escaping, capturing or blocking option - it's a mate.
        return 1 
                        
    def check_king_threat(self, cmd_input, promotion=False): 
        """
        Performs the move in cases of regular and promotion moves (non castle moves) including verification of the user's input.
        It also checks cases of illegal moves related to the king, mates and pins.
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
        target_square = self.board[new_position_indices[0]][new_position_indices[1]]
        if target_square is not None and target_square.color == piece.color:
            raise Exception("The target square is already occupied.")
        # simulate the move and check its validity, if the move is legal - return the new game after the move was played.
        new_game = copy.deepcopy(self)
        piece = new_game.board[old_position_indices[0]][old_position_indices[1]] # its ok to override the piece since its the same piece anyway.
        if promotion:
            if piece.__class__ != pawn:
                raise Exception("Only pawns can be promoted.")
            promotion_piece = cmd_input[-1]
            if promotion_piece not in ['Q', 'R', 'B', 'N']:
                raise Exception("The promotion piece is not valid.")
            piece.move(new_position, new_game)
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
            # check if there is another piece in the way
            if piece.__class__ != pawn:
                if new_position_indices not in piece.reachable_squares and piece.__class__ != king:
                    raise Exception("There is another piece in the way.")
            new_game.board[new_position_indices[0]][new_position_indices[1]] = piece
        # these lines should be executed for both promotion and regular move
        new_game.board[old_position_indices[0]][old_position_indices[1]] = None     
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
                print(new_game)
                print("Black wins!")
                exit()
        if new_game.player_turn == 1 and black_king_new.is_checked:
            if self.test_mate(new_game, black_king_new, new_game.kings_positions[1]):      
                print(new_game)
                print("White wins!")
                exit()  
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
        if cmd_input in ('O-O', 'O-O-O'):
            # regular end of move updates
            self.last_piece_moved = None # it doesn't really matter in castle case
            self.player_turn = 1 - self.player_turn
            self.update_reachable_squares_for_all_pieces()
        else: 
            if len(cmd_input) == 4: # normal case
                return self.check_king_threat(cmd_input)
            elif len(cmd_input) == 5: # promotion case
                return self.check_king_threat(cmd_input, True)         
            else: # if the input length is not 4, and neither a promotion nor a 
                # castle move ('e7e8', 'O-O', 'O-O-O') - it means it's an invalid move.     
                raise Exception("Invalid move") 
        # for castle cases return the updated game after the castle was played.
        return self           

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
        if stalemated_king.is_checked:
            return 0
        # at this point we know the king is not checked.
        if len(stalemated_king.reachable_squares) > 0:
            for candidate_square in stalemated_king.reachable_squares:
                cmd = stalemated_king.position + self.square_conversion_from_indices_to_str(candidate_square)
                if self.move_simulation(self, cmd):
                    return 0
                else:
                    continue
        # at this point we know the king is not checked and it can't move.
        # need to check if there is a piece of the king color that can move (legally)
        # starting with the en passant option since it's a lot different and could save the for loops that come afterwards.
        if self.last_piece_moved.__class__ == pawn and self.last_piece_moved.color != stalemated_king.color and \
            self.last_piece_moved.two_squares: # there is a pawn that potentially can be captured en passant
            en_passant_candidate_pos = self.sqaure_conversion_to_indices(self.last_piece_moved.position)
            if en_passant_candidate_pos[1] > 0: # need to check left
                left_square = self.board[en_passant_candidate_pos[0]][en_passant_candidate_pos[1] - 1]
                if left_square is not None and left_square.__class__ == pawn and left_square.color == stalemated_king.color:
                    # there is a pawn to the left of the candidate that can capture en passant
                    return 0
            if en_passant_candidate_pos[1] < 7: # need to check right
                right_square = self.board[en_passant_candidate_pos[0]][en_passant_candidate_pos[1] + 1]
                if right_square is not None and right_square.__class__ == pawn and right_square.color == stalemated_king.color:
                    # there is a pawn to the right of the candidate that can capture en passant
                    return 0
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
                                return 0
                            else:
                                continue 
        # at this point we know the king is not checked, it can't move and there are no pieces that can move - it's a stalemate.
        return 1
            
    
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
        self.reachable_squares = [] # squares that the pawn can capture or threat (not including the forward squares).

    def __repr__(self) -> str:
        return '  P '

    def move(self, new_position, game):
        """
        Checks if the move is legal and updates the pawn's position if it is.
        Args:
            new_position (str): the new position of the pawn on the board, a string of length 2.
            game (game, optional): an instance of a game class. This function uses methods and attributes of the game class, instead of inheritance because a pawn 'is-not-a' game.
        """
        # new_position_as_tup = game.sqaure_conversion_to_indices(new_position)
        # target_square = game.board[new_position_as_tup[0]][new_position_as_tup[1]]
        # if target_square is not None and target_square.color != self.color and new_position[0] == self.position[0]:
        #     raise Exception("The pawn is blocked.")
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
        
        
        
        # target_square = game.board[new_position_as_tup[0]][new_position_as_tup[1]]
        # if target_square is not None and target_square.color != self.color and new_position[0] == self.position[0]:
        #     raise Exception("The pawn is blocked.")
        
        
        
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

class rook:
    def __init__(self, color, position, has_not_moved=True):
        """ 
        Initializes a rook object.
        Args:
            color (str): the color of the rook, either 'white' or 'black'.
            position (str): the position of the rook on the board, a string of length 2.
            has_not_moved (bool): a flag to indicate if the rook has moved (a condition for castling).
        """
        self.color = color
        self.position = position
        self.has_not_moved = has_not_moved 
        self.reachable_squares = []

    def __repr__(self) -> str:
        return '  R '

    def move(self, new_position, game=None):
        """ 
        Checks if the move is legal and updates the rook's position if it is.
        Args:
            new_position (str): the new position of the rook on the board, a string of length 2.
            game (game, optional): not really used in this method, but it's here to keep the same method signature as the other pieces.
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
        return '  N '

    def move(self, new_position, game=None):
        """ 
        Checks if the move is legal and updates the knight's position if it is.
        Args:
            new_position (str): the new position of the knight on the board, a string of length 2.
            game (game, optional): not really used in this method, but it's here to keep the same method signature as the other pieces.
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
        return '  B '

    def move(self, new_position, game=None):
        """ 
        Checks if the move is legal and updates the bishop's position if it is.
        Args:
            new_position (str): the new position of the bishop on the board, a string of length 2.
            game (game, optional): not really used in this method, but it's here to keep the same method signature as the other pieces.
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
        
class queen(bishop, rook):
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
        return '  Q '

    def move(self, new_position, game=None):
        """ 
        Checks if the move is legal and updates the queen's position if it is.
        Args:
            new_position (str): the new position of the queen on the board, a string of length 2.
            game (game, optional): not really used in this method, but it's here to keep the same method signature as the other pieces.
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
        return '  K '

    def move(self, new_position, game=None):
        """ 
        Checks if the move is legal and updates the king's position if it is.
        Args:
            new_position (str): the new position of the king on the board, a string of length 2.
            game (game, optional): not really used in this method, but it's here to keep the same method signature as the other pieces.
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
        


# Execution (Playing the game)
def play_game(chess_game=None, pieces=None, testing_specific_position=False):
    """ 
    Enables to play a game of chess using cmd input.
    For playing from a specific position, the user should provide the game, a set of pieces objects and set the testing_specific_position flag to True.
    For playing from the initial position, no arguments are needed.
    Args:
        chess_game (game, optional): an instance of a game class. If not provided, a new game is created.
        pieces (set, optional): a set of pieces objects. If not provided, the board is initialized with the initial position.
        testing_specific_position (bool, optional): a flag to indicate if the game is played from a specific position, used for testing purposes.
    """
    # playing a given position
    if testing_specific_position: # testing a specific position of the game, game and pieces are provided by the user.
        # building the board using the pieces list.
        chess_game.board = [[None for _ in range(8)] for _ in range(8)]
        for piece in pieces:
            pos_tup = chess_game.sqaure_conversion_to_indices(piece.position)
            chess_game.board[pos_tup[0]][pos_tup[1]] = piece
    # playing an initial position
    else:
        chess_game = game()
    chess_game.update_reachable_squares_for_all_pieces() # relevant for knights only if it's an initial position
    color_dict = {0: 'White', 1: 'Black'}
    while True:
        print(chess_game)
        cmd_input = input(f"{color_dict[chess_game.player_turn]}'s move: ")
        if cmd_input == 'exit':
            exit()
        if cmd_input == 'draw?':
            while True:
                draw_response = input(f"{color_dict[1 - chess_game.player_turn]}'s response Y/N: ")
                if draw_response == 'Y':
                    print("It's a draw!")
                    exit()
                elif draw_response == 'N':
                    cmd_input = input(f"{color_dict[chess_game.player_turn]}'s move: ")
                    break
                else:
                    print("Invalid response to the draw offer.")
                    continue
        try:
            chess_game = chess_game.move_piece(cmd_input)
            # after a move was played legally - need to check if it's a draw by insufficient material.
            if chess_game.check_insufficient_material_draw():
                print(chess_game)
                print("It's a draw by insufficient material!")
                exit()  
            # need to check if it's a draw by stalemate.
            if chess_game.player_turn == 0: # black played a move, need to check if the white king is stalemated.
                stalemated_king = chess_game.board[chess_game.kings_positions[0][0]][chess_game.kings_positions[0][1]]
            else: # the opposite case
                stalemated_king = chess_game.board[chess_game.kings_positions[1][0]][chess_game.kings_positions[1][1]]
            # only relevant if the king is not checked after a move was played.
            if not stalemated_king.is_checked:
                if chess_game.check_stalemate_draw(stalemated_king):
                    print(chess_game)
                    print("It's a draw by a stalemate!")
                    exit()        
        except Exception as e:
            print(e)
            continue
        
        
            
if __name__ == "__main__":
    play_game()
    
    # setting the testing pieces
    # kings
    black_king = king('black', 'h8')
    white_king = king('white', 'f2')
    
    # black pieces
    black_bishop = bishop('black', 'f8')
    b_pawn1 = pawn('black', 'c7')
    b_pawn2 = pawn('black', 'b6')
    b_pawn3 = pawn('black', 'd6')
    b_pawn4 = pawn('black', 'd5')
    b_pawn5 = pawn('black', 'f4')
    
    # white pieces 
    white_rook_1 = rook('white', 'd8')
    white_rook_2 = rook('white', 'h1')
    white_bishop_1 = bishop('white', 'g5')
    white_knight_1 = knight('white', 'g7')
    white_knight_2 = knight('white', 'f5')
    white_pawn = pawn('white', 'h7')
    white_queen = queen('white', 'e6')
    w_pawn1 = pawn('white', 'c6')
    w_pawn2 = pawn('white', 'b5')
    w_pawn3 = pawn('white', 'd4')
    w_pawn4 = pawn('white', 'g2')

    
    kings = {black_king, white_king}
    pieces = {black_king, white_king, white_rook_1, white_rook_2, white_bishop_1, white_pawn, black_bishop}
    insufficient_draw_pieces = {black_king, white_king, white_rook_1, white_bishop_1}
    stalemate_draw_pieces_1 = kings.union({white_queen})
    stalemate_draw_pieces_2 = kings.union({white_rook_1, white_rook_2, white_pawn, black_bishop, white_knight_1, white_knight_2})
    p = kings.union({white_rook_2, white_pawn})
    stalemate_draw_pieces_3 = stalemate_draw_pieces_2.union({b_pawn1, b_pawn2, b_pawn3, b_pawn4, w_pawn1, w_pawn3, w_pawn2})
    stalemate_draw_pieces_4 = stalemate_draw_pieces_3.union({w_pawn4, b_pawn5})
    
    #initialize a new game    
    game_to_test = game(player_turn=0, move_cnt=40)
    
    # testing the given game
    play_game(game_to_test, stalemate_draw_pieces_4, True)