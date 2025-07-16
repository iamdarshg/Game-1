import pygame
import sys
import pickle
import os
import random

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GAME_SAVE_FILE = "game_console_save.pkl"

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

# --- Base Game Class ---
class BaseGame:
    """
    Base class for all mini-games. Provides common methods for initialization,
    event handling, updating, drawing, and state management.
    """
    def __init__(self, console):
        self.console = console
        self.running = True

    def handle_event(self, event):
        """Handle Pygame events for the specific game."""
        pass

    def update(self, dt):
        """Update game logic based on delta time."""
        pass

    def draw(self, screen):
        """Draw game elements on the screen."""
        pass

    def get_state(self):
        """Return a dictionary representing the current state of the game."""
        return {}

    def set_state(self, state):
        """Restore the game state from a dictionary."""
        pass

    def reset(self):
        """Reset the game to its initial state."""
        pass

# --- Pong Game ---
class PongGame(BaseGame):
    def __init__(self, console):
        super().__init__(console)
        self.paddle_width = 20
        self.paddle_height = 100
        self.ball_size = 20
        self.paddle_speed = 7
        self.ball_speed_x = 5 * random.choice([-1, 1])
        self.ball_speed_y = 5 * random.choice([-1, 1])
        self.player_score = 0
        self.ai_score = 0
        self.max_score = 5
        self.game_over = False
        self.reset() # Initial setup

    def reset(self):
        """Resets Pong game state."""
        self.player_paddle_y = (SCREEN_HEIGHT - self.paddle_height) // 2
        self.ai_paddle_y = (SCREEN_HEIGHT - self.paddle_height) // 2
        self.ball_x = SCREEN_WIDTH // 2 - self.ball_size // 2
        self.ball_y = SCREEN_HEIGHT // 2 - self.ball_size // 2
        self.ball_speed_x = 5 * random.choice([-1, 1])
        self.ball_speed_y = 5 * random.choice([-1, 1])
        self.player_score = 0
        self.ai_score = 0
        self.game_over = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.console.set_active_game("menu")
            elif event.key == pygame.K_r and self.game_over:
                self.reset()

    def update(self, dt):
        if self.game_over:
            return

        # Player paddle movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.player_paddle_y -= self.paddle_speed
        if keys[pygame.K_DOWN]:
            self.player_paddle_y += self.paddle_speed
        self.player_paddle_y = max(0, min(self.player_paddle_y, SCREEN_HEIGHT - self.paddle_height))

        # Ball movement
        self.ball_x += self.ball_speed_x
        self.ball_y += self.ball_speed_y

        # Ball collision with top/bottom walls
        if self.ball_y <= 0 or self.ball_y >= SCREEN_HEIGHT - self.ball_size:
            self.ball_speed_y *= -1

        # Ball collision with paddles
        player_paddle_rect = pygame.Rect(50, self.player_paddle_y, self.paddle_width, self.paddle_height)
        ai_paddle_rect = pygame.Rect(SCREEN_WIDTH - 50 - self.paddle_width, self.ai_paddle_y, self.paddle_width, self.paddle_height)
        ball_rect = pygame.Rect(self.ball_x, self.ball_y, self.ball_size, self.ball_size)

        if ball_rect.colliderect(player_paddle_rect) or ball_rect.colliderect(ai_paddle_rect):
            self.ball_speed_x *= -1
            # Add a slight random variation to y-speed for more dynamic play
            self.ball_speed_y += random.uniform(-0.5, 0.5)
            self.ball_speed_y = max(-10, min(10, self.ball_speed_y)) # Cap speed

        # Ball out of bounds (scoring)
        if self.ball_x < 0:
            self.ai_score += 1
            self._reset_ball()
        elif self.ball_x > SCREEN_WIDTH:
            self.player_score += 1
            self._reset_ball()

        # AI paddle movement (simple AI)
        if self.ai_paddle_y + self.paddle_height / 2 < self.ball_y:
            self.ai_paddle_y += self.paddle_speed * 0.8 # Slightly slower than player
        elif self.ai_paddle_y + self.paddle_height / 2 > self.ball_y:
            self.ai_paddle_y -= self.paddle_speed * 0.8
        self.ai_paddle_y = max(0, min(self.ai_paddle_y, SCREEN_HEIGHT - self.paddle_height))

        # Check for game over
        if self.player_score >= self.max_score or self.ai_score >= self.max_score:
            self.game_over = True

    def _reset_ball(self):
        """Resets ball position and direction after a score."""
        self.ball_x = SCREEN_WIDTH // 2 - self.ball_size // 2
        self.ball_y = SCREEN_HEIGHT // 2 - self.ball_size // 2
        self.ball_speed_x = 5 * random.choice([-1, 1])
        self.ball_speed_y = 5 * random.choice([-1, 1])

    def draw(self, screen):
        screen.fill(BLACK)
        pygame.draw.rect(screen, WHITE, (50, self.player_paddle_y, self.paddle_width, self.paddle_height))
        pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH - 50 - self.paddle_width, self.ai_paddle_y, self.paddle_width, self.paddle_height))
        pygame.draw.ellipse(screen, WHITE, (self.ball_x, self.ball_y, self.ball_size, self.ball_size))
        pygame.draw.aaline(screen, WHITE, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT))

        font = pygame.font.Font(None, 74)
        player_text = font.render(str(self.player_score), True, WHITE)
        ai_text = font.render(str(self.ai_score), True, WHITE)
        screen.blit(player_text, (SCREEN_WIDTH // 4, 20))
        screen.blit(ai_text, (SCREEN_WIDTH * 3 // 4 - ai_text.get_width(), 20))

        if self.game_over:
            game_over_font = pygame.font.Font(None, 100)
            winner = "Player" if self.player_score >= self.max_score else "AI"
            game_over_text = game_over_font.render(f"{winner} Wins!", True, YELLOW)
            restart_text = pygame.font.Font(None, 40).render("Press R to Restart or ESC to Menu", True, LIGHT_GRAY)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

    def get_state(self):
        return {
            "player_paddle_y": self.player_paddle_y,
            "ai_paddle_y": self.ai_paddle_y,
            "ball_x": self.ball_x,
            "ball_y": self.ball_y,
            "ball_speed_x": self.ball_speed_x,
            "ball_speed_y": self.ball_speed_y,
            "player_score": self.player_score,
            "ai_score": self.ai_score,
            "game_over": self.game_over
        }

    def set_state(self, state):
        self.player_paddle_y = state.get("player_paddle_y", (SCREEN_HEIGHT - self.paddle_height) // 2)
        self.ai_paddle_y = state.get("ai_paddle_y", (SCREEN_HEIGHT - self.paddle_height) // 2)
        self.ball_x = state.get("ball_x", SCREEN_WIDTH // 2 - self.ball_size // 2)
        self.ball_y = state.get("ball_y", SCREEN_HEIGHT // 2 - self.ball_size // 2)
        self.ball_speed_x = state.get("ball_speed_x", 5 * random.choice([-1, 1]))
        self.ball_speed_y = state.get("ball_speed_y", 5 * random.choice([-1, 1]))
        self.player_score = state.get("player_score", 0)
        self.ai_score = state.get("ai_score", 0)
        self.game_over = state.get("game_over", False)


# --- Minesweeper Game ---
class MinesweeperGame(BaseGame):
    def __init__(self, console):
        super().__init__(console)
        self.rows = 10
        self.cols = 10
        self.num_mines = 15
        self.cell_size = 40
        self.board_offset_x = (SCREEN_WIDTH - self.cols * self.cell_size) // 2
        self.board_offset_y = (SCREEN_HEIGHT - self.rows * self.cell_size) // 2
        self.board = []  # Stores (is_mine, num_adjacent_mines, is_revealed, is_flagged)
        self.game_over = False
        self.win = False
        self.reset()

    def reset(self):
        """Resets Minesweeper game state."""
        self.board = [[(False, 0, False, False) for _ in range(self.cols)] for _ in range(self.rows)]
        self._place_mines()
        self._calculate_adjacent_mines()
        self.game_over = False
        self.win = False

    def _place_mines(self):
        mines_placed = 0
        while mines_placed < self.num_mines:
            r = random.randint(0, self.rows - 1)
            c = random.randint(0, self.cols - 1)
            if not self.board[r][c][0]:  # If not already a mine
                self.board[r][c] = (True, 0, False, False) # Mark as mine
                mines_placed += 1

    def _calculate_adjacent_mines(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if not self.board[r][c][0]: # If not a mine
                    count = 0
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            if dr == 0 and dc == 0:
                                continue
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < self.rows and 0 <= nc < self.cols and self.board[nr][nc][0]:
                                count += 1
                    self.board[r][c] = (False, count, False, False) # Update adjacent count

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.console.set_active_game("menu")
            elif event.key == pygame.K_r and (self.game_over or self.win):
                self.reset()
        elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_over and not self.win:
            mx, my = event.pos
            # Convert mouse coords to board coords
            c = (mx - self.board_offset_x) // self.cell_size
            r = (my - self.board_offset_y) // self.cell_size

            if 0 <= r < self.rows and 0 <= c < self.cols:
                is_mine, adj_mines, is_revealed, is_flagged = self.board[r][c]

                if event.button == 1:  # Left click (reveal)
                    if not is_revealed and not is_flagged:
                        if is_mine:
                            self.game_over = True
                            self._reveal_all_mines()
                        else:
                            self._reveal_cell(r, c)
                            self._check_win()
                elif event.button == 3:  # Right click (flag)
                    if not is_revealed:
                        self.board[r][c] = (is_mine, adj_mines, is_revealed, not is_flagged)

    def _reveal_cell(self, r, c):
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            return
        is_mine, adj_mines, is_revealed, is_flagged = self.board[r][c]

        if is_revealed or is_flagged:
            return

        self.board[r][c] = (is_mine, adj_mines, True, is_flagged) # Set revealed to True

        if adj_mines == 0 and not is_mine:
            # Recursively reveal neighbors if 0 adjacent mines
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    self._reveal_cell(r + dr, c + dc)

    def _reveal_all_mines(self):
        for r in range(self.rows):
            for c in range(self.cols):
                is_mine, adj_mines, is_revealed, is_flagged = self.board[r][c]
                if is_mine:
                    self.board[r][c] = (is_mine, adj_mines, True, is_flagged) # Reveal mine

    def _check_win(self):
        unrevealed_non_mines = 0
        for r in range(self.rows):
            for c in range(self.cols):
                is_mine, _, is_revealed, _ = self.board[r][c]
                if not is_mine and not is_revealed:
                    unrevealed_non_mines += 1
        if unrevealed_non_mines == 0:
            self.win = True
            self.game_over = True

    def update(self, dt):
        pass # Minesweeper logic is mostly event-driven

    def draw(self, screen):
        screen.fill(GRAY)
        font = pygame.font.Font(None, 30)

        for r in range(self.rows):
            for c in range(self.cols):
                x = self.board_offset_x + c * self.cell_size
                y = self.board_offset_y + r * self.cell_size
                cell_rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
                is_mine, adj_mines, is_revealed, is_flagged = self.board[r][c]

                if is_revealed:
                    pygame.draw.rect(screen, LIGHT_GRAY, cell_rect)
                    pygame.draw.rect(screen, BLACK, cell_rect, 1) # Border
                    if is_mine:
                        pygame.draw.circle(screen, RED, cell_rect.center, self.cell_size // 3)
                    elif adj_mines > 0:
                        text_color = BLACK
                        if adj_mines == 1: text_color = BLUE
                        elif adj_mines == 2: text_color = GREEN
                        elif adj_mines == 3: text_color = RED
                        elif adj_mines == 4: text_color = PURPLE
                        elif adj_mines == 5: text_color = ORANGE
                        text_surface = font.render(str(adj_mines), True, text_color)
                        screen.blit(text_surface, text_surface.get_rect(center=cell_rect.center))
                else:
                    pygame.draw.rect(screen, WHITE, cell_rect)
                    pygame.draw.rect(screen, BLACK, cell_rect, 1) # Border
                    if is_flagged:
                        # Draw a simple flag (triangle)
                        pygame.draw.polygon(screen, RED, [(x + self.cell_size * 0.2, y + self.cell_size * 0.2),
                                                          (x + self.cell_size * 0.8, y + self.cell_size * 0.4),
                                                          (x + self.cell_size * 0.2, y + self.cell_size * 0.6)])
                        pygame.draw.line(screen, BLACK, (x + self.cell_size * 0.2, y + self.cell_size * 0.2),
                                                       (x + self.cell_size * 0.2, y + self.cell_size * 0.8), 2)


        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150)) # Semi-transparent black
            screen.blit(overlay, (0, 0))

            game_over_font = pygame.font.Font(None, 80)
            message = "You Win!" if self.win else "Game Over!"
            message_color = GREEN if self.win else RED
            message_text = game_over_font.render(message, True, message_color)
            restart_text = pygame.font.Font(None, 40).render("Press R to Restart or ESC to Menu", True, LIGHT_GRAY)

            screen.blit(message_text, message_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)))
            screen.blit(restart_text, restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)))

    def get_state(self):
        return {
            "board": self.board,
            "game_over": self.game_over,
            "win": self.win
        }

    def set_state(self, state):
        self.board = state.get("board", [[(False, 0, False, False) for _ in range(self.cols)] for _ in range(self.rows)])
        self.game_over = state.get("game_over", False)
        self.win = state.get("win", False)
        # If board is empty (e.g., first load), re-initialize
        if not self.board or not self.board[0]:
            self.reset()


# --- Jump King Game (Simplified) ---
class JumpKingGame(BaseGame):
    def __init__(self, console):
        super().__init__(console)
        self.player_size = 30
        self.player_x = SCREEN_WIDTH // 2 - self.player_size // 2
        self.player_y = SCREEN_HEIGHT - 100 - self.player_size # Start above bottom
        self.player_vel_y = 0
        self.gravity = 0.5
        self.jump_power = -12
        self.on_ground = False
        self.charging_jump = False
        self.jump_charge_time = 0
        self.max_jump_charge = 60 # Frames
        self.game_over = False
        self.win = False

        self.platforms = []
        self.goal_platform = None
        self.reset()

    def reset(self):
        """Resets Jump King game state and generates a new level."""
        self.player_x = SCREEN_WIDTH // 2 - self.player_size // 2
        self.player_y = SCREEN_HEIGHT - 100 - self.player_size
        self.player_vel_y = 0
        self.on_ground = False
        self.charging_jump = False
        self.jump_charge_time = 0
        self.game_over = False
        self.win = False
        self._generate_platforms()

    def _generate_platforms(self):
        self.platforms = []
        # Starting platform
        self.platforms.append(pygame.Rect(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 100, 100, 20))

        # Generate a few random platforms
        current_y = SCREEN_HEIGHT - 200
        for _ in range(5): # 5 platforms
            width = random.randint(60, 150)
            height = 20
            x = random.randint(50, SCREEN_WIDTH - width - 50)
            y = current_y - random.randint(80, 150) # Platforms are above each other
            self.platforms.append(pygame.Rect(x, y, width, height))
            current_y = y

        # Goal platform at the top
        goal_width = 80
        goal_height = 20
        goal_x = random.randint(50, SCREEN_WIDTH - goal_width - 50)
        goal_y = 50 # Near the top
        self.goal_platform = pygame.Rect(goal_x, goal_y, goal_width, goal_height)
        self.platforms.append(self.goal_platform)


    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.console.set_active_game("menu")
            elif event.key == pygame.K_r and (self.game_over or self.win):
                self.reset()
            elif event.key == pygame.K_SPACE and self.on_ground and not self.game_over and not self.win:
                self.charging_jump = True
                self.jump_charge_time = 0
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE and self.charging_jump and not self.game_over and not self.win:
                self.charging_jump = False
                # Apply jump power based on charge time
                jump_strength = self.jump_power * (self.jump_charge_time / self.max_jump_charge)
                self.player_vel_y = max(self.jump_power, jump_strength) # Cap at full jump power
                self.on_ground = False # Player is now in air

    def update(self, dt):
        if self.game_over or self.win:
            return

        # Jump charge logic
        if self.charging_jump:
            self.jump_charge_time = min(self.max_jump_charge, self.jump_charge_time + 1)

        # Apply gravity
        self.player_vel_y += self.gravity
        self.player_y += self.player_vel_y

        # Basic horizontal movement (optional, for simple platforming)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player_x -= 3
        if keys[pygame.K_RIGHT]:
            self.player_x += 3

        # Keep player within horizontal bounds
        self.player_x = max(0, min(self.player_x, SCREEN_WIDTH - self.player_size))

        player_rect = pygame.Rect(self.player_x, self.player_y, self.player_size, self.player_size)
        self.on_ground = False

        # Platform collision
        for platform in self.platforms:
            if player_rect.colliderect(platform):
                # If falling and hit top of platform
                if self.player_vel_y > 0 and player_rect.bottom <= platform.top + abs(self.player_vel_y):
                    self.player_y = platform.top - self.player_size
                    self.player_vel_y = 0
                    self.on_ground = True
                    # Check for win condition
                    if platform == self.goal_platform:
                        self.win = True
                        self.game_over = True
                # If hitting bottom of platform (jumping into it)
                elif self.player_vel_y < 0 and player_rect.top >= platform.bottom - abs(self.player_vel_y):
                    self.player_y = platform.bottom
                    self.player_vel_y = 0 # Stop upward movement

        # Check for falling off screen (Game Over)
        if self.player_y > SCREEN_HEIGHT:
            self.game_over = True

    def draw(self, screen):
        screen.fill(BLUE) # Sky background

        # Draw platforms
        for platform in self.platforms:
            color = GREEN
            if platform == self.goal_platform:
                color = YELLOW # Goal platform is yellow
            pygame.draw.rect(screen, color, platform)

        # Draw player
        pygame.draw.rect(screen, RED, (self.player_x, self.player_y, self.player_size, self.player_size))

        # Draw jump charge bar
        if self.charging_jump:
            bar_width = 100
            bar_height = 10
            fill_width = (self.jump_charge_time / self.max_jump_charge) * bar_width
            pygame.draw.rect(screen, GRAY, (self.player_x + self.player_size // 2 - bar_width // 2, self.player_y - 20, bar_width, bar_height), 2) # Outline
            pygame.draw.rect(screen, GREEN, (self.player_x + self.player_size // 2 - bar_width // 2, self.player_y - 20, fill_width, bar_height)) # Fill

        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150)) # Semi-transparent black
            screen.blit(overlay, (0, 0))

            game_over_font = pygame.font.Font(None, 80)
            message = "You Win!" if self.win else "Game Over!"
            message_color = GREEN if self.win else RED
            message_text = game_over_font.render(message, True, message_color)
            restart_text = pygame.font.Font(None, 40).render("Press R to Restart or ESC to Menu", True, LIGHT_GRAY)

            screen.blit(message_text, message_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)))
            screen.blit(restart_text, restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)))


    def get_state(self):
        # Store platforms as list of rect tuples (x, y, w, h) for serialization
        platforms_data = [(p.x, p.y, p.width, p.height) for p in self.platforms]
        goal_platform_data = (self.goal_platform.x, self.goal_platform.y, self.goal_platform.width, self.goal_platform.height) if self.goal_platform else None

        return {
            "player_x": self.player_x,
            "player_y": self.player_y,
            "player_vel_y": self.player_vel_y,
            "on_ground": self.on_ground,
            "charging_jump": self.charging_jump,
            "jump_charge_time": self.jump_charge_time,
            "platforms": platforms_data,
            "goal_platform": goal_platform_data,
            "game_over": self.game_over,
            "win": self.win
        }

    def set_state(self, state):
        self.player_x = state.get("player_x", SCREEN_WIDTH // 2 - self.player_size // 2)
        self.player_y = state.get("player_y", SCREEN_HEIGHT - 100 - self.player_size)
        self.player_vel_y = state.get("player_vel_y", 0)
        self.on_ground = state.get("on_ground", False)
        self.charging_jump = state.get("charging_jump", False)
        self.jump_charge_time = state.get("jump_charge_time", 0)
        self.game_over = state.get("game_over", False)
        self.win = state.get("win", False)

        # Reconstruct platforms from tuples
        platforms_data = state.get("platforms")
        if platforms_data:
            self.platforms = [pygame.Rect(x, y, w, h) for x, y, w, h in platforms_data]
        else:
            self.platforms = [] # Reset if no data

        goal_platform_data = state.get("goal_platform")
        if goal_platform_data:
            self.goal_platform = pygame.Rect(*goal_platform_data)
            # Ensure goal platform is in the list if it was loaded
            if self.goal_platform not in self.platforms: # Check by value, not object identity
                # A simple way to re-add if missing, assuming it's the last one
                if not self.platforms or self.platforms[-1] != self.goal_platform:
                    self.platforms.append(self.goal_platform)
        else:
            self.goal_platform = None

        # If no platforms were loaded, generate a new level
        if not self.platforms:
            self._generate_platforms()


# --- Save/Load Manager ---
class SaveLoadManager:
    """Handles saving and loading of game states using pickle."""
    def __init__(self, filename):
        self.filename = filename

    def save_game(self, game_state_data):
        """
        Saves the current game state data to a file.
        game_state_data is a dictionary: {"game_type": str, "state": dict}
        """
        try:
            with open(self.filename, 'wb') as f:
                pickle.dump(game_state_data, f)
            print(f"Game saved successfully to {self.filename}")
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False

    def load_game(self):
        """
        Loads game state data from a file.
        Returns {"game_type": str, "state": dict} or None if no save file.
        """
        if not os.path.exists(self.filename):
            print("No save file found.")
            return None
        try:
            with open(self.filename, 'rb') as f:
                game_state_data = pickle.load(f)
            print(f"Game loaded successfully from {self.filename}")
            return game_state_data
        except Exception as e:
            print(f"Error loading game: {e}")
            # If there's an error loading, it might be a corrupted file, so delete it.
            os.remove(self.filename)
            print(f"Corrupted save file {self.filename} deleted.")
            return None

# --- Game Console ---
class GameConsole:
    """
    Manages the main game loop, active game state, and menu navigation.
    """
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pygame Mini-Game Console")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 50)

        self.games = {
            "pong": PongGame(self),
            "minesweeper": MinesweeperGame(self),
            "jump_king": JumpKingGame(self)
        }
        self.active_game_key = "menu" # Start at the main menu
        self.save_load_manager = SaveLoadManager(GAME_SAVE_FILE)

        self.menu_options = [
            ("Play Pong", "pong"),
            ("Play Minesweeper", "minesweeper"),
            ("Play Jump King", "jump_king"),
            ("Load Game", "load"),
            ("Exit", "exit")
        ]
        self.selected_menu_index = 0

    def set_active_game(self, game_key):
        """Sets the currently active game."""
        self.active_game_key = game_key
        # Reset game if it's a new game (not loading)
        if game_key in self.games and not self.loading_game:
            self.games[game_key].reset()
        self.loading_game = False # Reset loading flag after setting game

    def run(self):
        """Main game loop."""
        running = True
        self.loading_game = False # Flag to prevent resetting game on load

        while running:
            dt = self.clock.tick(FPS) / 1000.0 # Delta time in seconds

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif self.active_game_key == "menu":
                    self._handle_menu_event(event)
                else:
                    # Pass events to the active game
                    self.games[self.active_game_key].handle_event(event)

            if self.active_game_key == "menu":
                self._update_menu(dt)
                self._draw_menu()
            else:
                # Update and draw the active game
                self.games[self.active_game_key].update(dt)
                self.games[self.active_game_key].draw(self.screen)

            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def _handle_menu_event(self, event):
        """Handles events when the menu is active."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_menu_index = (self.selected_menu_index - 1) % len(self.menu_options)
            elif event.key == pygame.K_DOWN:
                self.selected_menu_index = (self.selected_menu_index + 1) % len(self.menu_options)
            elif event.key == pygame.K_RETURN:
                self._execute_menu_option()
            elif event.key == pygame.K_s: # Save current game
                self._save_current_game()

    def _update_menu(self, dt):
        """Updates menu logic (currently none needed beyond event handling)."""
        pass

    def _draw_menu(self):
        """Draws the main menu screen."""
        self.screen.fill(BLACK)
        title_font = pygame.font.Font(None, 80)
        title_text = title_font.render("Pygame Console", True, WHITE)
        self.screen.blit(title_text, title_text.get_rect(center=(SCREEN_WIDTH // 2, 100)))

        for i, (text, _) in enumerate(self.menu_options):
            color = YELLOW if i == self.selected_menu_index else WHITE
            menu_text = self.font.render(text, True, color)
            self.screen.blit(menu_text, menu_text.get_rect(center=(SCREEN_WIDTH // 2, 250 + i * 60)))

        save_hint_font = pygame.font.Font(None, 30)
        save_hint_text = save_hint_font.render("Press 'S' to Save Current Game (if active)", True, LIGHT_GRAY)
        self.screen.blit(save_hint_text, save_hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)))


    def _execute_menu_option(self):
        """Executes the selected menu option."""
        selected_action = self.menu_options[self.selected_menu_index][1]

        if selected_action in self.games:
            self.set_active_game(selected_action)
        elif selected_action == "load":
            self._load_saved_game()
        elif selected_action == "exit":
            pygame.quit()
            sys.exit()

    def _save_current_game(self):
        """Saves the state of the currently active game."""
        if self.active_game_key != "menu":
            current_game = self.games[self.active_game_key]
            game_state = current_game.get_state()
            save_data = {
                "game_type": self.active_game_key,
                "state": game_state
            }
            self.save_load_manager.save_game(save_data)
            # Optionally show a message to the user
            print(f"Saved {self.active_game_key} game state.")
        else:
            print("Cannot save from the main menu. Please start a game first.")

    def _load_saved_game(self):
        """Loads a previously saved game."""
        loaded_data = self.save_load_manager.load_game()
        if loaded_data:
            game_type = loaded_data.get("game_type")
            game_state = loaded_data.get("state")

            if game_type and game_state and game_type in self.games:
                self.loading_game = True # Set flag before setting active game
                self.set_active_game(game_type)
                self.games[game_type].set_state(game_state)
                print(f"Loaded {game_type} game.")
            else:
                print("Invalid or incomplete save data.")
        else:
            print("No game to load.")


# --- Main execution ---
if __name__ == "__main__":
    console = GameConsole()
    console.run()
