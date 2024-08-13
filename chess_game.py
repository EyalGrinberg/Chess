import copy # used for check_king_threat method in class game

class game:
    def __init__(self):
        self.player_turn = 0 # 0 for white, 1 for black
        self.last_piece_moved = None # used for checking en passant case
        self.kings_positions = [(0, 4), (7, 4)] # kings' positions, white is first and black is second
        # board initialzation
        self.board = [[None for i in range(8)] for i in range(8)]
        # pieces
        for tup in [(0, 'white'), (7, 'black')]:
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
        
    [1   R N B Q K B N R]]
    [2   P P P P P P P P]]     
    [3                   ]
    [4                   ]
    [5                   ]
    [6                   ]
    [7   P P P P P P P P]]
    [8   R N B Q K B N R]]
                            ]
    """ 
    
    def __repr__(self): 
        # for simplicity the board's upper left corner is (0,0) and the bottom right corner is (7,7), but when printed it should be reverted.
       return "\n".join([str(row) for row in self.board][::-1])
    
    def sqaure_conversion_to_indices(self, square):
        """
        Converts a square given as a letter and a number to indices in the board matrix,
        also validates the square input.

        Args:
            square (str): a string of length 2, with the first character should be a letter between 'a' and 'h'
            and the second character should be a number between '1' and '8'.
         
        Returns:
            tuple: a tuple of two integers representing the indices of the square in the board matrix.
        """
        if len(square) != 2:
            raise ValueError("The square should be a string of length 2")
        conversion_dict = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
        if square[0] not in conversion_dict:
            raise ValueError("The first character of the provided square should be a letter between 'a' and 'h'")
        if square[1] not in '12345678':
            raise ValueError("The second character of the provided square should be a number between '1' and '8'")
        return (int(square[1]) - 1, conversion_dict[square[0]])
    
    def update_reachable_squares_for_all_pieces(self):
        kings = [None] * 2
        # update the reachable squares of all the pieces after moving a piece
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
        kings[0].update_reachable_squares(self.board)
        kings[1].update_reachable_squares(self.board)
        # update kings_positions
        self.kings_positions = []
        for i in (0, 1):
            self.kings_positions.append(self.sqaure_conversion_to_indices(kings[i].position))
        
    
    def test_mate_stalemate(self, game, threatened_king, king_position):
        """
        king_position is the threatened king's position as tuple.
        checks if the game provided has a mate/stalemate position.
        the game is the new_game and the function is called only once via the check_king_threat method 
        if the king is being checked after the opponent played a move.
        the function returns 1 if its a mate, -1 if its a stalemate and 0 if the check is avoidable.
        """
        if len(threatened_king.reachable_squares) > 0: # the king can escape from being checked 
            return 0
        # by now we know the king is checked and it can't escape the check, 
        # need to check if there is a piece that can block the check or capture the threatenning piece.
        # I will do that using the king's method that given a board and the king's position turns on the
        # is_checked flag iff the king is checked - that's how I will handle cases of discovered check that are two checks and cases of pins.
        # still not sure how I will get access to the threatning piece because I have it in the same king's method
        threatening_piece = threatened_king.squares_threat_test(game.board, [king_position], king_position)[1]
        threatening_piece_pos = self.sqaure_conversion_to_indices(threatening_piece.position)
        # if the threatening piece is a pawn or a knight there is no blocking option, only capturing.
        # if its a qween, bishop or a rook then there is a blocking option in addition to capturing.
        capturing_square = [threatening_piece_pos]
        blocking_squares = []
        if threatening_piece.__class__ in (rook, queen):
            piece_reachable = threatening_piece.reachable_squares
            for i in (0, 1): # 0 for the same row and 1 for the same column.
                if king_position[i] == threatening_piece_pos[i]: 
                    squares = [x for x in piece_reachable if x[i] == king_position[i]]
                    if king_position[1 - i] > threatening_piece_pos[1 - i]: # need to keep only square to the right of the rook (between the rook and the king)
                        blocking_squares = [x for x in squares if x[1 - i] > threatening_piece_pos[1 - i]]
                    else: # need to keep only square to the left of the rook (between the rook and the king)
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
        # now need to check if there's a piece of the king's side that can block the check or capture the threatening piece.
        for row in game.board:
            for square in row:
                if square is not None and square.color == threatened_king.color and square.__class__ != king:
                    for block in blocking_squares:
                        if block in square.reachable_squares: # this piece can block the check if its not pinned
                            updated_game = copy.deepcopy(game)
                            updated_game.board[block[0]][block[1]] = square
                            updated_game.board[self.sqaure_conversion_to_indices(square.position)[0]][self.sqaure_conversion_to_indices(square.position)[1]] = None
                            new_king = updated_game.board[king_position[0]][king_position[1]] # the king hasn't moved
                            x, y = new_king.squares_threat_test(updated_game.board, [king_position], king_position)
                            if not new_king.is_checked: # the block wasn't legal, the piece was pinned or there were 2 checks
                                return 0
        return 1
                        
        
    def check_king_threat(self, cmd_input, promotion=False): 
        """
        This function checks cases of mates, stalemates and pins
        """
        # general checks
        old_position = cmd_input[:2]
        new_position = cmd_input[2:4]
        old_position_indices = self.sqaure_conversion_to_indices(old_position)
        new_position_indices = self.sqaure_conversion_to_indices(new_position)
        piece = self.board[old_position_indices[0]][old_position_indices[1]]
        if piece is None:
            raise ValueError("There is no piece at the input square")
        if (self.player_turn == 0 and piece.color == 'black') or (self.player_turn == 1 and piece.color == 'white'):
            raise Exception("The chosen piece is not yours")
        target_square = self.board[new_position_indices[0]][new_position_indices[1]]
        if target_square is not None and target_square.color == piece.color:
            raise ValueError("The new position is already occupied")
        
        # simulate the move and check its validity, if the move is legal - return the new game after the move was played.
        new_game = copy.deepcopy(self)
        piece = new_game.board[old_position_indices[0]][old_position_indices[1]] #its ok to override the piece since its the same piece anyway.
        if promotion:
            if piece.__class__ != pawn:
                raise ValueError("Only pawns can be promoted")
            promotion_piece = cmd_input[-1]
            if promotion_piece not in ['Q', 'R', 'B', 'N']:
                raise ValueError("The promotion piece is not valid")
            piece.move(new_position, promotion_piece, new_game)
            if promotion_piece == 'Q':
                new_game.board[new_position_indices[0]][new_position_indices[1]] = queen(piece.color, new_position)
            elif promotion_piece == 'R': 
                new_game.board[new_position_indices[0]][new_position_indices[1]] = rook(piece.color, new_position)
            elif promotion_piece == 'B':
                new_game.board[new_position_indices[0]][new_position_indices[1]] = bishop(piece.color, new_position)
            else: # promotion_piece == 'N'
                new_game.board[new_position_indices[0]][new_position_indices[1]] = knight(piece.color, new_position)
        else:
            piece.move(new_position, game=new_game)
            new_game.board[new_position_indices[0]][new_position_indices[1]] = piece
        new_game.board[old_position_indices[0]][old_position_indices[1]] = None     
        new_game.last_piece_moved = piece
        new_game.player_turn = 1 - new_game.player_turn
        new_game.update_reachable_squares_for_all_pieces()
        
        white_king_self = self.board[self.kings_positions[0][0]][self.kings_positions[0][1]]
        white_king_new = new_game.board[new_game.kings_positions[0][0]][new_game.kings_positions[0][1]]
        black_king_self = self.board[self.kings_positions[1][0]][self.kings_positions[1][1]]
        black_king_new = new_game.board[new_game.kings_positions[1][0]][new_game.kings_positions[1][1]]
        # check if the player playing is not avoiding being checked
        print(white_king_self.is_checked)
        print(white_king_new.is_checked)
        if white_king_self.is_checked and white_king_new.is_checked or black_king_self.is_checked and black_king_new.is_checked:
            raise Exception("Your king is being checked, you cannot play this move.")
        # check if the moved piece is pinned
        if self.player_turn == 0:
            if white_king_new.is_checked:
                raise Exception("The chosen piece is pinned.")
        else:
            if black_king_new.is_checked:
                raise Exception("The chosen piece is pinned.")     
        
        if new_game.player_turn == 0 and white_king_new.is_checked:
            # black played a move and checked the white king, need to see if its a mate or stalemate
            self.test_mate_stalemate(new_game, white_king_new, new_game.kings_positions[0])
                  
        return new_game
        
                                           
    def move_piece(self, cmd_input):
        # short castle case
        if cmd_input == 'O-O':
            if self.player_turn == 0: # white player
                if self.board[0][5] is not None or self.board[0][6] is not None:
                    raise Exception("The squares between the king and the rook should be empty")
                white_king = self.board[0][4]
                white_rook = self.board[0][7]
                if not white_king.is_castle_legal or not white_rook.is_castle_legal:
                    raise Exception("The king or the rook has moved before")
                # check if the squares that the king will pass through are threatened
                if white_king.squares_threat_test(board=self.board, squares=[(0, 4), (0, 5), (0, 6)], king_square=(0, 4)) == [(0, 4), (0, 5), (0, 6)]: # maybe (0, 4) is redundant if i will have a check attribute for the king       
                    self.board[0][6] = white_king
                    self.board[0][5] = white_rook
                    white_king.position = 'g1'
                    white_rook.position = 'f1'
                    self.board[0][4] = None
                    self.board[0][7] = None
                else:
                    raise Exception("The squares that the king will pass through are threatened")
            else: # black player
                if self.board[7][5] is not None or self.board[7][6] is not None:
                    raise Exception("The squares between the king and the rook should be empty")
                black_king = self.board[7][4]
                black_Rook = self.board[7][7]
                if not black_king.is_castle_legal or not black_Rook.is_castle_legal:
                    raise Exception("The king or the rook has moved before")
                # check if the squares that the king will pass through are threatened
                if black_king.squares_threat_test(self.board, [(7, 4), (7, 5), (7, 6)], (7, 4)) == [(7, 4), (7, 5), (7, 6)]: # maybe (7, 4) is redundant if i will have a check attribute for the king       
                    self.board[7][6] = black_king
                    self.board[7][5] = black_Rook
                    black_king.position = 'g8'
                    black_Rook.position = 'f8'
                    self.board[7][4] = None
                    self.board[7][7] = None
                else:
                    raise Exception("The squares that the king will pass through are threatened")
            self.last_piece_moved = None # it doesn't really matter in castle case
            self.player_turn = 1 - self.player_turn
            self.update_reachable_squares_for_all_pieces()
        # long castle case
        elif cmd_input == 'O-O-O':
            if self.player_turn == 0: # white player
                if self.board[0][1] is not None or self.board[0][2] is not None or self.board[0][3] is not None:
                    raise Exception("The squares between the king and the rook should be empty")
                white_king = self.board[0][4]
                white_rook = self.board[0][0]
                if not white_king.is_castle_legal or not white_rook.is_castle_legal:
                    raise Exception("The king or the rook has moved before")
                if white_king.squares_threat_test(self.board, [(0, 4), (0, 3), (0, 2)], (0, 4)) == [(0, 4), (0, 3), (0, 2)]:
                    self.board[0][2] = white_king
                    self.board[0][3] = white_rook
                    white_king.position = 'c1'
                    white_rook.position = 'd1'
                    self.board[0][4] = None
                    self.board[0][0] = None
                else:
                    raise Exception("The squares that the king will pass through are threatened")
            else: # black player
                if self.board[7][1] is not None or self.board[7][2] is not None or self.board[7][3] is not None:
                    raise Exception("The squares between the king and the rook should be empty")
                black_king = self.board[7][4]
                black_rook = self.board[7][0]
                if not black_king.is_castle_legal or not black_rook.is_castle_legal:
                    raise Exception("The king or the rook has moved before")
                if black_king.squares_threat_test(self.board, [(7, 4), (7, 3), (7, 2)], (7, 4)) == [(7, 4), (7, 3), (7, 2)]:
                    self.board[7][2] = black_king
                    self.board[7][3] = black_rook
                    black_king.position = 'c8'
                    black_rook.position = 'd8'
                    self.board[7][4] = None
                    self.board[7][0] = None 
                else:
                    raise Exception("The squares that the king will pass through are threatened")
            # maybe combine these 3 lines with the shotr castle
            self.last_piece_moved = None
            self.player_turn = 1 - self.player_turn
            self.update_reachable_squares_for_all_pieces() 
        if cmd_input != 'O-O' and cmd_input != 'O-O-O':
            if len(cmd_input) == 4: # normal case
                return self.check_king_threat(cmd_input)
            elif len(cmd_input) == 5: # promotion case
                return self.check_king_threat(cmd_input, True)         
            else: # if the input length is not 4, and neither a promotion nor a 
                # castle move ('e7e8', 'O-O', 'O-O-O') - it means it's an invalid move.     
                raise Exception("Invalid move") 
        
        return self           
        
            
# 2. work on the error messages, some cases are not really possible to get.
# 5. add letters and numbers to the board visualization ?

# 2. work on pins and checks. - use the king threat attribute for identifying it
# 3. work on the checkmate and stalemate conditions.   

    
class pawn: 
    def __init__(self, color, position):
        self.color = color
        self.position = position
        self.two_squares = False
        self.is_en_passant = False
        self.reachable_squares = [] # squares that the pawn can capture or threat

    def __repr__(self) -> str:
        return '  P '

    def move(self, new_position, promotion_piece=None, game=None):
        self.is_en_passant = False # turn the en passant flag off
        self.two_squares = False
        # check if it's a capture move
        if abs(ord(new_position[0]) - ord(self.position[0])) == 1:
            if int(new_position[1]) - int(self.position[1]) == 1 and game.player_turn == 0 or \
                int(new_position[1]) - int(self.position[1]) == -1 and game.player_turn == 1:
                    self.capture(new_position, game, promotion_piece)
            else:
                raise Exception("Pawns cannot move that way")
        # regular move
        print("self pos: ", self.position)
        print("new pos: ", new_position)
        if new_position[0] != self.position[0] or self.color == 'white' and int(self.position[1]) > int(new_position[1]) or self.color == 'black' and int(self.position[1]) < int(new_position[1]):
            raise Exception("Pawns can only move forward")
        if int(new_position[1]) - int(self.position[1]) > 2:
            raise Exception("Pawns can't move more than 2 squares")
        if int(new_position[1]) - int(self.position[1]) == 2 and self.position[1] != '2':
            raise Exception("Pawns can move 2 squares only from their opening position")
        # check if it's a 2 squares move
        if self.color == 'white' and self.position[1] == '2' and new_position[1] == '4':
            self.two_squares = True 
        if self.color == 'black' and self.position[1] == '7' and new_position[1] == '5':
            self.two_squares = True
        self.position = new_position 
        # check if the pawn can be promoted
        if self.position[1] == 7 or self.position[1] == 0:
            self.promote(promotion_piece)

    def promote(self, new_piece):
        if self.position[1] != 7 and self.position[1] != 0:
            raise Exception("Pawns can only be promoted when they reach the end of the board")
        self.__class__ = new_piece(self.color)
        
    def capture(self, new_position, game, promotion_piece=None):
        # check if the pawn can be promoted
        if self.position[1] == 7 or self.position[1] == 0:
            self.promote(promotion_piece)        
        # check if it's an en passant move
        if game.player_turn == 0: # white takes black's pawn en passant
            piece_to_capture = game.board[4][ord(new_position[0]) - 97]
            if piece_to_capture is not None:
                if int(self.position[1]) == 5 and piece_to_capture.__class__ == pawn and piece_to_capture.two_squares == True \
                    and game.last_piece_moved == piece_to_capture and new_position[0] == piece_to_capture.position[0] and new_position[1] == '6':
                        self.is_en_passant = True
                        self.en_passant(new_position, game)
        else: # black takes white's pawn en passant
            piece_to_capture = game.board[3][ord(new_position[0]) - 97]
            if piece_to_capture is not None:
                if int(self.position[1]) == 4 and piece_to_capture.__class__ == pawn and piece_to_capture.two_squares == True \
                    and game.last_piece_moved == piece_to_capture and new_position[0] == piece_to_capture.position[0] and new_position[1] == '3':
                        self.is_en_passant = True
                        self.en_passant(new_position, game)
        # if it is not an en passant capture it's a regular capture
        if self.is_en_passant == False:
            target_square_indices = game.sqaure_conversion_to_indices(new_position) 
            # I chose to pass an instance of game and use it's 'sqaure_conversion_to_indices' method, instead of using inheritance because a pawn 'is-not-a' game.
            target_sqaure_piece = game.board[target_square_indices[0]][target_square_indices[1]]
            if target_sqaure_piece is None:
                raise Exception("there is no piece to capture at this square") # maybe drop this part because the 'move_piece' method already checks this case (for a general piece)
            elif target_sqaure_piece.color == 'white' and game.player_turn == 0 or target_sqaure_piece.color == 'black' and game.player_turn == 1:
                raise Exception("A pawn cannot capture pieces of it's own color") # maybe drop this part because the 'move_piece' method already checks this case (for a general piece)
            else:
                self.position = new_position          

    def en_passant(self, new_position, game):
        # update the board after the en passant move, the 'move_piece' method updates everything except the opponent's pawn being taken
        if game.player_turn == 0:
            game.board[4][ord(new_position[0]) - 97] = None
        else:
            game.board[3][ord(new_position[0]) - 97] = None
        self.position = new_position        
        
    def update_reachable_squares(self, board):
        self.reachable_squares = []
        piece_col = ord(self.position[0]) - 97 # 0,1,...,7
        piece_row = int(self.position[1]) - 1 # 0,1,...,7
        if self.color == 'white':
            if piece_row < 7:
                if piece_col > 0:
                    self.reachable_squares.append((piece_row + 1, piece_col - 1))
                if piece_col < 7:
                    self.reachable_squares.append((piece_row + 1, piece_col + 1))
        else:
            if piece_row > 0:
                if piece_col > 0:
                    self.reachable_squares.append((piece_row - 1, piece_col - 1))
                if piece_col < 7:
                    self.reachable_squares.append((piece_row - 1, piece_col + 1))

class rook:
    def __init__(self, color, position):
        self.color = color
        self.position = position
        self.is_castle_legal = True
        self.reachable_squares = []

    def __repr__(self) -> str:
        return '  R '

    def move(self, new_position, game=None):
        if new_position[0] != self.position[0] and new_position[1] != self.position[1]:
            raise Exception("Rooks can only move in straight lines")
        self.position = new_position 
        self.is_castle_legal = False
    
    def update_reachable_squares(self, board):
        # maybe modularize the code by creating a helper function that checks the squares in a certain direction (the for loop part)
        self.reachable_squares = []
        piece_col = ord(self.position[0]) - 97 # 0,1,...,7
        piece_row = int(self.position[1]) - 1 # 0,1,...,7
        # check the squares to the right
        if piece_col < 7:
            for col in range(piece_col + 1, 8):
                square = board[piece_row][col]
                # check if there's a piece of the same color in the way
                if square is not None:
                    if square.color == self.color:
                        break
                    else: # add the last square that can be reached if the Rook captures a piece of the opposite color
                        self.reachable_squares.append((piece_row, col))
                        break
                else: # add the square if it's empty
                    self.reachable_squares.append((piece_row, col))
        # check the squares to the left
        if piece_col > 0:
            for col in range(piece_col - 1, -1, -1):
                square = board[piece_row][col]
                if square is not None:
                    if square.color == self.color:
                        break
                    else: 
                        self.reachable_squares.append((piece_row, col))
                        break
                else: 
                    self.reachable_squares.append((piece_row, col))
        # check the squares below
        if piece_row < 7:
            for row in range(piece_row + 1, 8):
                square = board[row][piece_col]
                if square is not None:
                    if square.color == self.color:
                        break
                    else: 
                        self.reachable_squares.append((row, piece_col))
                        break
                else: 
                    self.reachable_squares.append((row, piece_col))
        # check the squares above
        if piece_row > 0:
            for row in range(piece_row - 1, -1, -1):
                square = board[row][piece_col]
                if square is not None:
                    if square.color == self.color:
                        break
                    else: 
                        self.reachable_squares.append((row, piece_col))
                        break
                else: 
                    self.reachable_squares.append((row, piece_col))
        return self.reachable_squares                  
        
class knight:
    def __init__(self, color, position):
        self.color = color
        self.position = position
        self.reachable_squares = []

    def __repr__(self) -> str:
        return '  N '

    def move(self, new_position, game=None):
        if abs(ord(new_position[0]) - ord(self.position[0])) == 2 and abs(ord(new_position[1]) - ord(self.position[1])) == 1:
            self.position = new_position
        elif abs(ord(new_position[0]) - ord(self.position[0])) == 1 and abs(ord(new_position[1]) - ord(self.position[1])) == 2:
            self.position = new_position
        else:
            raise Exception("Knights move in an L shape")
        
    def update_reachable_squares(self, board):
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
        self.color = color
        self.position = position
        self.reachable_squares = []

    def __repr__(self) -> str:
        return '  B '

    def move(self, new_position, game=None):
        if abs(ord(new_position[0]) - ord(self.position[0])) != abs(int(new_position[1]) - int(self.position[1])):
            raise Exception("Bishops move diagonally")
        self.position = new_position
        
    def update_reachable_squares(self, board):
        self.reachable_squares = []
        piece_col = ord(self.position[0]) - 97 # 0,1,...,7
        piece_row = int(self.position[1]) - 1 # 0,1,...,7
        # check the squares to the right and down
        if piece_col < 7 and piece_row < 7:
            for i in range(1, min(8 - piece_row, 8 - piece_col)):
                square = board[piece_row + i][piece_col + i]
                if square is not None:
                    if square.color == self.color:
                        break
                    else: 
                        self.reachable_squares.append((piece_row + i, piece_col + i))
                        break
                else: 
                    self.reachable_squares.append((piece_row + i, piece_col + i))
        # check the squares to the left and down
        if piece_col > 0 and piece_row < 7:
            for i in range(1, min(8 - piece_row, piece_col + 1)):
                square = board[piece_row + i][piece_col - i]
                if square is not None:
                    if square.color == self.color:
                        break
                    else: 
                        self.reachable_squares.append((piece_row + i, piece_col - i))
                        break
                else: 
                    self.reachable_squares.append((piece_row + i, piece_col - i))
        # check the squares to the right and up
        if piece_col < 7 and piece_row > 0:
            for i in range(1, min(piece_row + 1, 8 - piece_col)):
                square = board[piece_row - i][piece_col + i]
                if square is not None:
                    if square.color == self.color:
                        break
                    else: 
                        self.reachable_squares.append((piece_row - i, piece_col + i))
                        break
                else: 
                    self.reachable_squares.append((piece_row - i, piece_col + i))
        # check the squares to the left and up
        if piece_col > 0 and piece_row > 0:
            for i in range(1, min(piece_row + 1, piece_col + 1)):
                square = board[piece_row - i][piece_col - i]
                if square is not None:
                    if square.color == self.color:
                        break
                    else: 
                        self.reachable_squares.append((piece_row - i, piece_col - i))
                        break
                else: 
                    self.reachable_squares.append((piece_row - i, piece_col - i))
        return self.reachable_squares           
        
class queen(bishop, rook):
    def __init__(self, color, position):
        self.color = color
        self.position = position
        self.reachable_squares = []

    def __repr__(self) -> str:
        return '  Q '

    def move(self, new_position, game=None):
        if new_position[0] != self.position[0] and new_position[1] != self.position[1] \
            and abs(ord(new_position[0]) - ord(self.position[0])) != abs(int(new_position[1]) - int(self.position[1])):
            raise Exception("Queens can move in straight lines and diagonally")
        self.position = new_position
        
    def update_reachable_squares(self, board):
        self.reachable_squares = []
        # piece_col = ord(self.position[0]) - 97 # 0,1,...,7
        # piece_row = int(self.position[1]) - 1 # 0,1,...,7
        diag_squares = bishop.update_reachable_squares(self, board=board)
        non_diag_squares = rook.update_reachable_squares(self, board=board)
        self.reachable_squares = diag_squares + non_diag_squares
        
        

class king:
    def __init__(self, color, position):
        self.color = color
        self.position = position
        self.is_castle_legal = True
        self.has_castled = False
        self.reachable_squares = [] # including threatened squares
        self.is_checked = False

    def __repr__(self) -> str:
        return '  K '

    def move(self, new_position, game=None):
        if abs(ord(new_position[0]) - ord(self.position[0])) > 1 or abs(int(new_position[1]) - int(self.position[1])) > 1:
            raise Exception("Kings can only move one square in any direction")
        self.position = new_position
        self.is_castle_legal = False    
        
    
    def squares_threat_test(self, board, squares, king_square):
        """
        Checks if the squares in the input list are threatened by the opponent pieces on the board.
        squares is a list of tuples.
        king_square is the king's position as a tuple.
        """
        self.is_checked = False
        unthreatened_inboard_squares = squares.copy()
        king_threatening_piece = None
        for tested_square in squares:             
            for row in board:
                for square in row:
                    if square is not None and square.color != self.color: # check if the opponent piece located in square is threatening the tested square 
                        if tested_square in square.reachable_squares:
                            unthreatened_inboard_squares.remove(tested_square)
                        if king_square in square.reachable_squares:
                            self.is_checked = True
                            king_threatening_piece = square
        return unthreatened_inboard_squares, king_threatening_piece

    def update_reachable_squares(self, board):
        self.reachable_squares = []
        piece_col = ord(self.position[0]) - 97 # 0,1,...,7
        piece_row = int(self.position[1]) - 1 # 0,1,...,7
        eight_squares = [(piece_row + 1, piece_col), (piece_row - 1, piece_col), (piece_row, piece_col + 1), (piece_row, piece_col - 1),
                         (piece_row + 1, piece_col + 1), (piece_row + 1, piece_col - 1), (piece_row - 1, piece_col + 1), (piece_row - 1, piece_col - 1)]
        in_board_squares = [(row, col) for row, col in eight_squares if 0 <= row <= 7 and 0 <= col <= 7]
        in_board_squares_copy = in_board_squares.copy()
        for square in in_board_squares_copy:
            square_piece = board[square[0]][square[1]]
            if square_piece is not None and square_piece.color == self.color:
                in_board_squares.remove(square)
        self.reachable_squares = self.squares_threat_test(board, in_board_squares, (piece_row, piece_col))[0]  
        
    
        
        
    # def squares_threat_test(self, board, squares, king_square):
    #     """
    #     Checks if the squares in the input list are threatened by the opponent pieces on the board.
    #     squares is a list of tuples.
    #     king_square is the king's position as a tuple.
    #     """
    #     self.is_checked = False
    #     unthreatened_inboard_squares = squares.copy()
    #     for tested_square in squares:             
    #         for row in board:
    #             for square in row:
    #                 if square is not None and square.color != self.color: # check if the opponent piece located in square is threatening the tested square 
    #                     if tested_square in square.reachable_squares:
    #                         unthreatened_inboard_squares.remove(tested_square)
    #                     if king_square in square.reachable_squares:
    #                         self.is_checked = True
    #     return unthreatened_inboard_squares

    # def update_reachable_squares(self, board):
    #     self.reachable_squares = []
    #     piece_col = ord(self.position[0]) - 97 # 0,1,...,7
    #     piece_row = int(self.position[1]) - 1 # 0,1,...,7
    #     eight_squares = [(piece_row + 1, piece_col), (piece_row - 1, piece_col), (piece_row, piece_col + 1), (piece_row, piece_col - 1),
    #                      (piece_row + 1, piece_col + 1), (piece_row + 1, piece_col - 1), (piece_row - 1, piece_col + 1), (piece_row - 1, piece_col - 1)]
    #     in_board_squares = [(row, col) for row, col in eight_squares if 0 <= row <= 7 and 0 <= col <= 7]
    #     in_board_squares_copy = in_board_squares.copy()
    #     for square in in_board_squares_copy:
    #         square_piece = board[square[0]][square[1]]
    #         if square_piece is not None and square_piece.color == self.color:
    #             in_board_squares.remove(square)
    #     self.reachable_squares = self.squares_threat_test(board, in_board_squares, (piece_row, piece_col))
        

# Execution (Playing the game)
def play_game():
    chess_game = game()
    color_dict = {0: 'White', 1: 'Black'}
    while True:
        print(chess_game)
        cmd_input = input(f"{color_dict[chess_game.player_turn]}'s move: ")
        if cmd_input == 'exit':
            break
        try:
            chess_game = chess_game.move_piece(cmd_input)
        except Exception as e:
            print(e)
            continue
            
if __name__ == "__main__":
    play_game()
    