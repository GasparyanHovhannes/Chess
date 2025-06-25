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

    def __init__(self, board, old_x, old_y, color):
        self.old_x = old_x
        self.old_y = old_y
        self.color = color
        board.figures_on_board.append(self)

    @abstractmethod
    def move(self, board, new_x, new_y):
        pass

    @abstractmethod
    def get_attacks(self,board):
        pass



class Board:
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    nums = ['8', '7', '6', '5', '4', '3', '2', '1']

    figures_on_board = []
    _instance = None

    def __new__(cls, board=None):
        if cls._instance is None:
            cls._instance = super(Board, cls).__new__(cls)
            cls._instance.board = board
            cls._instance.figures_on_board = []
        return cls._instance


    def print_board(self):#The black pieces are colored red
        print("\n")
        print("  " + ' '.join(self.letters))

        for i in range(8):
            print(Fore.WHITE + self.nums[i] + ' ', end = "")
            for j in range(8):
                fig = self.get_figure(i,j)
                if fig == None:
                    print(Fore.WHITE + "- ", end = "")
                else:
                    if fig.color == 'w':
                        print(Fore.WHITE + f"{fig.name} ", end = "")
                    else:
                        print(Fore.RED + f"{fig.name} ", end = "")

            print("\n", end = "")

        print("\n")

    # def print_board(self):#all the pieces are white
    #     print ("  " + ' '.join(self.letters))
    #     i = 1
    #     for row in self.board:
    #         print (self.nums[-i] + ' ' + ' '.join(str(x) for x in row))
    #         i += 1

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

class King(Figure):
    name = 'K'
    move_x = [1, -1, 0, 0, 1, -1]
    move_y = [0, 0, 1, -1, 1, -1]

    def __init__(self, board, old_x, old_y, color):
        super().__init__(board, old_x, old_y, color)
        self.has_moved = False

    def move(self, board, new_x, new_y):
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
                    if board[self.old_x][y] != '-':
                        clear = False
                        break
                if clear:
                    board[self.old_x][self.old_y] = '-'
                    board[self.old_x][rook.old_y] = '-'
                    board[new_x][new_y] = self.name
                    new_rook_y = new_y - 1 if dy > 0 else new_y + 1
                    board[self.old_x][new_rook_y] = rook.name

                    rook.old_y = new_rook_y
                    rook.has_moved = True

                    self.old_y = new_y
                    self.has_moved = True
                    self.legal_move = True
                    return

        # --- NORMAL KING MOVE ---
        if abs(dx) <= 1 and abs(dy) <= 1 and (dx != 0 or dy != 0):
            if not (0 <= new_x < 8 and 0 <= new_y < 8):
                return
            if board[new_x][new_y] != '-':
                target = Board().get_figure(new_x, new_y)
                if target and target.color == self.color:
                    return
                else:
                    Board().figures_on_board.remove(target)
            board[self.old_x][self.old_y] = '-'
            board[new_x][new_y] = self.name
            self.old_x = new_x
            self.old_y = new_y
            self.has_moved = True
            self.legal_move = True


    def get_attacks(self, board):
        squares = []
        for i in range(len(self.move_x)):
            nx = self.old_x + self.move_x[i]
            ny = self.old_y + self.move_y[i]

            if 0 <= nx < len(board) and 0 <= ny < len(board):
                if board[nx][ny] == '-' or Board().get_figure(nx,ny).color != self.color:
                    squares.append((nx,ny))
        return squares

    def is_checked(self):
        board = Board()
        for fig in board.figures_on_board:
            if fig.color == self.color:
                continue

            for pos in fig.get_attacks(chess_board):
                if pos[0] == self.old_x and pos[1] == self.old_y:
                    if fig.name == 'Q' or fig.name == 'R' or fig.name == 'B':
                        dx = self.old_x - fig.old_x
                        dy = self.old_y - fig.old_y

                        if dx > 0:
                            step_x = 1
                        elif dx < 0:
                            step_x = -1
                        else:
                            step_x = 0

                        if dy > 0:
                            step_y = 1
                        elif dy < 0:
                            step_y = -1
                        else:
                            step_y = 0

                        x = fig.old_x + step_x
                        y = fig.old_y + step_y

                        blocked = False
                        while x != self.old_x or y != self.old_y:
                            if board.get_figure(x, y) is not None:
                                blocked = True
                                break
                            x = x + step_x
                            y = y + step_y

                        if not blocked:
                            return True
                    else:
                        return True
        return False


