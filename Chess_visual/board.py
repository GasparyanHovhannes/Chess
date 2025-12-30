import tkinter as tk
from PIL import Image, ImageTk
from logic import Board, is_checkmate, promote_pawn, King, Pawn
import logic

TILE_SIZE = 100
BOARD_SIZE = 8
LIGHT_COLOR = "#EEEED2"
DARK_COLOR = "#769656"

root = tk.Tk()
root.title("Chess Board")

canvas = tk.Canvas(root, width=TILE_SIZE * BOARD_SIZE, height=TILE_SIZE * BOARD_SIZE)
canvas.pack()

promote_canvas = tk.Canvas(root, width=4*TILE_SIZE, height=TILE_SIZE, bg="lightgray")
promote_window = None
promote_figures = []
promoted_fig = None

images = {}
selected_square = None
highlight_rect = []
legal_squares = []
highlight_circles = []
hover_square = None
turn = 0

def load_images():
    for f in Board().figures_on_board:
            image = Image.open(f.image).resize((TILE_SIZE, TILE_SIZE)).convert("RGBA")
            images[f"{f.color}{f.name}"] = ImageTk.PhotoImage(image)

    image = Image.open("./assets/dot.png").resize((TILE_SIZE//2, TILE_SIZE//2)).convert("RGBA")
    images["dot"] = ImageTk.PhotoImage(image)


def draw_pieces():
    for fig in Board().figures_on_board:
        x = fig.old_y * TILE_SIZE
        y = fig.old_x * TILE_SIZE
        key = f"{fig.color}{fig.name}"
        if key in images:
            canvas.create_image(x, y, anchor=tk.NW, image=images[key])


def draw_board():
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            x1 = col * TILE_SIZE + 2
            y1 = row * TILE_SIZE + 2
            x2 = x1 + TILE_SIZE
            y2 = y1 + TILE_SIZE
            color = LIGHT_COLOR if (row + col) % 2 == 0 else DARK_COLOR
            canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
    for row in range(BOARD_SIZE):
        y = row * TILE_SIZE + 11
        if row%2==0:
            canvas.create_text(10, y, text=str(8 - row), font=("Arial", 12), fill=DARK_COLOR)
        else:
            canvas.create_text(10, y, text=str(8 - row), font=("Arial", 12), fill=LIGHT_COLOR)

    for col in range(BOARD_SIZE):
        x = col * TILE_SIZE + 90
        if col%2==0:
            canvas.create_text(x, BOARD_SIZE * TILE_SIZE - 12, text=chr(ord('a') + col), font=("Arial", 12), fill=LIGHT_COLOR)
        else:
            canvas.create_text(x, BOARD_SIZE * TILE_SIZE - 12, text=chr(ord('a') + col), font=("Arial", 12), fill=DARK_COLOR)
    draw_pieces()


def highlight_square(row, col, color, canv):
    global highlight_rect

    width = 4
    x1 = col * TILE_SIZE + width/2 + 2
    y1 = row * TILE_SIZE + width/2 + 2
    x2 = x1 + TILE_SIZE - width
    y2 = y1 + TILE_SIZE - width
    rect = canv.create_rectangle(x1, y1, x2, y2, outline=color, width=width)
    highlight_rect.append(rect)
    return rect
    

def draw_moves(piece):
    global highlight_circles, highlight_rect

    for square in piece.get_legal_moves():
        p = Board().get_figure(square[0], square[1])
        if p is not None:
            highlight_square(square[0], square[1], "red", canvas)
        else:
            x = square[1] * TILE_SIZE + TILE_SIZE//4
            y = square[0] * TILE_SIZE + TILE_SIZE//4
            highlight_circles.append(canvas.create_image(x, y, anchor=tk.NW, image=images["dot"]))


def clear_highlights():
    global highlight_rect, highlight_circles

    for c in highlight_circles:
        canvas.delete(c)

    for r in highlight_rect:
        canvas.delete(r)

    highlight_circles.clear()
    highlight_rect.clear()

def draw_promote_figures(color):
    global promote_figures

    q = logic.Queen(0, 0, color)
    r = logic.Rook(0,1,color)
    b = logic.Bishop(0,2,color)
    n = logic.Knight(0,3,color)
    promote_figures.append(q)
    promote_figures.append(r)
    promote_figures.append(b)
    promote_figures.append(n)

    for f in promote_figures:
        Board().figures_on_board.remove(f)
        x = f.old_y * TILE_SIZE
        y = f.old_x * TILE_SIZE
        key = f"{f.color}{f.name}"
        if key in images:
            promote_canvas.create_image(x, y, anchor=tk.NW, image=images[key])

def draw_promote_window(row, col, color):
    global promote_window, promoted_fig

    if col > 4:
        col -= 4

    x = col * TILE_SIZE + 2
    y = row * TILE_SIZE + 2

    promote_window = canvas.create_window(x, y, window=promote_canvas, anchor="nw")

    draw_promote_figures(color)


def on_hover(event):
    global hover_square

    if hover_square is not None:
        promote_canvas.delete(hover_square)

    row = event.y // TILE_SIZE
    col = event.x // TILE_SIZE

    hover_square = highlight_square(row, col, 'black', promote_canvas)


def on_click(event):
    global turn, legal_squares, selected_square, promoted_fig

    legal_squares.clear()


    row = event.y // TILE_SIZE
    col = event.x // TILE_SIZE


    if selected_square is None:
        figure = Board().get_figure(row, col)
        
        if figure is not None:
            if (turn % 2 == 0 and figure.color == 'w') or (turn % 2 != 0 and figure.color == 'b'):
                selected_square = (row, col)
                draw_moves(figure)
                highlight_square(row, col, "black", canvas)
    else:
        figure = Board().get_figure(selected_square[0], selected_square[1])
        
        figure.legal_move = False
        old_x = figure.old_x
        old_y = figure.old_y
        
        target_piece = Board().get_figure(row, col)

        if target_piece == figure: #Undo move
            selected_square = None
            clear_highlights()
        else:
            if (row, col) in figure.get_attacks():
                figure.move(row, col)

                if figure.legal_move:
                    king = Board().find_king(figure.color)
                    if king is not None and king.is_checked():
                        figure.old_x = old_x
                        figure.old_y = old_y
                        if target_piece is not None:
                            Board().figures_on_board.append(target_piece)
                    else: #if the move was legal, we change the turn and draw the board
                        selected_square = None
                        if isinstance(figure, Pawn) and figure.should_promote():
                            promoted_fig = figure
                            draw_promote_window(figure.old_x, figure.old_y, figure.color)
                        draw_board()
                        turn += 1
                        Board().clear_en_passant_flags('w' if turn % 2 == 0 else 'b')
                        if turn % 2 == 0:
                            if logic.wking.is_checked() and is_checkmate('w'):
                                print("Checkmate! Black wins!")
                                return
                        else:
                            if logic.bking.is_checked() and is_checkmate('b'):
                                print("Checkmate! White wins!")
                                return

                            

def on_click_promote_window(event):
    global promote_figures, promoted_fig

    row = event.y // TILE_SIZE
    col = event.x // TILE_SIZE

    for f in promote_figures:
        if f.old_x == row and f.old_y == col:
            Board().promote_decision = f

    promote_figures.clear()
    canvas.delete(promote_window)
    promote_pawn(promoted_fig)
    draw_board()


canvas.bind("<Button-1>", on_click)
promote_canvas.bind("<Button-1>", on_click_promote_window)
promote_canvas.bind("<Motion>", on_hover)

load_images()
draw_board()

root.mainloop()
