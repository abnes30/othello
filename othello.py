import pygame
import copy
import sys
import time  # Added for AI delay

# Constants
WIDTH, HEIGHT = 600, 600
ROWS, COLS = 8, 8
CELL_SIZE = WIDTH // COLS
EMPTY = '.'
BLACK = 'B'
WHITE = 'W'
DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

# Colors
GREEN = (34, 139, 34)
WHITE_COLOR = (255, 255, 255)
BLACK_COLOR = (0, 0, 0)
GRAY = (50, 50, 50)
RED = (255, 0, 0)
LIGHT_GREEN = (0, 255, 0)
DARK_GRAY = (30, 30, 30)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Othello (Reversi)")
font = pygame.font.Font(None, 50)
small_font = pygame.font.Font(None, 40)

# Initialize Board
def create_board():
    board = [[EMPTY] * COLS for _ in range(ROWS)]
    board[3][3], board[3][4] = WHITE, BLACK
    board[4][3], board[4][4] = BLACK, WHITE
    return board

# Draw the board
def draw_board(board):
    screen.fill(GREEN)
    for row in range(ROWS):
        for col in range(COLS):
            rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, BLACK_COLOR, rect, 2)
            if board[row][col] == BLACK:
                pygame.draw.circle(screen, BLACK_COLOR, (col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3)
            elif board[row][col] == WHITE:
                pygame.draw.circle(screen, WHITE_COLOR, (col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3)
    pygame.display.flip()

# Get board coordinates from mouse click
def get_board_pos(pos):
    x, y = pos
    return y // CELL_SIZE, x // CELL_SIZE

# Check if a move is valid
def is_valid_move(board, row, col, player):
    if board[row][col] != EMPTY:
        return False
    opponent = BLACK if player == WHITE else WHITE
    for dr, dc in DIRECTIONS:
        r, c = row + dr, col + dc
        found_opponent = False
        while 0 <= r < ROWS and 0 <= c < COLS and board[r][c] == opponent:
            found_opponent = True
            r += dr
            c += dc
        if found_opponent and 0 <= r < ROWS and 0 <= c < COLS and board[r][c] == player:
            return True
    return False

# Get all valid moves
def get_valid_moves(board, player):
    return [(r, c) for r in range(ROWS) for c in range(COLS) if is_valid_move(board, r, c, player)]

# Make a move
def make_move(board, row, col, player):
    if not is_valid_move(board, row, col, player):
        return None
    new_board = copy.deepcopy(board)
    new_board[row][col] = player
    opponent = BLACK if player == WHITE else WHITE

    for dr, dc in DIRECTIONS:
        r, c = row + dr, col + dc
        captured = []
        while 0 <= r < ROWS and 0 <= c < COLS and new_board[r][c] == opponent:
            captured.append((r, c))
            r += dr
            c += dc
        if captured and 0 <= r < ROWS and 0 <= c < COLS and new_board[r][c] == player:
            for cr, cc in captured:
                new_board[cr][cc] = player
    return new_board

# Minimax with Alpha-Beta Pruning
def minimax(board, depth, alpha, beta, maximizing_player, player):
    if depth == 0 or not get_valid_moves(board, player):  # Base case
        return sum(row.count(player) for row in board), None

    best_move = None
    opponent = BLACK if player == WHITE else WHITE

    if maximizing_player:
        max_eval = float('-inf')
        for move in get_valid_moves(board, player):
            new_board = make_move(board, move[0], move[1], player)
            evaluation, _ = minimax(new_board, depth - 1, alpha, beta, False, opponent)
            if evaluation > max_eval:
                max_eval = evaluation
                best_move = move
            alpha = max(alpha, evaluation)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for move in get_valid_moves(board, player):
            new_board = make_move(board, move[0], move[1], player)
            evaluation, _ = minimax(new_board, depth - 1, alpha, beta, True, opponent)
            if evaluation < min_eval:
                min_eval = evaluation
                best_move = move
            beta = min(beta, evaluation)
            if beta <= alpha:
                break
        return min_eval, best_move

# AI chooses the best move
def ai_move(board, player, depth=3):
    _, best_move = minimax(board, depth, float('-inf'), float('inf'), True, player)
    return best_move

# Show game over dialog box
def show_end_dialog(winner, black_score, white_score):
    dialog_width, dialog_height = 400, 250
    dialog_x, dialog_y = (WIDTH - dialog_width) // 2, (HEIGHT - dialog_height) // 2

    while True:
        pygame.draw.rect(screen, DARK_GRAY, (dialog_x, dialog_y, dialog_width, dialog_height), border_radius=15)
        pygame.draw.rect(screen, WHITE_COLOR, (dialog_x, dialog_y, dialog_width, dialog_height), 5, border_radius=15)

        title_text = f"{winner} WINS!"
        screen.blit(font.render(title_text, True, WHITE_COLOR), (dialog_x + 100, dialog_y + 30))

        score_text = f"Black: {black_score}  White: {white_score}"
        screen.blit(small_font.render(score_text, True, WHITE_COLOR), (dialog_x + 100, dialog_y + 80))

        exit_button = pygame.Rect(dialog_x + 40, dialog_y + 160, 140, 50)
        restart_button = pygame.Rect(dialog_x + 220, dialog_y + 160, 140, 50)

        pygame.draw.rect(screen, RED, exit_button, border_radius=10)
        pygame.draw.rect(screen, LIGHT_GREEN, restart_button, border_radius=10)

        screen.blit(small_font.render("Exit", True, BLACK_COLOR), (exit_button.x + 50, exit_button.y + 12))
        screen.blit(small_font.render("Restart", True, BLACK_COLOR), (restart_button.x + 30, restart_button.y + 12))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if exit_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
                elif restart_button.collidepoint(event.pos):
                    return True  # Indicate restart

# Main game loop
def play_game():
    board = create_board()
    current_player = BLACK

    while True:
        draw_board(board)
        if not get_valid_moves(board, current_player):
            current_player = BLACK if current_player == WHITE else WHITE
            if not get_valid_moves(board, current_player):
                break

        if current_player == BLACK:
            time.sleep(0.5)  # AI move delay
            move = ai_move(board, BLACK)
            if move:
                board = make_move(board, move[0], move[1], BLACK)
            current_player = WHITE
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    row, col = get_board_pos(event.pos)
                    if is_valid_move(board, row, col, WHITE):
                        board = make_move(board, row, col, WHITE)
                        current_player = BLACK

    if show_end_dialog("Black" if sum(row.count(BLACK) for row in board) > sum(row.count(WHITE) for row in board) else "White", 
                       sum(row.count(BLACK) for row in board), 
                       sum(row.count(WHITE) for row in board)):
        play_game()

play_game()