class Queen(Figure):
    name = 'Q'
    move_x = [1, -1, 0, 0, 1, -1, 1, -1]
    move_y = [0, 0, 1, -1, 1, -1, -1, 1]

    def move(self, board, new_x, new_y):
        if board[self.old_x][self.old_y] != 'Q':
            print("You have no queen in that square!\n")
            return

        flag = False
        for i in range(8):
            nx = self.old_x + self.move_x[i]
            ny = self.old_y + self.move_y[i]

            while 0 <= nx < len(board) and 0 <= ny < len(board[0]):
                if nx == new_x and ny == new_y:
                    if board[nx][ny] != '-':
                        target = Board().get_figure(nx, ny)
                        if target.color == self.color:
                            break
                        else:
                            Board().figures_on_board.remove(Board().get_figure(new_x, new_y))
                    board[self.old_x][self.old_y] = '-'
                    board[new_x][new_y] = self.name
                    self.old_x = new_x
                    self.old_y = new_y
                    flag = True
                    break

                if board[nx][ny] != '-':
                    break

                nx += self.move_x[i]
                ny += self.move_y[i]

            if flag:
                self.legal_move = True
                break



    def get_attacks(self, board):
        squares = []
        for i in range(len(self.move_x)):
            nx = self.old_x + self.move_x[i]
            ny = self.old_y + self.move_y[i]
            while 0 <= nx < len(board) and 0 <= ny < len(board):
                target = Board().get_figure(nx,ny)
                if board[nx][ny] == '-' or (target and target.color != self.color):
                    squares.append((nx,ny))
                    nx += self.move_x[i]
                    ny += self.move_y[i]
                elif target and target.color != self.color:
                    squares.append((nx,ny))
                    break
                else:
                    break
        return squares

class Knight(Figure):
    name = 'N'
    move_x = [2, 1, -1, -2, -2, -1, 1, 2]
    move_y = [1, 2, 2, 1, -1, -2, -2, -1]

    def move(self, board, new_x, new_y):
        if board[self.old_x][self.old_y] != 'N':
            print("You have no knight in that square!\n")
            return

        flag = False
        for i in range(8):
            nx = self.old_x + self.move_x[i]
            ny = self.old_y + self.move_y[i]

            if nx == new_x and ny == new_y:
                if board[nx][ny] != '-':
                    target = Board().get_figure(nx,ny)
                    if target and target.color == self.color:
                        break
                    else:
                        Board().figures_on_board.remove(Board().get_figure(new_x, new_y))

                board[self.old_x][self.old_y] = '-'
                board[new_x][new_y] = self.name
                flag = True
                self.old_x = new_x
                self.old_y = new_y
                self.legal_move = True



    def get_attacks(self, board):
        squares = []
        for i in range(len(self.move_x)):
            nx = self.old_x + self.move_x[i]
            ny = self.old_y + self.move_y[i]

            if 0 <= nx < len(board) and 0 <= ny < len(board):
                target = Board().get_figure(nx,ny)
                if board[nx][ny] == '-' or target and (target.color != self.color):
                    squares.append((nx,ny))


        return squares


