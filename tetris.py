import pygame
import random

# Constants
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30
BOARD_WIDTH = SCREEN_WIDTH // BLOCK_SIZE
BOARD_HEIGHT = SCREEN_HEIGHT // BLOCK_SIZE

# Colors
COLORS = [
    (0, 0, 0),    # Black
    (255, 0, 0),  # Red
    (0, 255, 0),  # Green
    (0, 0, 255),  # Blue
    (255, 255, 0),# Yellow
    (255, 165, 0),# Orange
    (128, 0, 128),# Purple
    (0, 255, 255) # Cyan
]

SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],# O
    [[0, 1, 0], [1, 1, 1]], # T
    [[1, 1, 0], [0, 1, 1]], # S
    [[0, 1, 1], [1, 1, 0]], # Z
    [[1, 0, 0], [1, 1, 1]], # L
    [[0, 0, 1], [1, 1, 1]]  # J
]

class Tetris:
    def __init__(self):
        self.board = [[0] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.score = 0
        self.game_over = False

    def new_piece(self):
        shape = random.choice(SHAPES)
        color = random.randint(1, len(COLORS) - 1)
        return {'shape': shape, 'color': color, 'x': BOARD_WIDTH // 2 - len(shape[0]) // 2, 'y': 0}

    def rotate_piece(self):
        self.current_piece['shape'] = [list(row) for row in zip(*self.current_piece['shape'][::-1])]

    def move_piece(self, dx, dy):
        self.current_piece['x'] += dx
        self.current_piece['y'] += dy
        if self.check_collision():
            self.current_piece['x'] -= dx
            self.current_piece['y'] -= dy
            if dy > 0:
                self.merge_piece()
                self.clear_lines()
                self.current_piece = self.next_piece
                self.next_piece = self.new_piece()
                if self.check_collision():
                    self.game_over = True

    def check_collision(self):
        for y, row in enumerate(self.current_piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    board_x = self.current_piece['x'] + x
                    board_y = self.current_piece['y'] + y
                    if board_x < 0 or board_x >= BOARD_WIDTH or board_y >= BOARD_HEIGHT or (board_y >= 0 and self.board[board_y][board_x]):
                        return True
        return False

    def merge_piece(self):
        for y, row in enumerate(self.current_piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    self.board[self.current_piece['y'] + y][self.current_piece['x'] + x] = self.current_piece['color']

    def clear_lines(self):
        lines_to_clear = [i for i, row in enumerate(self.board) if all(cell != 0 for cell in row)]
        for i in lines_to_clear:
            del self.board[i]
            self.board.insert(0, [0] * BOARD_WIDTH)
            self.score += 1

    def draw_board(self, screen):
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                color = COLORS[self.board[y][x]]
                pygame.draw.rect(screen, color, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
        for y, row in enumerate(self.current_piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    color = COLORS[self.current_piece['color']]
                    pygame.draw.rect(screen, color, ((self.current_piece['x'] + x) * BLOCK_SIZE, (self.current_piece['y'] + y) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)

    def run(self):
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        clock = pygame.time.Clock()
        while not self.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.move_piece(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        self.move_piece(1, 0)
                    elif event.key == pygame.K_DOWN:
                        self.move_piece(0, 1)
                    elif event.key == pygame.K_UP:
                        self.rotate_piece()

            self.move_piece(0, 1)
            screen.fill((0, 0, 0))
            self.draw_board(screen)
            pygame.display.flip()
            clock.tick(10)

if __name__ == "__main__":
    Tetris().run()