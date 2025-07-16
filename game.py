import pygame
import sys
import random
import yaml

height = 0
safty_platform_interval = 1000
# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 30
HORIZONTAL_PLATFORM_RANGE = 300 # Max horizontal distance from previous platform's center   
# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAYER_COLOR = (255, 0, 0)
SAFTEY_PLATFORM_COLOR = (255, 250, 0)
PLATFORM_COLOR = (0, 128, 0)
BACKGROUND_COLOR = (135, 206, 235) # A sky blue color
UI_FONT_COLOR = (255, 255, 0)

# Player properties
PLAYER_WIDTH = 30
PLAYER_HEIGHT = 30
PLAYER_ACC = 1.5
PLAYER_FRICTION = -0.16
PLAYER_GRAVITY = 1
MAX_FALL_SPEED = 30

# Jump properties
JUMP_CHARGE_RATE = 1.5 # Increased for faster charging
MIN_JUMP_POWER = 5
MAX_JUMP_POWER = 25
JUMP_HORIZONTAL_BOOST = 5

# --- Player Class ---
class Player(pygame.sprite.Sprite):
    """
    Represents the player character.
    Handles movement, jumping, and collisions.
    """
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([PLAYER_WIDTH, PLAYER_HEIGHT])
        self.image.fill(PLAYER_COLOR)
        self.rect = self.image.get_rect()
        
        # Position and velocity vectors
        self.pos = pygame.math.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT - PLAYER_HEIGHT)
        self.vel = pygame.math.Vector2(0, 0)
        self.acc = pygame.math.Vector2(0, 0)

        # State variables
        self.on_ground = False
        self.is_charging = False
        self.jump_charge = 0
        self.direction = 1 # 1 for right, -1 for left

    def update(self, platforms):
        """
        Update player's state each frame.
        Handles physics, movement, and collisions.
        """
        # --- Physics and Input ---
        self.acc = pygame.math.Vector2(0, PLAYER_GRAVITY)
        keys = pygame.key.get_pressed()

        if not self.is_charging:
            if keys[pygame.K_LEFT]:
                self.acc.x = -PLAYER_ACC
                self.direction = -1
            if keys[pygame.K_RIGHT]:
                self.acc.x = PLAYER_ACC
                self.direction = 1

        # Apply friction
        self.acc.x += self.vel.x * PLAYER_FRICTION
        # Update velocity based on acceleration (Euler integration)
        self.vel += self.acc
        # Limit falling speed
        if self.vel.y > MAX_FALL_SPEED:
            self.vel.y = MAX_FALL_SPEED

        # --- Position Update and Collision Detection ---
        # Horizontal movement and collision
        self.pos.x += self.vel.x
        self.rect.centerx = round(self.pos.x)
        
        # Horizontal collision check
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel.x > 0:  # Moving right
                    self.rect.right = platform.rect.left
                elif self.vel.x < 0:  # Moving left
                    self.rect.left = platform.rect.right
                self.pos.x = self.rect.centerx

        # Vertical movement and collision
        self.pos.y += self.vel.y
        self.rect.midbottom = (self.rect.centerx, round(self.pos.y))
        
        # Vertical collision check
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel.y < 0:
                    self.rect.top = platform.rect.bottom
                    self.vel.y = 0
                elif self.vel.y > 0:
                    self.rect.bottom = platform.rect.top
                    self.vel.y = 0
                    self.on_ground = True
                self.pos.y = self.rect.bottom


        # --- Screen Boundaries ---
        if self.rect.left < 0:
            self.rect.left = 0
            self.pos.x = self.rect.centerx
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.pos.x = self.rect.centerx
        
    def start_charge(self):
        """Begin charging a jump if on the ground."""
        if self.on_ground:
            self.is_charging = True
            self.jump_charge = MIN_JUMP_POWER

    def charge_jump(self):
        """Increase the jump charge while the key is held."""
        if self.is_charging:

            self.jump_charge += JUMP_CHARGE_RATE
            if self.jump_charge > MAX_JUMP_POWER:
                self.jump_charge = MAX_JUMP_POWER

    def jump(self):
        """Execute the jump with the stored charge."""
        if self.is_charging:
            self.vel.y = -self.jump_charge
            self.vel.x = self.direction * JUMP_HORIZONTAL_BOOST
            self.is_charging = False
            self.on_ground = False
            self.jump_charge = 0

    def draw_charge_bar(self, surface, camera_offset):
        """Draws the visual indicator for jump charge, adjusted for camera."""
        bar_width = 50
        bar_height = 8
        charge_ratio = (self.jump_charge - MIN_JUMP_POWER) / (MAX_JUMP_POWER - MIN_JUMP_POWER)
        charge_ratio = max(0, min(charge_ratio, 1))
        fill_width = int(bar_width * charge_ratio)
        
        # Position the bar relative to the player's on-screen position
        bar_x = self.rect.centerx - bar_width // 2
        bar_y = self.rect.top - 15 + camera_offset
        
        pygame.draw.rect(surface, BLACK, (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4))
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height))
        if fill_width > 0:
            pygame.draw.rect(surface, (255, 255, 0), (bar_x, bar_y, fill_width, bar_height))

# --- Platform Class ---
class Platform(pygame.sprite.Sprite):
    """Represents a static platform for the player to jump on."""
    def __init__(self, x, y, width, height, color=PLATFORM_COLOR):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