class Rook(Figure):
    name = 'R'
    move_x = [1, -1, 0, 0]
    move_y = [0, 0, 1, -1]

    def __init__(self, board, old_x, old_y, color):
        super().__init__(board, old_x, old_y, color)
        self.has_moved = False

    def move(self, board, new_x, new_y):
        if board[self.old_x][self.old_y] != 'R':
            print("You have no rook in that square!\n")
            return
        flag = False
        for i in range(4):
            nx = self.old_x + self.move_x[i]
            ny = self.old_y + self.move_y[i]
            while 0 <= nx < len(board) and 0 <= ny < len(board):
                if board[nx][ny] != '-':
                    target = Board().get_figure(nx, ny)
                    if target and target.color == self.color:
                        break
                    else:
                        Board().figures_on_board.remove(Board().get_figure(new_x, new_y))
                if nx == new_x and ny == new_y:
                    board[self.old_x][self.old_y] = '-'
                    board[new_x][new_y] = self.name
                    flag = True
                    self.old_x = new_x
                    self.old_y = new_y
                    break
                nx += self.move_x[i]
                ny += self.move_y[i]
            if flag:
                self.legal_move = True
                self.has_moved = True
                break

    def get_attacks(self, board):
        squares = []
        for i in range(len(self.move_x)):
            nx = self.old_x + self.move_x[i]
            ny = self.old_y + self.move_y[i]
            while 0 <= nx < len(board) and 0 <= ny < len(board):
                target = Board().get_figure(nx,ny)
                if board[nx][ny] == '-' or (target and target.color != self.color):
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

    def move(self, board, new_x, new_y):
        if board[self.old_x][self.old_y] != 'B':
            print("You have no bishop in that square!\n")
            return
        flag = False
        for i in range(4):
            nx = self.old_x + self.move_x[i]
            ny = self.old_y + self.move_y[i]
            while 0 <= nx < len(board) and 0 <= ny < len(board):
                if board[nx][ny] != '-':
                    target = Board().get_figure(nx, ny)
                    if target and target.color == self.color:
                        break
                    else:
                        Board().figures_on_board.remove(Board().get_figure(new_x, new_y))
                if nx == new_x and ny == new_y:
                    board[self.old_x][self.old_y] = '-'
                    board[new_x][new_y] = self.name
                    flag = True
                    self.old_x = new_x
                    self.old_y = new_y
                    break
                nx += self.move_x[i]
                ny += self.move_y[i]
            if flag:
                self.legal_move = True
                break


    def get_attacks(self, board):
        squares = []
        for i in range(len(self.move_x)):
            nx = self.old_x + self.move_x[i]
            ny = self.old_y + self.move_y[i]
            while 0 <= nx < len(board) and 0 <= ny < len(board):
                target = Board().get_figure(nx,ny)
                if board[nx][ny] == '-' or (target and target.color != self.color):
                    squares.append((nx,ny))
                    nx += self.move_x[i]
                    ny += self.move_y[i]
                elif target and target.color != self.color:
                    squares.append((nx,ny))
                    break
                else:
                    break

        return squares


