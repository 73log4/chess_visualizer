from enum import Enum
import pygame
from itertools import product
import subprocess


BOT_EXE = "bot"


BLACK_SQUARE_COLOR = (170, 170, 170)
WHITE_SQUARE_COLOR = (225, 225, 225)

CLICK_1_WHITE_COLOR = (130, 130, 200)
CLICK_1_BLACK_COLOR = (130, 130, 200)

SCREEN_SIZE = (600, 600)
SQUARE_SIZE = SCREEN_SIZE[0] // 8


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


class Player(Enum):
    Black = 0
    White = 1


class Move(Enum):
    Normal = 0
    CastleRight = 1
    CastleLeft = 2
    PromotionQueen = 3
    PromotionKnight = 4
    EnPassant = 5


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


class ChessBoard:

    def __init__(self, start_board):
        self.board = start_board

    def __setitem__(self, index, value):
        self.board[index[0]][index[1]] = value

    def __getitem__(self, index):
        return self.board[index[0]][index[1]]

    def play_move(self, move):
        # move is a 3 tuple: (type, src, dst)
        self[move[2]] = self[move[1]]
        self[move[1]] = Piece.Empty

    def possible_moves(self, pos):
        pass


class ChessViz:

    def __init__(self, start_board, player_white, player_black, turn=Player.White):
        self.chess_board = ChessBoard(start_board)
        self.turn = turn
        self.player_white = player_white
        self.player_black = player_black

        self.screen = None

        self.click_1 = None
        self.click_2 = None

    def start_game(self):
        pygame.init()

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
                    elif self.click_2 == None:
                        if self.click_1 == pos:
                            self.click_1 = None
                        else:
                            self.click_2 = pos
                    
            if self.turn == Player.White:
                if self.player_white != None:
                    move = self.player_white(self.chess_board.board)
                    self.chess_board.play_move(move)
                    self.turn = Player.Black

                    print(f"white bot: {move[0]} -> {move[1]}")
                elif self.click_2 != None:
                    move = (Move.Normal, self.click_1, self.click_2)
                    self.click_1, self.click_2 = None, None
                    self.chess_board.play_move(move)
                    self.turn = Player.Black

                    print(f"user: {move[0]} -> {move[1]}")
            else:
                if self.player_black != None:
                    move = self.player_black(self.chess_board.board)
                    self.chess_board.play_move(move)
                    self.turn = Player.White

                    print(f"black bot: {move[0]} -> {move[1]}")
                elif self.click_2 != None:
                    move = (Move.Normal, self.click_1, self.click_2)
                    self.click_1, self.click_2 = None, None
                    self.chess_board.play_move(move)
                    self.turn = Player.White

                    print(f"user: {move[0]} -> {move[1]}")

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

        # draw pieces
        for i in range(8):
            for j in range(8):
                piece = self.chess_board[7 - i, j]
                if piece != Piece.Empty:
                    self.screen.blit(PIECE_IMG[piece], (j * SQUARE_SIZE, i * SQUARE_SIZE))


def bot(board):
    new_board = transform_board(board)
    board_str = ' '.join([' '.join([str(p).zfill(2) for p in r]) for r in new_board])
    r = str(subprocess.call(BOT_EXE + ' ' + board_str, stdin=None, stdout=None, stderr=None, shell=True))[1:]
    move = ((int(r[0]), int(r[1])), (int(r[2]), int(r[3])))
    return (Move.Normal, *move)


def main():
    viz = ChessViz(START_BOARD, bot, None)
    viz.start_game()
    # print(bot(viz.chess_board.board))


if __name__ == "__main__":
    main()