# --- Game Class ---
class Game:
    """Main game class to manage the game loop, states, and objects."""
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Test Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)
        self.running = True

        # Game objects
        self.player = Player()
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        self.max_height=0
        
        # Camera
        self.camera_offset_y = 0
        
        # Level generation
        self.last_platform_y = SCREEN_HEIGHT - 40
        self.last_platform_x = SCREEN_WIDTH / 2
        self.create_initial_level()

    def create_initial_level(self):
        """Creates the starting ground platform."""
        ground = Platform(0, SCREEN_HEIGHT - 30, SCREEN_WIDTH, 40)
        self.all_sprites.add(ground)
        self.platforms.add(ground)
        # Generate the first screen of platforms
        self.generate_platforms(self.last_platform_y, -SCREEN_HEIGHT)
    
    def delete_platforms(self,height):
        """Deletes platforms that are no longer visible to the player."""
        with open("POtato.obj", 'wb') as f:
            yaml.dump(self.platforms, f)
        for platform in self.platforms:
            if platform.rect.top > SCREEN_HEIGHT-30-(safty_platform_interval*(height//safty_platform_interval)):
                platform.kill()
                self.platforms.remove(platform)
                self.all_sprites.remove(platform)

    def generate_saftey_platform(self,height):
        ground = Platform(0,SCREEN_HEIGHT-30-(safty_platform_interval*(height//safty_platform_interval)), SCREEN_WIDTH, 10, SAFTEY_PLATFORM_COLOR)
        self.all_sprites.add(ground)
        self.platforms.add(ground)
        self.delete_platforms(height)



    def generate_platforms(self, start_y, end_y):
        """Procedurally generates platforms in a given y-range,
        ensuring new platforms are within a horizontal range of the previous one."""

        y = start_y
        while y > end_y:
            y_gap = random.randint(80, 150)
            y -= y_gap
            
            width = random.randint(100, 250)
            
            # Calculate min and max x based on the last platform's center and horizontal range
            min_x_allowed = int(max(0, self.last_platform_x - HORIZONTAL_PLATFORM_RANGE))
            max_x_allowed = int(min(SCREEN_WIDTH - width, self.last_platform_x + HORIZONTAL_PLATFORM_RANGE))
            
            # Ensure there's a valid range to pick from
            if min_x_allowed > max_x_allowed: # This can happen if width is too large or range is too small
                # If the range is invalid, try to center it or pick a default
                x = random.randint(0, SCREEN_WIDTH - width) # Fallback to full screen width
            else:
                x = random.randint(min_x_allowed, max_x_allowed)
            
            platform = Platform(x, y, width, 20)
            self.all_sprites.add(platform)
            self.platforms.add(platform)
            self.last_platform_y = y
            self.last_platform_x = x + width / 2 # Update last_platform_x to the center of the new platform

            end_y=height+100

    def manage_level(self):
        """Generates new platforms as player climbs and removes old ones."""
        # Generate new platforms if player is getting high
        if self.player.pos.y < -self.camera_offset_y + SCREEN_HEIGHT:
            self.generate_platforms(self.last_platform_y, self.last_platform_y - SCREEN_HEIGHT * 2*3/2)
            # self.delete_platforms(self.player.pos.y)



    def run(self):
        """The main game loop."""
        while self.running:
            x=1
            self.handle_events()
            self.clock.tick(FPS)
            self.update()
            self.draw()
            self.player.vel.x=round(self.player.vel.x,5)
            self.player.vel.y=round(self.player.vel.y,5)
        pygame.quit()
        sys.exit()

    def handle_events(self):
        """Process all user inputs and events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                    self.player.start_charge()
            if event.type == pygame.KEYUP and event.key == pygame.K_UP:
                self.player.jump()


    def update(self):
        """Update all game objects and game logic."""
        if self.player.is_charging:
            self.player.charge_jump()
            
        self.player.update(self.platforms)
        self.update_camera()
        self.manage_level()

    def update_camera(self):
        """Adjusts the camera's vertical position for smooth scrolling."""
        # The target for the camera is to have the player in the middle of the screen
        target_y = -self.player.pos.y + SCREEN_HEIGHT / 2
        
        # Smoothly move the camera towards the target y-position (lerp)
        # This creates the smooth scrolling effect
        self.camera_offset_y += (target_y - self.camera_offset_y) * 0.1

        # Reset player if they fall below the starting point of the world
        if self.player.pos.y > SCREEN_HEIGHT:
             self.reset_player()
    
    def reset_player(self):
        """Resets the player to the starting position."""
        self.player.pos = pygame.math.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT - PLAYER_HEIGHT)
        self.player.vel = pygame.math.Vector2(0, 0)
        # Don't reset camera immediately to avoid jarring jump
        # It will smoothly scroll back up to the player

    def draw(self):
        """Render all game objects to the screen."""
        self.screen.fill(BACKGROUND_COLOR)

        # Draw all sprites with the smooth camera offset
        for sprite in self.all_sprites:
            draw_rect = sprite.rect.copy()
            draw_rect.y += self.camera_offset_y
            self.screen.blit(sprite.image, draw_rect)
        
        # Draw the charge bar relative to the player's on-screen position
        if self.player.is_charging:
            self.player.draw_charge_bar(self.screen, self.camera_offset_y)
        
        # UI Text
        height = max(0, -int(self.player.pos.y - (SCREEN_HEIGHT - PLAYER_HEIGHT)))
        height_text = self.font.render(f"Height: {round(height+3,-1)}", True, UI_FONT_COLOR)
        if height>self.max_height:
            self.max_height=height
        max_height_text = self.font.render(f"Max Height: {self.max_height}", True, UI_FONT_COLOR)
        self.screen.blit(max_height_text, (10, 40))
        self.screen.blit(height_text, (10, 10))

        pygame.display.flip()
        if height%safty_platform_interval<20 and height%safty_platform_interval>0 and not height<safty_platform_interval:
            game.generate_saftey_platform(max(0, -int(self.player.pos.y - (SCREEN_HEIGHT - PLAYER_HEIGHT))))



# --- Main Execution ---
if __name__ == "__main__":
    game = Game()
    game.run()
