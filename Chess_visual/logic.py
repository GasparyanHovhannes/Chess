from abc import ABC, abstractmethod
from types import NoneType

from colorama import init, Fore, Style
init()

class Figure(ABC):
    name = ''
    color = ''
    old_x = 0
    old_y = 0
    move_x = []
    move_y = []
    legal_move = False

    def __init__(self, old_x, old_y, color):
        self.old_x = old_x
        self.old_y = old_y
        self.color = color
        Board().figures_on_board.append(self)
        self.image = f"./assets/{self.color}{self.name}.png"

    @abstractmethod
    def move(self, new_x, new_y):
        pass

    @abstractmethod
    def get_attacks(self):
        pass

    def get_legal_moves(self):
        king = Board().find_king(self.color)
        legal_moves = []

        for s in self.get_attacks():
            target = Board().get_figure(s[0], s[1])
            en_passant_targ = None

            if self.name == 'P':
                en_passant_targ = Board().get_figure(s[0] - self.direction, s[1])
                if (en_passant_targ is not None and (en_passant_targ.name != 'P' or 
                    not en_passant_targ.under_en_passant or en_passant_targ.color == self.color)):
                    en_passant_targ = None

            saved_x, saved_y = self.old_x, self.old_y
            self.move(s[0],s[1])

            if self.legal_move:
                if not king.is_checked():
                    legal_moves.append(s)

                self.old_x, self.old_y = saved_x, saved_y
                if target is not None:
                    Board().figures_on_board.append(target)
                if en_passant_targ is not None:
                    Board().figures_on_board.append(en_passant_targ)

        return legal_moves

                
class Board:

    figures_on_board = []
    promote_decision = None
    _instance = None

    def __new__(cls, board=None):
        if cls._instance is None:
            cls._instance = super(Board, cls).__new__(cls)
            cls._instance.board = board
            cls._instance.figures_on_board = []
        return cls._instance

    # def create_board(self):
    #     for piece in self.figures_on_board:
    #         if piece is not None:
    #             self.board[piece.old_x][piece.old_y] = piece.name

    def get_coords(self, coord):
        if len(coord) != 2 or len(coord[0]) != 2 or len(coord[1]) != 2:  # checks the length of the input
            return None
        if not coord[0][0].isalpha() or not coord[0][1].isdigit() or not coord[1][0].isalpha() or not coord[1][
            1].isdigit():  # checks if the data is valid
            return None

        i = 8 - int(coord[0][1])
        j = ord(coord[0][0]) - ord('a')

        newi = 8 - int(coord[1][1])
        newj = ord(coord[1][0]) - ord('a')

        if i > 7 or i < 0 or j > 7 or j < 0 or newi > 7 or newi < 0 or newj > 7 or newj < 0:
            print("Wrong coordinates!\n")
            return None

        return i, j, newi, newj

    def get_figure(self, x, y):
        for figure in self.figures_on_board:
            if figure.old_x == x and figure.old_y == y:
                return figure
        return None
    
    def find_king(self, color):
        for f in self.figures_on_board:
            if f.name == 'K' and f.color == color:
                return f
            
    def clear_en_passant_flags(self, color):
        for fig in self.figures_on_board:
            if isinstance(fig, Pawn) and fig.color == color:
                fig.under_en_passant = False

