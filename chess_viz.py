from enum import Enum
import pygame
from itertools import product
import subprocess


BOT_EXE = "bot"


BLACK_SQUARE_COLOR = (170, 170, 170)
WHITE_SQUARE_COLOR = (225, 225, 225)

CLICK_1_WHITE_COLOR = (50 + 7, 50 + 95, 50 + 90)
CLICK_1_BLACK_COLOR = (50 + 7, 50 + 95, 50 + 90)

WHITE_POSSIBLE_MOVE_COLOR = (50 + 7, 50 + 95, 50 + 90)
BLACK_POSSIBLE_MOVE_COLOR = WHITE_POSSIBLE_MOVE_COLOR

SCREEN_SIZE = (600, 600)
SQUARE_SIZE = SCREEN_SIZE[0] // 8

POSSIBLE_MOVE_CIRCLE_RADIUS_EMPTY = SQUARE_SIZE // 6
POSSIBLE_MOVE_CIRCLE_RADIUS_NON_EMPTY = SQUARE_SIZE // 2 - 5


class Piece(Enum):
    Empty = -1
    BP = 0
    BB = 1
    BK = 2
    BR = 3
    BQ = 4
    BN = 5
    WP = 6
    WB = 7
    WK = 8
    WR = 9
    WQ = 10
    WN = 11

    def player(self):
        if self == Piece.Empty:
            return None
        return Player.Black if self in [Piece.BP, Piece.BN, Piece.BB, Piece.BR, Piece.BQ, Piece.BK] else Player.White 


class Player(Enum):
    Black = 0
    White = 1


class MoveType(Enum):
    Normal = 0
    CastleRight = 1
    CastleLeft = 2
    PromotionQueen = 3
    PromotionKnight = 4
    EnPassant = 5

    def __str__(self):
        return "-"


INT_PIECE_FORMAT = {
    Piece.Empty: 0,
    Piece.BP: 1,
    Piece.BN: 2,
    Piece.BB: 3,
    Piece.BR: 5,
    Piece.BQ: 6,
    Piece.BK: 4,
    Piece.WP: 7,
    Piece.WN: 8,
    Piece.WB: 9,
    Piece.WR: 11,
    Piece.WQ: 12,
    Piece.WK: 10,
}


PIECE_TYPE = "light"
PIECE_IMG = {
    Piece.BP: pygame.image.load("images/" + PIECE_TYPE + "/bp.png"),
    Piece.BN: pygame.image.load("images/" + PIECE_TYPE + "/bn.png"),
    Piece.BB: pygame.image.load("images/" + PIECE_TYPE + "/bb.png"),
    Piece.BR: pygame.image.load("images/" + PIECE_TYPE + "/br.png"),
    Piece.BQ: pygame.image.load("images/" + PIECE_TYPE + "/bq.png"),
    Piece.BK: pygame.image.load("images/" + PIECE_TYPE + "/bk.png"),
    Piece.WP: pygame.image.load("images/" + PIECE_TYPE + "/wp.png"),
    Piece.WN: pygame.image.load("images/" + PIECE_TYPE + "/wn.png"),
    Piece.WB: pygame.image.load("images/" + PIECE_TYPE + "/wb.png"),
    Piece.WR: pygame.image.load("images/" + PIECE_TYPE + "/wr.png"),
    Piece.WQ: pygame.image.load("images/" + PIECE_TYPE + "/wq.png"),
    Piece.WK: pygame.image.load("images/" + PIECE_TYPE + "/wk.png"),
}


for p in PIECE_IMG:
    PIECE_IMG[p] = pygame.transform.scale(PIECE_IMG[p], (SQUARE_SIZE, SQUARE_SIZE))


START_BOARD = [
    [Piece.WR, Piece.WN, Piece.WB, Piece.WQ, Piece.WK, Piece.WB, Piece.WN, Piece.WR],
    [Piece.WP] * 8,
    [Piece.Empty] * 8,
    [Piece.Empty] * 8,
    [Piece.Empty] * 8,
    [Piece.Empty] * 8,
    [Piece.BP] * 8,
    [Piece.BR, Piece.BN, Piece.BB, Piece.BQ, Piece.BK, Piece.BB, Piece.BN, Piece.BR],
]


def transform_board(board):
        return [[INT_PIECE_FORMAT[p] for p in r] for r in board]


class Vec2:

    def __init__(self, i, j):
        self.i = i
        self.j = j

    def __str__(self):
        return f"({self.i}, {self.j})"

    def __add__(self, other):
        return Vec2(self.i + other.i, self.j + other.j)

    def is_legal(self):
        return abs(self.i - 3.5) < 4 and abs(self.j - 3.5) < 4  # ya, thats bad coding


VERTICAL_DIRECTIONS = [Vec2(1, 0), Vec2(0, 1), Vec2(-1, 0), Vec2(0, -1)]
DIAGONAL_DIRECTIONS = [Vec2(1, 1), Vec2(-1, 1), Vec2(1, -1), Vec2(-1, -1)]
KNIGHT_DIRECTIONS = [Vec2(2, 1), Vec2(2, -1), Vec2(-2, 1), Vec2(-2, -1), Vec2(1, 2), Vec2(1, -2), Vec2(-1, 2), Vec2(-1, -2)]
ALL_POS = [Vec2(i, j) for i, j in product(range(8), repeat=2)]


