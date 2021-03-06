class BasePiece:
    job = None

    def __init__(self, color, identifier=None):
        self.color = color
        self.identifier = identifier

    def __str__(self):
        return self.color + "_" + self.job

    def hash(self):
        str_representation = str(self)
        if self.identifier is None:
            return str_representation
        else:
            return str_representation + str(self.identifier)

    def in_bounds(self, i, j):
        return i >= 0 and j >= 0 and i < 8 and j < 8

    def empty(self, i, j, state):
        return not state[i][j].piece

    # True if space is empty or enemy
    def available(self, i, j, state):
        return not state[i][j].piece or state[i][j].piece.color != self.color

    # True if space occupied by enemy
    def enemy_occupied(self, i, j, state):
        return state[i][j].piece and state[i][j].piece.color != self.color

    # True if space occupied by friend
    def friend_occupied(self, i, j, state):
        return state[i][j].piece and state[i][j].piece.color == self.color

    def threatened_spaces(self, current_loc, state):
        return set()

    def is_legal(self, move, state):
        return move.to_loc in self.threatened_spaces(move.from_loc, state)


class King(BasePiece):
    def __init__(self, color):
        BasePiece.__init__(self, color)
        self.job = 'king'

    def threatened_spaces(self, current_loc, state):
        spaces = set()
        row, col = current_loc
        for i in range(row - 1, row + 2):
            for j in range(col - 1, col + 2):
                if self.in_bounds(i, j) and (i != row or j != col) and self.available(i, j, state):
                    spaces.add((i, j))
        return spaces


class Queen(BasePiece):
    def __init__(self, color):
        BasePiece.__init__(self, color)
        self.job = 'queen'

    def threatened_spaces(self, current_loc, state):
        spaces = set()
        row, col = current_loc
        # She's like a Rook
        for i in range(row + 1, 8):
            if self.available(i, col, state):
                spaces.add((i, col))
            if not self.empty(i, col, state):
                break
        for j in range(col + 1, 8):
            if self.available(row, j, state):
                spaces.add((row, j))
            if not self.empty(row, j, state):
                break
        for i in range(row - 1, -1, -1):
            if self.available(i, col, state):
                spaces.add((i, col))
            if not self.empty(i, col, state):
                break
        for j in range(col - 1, -1, -1):
            if self.available(row, j, state):
                spaces.add((row, j))
            if not self.empty(row, j, state):
                break
        # AND THEN ALSO like a Bishop
        for row_offset, col_offset in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
            i = row + row_offset
            j = col + col_offset
            while self.in_bounds(i, j):
                if self.available(i, j, state):
                    spaces.add((i, j))
                if not self.empty(i, j, state):
                    break
                i += row_offset
                j += col_offset
        return spaces


class Knight(BasePiece):
    def __init__(self, color, identifier):
        BasePiece.__init__(self, color, identifier)
        self.job = 'knight'

    def threatened_spaces(self, current_loc, state):
        spaces = set()
        row, col = current_loc
        for offset_i, offset_j in ((1, 2), (2, 1)):
            for mult_i, mult_j in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
                i = row + offset_i * mult_i
                j = col + offset_j * mult_j
                if self.in_bounds(i, j) and self.available(i, j, state):
                    spaces.add((i, j))
        return spaces


class Bishop(BasePiece):
    def __init__(self, color, identifier):
        BasePiece.__init__(self, color, identifier)
        self.job = 'bishop'

    def threatened_spaces(self, current_loc, state):
        spaces = set()
        row, col = current_loc
        for row_offset, col_offset in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
            i = row + row_offset
            j = col + col_offset
            while self.in_bounds(i, j):
                if self.available(i, j, state):
                    spaces.add((i, j))
                if not self.empty(i, j, state):
                    break
                i += row_offset
                j += col_offset
        return spaces


class Rook(BasePiece):
    def __init__(self, color, identifier):
        BasePiece.__init__(self, color, identifier)
        self.job = 'rook'

    def threatened_spaces(self, current_loc, state):
        spaces = set()
        row, col = current_loc
        for i in range(row + 1, 8):
            if self.available(i, col, state):
                spaces.add((i, col))
            if not self.empty(i, col, state):
                break
        for j in range(col + 1, 8):
            if self.available(row, j, state):
                spaces.add((row, j))
            if not self.empty(row, j, state):
                break
        for i in range(row - 1, -1, -1):
            if self.available(i, col, state):
                spaces.add((i, col))
            if not self.empty(i, col, state):
                break
        for j in range(col - 1, -1, -1):
            if self.available(row, j, state):
                spaces.add((row, j))
            if not self.empty(row, j, state):
                break
        return spaces