class King(Figure):
    name = 'K'
    move_x = [1, -1, 0, 0, 1, 1, -1, -1]
    move_y = [0, 0, 1, -1, 1, -1, 1, -1]

    def __init__(self, old_x, old_y, color):
        super().__init__(old_x, old_y, color)
        self.has_moved = False

    def move(self, new_x, new_y):
        dx = new_x - self.old_x
        dy = new_y - self.old_y

        # --- CASTLING LOGIC ---
        if not self.has_moved and dx == 0 and abs(dy) == 2:
            rook_y = 7 if dy > 0 else 0
            rook = Board().get_figure(self.old_x, rook_y)
            if isinstance(rook, Rook) and not getattr(rook, 'has_moved', True):
                step = 1 if dy > 0 else -1
                clear = True
                for y in range(self.old_y + step, rook_y, step):
                    if Board().get_figure(self.old_x, y) is not None:
                        clear = False
                        break
                if clear:
                    self.old_x, self.old_y = new_x, new_y
                    rook = Board().get_figure(self.old_x,rook.old_y)
                    new_rook_y = new_y - 1 if dy > 0 else new_y + 1

                    rook.old_y = new_rook_y
                    rook.has_moved = True
                    self.has_moved = True
                    self.legal_move = True
                    return

        # --- NORMAL KING MOVE ---
        if abs(dx) <= 1 and abs(dy) <= 1 and (dx != 0 or dy != 0):
            if not (0 <= new_x < 8 and 0 <= new_y < 8):
                return
            target = Board().get_figure(new_x, new_y)
            if target is not None:
                if target.color == self.color:
                    return
                else:
                    Board().figures_on_board.remove(target)

            self.old_x, self.old_y = new_x, new_y
            self.has_moved = True
            self.legal_move = True

    def get_attacks(self):
        squares = []
        for i in range(len(self.move_x)):
            nx = self.old_x + self.move_x[i]
            ny = self.old_y + self.move_y[i]
            if 0 <= nx < 8 and 0 <= ny < 8:
                target = Board().get_figure(nx, ny)
                if target is None or target.color != self.color:
                    squares.append((nx, ny))

        if not self.has_moved:
            rook = Board().get_figure(self.old_x, 7)
            if isinstance(rook, Rook) and not rook.has_moved:
                if all(Board().get_figure(self.old_x,y) is None for y in range(self.old_y + 1, 7)):
                    squares.append((self.old_x, self.old_y + 2))
            rook = Board().get_figure(self.old_x, 0)
            if isinstance(rook, Rook) and not rook.has_moved:
                if all(Board().get_figure(self.old_x,y) is None for y in range(1, self.old_y)):
                    squares.append((self.old_x, self.old_y - 2))

        return squares

    def is_checked(self):
        for fig in Board().figures_on_board:
            if fig.color == self.color:
                continue

            for pos in fig.get_attacks():
                if pos[0] == self.old_x and pos[1] == self.old_y:
                    return True
                
        return False


class Queen(Figure):
    name = 'Q'
    move_x = [1, -1, 0, 0, 1, -1, 1, -1]
    move_y = [0, 0, 1, -1, 1, -1, -1, 1]

    def move(self, new_x, new_y):
        flag = False
        for i in range(8):
            nx = self.old_x + self.move_x[i]
            ny = self.old_y + self.move_y[i]

            while 0 <= nx < 8 and 0 <= ny < 8:
                target = Board().get_figure(nx, ny)
                if nx == new_x and ny == new_y:
                    if target is not None:
                        if target.color != self.color:
                            Board().figures_on_board.remove(target)
                        else:
                            break
                    
                    self.old_x, self.old_y = new_x, new_y
                    flag = True
                    break

                nx += self.move_x[i]
                ny += self.move_y[i]

            if flag:
                self.legal_move = True
                break


    def get_attacks(self):
        squares = []

        for i in range(len(self.move_x)):
            nx = self.old_x + self.move_x[i]
            ny = self.old_y + self.move_y[i]
            while 0 <= nx < 8 and 0 <= ny < 8:
                target = Board().get_figure(nx,ny)
                if target is None:
                    squares.append((nx,ny))
                    nx += self.move_x[i]
                    ny += self.move_y[i]
                elif target.color != self.color:
                    squares.append((nx,ny))
                    break
                else:
                    break
            
        return squares
    