class Move:

    def __init__(self, t: MoveType, p1: Vec2, p2: Vec2):
        self.type = t
        self.src = p1
        self.dst = p2

    def __str__(self):
        return f"({self.type}, {self.src}, {self.dst})"


class ChessBoard:

    def __init__(self, start_board):
        self.board = start_board

    def __setitem__(self, pos: Vec2, value):
        self.board[pos.i][pos.j] = value

    def __getitem__(self, pos: Vec2):
        return self.board[pos.i][pos.j]

    def play_move(self, move: Move):
        # move is a 3 tuple: (type, src, dst)
        self[move.dst] = self[move.src]
        self[move.src] = Piece.Empty

    def reverse_move(self, move: Move):
        # move is a 3 tuple: (type, src, dst)
        pass

    def possible_moves(self, pos: Vec2, player: Player):
        p = self[pos]

        if p == Piece.Empty:
            return []
        elif p == Piece.WK and player == Player.White:
            return self.k_possible_moves(pos, player)
        elif p == Piece.BK and player == Player.Black:
            return self.k_possible_moves(pos, player)
        elif p == Piece.WQ and player == Player.White:
            return self.q_possible_moves(pos, player)
        elif p == Piece.BQ and player == Player.Black:
            return self.q_possible_moves(pos, player)
        elif p == Piece.WR and player == Player.White:
            return self.r_possible_moves(pos, player)
        elif p == Piece.BR and player == Player.Black:
            return self.r_possible_moves(pos, player)
        elif p == Piece.WB and player == Player.White:
            return self.b_possible_moves(pos, player)
        elif p == Piece.BB and player == Player.Black:
            return self.b_possible_moves(pos, player)
        elif p == Piece.WN and player == Player.White:
            return self.n_possible_moves(pos, player)
        elif p == Piece.BN and player == Player.Black:
            return self.n_possible_moves(pos, player)
        elif p == Piece.WP and player == Player.White:
            return self.p_possible_moves(pos, player)
        elif p == Piece.BP and player == Player.Black:
            return self.p_possible_moves(pos, player)
        
        return []

    def k_possible_moves(self, pos: Vec2, player: Player):
        moves = []

        for d in VERTICAL_DIRECTIONS + DIAGONAL_DIRECTIONS:
            p = pos + d
            if p.is_legal() and self[p].player() != player:
                m = Move(MoveType.Normal, pos, p)
                moves.append(m)

        return moves

    def q_possible_moves(self, pos: Vec2, player: Player):
        moves = []

        for d in VERTICAL_DIRECTIONS + DIAGONAL_DIRECTIONS:
            p = pos + d
            while p.is_legal() and self[p] == Piece.Empty:
                if p.is_legal():
                    m = Move(MoveType.Normal, pos, p)
                    moves.append(m)
                p = p + d
            if p.is_legal() and self[p].player() != player:
                m = Move(MoveType.Normal, pos, p)
                moves.append(m)

        return moves

    def r_possible_moves(self, pos: Vec2, player: Player):
        moves = []

        for d in VERTICAL_DIRECTIONS:
            p = pos + d
            while p.is_legal() and self[p] == Piece.Empty:
                if p.is_legal():
                    m = Move(MoveType.Normal, pos, p)
                    moves.append(m)
                p = p + d
            if p.is_legal() and self[p].player() != player:
                m = Move(MoveType.Normal, pos, p)
                moves.append(m)

        return moves

    def b_possible_moves(self, pos: Vec2, player: Player):
        moves = []

        for d in DIAGONAL_DIRECTIONS:
            p = pos + d
            while p.is_legal() and self[p] == Piece.Empty:
                if p.is_legal():
                    m = Move(MoveType.Normal, pos, p)
                    moves.append(m)
                p = p + d
            if p.is_legal() and self[p].player() != player:
                m = Move(MoveType.Normal, pos, p)
                moves.append(m)

        return moves

    def n_possible_moves(self, pos, player: Player):
        moves = []

        for d in KNIGHT_DIRECTIONS:
            p = pos + d
            if p.is_legal() and self[p].player() != player:
                m = Move(MoveType.Normal, pos, p)
                moves.append(m)
        return moves

    def p_possible_moves(self, pos, player: Player):
        moves = []

        d = Vec2(1, 0) if player == Player.White else Vec2(-1, 0)
        if self[pos + d] == Piece.Empty:
            moves.append(Move(MoveType.Normal, pos, pos + d))
            if self[(pos + d) + d] == Piece.Empty and (pos.i == (1 if player == Player.White else 6)):
                moves.append(Move(MoveType.Normal, pos, pos + d + d))

        new_p = pos + (Vec2(1, 1) if player == Player.White else Vec2(-1, 1))
        if new_p.is_legal():
            piece = self[new_p]
            if piece.player() != None and piece.player() != player:
                moves.append(Move(MoveType.Normal, pos, new_p))

        new_p = pos + (Vec2(1, -1) if player == Player.White else Vec2(-1, -1))
        if new_p.is_legal():
            piece = self[new_p]
            if piece.player() != None and piece.player() != player:
                moves.append(Move(MoveType.Normal, pos, new_p))

        return moves

