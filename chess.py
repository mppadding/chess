# TODO:
#   - Fix castling if in check
#   - En passant
#   - Stalemate Draw
#   - Threefold repetition
#   - 50 Move rule Draw
#   - Check
#   - Prevent king from moving into check

import pygame, random
from pygame.locals import *

import config, pieces, helper

pygame.init()
 
displaysurface = pygame.display.set_mode((config.window["width"], config.window["height"]))
pygame.display.set_caption(config.window["title"])

font = pygame.font.SysFont('Times New Roman', 16)

numbers = [font.render(str(i), False, (0, 0, 0)) for i in range(1, 9)]

gamestate = {
    "pieces": [],
    "run": True,
    "selected": (-1, -1),
    "white_next": True,
    "check": [0, 0],
    "half_moves": 0,
    # White Kingside, White Queenside, Black Kingside, Black Queenside
    "castle": [1, 1, 1, 1],
}

def drawBoard(surf):
    for y in range(8):
        for x in range(8):
            x_pos = x * config.window["tile_size"]
            y_pos = (7 - y) * config.window["tile_size"]

            if (y % 2 and not x % 2) or (not y % 2 and x % 2):
                if gamestate["selected"] == (x, y):
                    pygame.draw.rect(surf, config.window["selected"][1], pygame.Rect(x_pos, y_pos, config.window["tile_size"], config.window["tile_size"]))
                else:
                    pygame.draw.rect(surf, config.window["colors"][1], pygame.Rect(x_pos, y_pos, config.window["tile_size"], config.window["tile_size"]))
            elif gamestate["selected"] == (x, y):
                pygame.draw.rect(surf, config.window["selected"][0], pygame.Rect(x_pos, y_pos, config.window["tile_size"], config.window["tile_size"]))

def drawMoves(surf):
    sel = pieces.findPieceByPosition(gamestate["pieces"], gamestate["selected"])

    if sel == None:
        return

    moves = sel.getPermutableMoves()

    for m in moves:
        x_pos = m[0] * (config.window["tile_size"]) + (config.window["tile_size"] / 2)
        y_pos = (7 - m[1]) * (config.window["tile_size"]) + (config.window["tile_size"] / 2)

        pygame.draw.circle(surf, "#FF0000", (x_pos, y_pos), config.window["tile_size"] / 10)

def move(position):
    sel = pieces.findPieceByPosition(gamestate["pieces"], gamestate["selected"])
    moves = sel.getPermutableMoves()

    if position in moves:
        index = pieces.findIndexByPosition(gamestate["pieces"], position)

        if index != None:
            del gamestate["pieces"][index]

        sel.move(position)
        
        if sel.piece == pieces.Pieces.PAWN and sel.canPromote:
            sel_in = pieces.findIndexByPosition(gamestate["pieces"], position)

            gamestate["pieces"][sel_in] = pieces.Queen(position, sel.color, sprites["white" if sel.color == pieces.Color.WHITE else "black"]["queen"])

        if sel.piece == pieces.Pieces.KING:
            isBlack = 1 if sel.color == pieces.Color.BLACK else 0
            castleYOffset = 7 if isBlack else 0

            if position == (6, castleYOffset) and gamestate["castle"][0+(isBlack*2)]:
                # Castling king side, move rook as well.
                rook = pieces.findPieceByPosition(gamestate["pieces"], (7, castleYOffset))
                rook.move((5, castleYOffset))

            if position == (2, castleYOffset) and gamestate["castle"][1+(isBlack*2)]:
                # Castling queen side, move rook as well.
                rook = pieces.findPieceByPosition(gamestate["pieces"], (0, castleYOffset))
                rook.move((3, castleYOffset))

        # Prevent castling if king is moved
        if sel.piece == pieces.Pieces.KING:
            if sel.color == pieces.Color.WHITE:
                gamestate["castle"][0] = 0
                gamestate["castle"][1] = 0
            else:
                gamestate["castle"][2] = 0
                gamestate["castle"][3] = 0

        # Prevent castling a side if rook is moved
        if sel.piece == pieces.Pieces.ROOK:
            if sel.color == pieces.Color.WHITE:
                if gamestate["selected"] == (7, 0):
                    gamestate["castle"][0] = 0
                if gamestate["selected"] == (0, 0):
                    gamestate["castle"][1] = 0
            else:
                if gamestate["selected"] == (7, 7):
                    gamestate["castle"][2] = 0
                if gamestate["selected"] == (0, 7):
                    gamestate["castle"][3] = 0

        gamestate["selected"] = (-1, -1)
        gamestate["white_next"] = not gamestate["white_next"]

        for p in gamestate["pieces"]:
            p.calculatePermutableMoves(gamestate)
        