class Knight(Figure):
    name = 'N'
    move_x = [2, 1, -1, -2, -2, -1, 1, 2]
    move_y = [1, 2, 2, 1, -1, -2, -2, -1]

    def move(self, new_x, new_y):
        flag = False
        for i in range(8):
            nx = self.old_x + self.move_x[i]
            ny = self.old_y + self.move_y[i]

            if nx == new_x and ny == new_y:
                target = Board().get_figure(nx, ny)
                if target is not None:
                    if target.color != self.color:
                        Board().figures_on_board.remove(target)
                    else:
                        break

                flag = True
                self.old_x, self.old_y = new_x, new_y
                self.legal_move = True


    def get_attacks(self):
        squares = []
        for i in range(len(self.move_x)):
            nx = self.old_x + self.move_x[i]
            ny = self.old_y + self.move_y[i]

            if 0 <= nx < 8 and 0 <= ny < 8:
                target = Board().get_figure(nx, ny)
                if target is None or (target and target.color != self.color):
                    squares.append((nx,ny))

        return squares


class Rook(Figure):
    name = 'R'
    move_x = [1, -1, 0, 0]
    move_y = [0, 0, 1, -1]

    def __init__(self, old_x, old_y, color):
        super().__init__(old_x, old_y, color)
        self.has_moved = False

    def move(self, new_x, new_y):
        flag = False
        for i in range(4):
            nx = self.old_x + self.move_x[i]
            ny = self.old_y + self.move_y[i]
            while 0 <= nx < 8 and 0 <= ny < 8:
                if nx == new_x and ny == new_y:
                    target = Board().get_figure(nx, ny)
                    if target is not None:
                        if target.color != self.color:
                            Board().figures_on_board.remove(target)
                        else:
                            break
                    flag = True
                    self.old_x, self.old_y = new_x, new_y
                    break
                nx += self.move_x[i]
                ny += self.move_y[i]
            if flag:
                self.legal_move = True
                self.has_moved = True
                break

    def get_attacks(self):
        squares = []
        for i in range(len(self.move_x)):
            nx = self.old_x + self.move_x[i]
            ny = self.old_y + self.move_y[i]
            while 0 <= nx < 8 and 0 <= ny < 8:
                target = Board().get_figure(nx, ny)
                if target is None:
                    squares.append((nx, ny))
                    nx += self.move_x[i]
                    ny += self.move_y[i]
                elif target and target.color != self.color:
                    squares.append((nx, ny))
                    break
                else:
                    break
        return squares


class Bishop(Figure):
    name = 'B'
    move_x = [1, 1, -1, -1]
    move_y = [1, -1, 1, -1]

    def move(self,new_x, new_y):
        flag = False
        for i in range(len(self.move_x)):
            nx = self.old_x + self.move_x[i]
            ny = self.old_y + self.move_y[i]
            while 0 <= nx < 8 and 0 <= ny < 8:
                if nx == new_x and ny == new_y:
                    target = Board().get_figure(nx, ny)
                    if target is not None:
                        if target.color != self.color:
                            Board().figures_on_board.remove(target)
                        else:
                            break
                    flag = True
                    self.old_x, self.old_y = new_x, new_y
                    break

                nx += self.move_x[i]
                ny += self.move_y[i]
            if flag:
                self.legal_move = True
                break


    def get_attacks(self):
        squares = []
        for i in range(len(self.move_x)):
            nx = self.old_x + self.move_x[i]
            ny = self.old_y + self.move_y[i]
            while 0 <= nx < 8 and 0 <= ny < 8:
                target = Board().get_figure(nx, ny)
                if target is None:
                    squares.append((nx,ny))
                    nx += self.move_x[i]
                    ny += self.move_y[i]
                else:
                    if target.color != self.color:
                        squares.append((nx,ny))
                        break
                    else:
                        break
        
        return squares


