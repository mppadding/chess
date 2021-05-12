from enum import Enum
import config, helper

def isPieceOpposite(piece1, piece2):
    return piece2 != None and piece2.color != piece1.color

def findIndexByPosition(pieces, position):
    for i in range(len(pieces)):
        if pieces[i].position == position:
            return i

    return None

def findPieceByPosition(pieces, position):
    for p in pieces:
        if p.position == position:
            return p

    return None

def isInCheck(gamestate):
    black_attack = []
    white_attack = []

# List of all relative positions that a piece can move/strike towards.
# Note that there is no matrix for pawn, due to it being able to strike where it cannot move
# and that it can move 2 tiles if the pawn has not moved yet.
matrices = {
    "bishop": [[(-x, x) for x in range(1, 8)], [(x, x) for x in range(1, 8)], [(-x, -x) for x in range(1, 8)], [(x, -x) for x in range(1, 8)]],
    "knight": [
            (-1, 2), (1, 2),
            (-2, 1), (2, 1),
            (-2, -1), (2, -1),
            (-1, -2), (1, -2),
    ],
    "rook": [[(-x, 0) for x in range(1, 8)], [(x, 0) for x in range(1, 8)], [(0, x) for x in range(1, 8)], [(0, -x) for x in range(1, 8)]],
    "queen": [],
    "king": [
        (-1,  1), (0,  1), (1,  1),
        (-1,  0),          (1,  0),
        (-1, -1), (0, -1), (1, -1)
    ],
    "castle": []
}

matrices["queen"] = matrices["bishop"] + matrices["rook"]

class Pieces(Enum):
    PAWN = 0
    BISHOP = 1
    KNIGHT = 2
    ROOK = 3
    QUEEN = 4
    KING = 5

class Color(Enum):
    BLACK = 0
    WHITE = 1

class Piece(object):
    def __init__(self, position: tuple, piece: Pieces, color: Color, sprite):
        self.position = position
        self.piece = piece
        self.color = color
        self.sprite = sprite

        self.active = True
        self.moves = []

    def calculatePermutableMoves(self, gamestate):
        print("This function must be implemented by a piece")
    
    def getPermutableMoves(self):
        return self.moves

    def canMove(self, position: tuple, other):
        print("This function must be implemented by a piece")
        return False

    def draw(self, surface):
        x_pos = self.position[0] * config.window["tile_size"]
        y_pos = (7 - self.position[1]) * config.window["tile_size"]

        surface.blit(self.sprite, (x_pos, y_pos))

    def move(self, position):
        self.position = position

class Pawn(Piece):
    def __init__(self, position: tuple, color: Color, sprite):
        super().__init__(position, Pieces.PAWN, color, sprite)

        self.moved = False
        self.canPromote = False

    def move(self, position):
        super().move(position)
        self.moved = True

        # Either up for white, or down for black
        direction_mult = 1 if self.color == Color.WHITE else -1

        # Furthest it can go, should promote
        if (direction_mult == 1 and self.position[1] == 7) or (direction_mult == -1 and self.position[1] == 0):
            self.canPromote = True

    def calculatePermutableMoves(self, gamestate):
        pieces = gamestate["pieces"]
        # Either up for white, or down for black
        direction_mult = 1 if self.color == Color.WHITE else -1
        moves = []

        # Furthest it can go, should promote
        if (direction_mult == 1 and self.position[1] == 7) or (direction_mult == -1 and self.position[1] == 0):
            return moves

        # Check tile forwards of pawns direction
        if findPieceByPosition(pieces, (self.position[0], self.position[1] + direction_mult)) == None:
            moves.append((self.position[0], self.position[1] + direction_mult))

            if not self.moved and findPieceByPosition(pieces, (self.position[0], self.position[1] + direction_mult * 2)) == None:
                moves.append((self.position[0], self.position[1] + direction_mult * 2))

        # Check if can attack left
        if self.position[0] - 1 >= 0:
            attack_piece = findPieceByPosition(pieces, (self.position[0] - 1, self.position[1] + direction_mult))

            # Check if the attacked piece is not none and the color is opposite
            if isPieceOpposite(self, attack_piece):
                moves.append((self.position[0] - 1, self.position[1] + direction_mult))

        # Check if can attack right
        if self.position[0] + 1 < 8:
            attack_piece = findPieceByPosition(pieces, (self.position[0] + 1, self.position[1] + direction_mult))

            # Check if the attacked piece is not none and the color is opposite
            if isPieceOpposite(self, attack_piece):
                moves.append((self.position[0] + 1, self.position[1] + direction_mult))

        self.moves = moves

