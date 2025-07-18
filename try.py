import pygame
import sys
import pickle
import os
import random

# --- Constants ---
# These represent the internal rendering resolution, not the actual window size.
# All game logic and drawing will be done relative to these dimensions.
BASE_SCREEN_WIDTH = 1280 # Changed for 16:9 aspect ratio
BASE_SCREEN_HEIGHT = 720 # Changed for 16:9 aspect ratio
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
BROWN = (139, 69, 19)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)

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
        self.player_paddle_speed = 7 # Player's speed is constant
        self.ai_paddle_speed_base = 5 # Base AI speed
        self.ball_speed_x_base = 5
        self.ball_speed_y_base = 5
        self.player_score = 0
        self.ai_score = 0
        self.max_score = 5
        self.game_over = False
        self.difficulty = "normal" # Default difficulty
        self._set_difficulty_speed()
        self.reset() # Initial setup

    def _set_difficulty_speed(self):
        """Adjusts AI speed and ball speed based on difficulty."""
        if self.difficulty == "easy":
            self.ai_paddle_speed = self.ai_paddle_speed_base * 0.6
            self.ball_speed_multiplier = 0.8
        elif self.difficulty == "hard":
            self.ai_paddle_speed = self.ai_paddle_speed_base * 1.2
            self.ball_speed_multiplier = 1.2
        else: # Normal
            self.ai_paddle_speed = self.ai_paddle_speed_base * 0.8
            self.ball_speed_multiplier = 1.0

    def set_difficulty(self, difficulty_level):
        """Sets the game difficulty and updates speeds."""
        self.difficulty = difficulty_level
        self._set_difficulty_speed()
        # Reset ball to apply new speed immediately if game is active
        if not self.game_over: # Only reset if game is not already over
            self._reset_ball()
        else: # If game is over, just update speeds for next reset
            pass


    def reset(self):
        """Resets Pong game state."""
        self.player_paddle_y = (BASE_SCREEN_HEIGHT - self.paddle_height) // 2
        self.ai_paddle_y = (BASE_SCREEN_HEIGHT - self.paddle_height) // 2
        self.ball_x = BASE_SCREEN_WIDTH // 2 - self.ball_size // 2
        self.ball_y = BASE_SCREEN_HEIGHT // 2 - self.ball_size // 2
        self.ball_speed_x = self.ball_speed_x_base * self.ball_speed_multiplier * random.choice([-1, 1])
        self.ball_speed_y = self.ball_speed_y_base * self.ball_speed_multiplier * random.choice([-1, 1])
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
            self.player_paddle_y -= self.player_paddle_speed
        if keys[pygame.K_DOWN]:
            self.player_paddle_y += self.player_paddle_speed
        self.player_paddle_y = max(0, min(self.player_paddle_y, BASE_SCREEN_HEIGHT - self.paddle_height))

        # Ball movement
        self.ball_x += self.ball_speed_x
        self.ball_y += self.ball_speed_y

        # Ball collision with top/bottom walls
        if self.ball_y <= 0 or self.ball_y >= BASE_SCREEN_HEIGHT - self.ball_size:
            self.ball_speed_y *= -1

        # Ball collision with paddles
        player_paddle_rect = pygame.Rect(50, self.player_paddle_y, self.paddle_width, self.paddle_height)
        ai_paddle_rect = pygame.Rect(BASE_SCREEN_WIDTH - 50 - self.paddle_width, self.ai_paddle_y, self.paddle_width, self.paddle_height)
        ball_rect = pygame.Rect(self.ball_x, self.ball_y, self.ball_size, self.ball_size)

        if ball_rect.colliderect(player_paddle_rect) or ball_rect.colliderect(ai_paddle_rect):
            self.ball_speed_x *= -1
            # Add a slight random variation to y-speed for more dynamic play
            self.ball_speed_y += random.uniform(-0.5, 0.5)
            self.ball_speed_y = max(-10 * self.ball_speed_multiplier, min(10 * self.ball_speed_multiplier, self.ball_speed_y)) # Cap speed

        # Ball out of bounds (scoring)
        if self.ball_x < 0:
            self.ai_score += 1
            self._reset_ball()
        elif self.ball_x > BASE_SCREEN_WIDTH:
            self.player_score += 1
            self._reset_ball()

        # AI paddle movement (simple AI)
        if self.ai_paddle_y + self.paddle_height / 2 < self.ball_y:
            self.ai_paddle_y += self.ai_paddle_speed
        elif self.ai_paddle_y + self.paddle_height / 2 > self.ball_y:
            self.ai_paddle_y -= self.ai_paddle_speed
        self.ai_paddle_y = max(0, min(self.ai_paddle_y, BASE_SCREEN_HEIGHT - self.paddle_height))

        # Check for game over
        if self.player_score >= self.max_score or self.ai_score >= self.max_score:
            self.game_over = True

    def _reset_ball(self):
        """Resets ball position and direction after a score."""
        self.ball_x = BASE_SCREEN_WIDTH // 2 - self.ball_size // 2
        self.ball_y = BASE_SCREEN_HEIGHT // 2 - self.ball_size // 2
        self.ball_speed_x = self.ball_speed_x_base * self.ball_speed_multiplier * random.choice([-1, 1])
        self.ball_speed_y = self.ball_speed_y_base * self.ball_speed_multiplier * random.choice([-1, 1])


    def draw(self, screen):
        screen.fill(BLACK)
        pygame.draw.rect(screen, WHITE, (50, self.player_paddle_y, self.paddle_width, self.paddle_height))
        pygame.draw.rect(screen, WHITE, (BASE_SCREEN_WIDTH - 50 - self.paddle_width, self.ai_paddle_y, self.paddle_width, self.paddle_height))
        pygame.draw.ellipse(screen, WHITE, (self.ball_x, self.ball_y, self.ball_size, self.ball_size))
        pygame.draw.aaline(screen, WHITE, (BASE_SCREEN_WIDTH // 2, 0), (BASE_SCREEN_WIDTH // 2, BASE_SCREEN_HEIGHT))

        font = pygame.font.Font(None, self.console._get_scaled_font_size(74))
        player_text = font.render(str(self.player_score), True, WHITE)
        ai_text = font.render(str(self.ai_score), True, WHITE)
        screen.blit(player_text, (BASE_SCREEN_WIDTH // 4, 20))
        screen.blit(ai_text, (BASE_SCREEN_WIDTH * 3 // 4 - ai_text.get_width(), 20))

        if self.game_over:
            game_over_font = pygame.font.Font(None, self.console._get_scaled_font_size(100))
            winner = "Player" if self.player_score >= self.max_score else "AI"
            game_over_text = game_over_font.render(f"{winner} Wins!", True, YELLOW)
            restart_text = pygame.font.Font(None, self.console._get_scaled_font_size(40)).render("Press R to Restart or ESC to Menu", True, LIGHT_GRAY)
            screen.blit(game_over_text, (BASE_SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, BASE_SCREEN_HEIGHT // 2 - 50))
            screen.blit(restart_text, (BASE_SCREEN_WIDTH // 2 - restart_text.get_width() // 2, BASE_SCREEN_HEIGHT // 2 + 50))

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
            "game_over": self.game_over,
            "difficulty": self.difficulty # Save difficulty
        }

    def set_state(self, state):
        self.player_paddle_y = state.get("player_paddle_y", (BASE_SCREEN_HEIGHT - self.paddle_height) // 2)
        self.ai_paddle_y = state.get("ai_paddle_y", (BASE_SCREEN_HEIGHT - self.paddle_height) // 2)
        self.ball_x = state.get("ball_x", BASE_SCREEN_WIDTH // 2 - self.ball_size // 2)
        self.ball_y = state.get("ball_y", BASE_SCREEN_HEIGHT // 2 - self.ball_size // 2)
        self.player_score = state.get("player_score", 0)
        self.ai_score = state.get("ai_score", 0)
        self.game_over = state.get("game_over", False)
        self.difficulty = state.get("difficulty", "normal") # Load difficulty
        self._set_difficulty_speed() # Apply loaded difficulty speed
        self.ball_speed_x = state.get("ball_speed_x", self.ball_speed_x_base * self.ball_speed_multiplier * random.choice([-1, 1]))
        self.ball_speed_y = state.get("ball_speed_y", self.ball_speed_y_base * self.ball_speed_multiplier * random.choice([-1, 1]))


# --- Minesweeper Game ---
class MinesweeperGame(BaseGame):
    def __init__(self, console):
        super().__init__(console)
        self.cell_size = 40
        self.difficulty = "normal" # Default difficulty
        self._set_difficulty_params()
        self.board_offset_x = (BASE_SCREEN_WIDTH - self.cols * self.cell_size) // 2
        self.board_offset_y = (BASE_SCREEN_HEIGHT - self.rows * self.cell_size) // 2
        self.board = []  # Stores (is_mine, num_adjacent_mines, is_revealed, is_flagged)
        self.game_over = False
        self.win = False
        self.reset()

    def _set_difficulty_params(self):
        """Sets board dimensions and mine count based on difficulty."""
        if self.difficulty == "easy":
            self.rows = 8
            self.cols = 8
            self.num_mines = 10
        elif self.difficulty == "hard":
            self.rows = 12
            self.cols = 12
            self.num_mines = 30
        else: # Normal
            self.rows = 10
            self.cols = 10
            self.num_mines = 15
        # Recalculate offsets based on new dimensions
        self.board_offset_x = (BASE_SCREEN_WIDTH - self.cols * self.cell_size) // 2
        self.board_offset_y = (BASE_SCREEN_HEIGHT - self.rows * self.cell_size) // 2

    def set_difficulty(self, difficulty_level):
        """Sets the game difficulty and updates parameters."""
        self.difficulty = difficulty_level
        self._set_difficulty_params()
        self.reset() # Reset board with new difficulty settings

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
            # Scale mouse position from actual screen to base screen coordinates
            scaled_mx, scaled_my = self.console._scale_mouse_pos(event.pos)
            
            # Convert mouse coords to board coords
            c = (scaled_mx - self.board_offset_x) // self.cell_size
            r = (scaled_my - self.board_offset_y) // self.cell_size

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
        font = pygame.font.Font(None, self.console._get_scaled_font_size(30))

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
            overlay = pygame.Surface((BASE_SCREEN_WIDTH, BASE_SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150)) # Semi-transparent black
            screen.blit(overlay, (0, 0))

            game_over_font = pygame.font.Font(None, self.console._get_scaled_font_size(80))
            message = "You Win!" if self.win else "Game Over!"
            message_color = GREEN if self.win else RED
            message_text = game_over_font.render(message, True, message_color)
            restart_text = pygame.font.Font(None, self.console._get_scaled_font_size(40)).render("Press R to Restart or ESC to Menu", True, LIGHT_GRAY)

            screen.blit(message_text, message_text.get_rect(center=(BASE_SCREEN_WIDTH // 2, BASE_SCREEN_HEIGHT // 2 - 50)))
            screen.blit(restart_text, restart_text.get_rect(center=(BASE_SCREEN_WIDTH // 2, BASE_SCREEN_HEIGHT // 2 + 50)))

    def get_state(self):
        return {
            "board": self.board,
            "game_over": self.game_over,
            "win": self.win,
            "difficulty": self.difficulty # Save difficulty
        }

    def set_state(self, state):
        self.difficulty = state.get("difficulty", "normal") # Load difficulty first
        self._set_difficulty_params() # Apply loaded difficulty parameters
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
        self.player_vel_y = 0
        self.gravity = 0.5
        self.jump_power = -18 # Increased jump power for more height
        self.on_ground = False
        self.charging_jump = False
        self.jump_charge_time = 0
        self.max_jump_charge = 60 # Frames
        self.game_over = False
        self.win = False

        self.coyote_time_duration = 8 # Frames player can still jump after leaving ground
        self.coyote_time_counter = 0

        self.platforms = []
        self.goal_platform = None
        
        # World dimensions for scrolling
        self.world_height = BASE_SCREEN_HEIGHT * 3 # 3 screens tall
        self.camera_y_offset = 0 # Current camera offset (world_y - camera_y_offset = screen_y)

        self.reset()

    def reset(self):
        """Resets Jump King game state and generates a new level."""
        self.player_x = BASE_SCREEN_WIDTH // 2 - self.player_size // 2
        # Start player near the bottom of the world
        self.player_y = self.world_height - 100 - self.player_size 
        self.player_vel_y = 0
        self.on_ground = False
        self.charging_jump = False
        self.jump_charge_time = 0
        self.game_over = False
        self.win = False
        self.coyote_time_counter = 0 # Reset coyote time on game reset
        self._generate_platforms()
        # Set initial camera position to show the player at the bottom
        self.camera_y_offset = max(0, self.player_y - BASE_SCREEN_HEIGHT // 2)


    def _generate_platforms(self):
        self.platforms = []
        
        # Calculate max jump height to ensure platforms are reachable
        # Corrected formula for maximum height reached given initial upward velocity (abs(jump_power))
        # h = v0^2 / (2 * g)
        max_jump_height = (self.jump_power ** 2) / (2 * self.gravity)//2
        
        # Define min/max gaps based on jump height
        # Ensure min_vertical_gap is at least 1 to avoid empty range for random.randint
        min_vertical_gap = max(1, int(max_jump_height * 0.4)) 
        max_vertical_gap = int(max_jump_height * 0.8) 

        # Ensure max_vertical_gap is at least min_vertical_gap
        if min_vertical_gap > max_vertical_gap:
            max_vertical_gap = min_vertical_gap + 1 # Add a small buffer

        # Starting platform at the bottom of the world
        start_platform_y = self.world_height - 100
        self.platforms.append(pygame.Rect(BASE_SCREEN_WIDTH // 2 - 50, start_platform_y, 100, 20))

        # Generate platforms upwards
        # Start generating from above the initial platform, leaving some initial jump space
        current_world_y = start_platform_y - self.player_size - 20 # Small buffer above player on start platform
        
        # Target for the goal platform
        goal_y_target = 50 

        # Generate platforms until we are above the target goal Y
        while current_world_y > goal_y_target + 100: # Ensure enough space for goal platform
            width = random.randint(80, 150)
            height = 20
            x = random.randint(50, BASE_SCREEN_WIDTH - width - 50)
            
            # Calculate next platform's Y position
            # This ensures platforms are placed at reachable distances
            y_gap = random.randint(min_vertical_gap, max_vertical_gap)
            next_platform_y = current_world_y - y_gap
            
            # Ensure the platform doesn't go too high too quickly, or below current_world_y
            # Also ensure it doesn't go below the minimum Y for the goal
            next_platform_y = max(goal_y_target + 50, next_platform_y) # Don't overlap with goal area

            self.platforms.append(pygame.Rect(x, next_platform_y, width, height))
            current_world_y = next_platform_y # Update current_world_y to the new platform's Y
            
            # Add some randomness to horizontal placement for variety
            current_world_y -= random.randint(10, 30) # Small downward shift to ensure progression


        # Goal platform at the very top
        goal_width = 80
        goal_height = 20
        goal_x = random.randint(50, BASE_SCREEN_WIDTH - goal_width - 50)
        goal_y = 50 # Fixed near the top of the world
        self.goal_platform = pygame.Rect(goal_x, goal_y, goal_width, goal_height)
        self.platforms.append(self.goal_platform)

        # Sort platforms by Y-coordinate for consistent drawing and collision checking (optional but good practice)
        self.platforms.sort(key=lambda p: p.y)


    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.console.set_active_game("menu")
            elif event.key == pygame.K_r and (self.game_over or self.win):
                self.reset()
            # Modified jump condition to include coyote time
            elif event.key == pygame.K_SPACE and \
                 (self.on_ground or self.coyote_time_counter > 0) and \
                 not self.charging_jump and not self.game_over and not self.win:
                self.charging_jump = True
                self.jump_charge_time = 0
                self.coyote_time_counter = 0 # Consume coyote time when jump is initiated
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE and self.charging_jump and not self.game_over and not self.win:
                self.charging_jump = False
                # Apply jump power based on charge time
                jump_strength = self.jump_power * (self.jump_charge_time / self.max_jump_charge)
                self.player_vel_y = max(self.jump_power, jump_strength) # Cap at full jump power (negative for upward)
                self.on_ground = False # Player is now in air (important for subsequent fall/coyote time)

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

        # Keep player within horizontal bounds of the screen
        self.player_x = max(0, min(self.player_x, BASE_SCREEN_WIDTH - self.player_size))

        player_rect = pygame.Rect(self.player_x, self.player_y, self.player_size, self.player_size)
        
        # Check for actual ground collision
        was_on_ground_this_frame = False
        for platform in self.platforms:
            # Create a rect for the platform for collision detection
            platform_rect = platform # Platforms are already world coordinates
            
            # Check for collision from top (player falling onto platform)
            # Add a small buffer (e.g., 2 pixels) to the collision check for robustness
            if self.player_vel_y >= 0 and player_rect.colliderect(platform_rect) and \
               player_rect.bottom >= platform_rect.top and player_rect.bottom <= platform_rect.top + self.player_vel_y + 2:
                self.player_y = platform_rect.top - self.player_size # Snap to top
                self.player_vel_y = 0
                was_on_ground_this_frame = True
                if platform_rect == self.goal_platform:
                    self.win = True
                    self.game_over = True
            # Handle hitting bottom of platform (player jumping into it)
            elif self.player_vel_y < 0 and player_rect.colliderect(platform_rect) and \
                 player_rect.top <= platform_rect.bottom and player_rect.top >= platform_rect.bottom - abs(self.player_vel_y) - 2:
                self.player_y = platform_rect.bottom # Snap to bottom
                self.player_vel_y = 0 # Stop upward movement

        # Update on_ground and coyote time counter
        if was_on_ground_this_frame:
            self.on_ground = True
            self.coyote_time_counter = self.coyote_time_duration # Reset coyote time
        else:
            self.on_ground = False # Not currently touching ground
            if self.coyote_time_counter > 0:
                self.coyote_time_counter -= 1 # Decrement coyote time if not on ground

        # Check for falling off screen (Game Over) - now checks against world height
        if self.player_y > self.world_height:
            self.game_over = True

        # Camera logic: Keep player roughly centered vertically, but clamp to world bounds
        # Target camera_y_offset to keep player at 40% from the top of the screen
        target_camera_y_offset = self.player_y - (BASE_SCREEN_HEIGHT * 0.4) 
        
        # Clamp camera_y_offset to world boundaries
        # The camera's top (y=0) cannot go below 0 world coordinate
        # The camera's bottom (y=BASE_SCREEN_HEIGHT) cannot go above world_height
        max_camera_y_offset = self.world_height - BASE_SCREEN_HEIGHT
        min_camera_y_offset = 0

        self.camera_y_offset = max(min_camera_y_offset, min(max_camera_y_offset, target_camera_y_offset))


    def draw(self, screen):
        screen.fill(BLUE) # Sky background

        # Draw platforms, adjusting for camera offset
        for platform in self.platforms:
            color = GREEN
            if platform == self.goal_platform:
                color = YELLOW # Goal platform is yellow
            # Draw platform using its world coordinates minus the camera offset
            pygame.draw.rect(screen, color, (platform.x, platform.y - self.camera_y_offset, platform.width, platform.height))

        # Draw player, adjusting for camera offset
        pygame.draw.rect(screen, RED, (self.player_x, self.player_y - self.camera_y_offset, self.player_size, self.player_size))

        # Draw jump charge bar, adjusting for camera offset
        if self.charging_jump:
            bar_width = 100
            bar_height = 10
            fill_width = (self.jump_charge_time / self.max_jump_charge) * bar_width
            pygame.draw.rect(screen, GRAY, (self.player_x + self.player_size // 2 - bar_width // 2, 
                                            self.player_y - self.camera_y_offset - 20, 
                                            bar_width, bar_height), 2) # Outline
            pygame.draw.rect(screen, GREEN, (self.player_x + self.player_size // 2 - bar_width // 2, 
                                             self.player_y - self.camera_y_offset - 20, 
                                             fill_width, bar_height)) # Fill

        if self.game_over:
            overlay = pygame.Surface((BASE_SCREEN_WIDTH, BASE_SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150)) # Semi-transparent black
            screen.blit(overlay, (0, 0))

            game_over_font = pygame.font.Font(None, self.console._get_scaled_font_size(80))
            message = "You Win!" if self.win else "Game Over!"
            message_color = GREEN if self.win else RED
            message_text = game_over_font.render(message, True, message_color)
            restart_text = pygame.font.Font(None, self.console._get_scaled_font_size(40)).render("Press R to Restart or ESC to Menu", True, LIGHT_GRAY)

            screen.blit(message_text, message_text.get_rect(center=(BASE_SCREEN_WIDTH // 2, BASE_SCREEN_HEIGHT // 2 - 50)))
            screen.blit(restart_text, restart_text.get_rect(center=(BASE_SCREEN_WIDTH // 2, BASE_SCREEN_HEIGHT // 2 + 50)))


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
            "coyote_time_counter": self.coyote_time_counter, # Save coyote time
            "platforms": platforms_data,
            "goal_platform": goal_platform_data,
            "game_over": self.game_over,
            "win": self.win,
            "camera_y_offset": self.camera_y_offset, # Save camera offset
            "world_height": self.world_height # Save world height
        }

    def set_state(self, state):
        self.player_x = state.get("player_x", BASE_SCREEN_WIDTH // 2 - self.player_size // 2)
        self.player_y = state.get("player_y", self.world_height - 100 - self.player_size) # Default to bottom of world
        self.player_vel_y = state.get("player_vel_y", 0)
        self.on_ground = state.get("on_ground", False)
        self.charging_jump = state.get("charging_jump", False)
        self.jump_charge_time = state.get("jump_charge_time", 0)
        self.coyote_time_counter = state.get("coyote_time_counter", 0) # Load coyote time
        self.game_over = state.get("game_over", False)
        self.win = state.get("win", False)
        self.camera_y_offset = state.get("camera_y_offset", 0) # Load camera offset
        self.world_height = state.get("world_height", BASE_SCREEN_HEIGHT * 3) # Load world height

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

# --- Maze Game ---
class MazeGame(BaseGame):
    def __init__(self, console):
        super().__init__(console)
        self.cell_size = 40
        self.size = "medium" # Default size
        self._set_size_params() # Set initial maze dimensions
        # Corrected: Use maze_width and maze_height directly
        self.maze_offset_x = (BASE_SCREEN_WIDTH - self.maze_width * self.cell_size) // 2
        self.maze_offset_y = (BASE_SCREEN_HEIGHT - self.maze_height * self.cell_size) // 2
        self.maze = [] # Stores maze cells (0: path, 1: wall)
        self.player_pos = [0, 0] # [col, row]
        self.end_pos = [0, 0] # [col, row]
        self.game_over = False
        self.win = False
        self.reset()

    def _set_size_params(self):
        """Sets maze dimensions based on selected size."""
        if self.size == "small":
            self.maze_width = 10
            self.maze_height = 8
        elif self.size == "large":
            self.maze_width = 20
            self.maze_height = 15
        else: # Medium
            self.maze_width = 15
            self.maze_height = 10
        # Recalculate offsets based on new dimensions
        self.maze_offset_x = (BASE_SCREEN_WIDTH - self.maze_width * self.cell_size) // 2
        self.maze_offset_y = (BASE_SCREEN_HEIGHT - self.maze_height * self.cell_size) // 2

    def set_size(self, maze_size_level):
        """Sets the maze size and updates parameters."""
        self.size = maze_size_level
        self._set_size_params()
        self.reset() # Reset board with new size settings

    def reset(self):
        """Resets Maze game state and generates a new maze."""
        self.game_over = False
        self.win = False
        self._generate_maze()
        self.player_pos = [0, 0] # Start at top-left
        self.end_pos = [self.maze_width - 1, self.maze_height - 1] # End at bottom-right
        # Ensure start and end are paths
        self.maze[self.player_pos[1]][self.player_pos[0]] = 0
        self.maze[self.end_pos[1]][self.end_pos[0]] = 0


    def _generate_maze(self):
        """Generates a simple maze using a randomized Prim's algorithm.
        This algorithm inherently creates a solvable maze with a single path
        between any two points within the maze."""
        # Initialize grid with all walls
        self.maze = [[1 for _ in range(self.maze_width)] for _ in range(self.maze_height)]

        # Choose a random starting cell and mark it as a path
        start_x, start_y = random.randint(0, self.maze_width - 1), random.randint(0, self.maze_height - 1)
        self.maze[start_y][start_x] = 0

        # List of walls to be processed (wall_coords, passage_coords)
        walls = []
        # Add walls of the starting cell to the list
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = start_x + dx, start_y + dy
            if 0 <= nx < self.maze_width and 0 <= ny < self.maze_height and self.maze[ny][nx] == 1:
                walls.append(((nx, ny), (start_x, start_y)))

        while walls:
            # Pick a random wall from the list
            wall_index = random.randrange(len(walls))
            (wx, wy), (px, py) = walls.pop(wall_index)

            # Check if the cell on the other side of the wall is unvisited (still a wall)
            if 0 <= wx < self.maze_width and 0 <= wy < self.maze_height and self.maze[wy][wx] == 1:
                # Count visited neighbors for the cell on the other side of the wall
                visited_neighbors = 0
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nx, ny = wx + dx, wy + dy
                    if 0 <= nx < self.maze_width and 0 <= ny < self.maze_height and self.maze[ny][nx] == 0:
                        visited_neighbors += 1

                # If the cell on the other side has only one visited neighbor (the current path)
                # This ensures we don't create loops and maintain a single connected component
                if visited_neighbors == 1:
                    self.maze[wy][wx] = 0 # Carve a path through the wall
                    # Add new walls of the newly carved cell
                    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        nx, ny = wx + dx, wy + dy
                        if 0 <= nx < self.maze_width and 0 <= ny < self.maze_height and self.maze[ny][nx] == 1:
                            walls.append(((nx, ny), (wx, wy)))
        # Ensure the maze is solvable by setting start and end points
        if self.maze[0][1] == 1 and self.maze[1][0] == 1:
            self.maze[0][1] = 0
        if self.maze[self.maze_height - 1][self.maze_width - 2] == 1 and self.maze[self.maze_height - 2][self.maze_width - 1] == 1:
            self.maze[self.maze_height - 1][self.maze_width - 2] = 0

            


    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.console.set_active_game("menu")
            elif event.key == pygame.K_r and (self.game_over or self.win):
                self.reset()
            elif not self.game_over and not self.win:
                new_x, new_y = self.player_pos[0], self.player_pos[1]
                if event.key == pygame.K_LEFT:
                    new_x -= 1
                elif event.key == pygame.K_RIGHT:
                    new_x += 1
                elif event.key == pygame.K_UP:
                    new_y -= 1
                elif event.key == pygame.K_DOWN:
                    new_y += 1

                # Check for valid move (within bounds and not a wall)
                if (0 <= new_x < self.maze_width and
                    0 <= new_y < self.maze_height and
                    self.maze[new_y][new_x] == 0): # 0 means path
                    self.player_pos = [new_x, new_y]
                    if self.player_pos == self.end_pos:
                        self.win = True
                        self.game_over = True

    def update(self, dt):
        pass # Maze game logic is mostly event-driven

    def draw(self, screen):
        screen.fill(BLACK)

        # Draw maze
        for r in range(self.maze_height): # Corrected: Use maze_height
            for c in range(self.maze_width): # Corrected: Use maze_width
                x = self.maze_offset_x + c * self.cell_size
                y = self.maze_offset_y + r * self.cell_size
                cell_rect = pygame.Rect(x, y, self.cell_size, self.cell_size)

                if self.maze[r][c] == 1: # Wall
                    pygame.draw.rect(screen, BROWN, cell_rect)
                else: # Path
                    pygame.draw.rect(screen, LIGHT_GRAY, cell_rect)

                # Draw borders for all cells
                pygame.draw.rect(screen, BLACK, cell_rect, 1)

        # Draw start and end points
        start_rect = pygame.Rect(self.maze_offset_x + self.player_pos[0] * self.cell_size,
                                 self.maze_offset_y + self.player_pos[1] * self.cell_size,
                                 self.cell_size, self.cell_size)
        end_rect = pygame.Rect(self.maze_offset_x + self.end_pos[0] * self.cell_size,
                               self.maze_offset_y + self.end_pos[1] * self.cell_size,
                               self.cell_size, self.cell_size)

        pygame.draw.rect(screen, GREEN, start_rect, 4) # Start marker
        pygame.draw.circle(screen, RED, end_rect.center, self.cell_size // 3) # End marker

        # Draw player
        player_circle_center = (self.maze_offset_x + self.player_pos[0] * self.cell_size + self.cell_size // 2,
                                self.maze_offset_y + self.player_pos[1] * self.cell_size + self.cell_size // 2)
        pygame.draw.circle(screen, BLUE, player_circle_center, self.cell_size // 3)

        if self.game_over:
            overlay = pygame.Surface((BASE_SCREEN_WIDTH, BASE_SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150)) # Semi-transparent black
            screen.blit(overlay, (0, 0))

            game_over_font = pygame.font.Font(None, self.console._get_scaled_font_size(80))
            message = "You Win!" if self.win else "Game Over!"
            message_color = GREEN if self.win else RED
            message_text = game_over_font.render(message, True, message_color)
            restart_text = pygame.font.Font(None, self.console._get_scaled_font_size(40)).render("Press R to Restart or ESC to Menu", True, LIGHT_GRAY)

            screen.blit(message_text, message_text.get_rect(center=(BASE_SCREEN_WIDTH // 2, BASE_SCREEN_HEIGHT // 2 - 50)))
            screen.blit(restart_text, restart_text.get_rect(center=(BASE_SCREEN_WIDTH // 2, BASE_SCREEN_HEIGHT // 2 + 50)))

    def get_state(self):
        return {
            "maze": self.maze,
            "player_pos": self.player_pos,
            "end_pos": self.end_pos,
            "game_over": self.game_over,
            "win": self.win,
            "size": self.size # Save maze size
        }

    def set_state(self, state):
        self.size = state.get("size", "medium") # Load maze size first
        self._set_size_params() # Apply loaded maze dimensions
        self.maze = state.get("maze", [])
        self.player_pos = state.get("player_pos", [0, 0])
        self.end_pos = state.get("end_pos", [self.maze_width - 1, self.maze_height - 1])
        self.game_over = state.get("game_over", False)
        self.win = state.get("win", False)
        # If maze is empty (e.g., first load or corrupted), generate a new one
        if not self.maze or not self.maze[0]:
            self.reset()


# --- Tetris Game ---
class TetrisGame(BaseGame):
    def __init__(self, console):
        super().__init__(console)
        self.grid_width = 10
        self.grid_height = 20
        self.block_size = 25
        self.grid_offset_x = (BASE_SCREEN_WIDTH - self.grid_width * self.block_size) // 2
        self.grid_offset_y = (BASE_SCREEN_HEIGHT - self.grid_height * self.block_size) // 2 - 50 # Adjust for score/next piece display

        self.grid = [[BLACK for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False

        self.tetrominoes = {
            'I': {'shape': [[0,0,0,0], [1,1,1,1], [0,0,0,0], [0,0,0,0]], 'color': CYAN},
            'J': {'shape': [[1,0,0], [1,1,1], [0,0,0]], 'color': BLUE},
            'L': {'shape': [[0,0,1], [1,1,1], [0,0,0]], 'color': ORANGE},
            'O': {'shape': [[1,1], [1,1]], 'color': YELLOW},
            'S': {'shape': [[0,1,1], [1,1,0], [0,0,0]], 'color': GREEN},
            'T': {'shape': [[0,1,0], [1,1,1], [0,0,0]], 'color': PURPLE},
            'Z': {'shape': [[1,1,0], [0,1,1], [0,0,0]], 'color': RED}
        }
        self.current_piece = None
        self.next_piece = None
        self.piece_x = 0
        self.piece_y = 0

        self.fall_time = 0
        self.fall_speed = 0.5 # Seconds per grid row

        self.reset()

    def reset(self):
        """Resets the Tetris game state."""
        self.grid = [[BLACK for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        self.fall_time = 0
        self.fall_speed = 0.5
        self.current_piece = self._get_new_piece()
        self.next_piece = self._get_new_piece()
        self._set_initial_piece_position()

    def _get_new_piece(self):
        """Returns a random new tetromino."""
        shape_name = random.choice(list(self.tetrominoes.keys()))
        return {'shape_name': shape_name,
                'shape': self.tetrominoes[shape_name]['shape'],
                'color': self.tetrominoes[shape_name]['color']}

    def _set_initial_piece_position(self):
        """Sets the initial position of the current piece."""
        self.piece_x = self.grid_width // 2 - len(self.current_piece['shape'][0]) // 2
        self.piece_y = 0
        if not self._check_collision(self.current_piece['shape'], self.piece_x, self.piece_y):
            self.game_over = True # Game over if new piece can't be placed

    def _check_collision(self, shape, x_offset, y_offset):
        """Checks if the given shape collides with the grid boundaries or existing blocks."""
        for r_idx, row in enumerate(shape):
            for c_idx, cell in enumerate(row):
                if cell == 1:
                    grid_x = x_offset + c_idx
                    grid_y = y_offset + r_idx
                    if not (0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height):
                        return False # Out of bounds
                    if self.grid[grid_y][grid_x] != BLACK:
                        return False # Collision with existing block
        return True

    def _merge_piece_to_grid(self):
        """Merges the current piece into the main grid."""
        for r_idx, row in enumerate(self.current_piece['shape']):
            for c_idx, cell in enumerate(row):
                if cell == 1:
                    self.grid[self.piece_y + r_idx][self.piece_x + c_idx] = self.current_piece['color']

    def _clear_lines(self):
        """Checks for and clears full lines, then shifts blocks down."""
        new_grid = [row for row in self.grid if any(cell == BLACK for cell in row)]
        cleared_rows = self.grid_height - len(new_grid)
        for _ in range(cleared_rows):
            new_grid.insert(0, [BLACK for _ in range(self.grid_width)])
        self.grid = new_grid
        self.lines_cleared += cleared_rows
        self.score += cleared_rows * 100 * self.level # Basic scoring
        self.level = 1 + (self.lines_cleared // 10) # Increase level every 10 lines
        self.fall_speed = max(0.1, 0.5 - (self.level - 1) * 0.05) # Speed up

    def _rotate_piece(self, shape):
        """Rotates a 2D list (matrix) clockwise."""
        num_rows = len(shape)
        num_cols = len(shape[0])
        rotated_shape = [[0 for _ in range(num_rows)] for _ in range(num_cols)]
        for r in range(num_rows):
            for c in range(num_cols):
                rotated_shape[c][num_rows - 1 - r] = shape[r][c]
        return rotated_shape

    def handle_event(self, event):
        if self.game_over:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.console.set_active_game("menu")
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.console.set_active_game("menu")
            elif event.key == pygame.K_LEFT:
                if self._check_collision(self.current_piece['shape'], self.piece_x - 1, self.piece_y):
                    self.piece_x -= 1
            elif event.key == pygame.K_RIGHT:
                if self._check_collision(self.current_piece['shape'], self.piece_x + 1, self.piece_y):
                    self.piece_x += 1
            elif event.key == pygame.K_DOWN:
                # Soft drop
                if self._check_collision(self.current_piece['shape'], self.piece_x, self.piece_y + 1):
                    self.piece_y += 1
                    self.score += 1 # Small score for soft drop
            elif event.key == pygame.K_SPACE:
                # Hard drop
                while self._check_collision(self.current_piece['shape'], self.piece_x, self.piece_y + 1):
                    self.piece_y += 1
                    self.score += 2 # More score for hard drop
                self._merge_piece_to_grid()
                self._clear_lines()
                self.current_piece = self.next_piece
                self.next_piece = self._get_new_piece()
                self._set_initial_piece_position()
                self.fall_time = 0 # Reset fall time after hard drop
            elif event.key == pygame.K_UP:
                # Rotate
                rotated_shape = self._rotate_piece(self.current_piece['shape'])
                if self._check_collision(rotated_shape, self.piece_x, self.piece_y):
                    self.current_piece['shape'] = rotated_shape

    def update(self, dt):
        if self.game_over:
            return

        self.fall_time += dt
        if self.fall_time >= self.fall_speed:
            if self._check_collision(self.current_piece['shape'], self.piece_x, self.piece_y + 1):
                self.piece_y += 1
            else:
                # Piece landed
                self._merge_piece_to_grid()
                self._clear_lines()
                self.current_piece = self.next_piece
                self.next_piece = self._get_new_piece()
                self._set_initial_piece_position() # This also checks for game over
            self.fall_time = 0

    def draw(self, screen):
        screen.fill(BLACK)

        # Draw grid background
        for r in range(self.grid_height):
            for c in range(self.grid_width):
                pygame.draw.rect(screen, GRAY, (self.grid_offset_x + c * self.block_size,
                                                 self.grid_offset_y + r * self.block_size,
                                                 self.block_size, self.block_size), 1) # Border

        # Draw filled blocks on the grid
        for r in range(self.grid_height):
            for c in range(self.grid_width):
                color = self.grid[r][c]
                if color != BLACK:
                    pygame.draw.rect(screen, color, (self.grid_offset_x + c * self.block_size,
                                                      self.grid_offset_y + r * self.block_size,
                                                      self.block_size, self.block_size))
                    pygame.draw.rect(screen, WHITE, (self.grid_offset_x + c * self.block_size,
                                                      self.grid_offset_y + r * self.block_size,
                                                      self.block_size, self.block_size), 1) # Border

        # Draw current falling piece
        if self.current_piece:
            for r_idx, row in enumerate(self.current_piece['shape']):
                for c_idx, cell in enumerate(row):
                    if cell == 1:
                        pygame.draw.rect(screen, self.current_piece['color'],
                                         (self.grid_offset_x + (self.piece_x + c_idx) * self.block_size,
                                          self.grid_offset_y + (self.piece_y + r_idx) * self.block_size,
                                          self.block_size, self.block_size))
                        pygame.draw.rect(screen, WHITE,
                                         (self.grid_offset_x + (self.piece_x + c_idx) * self.block_size,
                                          self.grid_offset_y + (self.piece_y + r_idx) * self.block_size,
                                          self.block_size, self.block_size), 1) # Border

        # Draw next piece preview
        font = pygame.font.Font(None, self.console._get_scaled_font_size(30))
        next_text = font.render("NEXT:", True, WHITE)
        screen.blit(next_text, (self.grid_offset_x + self.grid_width * self.block_size + 20, self.grid_offset_y + 50))
        if self.next_piece:
            for r_idx, row in enumerate(self.next_piece['shape']):
                for c_idx, cell in enumerate(row):
                    if cell == 1:
                        pygame.draw.rect(screen, self.next_piece['color'],
                                         (self.grid_offset_x + self.grid_width * self.block_size + 20 + c_idx * self.block_size,
                                          self.grid_offset_y + 80 + r_idx * self.block_size,
                                          self.block_size, self.block_size))
                        pygame.draw.rect(screen, WHITE,
                                         (self.grid_offset_x + self.grid_width * self.block_size + 20 + c_idx * self.block_size,
                                          self.grid_offset_y + 80 + r_idx * self.block_size,
                                          self.block_size, self.block_size), 1) # Border

        # Draw score and level
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        level_text = font.render(f"Level: {self.level}", True, WHITE)
        screen.blit(score_text, (self.grid_offset_x + self.grid_width * self.block_size + 20, self.grid_offset_y + 200))
        screen.blit(level_text, (self.grid_offset_x + self.grid_width * self.block_size + 20, self.grid_offset_y + 230))
        lines_text = font.render(f"Lines: {self.lines_cleared}", True, WHITE)
        screen.blit(lines_text, (self.grid_offset_x + self.grid_width * self.block_size + 20, self.grid_offset_y + 260))


        if self.game_over:
            overlay = pygame.Surface((BASE_SCREEN_WIDTH, BASE_SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150)) # Semi-transparent black
            screen.blit(overlay, (0, 0))

            game_over_font = pygame.font.Font(None, self.console._get_scaled_font_size(80))
            game_over_text = game_over_font.render("GAME OVER", True, RED)
            final_score_text = font.render(f"Final Score: {self.score}", True, WHITE)
            restart_text = pygame.font.Font(None, self.console._get_scaled_font_size(40)).render("Press R to Restart or ESC to Menu", True, LIGHT_GRAY)

            screen.blit(game_over_text, game_over_text.get_rect(center=(BASE_SCREEN_WIDTH // 2, BASE_SCREEN_HEIGHT // 2 - 50)))
            screen.blit(final_score_text, final_score_text.get_rect(center=(BASE_SCREEN_WIDTH // 2, BASE_SCREEN_HEIGHT // 2 + 10)))
            screen.blit(restart_text, restart_text.get_rect(center=(BASE_SCREEN_WIDTH // 2, BASE_SCREEN_HEIGHT // 2 + 80)))


    def get_state(self):
        # Convert piece shapes to tuples for pickling
        current_piece_serializable = None
        if self.current_piece:
            current_piece_serializable = {
                'shape_name': self.current_piece['shape_name'],
                'shape': tuple(tuple(row) for row in self.current_piece['shape']),
                'color': self.current_piece['color']
            }
        next_piece_serializable = None
        if self.next_piece:
            next_piece_serializable = {
                'shape_name': self.next_piece['shape_name'],
                'shape': tuple(tuple(row) for row in self.next_piece['shape']),
                'color': self.next_piece['color']
            }

        return {
            "grid": tuple(tuple(row) for row in self.grid), # Convert grid to tuple of tuples
            "score": self.score,
            "level": self.level,
            "lines_cleared": self.lines_cleared,
            "game_over": self.game_over,
            "current_piece": current_piece_serializable,
            "next_piece": next_piece_serializable,
            "piece_x": self.piece_x,
            "piece_y": self.piece_y,
            "fall_time": self.fall_time,
            "fall_speed": self.fall_speed
        }

    def set_state(self, state):
        self.grid = [list(row) for row in state.get("grid", [[BLACK for _ in range(self.grid_width)] for _ in range(self.grid_height)])]
        self.score = state.get("score", 0)
        self.level = state.get("level", 1)
        self.lines_cleared = state.get("lines_cleared", 0)
        self.game_over = state.get("game_over", False)
        self.piece_x = state.get("piece_x", 0)
        self.piece_y = state.get("piece_y", 0)
        self.fall_time = state.get("fall_time", 0)
        self.fall_speed = state.get("fall_speed", 0.5)

        current_piece_data = state.get("current_piece")
        if current_piece_data:
            self.current_piece = {
                'shape_name': current_piece_data['shape_name'],
                'shape': [list(row) for row in current_piece_data['shape']],
                'color': tuple(current_piece_data['color'])
            }
        else:
            self.current_piece = self._get_new_piece()

        next_piece_data = state.get("next_piece")
        if next_piece_data:
            self.next_piece = {
                'shape_name': next_piece_data['shape_name'],
                'shape': [list(row) for row in next_piece_data['shape']],
                'color': tuple(next_piece_data['color'])
            }
        else:
            self.next_piece = self._get_new_piece()

        # If loaded state is empty or corrupted, reset fully
        if not self.grid or not self.current_piece:
            self.reset()


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
    Handles screen scaling and font scaling.
    """
    def __init__(self):
        pygame.init()
        # Initial window size, can be resized by user
        self.window_width = 1920
        self.window_height = 1080
        self.screen = pygame.display.set_mode((self.window_width, self.window_height), pygame.RESIZABLE)
        pygame.display.set_caption("Pygame Mini-Game Console")

        # This is the internal surface where all game drawing happens at a fixed resolution
        self.display_surface = pygame.Surface((BASE_SCREEN_WIDTH, BASE_SCREEN_HEIGHT))

        self.clock = pygame.time.Clock()
        self.base_font_size = 30 # Base font size for calculations
        self.MAX_FONT_SIZE = 60 # Maximum font size to prevent over-scaling
        self.font = pygame.font.Font(None, self.base_font_size) # Initial font, will be scaled

        self.games = {
            "pong": PongGame(self),
            "minesweeper": MinesweeperGame(self),
            "jump_king": JumpKingGame(self),
            "maze": MazeGame(self),
            "tetris": TetrisGame(self)
        }
        self.active_game_key = "menu" # Start at the main menu
        self.save_load_manager = SaveLoadManager(GAME_SAVE_FILE)

        self.menu_options = [
            ("Play Pong", "pong_difficulty_selection"),
            ("Set Pong Difficulty", "pong_difficulty_settings"),
            ("Play Minesweeper", "minesweeper_difficulty_selection"),
            ("Set Minesweeper Difficulty", "minesweeper_difficulty_settings"),
            ("Play Jump King", "jump_king"),
            ("Play Maze Game", "maze_size_selection"),
            ("Set Maze Size", "maze_size_settings"),
            ("Play Tetris", "tetris"),
            ("Load Game", "load"),
            ("Help", "help"),
            ("Exit", "exit")
        ]
        self.selected_menu_index = 0

        self.pong_difficulty_options = [
            ("Easy", "easy"),
            ("Normal", "normal"),
            ("Hard", "hard"),
            ("Back to Main Menu", "back")
        ]
        self.selected_pong_difficulty_index = 0

        self.minesweeper_difficulty_options = [
            ("Easy (8x8, 10 mines)", "easy"),
            ("Normal (10x10, 15 mines)", "normal"),
            ("Hard (12x12, 30 mines)", "hard"),
            ("Back to Main Menu", "back")
        ]
        self.selected_minesweeper_difficulty_index = 0

        self.maze_size_options = [
            ("Small (10x8)", "small"),
            ("Medium (15x10)", "medium"),
            ("Large (20x15)", "large"),
            ("Back to Main Menu", "back")
        ]
        self.selected_maze_size_index = 0


        self.help_menu_content = {
            "Pong": "Controls: UP/DOWN arrow keys for paddle. ESC to menu, R to restart. Difficulty affects AI & ball speed.",
            "Minesweeper": "Controls: Left Click to reveal, Right Click to flag. ESC to menu, R to restart. Difficulty affects board size & mines.",
            "Jump King": "Controls: LEFT/RIGHT arrow keys to move. Hold SPACE to charge jump, release to jump. ESC to menu, R to restart.",
            "Maze Game": "Controls: ARROW keys to move. Find the red circle. ESC to menu, R to restart. Size affects maze dimensions.",
            "Tetris": "Controls: LEFT/RIGHT arrow keys to move. UP arrow to rotate. DOWN arrow for soft drop. SPACE for hard drop. ESC to menu, R to restart.",
            "Console": "Press 'S' in any game to save its state. Load from Main Menu. Use 'Set Difficulty/Size' options to change settings without starting a new game."
        }
        self.help_menu_lines = []
        self._format_help_menu_content()

    def _get_scaled_font_size(self, base_size):
        """Calculates a scaled font size based on the current window height, with an upper limit."""
        scale_factor = self.screen.get_height() / BASE_SCREEN_HEIGHT
        return min(int(base_size * scale_factor), self.MAX_FONT_SIZE)

    def _scale_mouse_pos(self, pos):
        """Converts mouse coordinates from actual window size to base screen size."""
        current_window_width, current_window_height = self.screen.get_size()
        scale_x = BASE_SCREEN_WIDTH / current_window_width
        scale_y = BASE_SCREEN_HEIGHT / current_window_height
        return int(pos[0] * scale_x), int(pos[1] * scale_y)

    def _format_help_menu_content(self):
        """Formats help menu content into lines for display."""
        # Re-render help menu lines when font size might change
        self.help_menu_lines = []
        # No title for help menu anymore, so the main font size is used for section titles
        title_font = pygame.font.Font(None, self._get_scaled_font_size(self.base_font_size))
        
        # Content font is smaller
        content_font_size_ratio = 0.6 # Content font is 60% of base_font_size
        content_font = pygame.font.Font(None, self._get_scaled_font_size(int(self.base_font_size * content_font_size_ratio))) 
        
        # Max width for text wrapping, scaled by current window width
        # This should be based on BASE_SCREEN_WIDTH for consistency, then scaled by window aspect ratio
        max_line_width_base = BASE_SCREEN_WIDTH - 100 # 50px padding on each side
        
        for title, text in self.help_menu_content.items():
            self.help_menu_lines.append(title_font.render(title, True, YELLOW))
            
            words = text.split(' ')
            current_line = ""
            for word in words:
                test_line = current_line + word + " "
                # Check against the scaled width of the text using the content_font
                if content_font.size(test_line)[0] < max_line_width_base:
                    current_line = test_line
                else:
                    self.help_menu_lines.append(content_font.render(current_line, True, WHITE))
                    current_line = word + " "
            self.help_menu_lines.append(content_font.render(current_line, True, WHITE))
            self.help_menu_lines.append(content_font.render("", True, WHITE)) # Blank line for spacing


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
                elif event.type == pygame.VIDEORESIZE:
                    # Update the actual window surface and re-render help text if needed
                    self.window_width, self.window_height = event.size
                    self.screen = pygame.display.set_mode((self.window_width, self.window_height), pygame.RESIZABLE)
                    self._format_help_menu_content() # Reformat help text for new font size
                elif self.active_game_key == "menu":
                    self._handle_menu_event(event)
                elif self.active_game_key == "pong_difficulty_selection" or self.active_game_key == "pong_difficulty_settings":
                    self._handle_pong_difficulty_menu_event(event)
                elif self.active_game_key == "minesweeper_difficulty_selection" or self.active_game_key == "minesweeper_difficulty_settings":
                    self._handle_minesweeper_difficulty_menu_event(event)
                elif self.active_game_key == "maze_size_selection" or self.active_game_key == "maze_size_settings":
                    self._handle_maze_size_menu_event(event)
                elif self.active_game_key == "help":
                    self._handle_help_menu_event(event)
                else:
                    # Pass events to the active game
                    self.games[self.active_game_key].handle_event(event)

            # All drawing happens on the internal display_surface
            if self.active_game_key == "menu":
                self._update_menu(dt)
                self._draw_menu()
            elif self.active_game_key == "pong_difficulty_selection" or self.active_game_key == "pong_difficulty_settings":
                self._update_pong_difficulty_menu(dt)
                self._draw_pong_difficulty_menu(self.active_game_key == "pong_difficulty_selection") # Pass flag for title
            elif self.active_game_key == "minesweeper_difficulty_selection" or self.active_game_key == "minesweeper_difficulty_settings":
                self._update_minesweeper_difficulty_menu(dt)
                self._draw_minesweeper_difficulty_menu(self.active_game_key == "minesweeper_difficulty_selection") # Pass flag for title
            elif self.active_game_key == "maze_size_selection" or self.active_game_key == "maze_size_settings":
                self._update_maze_size_menu(dt)
                self._draw_maze_size_menu(self.active_game_key == "maze_size_selection")
            elif self.active_game_key == "help":
                self._update_help_menu(dt)
                self._draw_help_menu()
            else:
                # Update and draw the active game
                self.games[self.active_game_key].update(dt)
                self.games[self.active_game_key].draw(self.display_surface) # Draw to display_surface

            # Scale the internal display_surface to the actual window size and blit it
            self.screen.blit(pygame.transform.scale(self.display_surface, self.screen.get_size()), (0, 0))
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def _handle_menu_event(self, event):
        """Handles events when the main menu is active."""
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
        """Updates main menu logic (currently none needed beyond event handling)."""
        pass

    def _draw_menu(self):
        """Draws the main menu screen on display_surface."""
        self.display_surface.fill(BLACK)
        
        menu_font = pygame.font.Font(None, self._get_scaled_font_size(self.base_font_size))
        
        # Calculate ideal vertical spacing based on a fixed ratio
        ideal_spacing = self._get_scaled_font_size(40) 
        
        # Calculate total height of menu items + spacing
        # No title, so start from a fixed top padding
        top_padding = self._get_scaled_font_size(80) # Padding from the top of the screen
        min_bottom_clearance = self._get_scaled_font_size(30) # Minimum clearance for the save hint
        
        # Available vertical space for the menu, excluding top padding and bottom clearance
        available_menu_space = BASE_SCREEN_HEIGHT - top_padding - min_bottom_clearance

        # Calculate total height of all menu items if they were stacked with their actual font height
        total_font_height = sum(menu_font.size(text)[1] for text, _ in self.menu_options)

        # Calculate the number of gaps between menu items
        num_gaps = len(self.menu_options) - 1
        num_gaps = max(0, num_gaps) # Ensure non-negative

        # Calculate the total height required by menu items including their own height and desired spacing
        total_required_height = total_font_height + (ideal_spacing * num_gaps)

        # Determine actual spacing. If ideal height fits, use ideal spacing.
        # Otherwise, compress spacing to fit.
        if total_required_height > available_menu_space:
            # If menu is too tall, calculate new compressed spacing
            if num_gaps > 0:
                adjusted_spacing = (available_menu_space - total_font_height) // num_gaps
                adjusted_spacing = max(self._get_scaled_font_size(10), adjusted_spacing) # Ensure a minimum spacing
            else: # Only one item, no spacing between items
                adjusted_spacing = 0
            
            current_spacing_offset = adjusted_spacing + menu_font.get_height()
            # Recalculate start_y to center the compressed menu block
            effective_menu_height = total_font_height + adjusted_spacing * num_gaps
            start_y = top_padding + (available_menu_space - effective_menu_height) // 2
        else:
            # If ideal height fits, use ideal spacing and center the whole block
            current_spacing_offset = ideal_spacing
            start_y = top_padding + (available_menu_space - total_required_height) // 2


        current_y_pos = start_y
        for i, (text, _) in enumerate(self.menu_options):
            color = YELLOW if i == self.selected_menu_index else WHITE
            menu_text = menu_font.render(text, True, color)
            self.display_surface.blit(menu_text, menu_text.get_rect(center=(BASE_SCREEN_WIDTH // 2, current_y_pos + menu_text.get_height() // 2)))
            current_y_pos += current_spacing_offset


        save_hint_font = pygame.font.Font(None, self._get_scaled_font_size(30))
        save_hint_text = save_hint_font.render("Press 'S' to Save Current Game (if active)", True, LIGHT_GRAY)
        # Position save hint text at a fixed offset from the bottom of BASE_SCREEN_HEIGHT
        self.display_surface.blit(save_hint_text, save_hint_text.get_rect(center=(BASE_SCREEN_WIDTH // 2, BASE_SCREEN_HEIGHT - self._get_scaled_font_size(20))))


    def _execute_menu_option(self):
        """Executes the selected menu option."""
        selected_action = self.menu_options[self.selected_menu_index][1]

        if selected_action == "pong_difficulty_selection":
            self.active_game_key = "pong_difficulty_selection"
            self.selected_pong_difficulty_index = 0
        elif selected_action == "pong_difficulty_settings":
            self.active_game_key = "pong_difficulty_settings"
            self.selected_pong_difficulty_index = 0
        elif selected_action == "minesweeper_difficulty_selection":
            self.active_game_key = "minesweeper_difficulty_selection"
            self.selected_minesweeper_difficulty_index = 0
        elif selected_action == "minesweeper_difficulty_settings":
            self.active_game_key = "minesweeper_difficulty_settings"
            self.selected_minesweeper_difficulty_index = 0
        elif selected_action == "jump_king":
            self.set_active_game("jump_king")
        elif selected_action == "maze_size_selection":
            self.active_game_key = "maze_size_selection"
            self.selected_maze_size_index = 0
        elif selected_action == "maze_size_settings":
            self.active_game_key = "maze_size_settings"
            self.selected_maze_size_index = 0
        elif selected_action == "tetris":
            self.set_active_game("tetris")
        elif selected_action == "load":
            self._load_saved_game()
        elif selected_action == "help":
            self.active_game_key = "help"
        elif selected_action == "exit":
            pygame.quit()
            sys.exit()

    def _handle_pong_difficulty_menu_event(self, event):
        """Handles events for the Pong difficulty menu."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_pong_difficulty_index = (self.selected_pong_difficulty_index - 1) % len(self.pong_difficulty_options)
            elif event.key == pygame.K_DOWN:
                self.selected_pong_difficulty_index = (self.selected_pong_difficulty_index + 1) % len(self.pong_difficulty_options)
            elif event.key == pygame.K_RETURN:
                selected_difficulty_action = self.pong_difficulty_options[self.selected_pong_difficulty_index][1]
                if selected_difficulty_action == "back":
                    self.active_game_key = "menu"
                else:
                    self.games["pong"].set_difficulty(selected_difficulty_action)
                    print(f"Pong difficulty set to: {selected_difficulty_action.capitalize()}")
                    if self.active_game_key == "pong_difficulty_selection": # If coming from "Play Pong"
                        self.set_active_game("pong") # Start the game
                    else: # If coming from "Set Pong Difficulty"
                        self.active_game_key = "menu" # Return to main menu

    def _update_pong_difficulty_menu(self, dt):
        """Updates Pong difficulty menu logic."""
        pass # No dynamic updates needed here

    def _draw_pong_difficulty_menu(self, is_selection_menu):
        """Draws the Pong difficulty menu on display_surface."""
        self.display_surface.fill(BLACK)
        title_font = pygame.font.Font(None, self._get_scaled_font_size(70))
        title_text_str = "Select Pong Difficulty" if is_selection_menu else "Set Pong Difficulty"
        title_text = title_font.render(title_text_str, True, WHITE)
        title_rect = title_text.get_rect(center=(BASE_SCREEN_WIDTH // 2, 80)) # Adjusted for no main title
        self.display_surface.blit(title_text, title_rect)

        menu_font = pygame.font.Font(None, self._get_scaled_font_size(self.base_font_size))
        
        ideal_spacing = self._get_scaled_font_size(40)
        
        top_padding = title_rect.bottom + self._get_scaled_font_size(20) # Padding below title
        min_bottom_clearance = self._get_scaled_font_size(30)
        available_menu_space = BASE_SCREEN_HEIGHT - top_padding - min_bottom_clearance

        total_font_height = sum(menu_font.size(text)[1] for text, _ in self.pong_difficulty_options)
        num_gaps = len(self.pong_difficulty_options) - 1
        num_gaps = max(0, num_gaps)

        total_required_height = total_font_height + (ideal_spacing * num_gaps)

        if total_required_height > available_menu_space:
            if num_gaps > 0:
                adjusted_spacing = (available_menu_space - total_font_height) // num_gaps
                adjusted_spacing = max(self._get_scaled_font_size(10), adjusted_spacing)
            else:
                adjusted_spacing = 0
            
            current_spacing_offset = adjusted_spacing + menu_font.get_height()
            effective_menu_height = total_font_height + adjusted_spacing * num_gaps
            start_y = top_padding + (available_menu_space - effective_menu_height) // 2
        else:
            current_spacing_offset = ideal_spacing
            start_y = top_padding + (available_menu_space - total_required_height) // 2

        current_y_pos = start_y
        for i, (text, difficulty_level) in enumerate(self.pong_difficulty_options):
            color = YELLOW if i == self.selected_pong_difficulty_index else WHITE
            # Highlight current difficulty if it matches
            if difficulty_level == self.games["pong"].difficulty and difficulty_level != "back":
                color = ORANGE # Use a different color for the currently active setting
            menu_text = menu_font.render(text, True, color)
            self.display_surface.blit(menu_text, menu_text.get_rect(center=(BASE_SCREEN_WIDTH // 2, current_y_pos + menu_text.get_height() // 2)))
            current_y_pos += current_spacing_offset

    def _handle_minesweeper_difficulty_menu_event(self, event):
        """Handles events for the Minesweeper difficulty menu."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_minesweeper_difficulty_index = (self.selected_minesweeper_difficulty_index - 1) % len(self.minesweeper_difficulty_options)
            elif event.key == pygame.K_DOWN:
                self.selected_minesweeper_difficulty_index = (self.selected_minesweeper_difficulty_index + 1) % len(self.minesweeper_difficulty_options)
            elif event.key == pygame.K_RETURN:
                selected_difficulty_action = self.minesweeper_difficulty_options[self.selected_minesweeper_difficulty_index][1]
                if selected_difficulty_action == "back":
                    self.active_game_key = "menu"
                else:
                    self.games["minesweeper"].set_difficulty(selected_difficulty_action)
                    print(f"Minesweeper difficulty set to: {selected_difficulty_action.capitalize()}")
                    if self.active_game_key == "minesweeper_difficulty_selection": # If coming from "Play Minesweeper"
                        self.set_active_game("minesweeper") # Start the game
                    else: # If coming from "Set Minesweeper Difficulty"
                        self.active_game_key = "menu" # Return to main menu

    def _update_minesweeper_difficulty_menu(self, dt):
        """Updates Minesweeper difficulty menu logic."""
        pass

    def _draw_minesweeper_difficulty_menu(self, is_selection_menu):
        """Draws the Minesweeper difficulty menu on display_surface."""
        self.display_surface.fill(BLACK)
        title_font = pygame.font.Font(None, self._get_scaled_font_size(70))
        title_text_str = "Select Minesweeper Difficulty" if is_selection_menu else "Set Minesweeper Difficulty"
        title_text = title_font.render(title_text_str, True, WHITE)
        title_rect = title_text.get_rect(center=(BASE_SCREEN_WIDTH // 2, 80)) # Adjusted for no main title
        self.display_surface.blit(title_text, title_rect)

        menu_font = pygame.font.Font(None, self._get_scaled_font_size(self.base_font_size))
        
        ideal_spacing = self._get_scaled_font_size(40)
        
        top_padding = title_rect.bottom + self._get_scaled_font_size(20)
        min_bottom_clearance = self._get_scaled_font_size(30)
        available_menu_space = BASE_SCREEN_HEIGHT - top_padding - min_bottom_clearance

        total_font_height = sum(menu_font.size(text)[1] for text, _ in self.minesweeper_difficulty_options)
        num_gaps = len(self.minesweeper_difficulty_options) - 1
        num_gaps = max(0, num_gaps)

        total_required_height = total_font_height + (ideal_spacing * num_gaps)

        if total_required_height > available_menu_space:
            if num_gaps > 0:
                adjusted_spacing = (available_menu_space - total_font_height) // num_gaps
                adjusted_spacing = max(self._get_scaled_font_size(10), adjusted_spacing)
            else:
                adjusted_spacing = 0
            
            current_spacing_offset = adjusted_spacing + menu_font.get_height()
            effective_menu_height = total_font_height + adjusted_spacing * num_gaps
            start_y = top_padding + (available_menu_space - effective_menu_height) // 2
        else:
            current_spacing_offset = ideal_spacing
            start_y = top_padding + (available_menu_space - total_required_height) // 2

        current_y_pos = start_y
        for i, (text, difficulty_level) in enumerate(self.minesweeper_difficulty_options):
            color = YELLOW if i == self.selected_minesweeper_difficulty_index else WHITE
            if difficulty_level == self.games["minesweeper"].difficulty and difficulty_level != "back":
                color = ORANGE
            menu_text = menu_font.render(text, True, color)
            self.display_surface.blit(menu_text, menu_text.get_rect(center=(BASE_SCREEN_WIDTH // 2, current_y_pos + menu_text.get_height() // 2)))
            current_y_pos += current_spacing_offset

    def _handle_maze_size_menu_event(self, event):
        """Handles events for the Maze size menu."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_maze_size_index = (self.selected_maze_size_index - 1) % len(self.maze_size_options)
            elif event.key == pygame.K_DOWN:
                self.selected_maze_size_index = (self.selected_maze_size_index + 1) % len(self.maze_size_options)
            elif event.key == pygame.K_RETURN:
                selected_size_action = self.maze_size_options[self.selected_maze_size_index][1]
                if selected_size_action == "back":
                    self.active_game_key = "menu"
                else:
                    self.games["maze"].set_size(selected_size_action)
                    print(f"Maze size set to: {selected_size_action.capitalize()}")
                    if self.active_game_key == "maze_size_selection": # If coming from "Play Maze Game"
                        self.set_active_game("maze") # Start the game
                    else: # If coming from "Set Maze Size"
                        self.active_game_key = "menu" # Return to main menu

    def _update_maze_size_menu(self, dt):
        """Updates Maze size menu logic."""
        pass

    def _draw_maze_size_menu(self, is_selection_menu):
        """Draws the Maze size menu on display_surface."""
        self.display_surface.fill(BLACK)
        title_font = pygame.font.Font(None, self._get_scaled_font_size(70))
        title_text_str = "Select Maze Size" if is_selection_menu else "Set Maze Size"
        title_text = title_font.render(title_text_str, True, WHITE)
        title_rect = title_text.get_rect(center=(BASE_SCREEN_WIDTH // 2, 80)) # Adjusted for no main title
        self.display_surface.blit(title_text, title_rect)

        menu_font = pygame.font.Font(None, self._get_scaled_font_size(self.base_font_size))

        ideal_spacing = self._get_scaled_font_size(40)
        
        top_padding = title_rect.bottom + self._get_scaled_font_size(20)
        min_bottom_clearance = self._get_scaled_font_size(30)
        available_menu_space = BASE_SCREEN_HEIGHT - top_padding - min_bottom_clearance

        total_font_height = sum(menu_font.size(text)[1] for text, _ in self.maze_size_options)
        num_gaps = len(self.maze_size_options) - 1
        num_gaps = max(0, num_gaps)

        total_required_height = total_font_height + (ideal_spacing * num_gaps)

        if total_required_height > available_menu_space:
            if num_gaps > 0:
                adjusted_spacing = (available_menu_space - total_font_height) // num_gaps
                adjusted_spacing = max(self._get_scaled_font_size(10), adjusted_spacing)
            else:
                adjusted_spacing = 0
            
            current_spacing_offset = adjusted_spacing + menu_font.get_height()
            effective_menu_height = total_font_height + adjusted_spacing * num_gaps
            start_y = top_padding + (available_menu_space - effective_menu_height) // 2
        else:
            current_spacing_offset = ideal_spacing
            start_y = top_padding + (available_menu_space - total_required_height) // 2

        current_y_pos = start_y
        for i, (text, size_level) in enumerate(self.maze_size_options):
            color = YELLOW if i == self.selected_maze_size_index else WHITE
            if size_level == self.games["maze"].size and size_level != "back":
                color = ORANGE
            menu_text = menu_font.render(text, True, color)
            self.display_surface.blit(menu_text, menu_text.get_rect(center=(BASE_SCREEN_WIDTH // 2, current_y_pos + menu_text.get_height() // 2)))
            current_y_pos += current_spacing_offset


    def _handle_help_menu_event(self, event):
        """Handles events for the Help menu."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                self.active_game_key = "menu" # Return to main menu

    def _update_help_menu(self, dt):
        """Updates Help menu logic."""
        pass # No dynamic updates needed here

    def _draw_help_menu(self):
        """Draws the Help menu on display_surface."""
        self.display_surface.fill(BLACK)
        # No main title for help menu anymore
        # title_font = pygame.font.Font(None, self._get_scaled_font_size(70))
        # title_text = title_font.render("Help & Controls", True, WHITE)
        # self.display_surface.blit(title_text, title_text.get_rect(center=(BASE_SCREEN_WIDTH // 2, 50)))

        y_offset = self._get_scaled_font_size(50) # Start from a reasonable top padding
        # Use the pre-formatted lines from _format_help_menu_content
        for line_surface in self.help_menu_lines:
            self.display_surface.blit(line_surface, (50, y_offset))
            y_offset += line_surface.get_height() + self._get_scaled_font_size(5) # Add some line spacing

        return_text_font = pygame.font.Font(None, self._get_scaled_font_size(40))
        return_text = return_text_font.render("Press ESC or ENTER to return to Main Menu", True, LIGHT_GRAY)
        self.display_surface.blit(return_text, return_text.get_rect(center=(BASE_SCREEN_WIDTH // 2, BASE_SCREEN_HEIGHT - self._get_scaled_font_size(20))))


    def _save_current_game(self):
        """Saves the state of the currently active game."""
        if self.active_game_key in self.games: # Only save if a game is active, not a menu
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
            print("Cannot save from the current screen. Please start a game first.")

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