class ChessViz:

    def __init__(self, start_board, player_white, player_black, turn=Player.White):
        self.chess_board = ChessBoard(start_board)
        self.turn = turn
        self.player_white = player_white
        self.player_black = player_black

        self.screen = None

        self.click_1 = None
        self.click_2 = None

        self.possible_moves = []

    def start_game(self):
        pygame.init()
        pygame.display.set_caption('ChessMonster Visualizer')

        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        self.draw_board()
        pygame.display.update()
        while True:
            # add potential delay here
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit(0)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    pos = (7 - pos[1] // SQUARE_SIZE, pos[0] // SQUARE_SIZE)
                    if self.click_1 == None:
                        self.click_1 = pos
                        self.possible_moves = self.chess_board.possible_moves(Vec2(*pos), self.turn)
                    elif self.click_2 == None:
                        if self.click_1 == pos:
                            self.click_1 = None
                            self.possible_moves = []
                        else:
                            possible_dst = [(m.dst.i, m.dst.j) for m in self.possible_moves]
                            if pos in possible_dst:
                                self.click_2 = pos
                            else:
                                self.click_1 = None
                                self.possible_moves = []
                    
            if self.turn == Player.White:
                played = True
                if self.player_white != None:  # bot
                    move = self.player_white(self.chess_board.board)
                elif self.click_2 != None:  # user input
                    move = Move(MoveType.Normal, Vec2(*self.click_1), Vec2(*self.click_2))
                    self.click_1, self.click_2 = None, None
                else:
                    played = False

                if played:
                    self.chess_board.play_move(move)
                    self.turn = Player.Black
                    self.possible_moves = []

                    print(f"white: {move.src} -> {move.dst}")
            else:
                played = True
                if self.player_black != None:  # bot
                    move = self.player_black(self.chess_board.board)
                elif self.click_2 != None:  # user input
                    move = Move(MoveType.Normal, Vec2(*self.click_1), Vec2(*self.click_2))
                    self.click_1, self.click_2 = None, None
                else:
                    played = False

                if played:
                    self.chess_board.play_move(move)
                    self.turn = Player.White
                    self.possible_moves = []

                    print(f"black: {move.src} -> {move.dst}")

            self.draw_board()
            pygame.display.update()
            
    def draw_board(self):
        # draw board squares
        self.screen.fill(BLACK_SQUARE_COLOR)
        for i in range(8):
            for j in range(8):
                square = (j * SQUARE_SIZE, (7 - i) * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                if (i + j) % 2 == 0:
                    if (i, j) == self.click_1:
                        color = CLICK_1_WHITE_COLOR
                    else:
                        color = WHITE_SQUARE_COLOR
                else:
                    if (i, j) == self.click_1:
                        color = CLICK_1_BLACK_COLOR
                    else:
                        color = BLACK_SQUARE_COLOR
                pygame.draw.rect(self.screen, color, square)

        # draw possible moves
        move_dst = [(m.dst.i, m.dst.j) for m in self.possible_moves]
        for pos in move_dst:
            center = (pos[1] * SQUARE_SIZE + SQUARE_SIZE // 2, (7 - pos[0]) * SQUARE_SIZE + SQUARE_SIZE // 2)
            color = WHITE_POSSIBLE_MOVE_COLOR if (pos[0] + pos[1]) % 2 == 0 else BLACK_POSSIBLE_MOVE_COLOR
            radius = POSSIBLE_MOVE_CIRCLE_RADIUS_EMPTY if self.chess_board[Vec2(*pos)] == Piece.Empty else POSSIBLE_MOVE_CIRCLE_RADIUS_NON_EMPTY
            pygame.draw.circle(self.screen, color , center, radius)

        # draw pieces
        for i in range(8):
            for j in range(8):
                piece = self.chess_board[Vec2(7 - i, j)]
                if piece != Piece.Empty:
                    self.screen.blit(PIECE_IMG[piece], (j * SQUARE_SIZE, i * SQUARE_SIZE))


def bot(board):
    new_board = transform_board(board)
    board_str = ' '.join([' '.join([str(p).zfill(2) for p in r]) for r in new_board])
    r = str(subprocess.call(BOT_EXE + ' ' + board_str, stdin=None, stdout=None, stderr=None, shell=True))[1:]
    move = ((int(r[0]), int(r[1])), (int(r[2]), int(r[3])))
    return Move(MoveType.Normal, Vec2(*move[0]), Vec2(*move[1]))


def main():
    viz = ChessViz(START_BOARD, None, None)
    viz.start_game()
    # print(bot(viz.chess_board.board))


if __name__ == "__main__":
    main()