class Pawn(Figure):
    name = 'P'
    under_en_passant = False

    def __init__(self, old_x, old_y, color):
        super().__init__(old_x, old_y, color)
        self.direction = -1 if self.color == 'w' else 1  # White moves up, black down

    def should_promote(self):
        return (self.color == 'w' and self.old_x == 0) or (self.color == 'b' and self.old_x == 7)

    def move(self, new_x, new_y):
        start_row = 6 if self.color == 'w' else 1

        target = Board().get_figure(new_x,new_y)
        if new_x == self.old_x + self.direction and new_y == self.old_y and target is None:
            self.old_x, self.old_y = new_x, new_y
            self.legal_move = True
            return

        if (self.old_x == start_row and
                new_x == self.old_x + 2 * self.direction and new_y == self.old_y and
                Board().get_figure(self.old_x + self.direction, new_y) is None and target is None):
            self.old_x, self.old_y = new_x, new_y
            self.legal_move = True
            self.under_en_passant = True
            return

        if new_x == self.old_x + self.direction and abs(new_y - self.old_y) == 1:
            if target is not None:
                if target.color != self.color:
                    Board().figures_on_board.remove(target)
                    self.old_x, self.old_y = new_x, new_y
                    self.legal_move = True
                    return
            else:
                en_passant_targ = Board().get_figure(new_x - self.direction, new_y)
                if en_passant_targ is not None:
                    if en_passant_targ.name == 'P' and en_passant_targ.under_en_passant:
                        Board().figures_on_board.remove(en_passant_targ)
                        self.old_x, self.old_y = new_x, new_y
                        self.legal_move = True
                        return

    def get_attacks(self):
        squares = []
        direction = -1 if self.color == 'w' else 1
        start_row = 6 if self.color == 'w' else 1

        one_step_x = self.old_x + direction
        if 0 <= one_step_x < 8 and Board().get_figure(one_step_x,self.old_y) is None:
            squares.append((one_step_x, self.old_y))
            two_step_x = self.old_x + 2 * direction
            if self.old_x == start_row and Board().get_figure(two_step_x,self.old_y) is None:
                squares.append((two_step_x, self.old_y))

        for dy in (-1, 1):
            nx = self.old_x + direction
            ny = self.old_y + dy
            if 0 <= nx < 8 and 0 <= ny < 8:
                target = Board().get_figure(nx, ny)
                if target and target.color != self.color:
                    squares.append((nx, ny))
                elif target is None:
                    side = Board().get_figure(self.old_x, ny)
                    if side and side.name == 'P' and side.color != self.color and side.under_en_passant:
                        squares.append((nx, ny))

        return squares

def is_checkmate(color):

    for fig in Board().figures_on_board:

        if fig.color == color and len(fig.get_legal_moves()) != 0:
            return False
            
    return True


def promote_pawn(pawn):
    x, y = pawn.old_x, pawn.old_y

    promote_fig = Board().promote_decision

    if promote_fig is not None:
        Board().figures_on_board.remove(pawn)
        promote_fig.old_x = x
        promote_fig.old_y = y
        Board().figures_on_board.append(Board().promote_decision)


wking = King(7, 4, 'w')
bking = King(0, 4, 'b')
wqueen = Queen(7, 3, 'w')
bqueen = Queen(0, 3, 'b')
wknight1 = Knight(7, 1, 'w')
wknight2 = Knight(7, 6, 'w')
bknight1 = Knight(0, 1, 'b')
bknight2 = Knight(0, 6, 'b')
wrook1 = Rook(7, 0, 'w')
wrook2 = Rook(7, 7, 'w')
brook1 = Rook(0, 0, 'b')
brook2 = Rook(0, 7, 'b')
wbishop1 = Bishop(7, 2, 'w')
wbishop2 = Bishop(7, 5, 'w')
bbishop1 = Bishop(0, 2, 'b')
bbishop2 = Bishop(0, 5, 'b')
wpawns = [Pawn(6, i, 'w') for i in range(8)]
bpawns = [Pawn(1, i, 'b') for i in range(8)]

#Board().create_board()