class Bishop(Piece):
    def __init__(self, position: tuple, color: Color, sprite):
        super().__init__(position, Pieces.BISHOP, color, sprite)

    def calculatePermutableMoves(self, gamestate):
        pieces = gamestate["pieces"]
        moves = []

        for m in matrices["bishop"]:
            mat = helper.applyMatrixTransform(self.position, m, (0, 7, 0, 7))

            for i in mat:
                check_piece = findPieceByPosition(pieces, i)

                if check_piece == None:
                    moves.append(i)
                else:
                    if isPieceOpposite(self, check_piece):
                        moves.append(i)
                    break

        self.moves = moves

class Knight(Piece):
    def __init__(self, position: tuple, color: Color, sprite):
        super().__init__(position, Pieces.KNIGHT, color, sprite)

    def calculatePermutableMoves(self, gamestate):
        pieces = gamestate["pieces"]
        moves = []

        matrix = helper.applyMatrixTransform(self.position, matrices["knight"], (0, 7, 0, 7))

        for i in matrix:
            check_piece = findPieceByPosition(pieces, i)

            if check_piece == None or isPieceOpposite(self, check_piece):
                moves.append(i)

        self.moves = moves

class Rook(Piece):
    def __init__(self, position: tuple, color: Color, sprite):
        super().__init__(position, Pieces.ROOK, color, sprite)
        self.moved = False

    def calculatePermutableMoves(self, gamestate):
        pieces = gamestate["pieces"]
        moves = []

        for m in matrices["rook"]:
            mat = helper.applyMatrixTransform(self.position, m, (0, 7, 0, 7))

            for i in mat:
                check_piece = findPieceByPosition(pieces, i)

                if check_piece == None:
                    moves.append(i)
                else:
                    if isPieceOpposite(self, check_piece):
                        moves.append(i)
                    break

        self.moves = moves

class Queen(Piece):
    def __init__(self, position: tuple, color: Color, sprite):
        super().__init__(position, Pieces.QUEEN, color, sprite)

    def calculatePermutableMoves(self, gamestate):
        pieces = gamestate["pieces"]
        moves = []

        for m in matrices["queen"]:
            mat = helper.applyMatrixTransform(self.position, m, (0, 7, 0, 7))

            for i in mat:
                check_piece = findPieceByPosition(pieces, i)

                if check_piece == None:
                    moves.append(i)
                else:
                    if isPieceOpposite(self, check_piece):
                        moves.append(i)
                    break

        self.moves = moves

class King(Piece):
    def __init__(self, position: tuple, color: Color, sprite):
        super().__init__(position, Pieces.KING, color, sprite)
        self.moved = False

    def calculatePermutableMoves(self, gamestate):
        pieces = gamestate["pieces"]
        moves = []

        mat = helper.applyMatrixTransform(self.position, matrices["king"], (0, 7, 0, 7))

        for i in mat:
            check_piece = findPieceByPosition(pieces, i)

            if check_piece == None:
                moves.append(i)
            else:
                if isPieceOpposite(self, check_piece):
                    moves.append(i)

        canCastleMove = True
        isBlack = self.color == Color.BLACK
        castleYOffset = 7 if isBlack else 0

        # King side castle
        if gamestate["castle"][0+(isBlack*2)] == 1:
            checks = [(5, castleYOffset), (6, castleYOffset)]
            # Check if clear line between pieces
            
            for i in checks:
                check_piece = findPieceByPosition(pieces, i)

                if check_piece != None:
                    canCastleMove = False
                    break
            
            if canCastleMove:
                moves.append((6, castleYOffset))

        # Queen side castle      
        if gamestate["castle"][1+(isBlack*2)] == 1:
            checks = [(1, castleYOffset), (2, castleYOffset), (3, castleYOffset)]
            for i in checks:
                check_piece = findPieceByPosition(pieces, i)

                if check_piece != None:
                    canCastleMove = False
                    break
            
            if canCastleMove:
                moves.append((2, castleYOffset))
            

        self.moves = moves