sprites = {
    "black": {
        "pawn": pygame.image.load('sprites/black_pawn.png'),
        "rook": pygame.image.load('sprites/black_rook.png'),
        "knight": pygame.image.load('sprites/black_knight.png'),
        "bishop": pygame.image.load('sprites/black_bishop.png'),
        "king": pygame.image.load('sprites/black_king.png'),
        "queen": pygame.image.load('sprites/black_queen.png')
    }, 
    "white": {
        "pawn": pygame.image.load('sprites/white_pawn.png'),
        "rook": pygame.image.load('sprites/white_rook.png'),
        "knight": pygame.image.load('sprites/white_knight.png'),
        "bishop": pygame.image.load('sprites/white_bishop.png'),
        "king": pygame.image.load('sprites/white_king.png'),
        "queen": pygame.image.load('sprites/white_queen.png')
    }
}

fen_lookup = {
    'p': [pieces.Pawn, pieces.Color.BLACK, ["black", "pawn"]],
    'n': [pieces.Knight, pieces.Color.BLACK, ["black", "knight"]],
    'b': [pieces.Bishop, pieces.Color.BLACK, ["black", "bishop"]],
    'r': [pieces.Rook, pieces.Color.BLACK, ["black", "rook"]],
    'q': [pieces.Queen, pieces.Color.BLACK, ["black", "queen"]],
    'k': [pieces.King, pieces.Color.BLACK, ["black", "king"]],

    'P': [pieces.Pawn, pieces.Color.WHITE, ["white", "pawn"]],
    'N': [pieces.Knight, pieces.Color.WHITE, ["white", "knight"]],
    'B': [pieces.Bishop, pieces.Color.WHITE, ["white", "bishop"]],
    'R': [pieces.Rook, pieces.Color.WHITE, ["white", "rook"]],
    'Q': [pieces.Queen, pieces.Color.WHITE, ["white", "queen"]],
    'K': [pieces.King, pieces.Color.WHITE, ["white", "king"]],
}

# Function to parse FEN (Forsyth-Edwards Notation) and return a gamestate
def parseFEN(gamestate, str):
    state = gamestate

    arr = str.split(' ')
    positions = arr[0].split('/')
    state["white_next"] = (arr[1] == 'w')
    castling = arr[2]
    passant = arr[3]
    state["half_moves"] = arr[4]
    fullmoves = arr[5]

    for rank in range(8):
        r = 7 - rank
        rank_str = positions[rank]

        f = 0

        for c in rank_str:
            if c.isdigit():
                f += int(c) - 1
            elif c in fen_lookup:
                pc = fen_lookup[c]
                state["pieces"].append(pc[0]((f, r), pc[1], sprites[pc[2][0]][pc[2][1]]))
            
            f += 1
            if f == 8:
                continue
    
    return gamestate

gamestate = parseFEN(gamestate, "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

for p in gamestate["pieces"]:
    p.calculatePermutableMoves(gamestate)

while gamestate["run"]:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            gamestate["run"] = False

        if event.type == pygame.MOUSEBUTTONUP:
            mouse_pos = pygame.mouse.get_pos()
            tile_clicked = helper.getTileFromPosition(mouse_pos)

            selected_piece = pieces.findPieceByPosition(gamestate["pieces"], tile_clicked)
            if selected_piece != None:
                if (gamestate["white_next"] and selected_piece.color == pieces.Color.WHITE) or (not gamestate["white_next"] and selected_piece.color == pieces.Color.BLACK):
                    gamestate["selected"] = tile_clicked
                elif gamestate["selected"] != (-1, -1):
                    move(tile_clicked)
            elif gamestate["selected"] != (-1, -1):
                    move(tile_clicked)

    displaysurface.fill(config.window["colors"][0])

    drawBoard(displaysurface)

    for p in gamestate["pieces"]:
        p.draw(displaysurface)

    drawMoves(displaysurface)

    pygame.display.update()

pygame.quit()