class Pawn(Figure):
    name = 'P'
    under_en_passant = False
    
    def __init__(self, board, old_x, old_y, color):
        super().__init__(board, old_x, old_y, color)
        self.direction = -1 if self.color == 'w' else 1  # White moves up, black down

    def should_promote(self):
        return (self.color == 'w' and self.old_x == 0) or (self.color == 'b' and self.old_x == 7)

    def move(self, board, new_x, new_y):
        start_row = 6 if self.color == 'w' else 1

        if new_x == self.old_x + self.direction and new_y == self.old_y and board[new_x][new_y] == '-':
            board[self.old_x][self.old_y] = '-'
            board[new_x][new_y] = self.name
            self.old_x, self.old_y = new_x, new_y
            self.legal_move = True
            return

        if (self.old_x == start_row and
                new_x == self.old_x + 2 * self.direction and new_y == self.old_y and
                board[self.old_x + self.direction][new_y] == '-' and board[new_x][new_y] == '-'):
            board[self.old_x][self.old_y] = '-'
            board[new_x][new_y] = self.name
            self.old_x, self.old_y = new_x, new_y
            self.legal_move = True
            self.under_en_passant = True
            return

        if new_x == self.old_x + self.direction and abs(new_y - self.old_y) == 1:
            target = board[new_x][new_y]
            if target != '-':
                target_fig = Board().get_figure(new_x, new_y)
                if target_fig.color != self.color:
                    board[self.old_x][self.old_y] = '-'
                    Board().figures_on_board.remove(Board().get_figure(new_x, new_y))
                    board[new_x][new_y] = self.name
                    self.old_x, self.old_y = new_x, new_y
                    self.legal_move = True
                    return
            elif target == '-':
                en_passant_targ = Board().get_figure(new_x - self.direction, new_y)
                if en_passant_targ:
                    if en_passant_targ.name == 'P' and en_passant_targ.under_en_passant:
                        board[self.old_x][self.old_y] = '-'
                        Board().figures_on_board.remove(en_passant_targ)
                        board[new_x][new_y] = self.name
                        self.old_x, self.old_y = new_x, new_y
                        self.legal_move = True
                        return

                

    def get_attacks(self, board):
        squares = []
        attack_x = []
        attack_y = []

        if self.color == 'w':
            attack_x = [-1, -1]
            attack_y = [1, -1]
        else:
            attack_x = [1, 1]
            attack_y = [1, -1]

        for i in range(len(attack_x)):
            nx = self.old_x + attack_x[i]
            ny = self.old_y + attack_y[i]
            if 0 <= nx < len(board) and 0 <= ny < len(board):
                target = Board().get_figure(nx,ny)
                if board[nx][ny] == '-' or (target and target.color != self.color):
                    squares.append((nx,ny))


        return squares

def is_checkmate(color):
    board = Board()
    king = None
    for fig in board.figures_on_board:
        if fig.color != color:
            continue

        for i in range(8):
            for j in range(8):
                target = board.get_figure(i, j)
                if target is not None and target.color == color:
                    continue

                saved_target = target
                saved_old_x = fig.old_x
                saved_old_y = fig.old_y

                fig.legal_move = False
                fig.move(chess_board, i, j)

                if fig.legal_move:
                    for f in board.figures_on_board:
                        if f.name == 'K' and f.color == color:
                            king = f
                            break

                    if not king.is_checked():
                        fig.old_x = saved_old_x
                        fig.old_y = saved_old_y
                        chess_board[saved_old_x][saved_old_y] = fig.name
                        if saved_target is None:
                            chess_board[i][j] = '-'
                        else:
                            chess_board[i][j] = saved_target.name
                        if saved_target is not None:
                            board.figures_on_board.append(saved_target)
                        return False

                    fig.old_x = saved_old_x
                    fig.old_y = saved_old_y
                    chess_board[saved_old_x][saved_old_y] = fig.name
                    chess_board[i][j] = '-' if saved_target is None else saved_target.name
                    if saved_target is not None:
                        board.figures_on_board.append(saved_target)

    return True


def promote_pawn(pawn):
    while True:
        promotion = input(f"Promote pawn to (Q, R, B, N): ").upper()
        if promotion in ['Q', 'R', 'B', 'N']:
            break
        print("Invalid choice. Please enter Q, R, B, or N")

    Board().figures_on_board.remove(pawn)

    x, y = pawn.old_x, pawn.old_y
    color = pawn.color

    if promotion == 'Q':
        Queen(Board(), x, y, color)
    elif promotion == 'R':
        Rook(Board(), x, y, color)
    elif promotion == 'B':
        Bishop(Board(), x, y, color)
    elif promotion == 'N':
        Knight(Board(), x, y, color)

    chess_board[x][y] = promotion

chess_board = [
    ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'],
    ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
    ['-', '-', '-', '-', '-', '-', '-', '-'],
    ['-', '-', '-', '-', '-', '-', '-', '-'],
    ['-', '-', '-', '-', '-', '-', '-', '-'],
    ['-', '-', '-', '-', '-', '-', '-', '-'],
    ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
    ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
]