class Pawn(BasePiece):
    def __init__(self, color, identifier):
        BasePiece.__init__(self, color, identifier)
        self.job = 'pawn'

    def threatened_spaces(self, current_loc, state):
        spaces = set()
        row, col = current_loc
        row_offset = 1 if self.color == 'white' else -1
        for col_offset in [-1, 1]:
            if self.in_bounds(row + row_offset, col + col_offset):
                spaces.add((row + row_offset, col + col_offset))
        return spaces


class Move:
    from_loc = None
    to_loc = None

    def __init__(self, from_loc, to_loc):
        self.from_loc = from_loc
        self.to_loc = to_loc

    def __str__(self):
        return str(self.from_loc) + "_to_" + str(self.to_loc)


class Space:
    def __init__(self, piece=None):
        self.piece = piece
        self.danger_from_white = False
        self.danger_from_black = False

    def __str__(self):
        output = str(self.piece) if self.piece else '_'
        output += '<w>' if self.danger_from_white else ''
        output += '<b>' if self.danger_from_black else ''
        return output


class Board:
    def __init__(self):
        # The indices are:    [[(0,0), (0,1), ... (0,7)],
        #                                        [(1,0) (1,1) ... (1,7)],
        #                                                     ....
        #                                        [(7,0), (7,1) ... (7,7)]]
        self.state = [[]]
        for row in [[Rook('white', 1), Knight('white', 1), Bishop('white', 1), Queen('white'),
                     King('white'), Bishop('white', 2), Knight('white', 2), Rook('white', 2)],
                    [Pawn('white', 1), Pawn('white', 2), Pawn('white', 3), Pawn('white', 4),
                     Pawn('white', 5), Pawn('white', 6), Pawn('white', 7), Pawn('white', 8)],
                    [None]*8,
                    [None]*8,
                    [None]*8,
                    [None]*8,
                    [Pawn('black', 1), Pawn('black', 2), Pawn('black', 3), Pawn('black', 4),
                     Pawn('black', 5), Pawn('black', 6), Pawn('black', 7), Pawn('black', 8)],
                    [Rook('black', 1), Knight('black', 1), Bishop('black', 1), Queen('black'),
                     King('black'), Bishop('black', 2), Knight('black', 2), Rook('black', 2)]]:
            for piece in row:
                if len(self.state[-1]) == 8:
                    self.state.append([])
                self.state[-1].append(Space(piece))
        self.moves = []
        self.turn = 'white'

    def __str__(self):
        output = ''
        for row in self.state:
            for space in row:
                output += str(space) + ' '
            output += '\n'
        return output

    def reset_danger_from(self, color):
        threatened_spaces = set()
        for i in range(0, 8):
            row = self.state[i]
            for j in range(0, 8):
                space = row[j]
                if color == 'white':
                    space.danger_from_white = False
                else:
                    space.danger_from_black = False
                if space.piece and space.piece.color == color:
                    for each in space.piece.threatened_spaces((i, j), self.state):
                        threatened_spaces.add(each)
        for x, y in threatened_spaces:
            if color == 'white':
                self.state[x][y].danger_from_white = True
            else:
                self.state[x][y].danger_from_black = True

    def replay_moves(self):
        for move in self.moves:
            self.exec_move(move)

    def update_turn(self):
        self.turn = 'white' if self.turn == 'black' else 'black'

    def exec_move(self, move, force=False):
        moving_piece = self.state[move.from_loc[0]][move.from_loc[1]].piece
        if not force:
            assert moving_piece
            assert moving_piece.color == self.turn
            assert moving_piece.is_legal(move, self.state)
        displaced_piece = self.state[move.to_loc[0]][move.to_loc[1]].piece
        self.state[move.to_loc[0]][move.to_loc[1]].piece = moving_piece
        self.state[move.from_loc[0]][move.from_loc[1]].piece = None
        if displaced_piece:
            print "MURDERED " + str(displaced_piece)
        self.update_turn()