Board(chess_board)

wking = King(Board(), 7, 4, 'w')
bking = King(Board(), 0, 4, 'b')
wqueen = Queen(Board(), 7, 3, 'w')
bqueen = Queen(Board(), 0, 3, 'b')
wknight1 = Knight(Board(), 7, 1, 'w')
wknight2 = Knight(Board(), 7, 6, 'w')
bknight1 = Knight(Board(), 0, 1, 'b')
bknight2 = Knight(Board(), 0, 6, 'b')
wrook1 = Rook(Board(), 7, 0, 'w')
wrook2 = Rook(Board(), 7, 7, 'w')
brook1 = Rook(Board(), 0, 0, 'b')
brook2 = Rook(Board(), 0, 7, 'b')
wbishop1 = Bishop(Board(), 7, 2, 'w')
wbishop2 = Bishop(Board(), 7, 5, 'w')
bbishop1 = Bishop(Board(), 0, 2, 'b')
bbishop2 = Bishop(Board(), 0, 5, 'b')
wpawns = [Pawn(Board(), 6, i, 'w') for i in range(8)]
bpawns = [Pawn(Board(), 1, i, 'b') for i in range(8)]

turn = 0


while True:
    legal_moves = False
    Board().print_board()
    exited = False

    while True:
        input_string = input("Input the piece, the old position and the new position (ex. a5 c4): ").split(' ')

        piece = input_string[0]
        if piece == "exit":
            exited = True
            break

        if len(input_string) < 2:
            print("Invalid input format. Try again.")
            continue

        coords = Board().get_coords(input_string)
        if coords is None:
            print("Invalid input. Try again")
            continue

        oldX, oldY, newX, newY = coords
        figure = Board().get_figure(oldX, oldY)

        if figure is None:
            print("There is no piece in that square")
            continue



        if (turn % 2 == 0 and figure.color != 'w') or (turn % 2 != 0 and figure.color != 'b'):
            if turn % 2 == 0 and Board().get_figure(oldX, oldY).color != 'w':
                print("It is white's move")
            elif turn % 2 != 0 and Board().get_figure(oldX, oldY).color != 'b':
                print("It is black's move")
            continue

        figure.legal_move = False
        old_x = figure.old_x
        old_y = figure.old_y
        target_piece = Board().get_figure(newX, newY)

        figure.move(chess_board, newX, newY)

        if figure.legal_move:

            if figure.name != 'P':
                if turn % 2 == 0:
                    for p in bpawns:
                        p.under_en_passant = False
                else:
                    for p in wpawns:
                        p.under_en_passant = False


            king = None
            for f in Board().figures_on_board:
                if f.name == 'K' and f.color == figure.color:
                    king = f
                    break

            if king is not None and king.is_checked():
                print("You cannot make this move because your king would be in check!")

                chess_board[newX][newY] = '-' if target_piece is None else target_piece.name
                chess_board[old_x][old_y] = figure.name
                figure.old_x = old_x
                figure.old_y = old_y

                if target_piece is not None:
                    Board().figures_on_board.append(target_piece)

                figure.legal_move = False
                continue

            legal_moves = True
            break
        else:
            print("Move was not legal. Try again.")

    if legal_moves:
        if isinstance(figure, Pawn) and figure.should_promote():
            promote_pawn(figure)
        turn += 1
        if turn % 2 == 0:
            if wking.is_checked():
                if is_checkmate('w'):
                    Board().print_board()
                    print("Checkmate! Black wins!")
                    break
                else:
                    print("Check!")
        else:
            if bking.is_checked():
                if is_checkmate('b'):
                    Board().print_board()
                    print("Checkmate! White wins!")
                    break
                else:
                    print("Check!")

    if exited:
        print("Exiting...")
        break