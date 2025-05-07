import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2D Car Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0) # Added for Game Over message

# Font for Game Over message
game_over_font = pygame.font.Font(None, 74)
restart_quit_font = pygame.font.Font(None, 36) # Font for restart/quit messages

# Sprite and Scaling Constants
CAR_SPRITE_WIDTH = 16
CAR_SPRITE_HEIGHT = 16
SCALED_CAR_WIDTH = 64
SCALED_CAR_HEIGHT = 64

OBSTACLE_SPRITE_WIDTH = 16
OBSTACLE_SPRITE_HEIGHT = 16
SCALED_OBSTACLE_WIDTH = 48
SCALED_OBSTACLE_HEIGHT = 48

# Function to display Game Over message
def display_game_over_message(surface):
    text_surface = game_over_font.render('Game Over', True, RED)
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
    surface.blit(text_surface, text_rect)

    restart_text = restart_quit_font.render('Press R to Restart or Q to Quit', True, BLACK)
    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
    surface.blit(restart_text, restart_rect)

# Load car image (spritesheet processing)
try:
    loaded_car_spritesheet = pygame.image.load("Mini Pixel Pack 2/Cars/Player_red (16 x 16).png").convert_alpha()
    # Extract the first car sprite (0,0) with size CAR_SPRITE_WIDTH x CAR_SPRITE_HEIGHT
    player_car_image_template = loaded_car_spritesheet.subsurface(pygame.Rect(0, 0, CAR_SPRITE_WIDTH, CAR_SPRITE_HEIGHT))
    scaled_player_car_image = pygame.transform.scale(player_car_image_template, (SCALED_CAR_WIDTH, SCALED_CAR_HEIGHT))
except pygame.error as e:
    print(f"Unable to load car image: {e}")
    # Create a placeholder surface if image loading fails
    scaled_player_car_image = pygame.Surface((SCALED_CAR_WIDTH, SCALED_CAR_HEIGHT))
    scaled_player_car_image.fill(BLACK) # Fill with a color, e.g., black

# Load obstacle spritesheet
try:
    loaded_obstacle_spritesheet = pygame.image.load("Mini Pixel Pack 2/Props/Misc_props (16 x 16).png").convert_alpha()
except pygame.error as e:
    print(f"Unable to load obstacle spritesheet: {e}")
    loaded_obstacle_spritesheet = None

# Placeholder surface if obstacle spritesheet loading fails, for the Obstacle class to use
default_obstacle_surface = pygame.Surface((SCALED_OBSTACLE_WIDTH, SCALED_OBSTACLE_HEIGHT))
default_obstacle_surface.fill(BLACK)

# Player Car Class
class PlayerCar(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 5 # Adjusted speed for better control without background scroll reference

    def update(self, keys):
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_d]:
            self.rect.x += self.speed

        # Keep car within screen boundaries (horizontal)
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

# Obstacle Class
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, spritesheet): # Added spritesheet parameter
        super().__init__()
        
        if spritesheet:
            # Assuming sprites are arranged horizontally, each OBSTACLE_SPRITE_WIDTH wide
            num_sprites = spritesheet.get_width() // OBSTACLE_SPRITE_WIDTH
            if num_sprites > 0:
                sprite_index = random.randint(0, num_sprites - 1)
                sprite_x_offset = sprite_index * OBSTACLE_SPRITE_WIDTH
                
                sub_image = spritesheet.subsurface(pygame.Rect(sprite_x_offset, 0, OBSTACLE_SPRITE_WIDTH, OBSTACLE_SPRITE_HEIGHT))
                self.image = pygame.transform.scale(sub_image, (SCALED_OBSTACLE_WIDTH, SCALED_OBSTACLE_HEIGHT))
            else: # Spritesheet might be empty or not wide enough
                self.image = default_obstacle_surface.copy()
        else:
            # Use a placeholder if spritesheet failed to load or was None
            self.image = default_obstacle_surface.copy()

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill() # Remove obstacle if it goes off screen

player_car = PlayerCar(scaled_player_car_image, (SCREEN_WIDTH - SCALED_CAR_WIDTH) // 2, SCREEN_HEIGHT - SCALED_CAR_HEIGHT - 10)
all_sprites = pygame.sprite.Group()
all_sprites.add(player_car)

# Obstacle properties
obstacles = pygame.sprite.Group()
obstacle_spawn_timer = 0
obstacle_spawn_delay = 100 # Adjusted spawn delay
obstacle_speed = 5 # Adjusted obstacle speed

# Game state
game_over = False

# Function to reset the game state
def reset_game():
    global player_car, obstacles, all_sprites, obstacle_spawn_timer, game_over, camera_x
    player_car = PlayerCar(scaled_player_car_image, (SCREEN_WIDTH - SCALED_CAR_WIDTH) // 2, SCREEN_HEIGHT - SCALED_CAR_HEIGHT - 10)
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player_car)
    obstacles = pygame.sprite.Group()
    obstacle_spawn_timer = 0
    camera_x = 0
    game_over = False

# Game loop
running = True
clock = pygame.time.Clock() # For managing FPS
camera_x = 0 # Initialize camera_x

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if game_over:
                if event.key == pygame.K_r:
                    reset_game()
                if event.key == pygame.K_q:
                    running = False

    # Handle key presses
    keys = pygame.key.get_pressed()
    
    if not game_over:
        # Update player car
        player_car.update(keys) # Call update once with the current keys state

        # Update camera based on player's position
        # The camera tries to keep the player in the middle of the screen.
        # The player's rect.x is its "world" position.
        camera_x = player_car.rect.centerx - SCREEN_WIDTH // 2
        # Clamp camera to prevent showing too much empty space if the world is smaller than the screen
        # For now, assume world is at least as wide as the screen, or player is bounded.
        # If we had a defined world width:
        # world_width = 1600 # Example world width
        # if camera_x < 0:
        #     camera_x = 0
        # if camera_x > world_width - SCREEN_WIDTH:
        #     camera_x = world_width - SCREEN_WIDTH

        # Spawn obstacles
        obstacle_spawn_timer += 1
        if obstacle_spawn_timer >= obstacle_spawn_delay:
            obstacle_spawn_timer = 0
            obstacle_x = random.randint(0, SCREEN_WIDTH - SCALED_OBSTACLE_WIDTH)
            new_obstacle = Obstacle(obstacle_x, -SCALED_OBSTACLE_HEIGHT, obstacle_speed, loaded_obstacle_spritesheet)
            obstacles.add(new_obstacle)
            all_sprites.add(new_obstacle) # Add obstacles to all_sprites to be drawn

        # Update obstacles
        obstacles.update()

        # Check for collisions
        collided_obstacles = pygame.sprite.spritecollide(player_car, obstacles, True) # True: kill obstacle on collision
        if collided_obstacles:
            print("Collision detected!")
            player_car.kill()
            game_over = True
            # running = False # We will handle game over screen within the loop

    # Drawing...
    screen.fill(WHITE)  # Fill screen with white

    # Draw obstacles with camera offset
    for obstacle in obstacles:
        # Create a new rect for drawing, offset by the camera
        obstacle_draw_rect = obstacle.rect.move(-camera_x, 0)
        screen.blit(obstacle.image, obstacle_draw_rect)

    # Draw the player car - it's drawn relative to the screen, effectively centered by the camera
    # The player_car.rect.x is its world position. To draw it centered:
    # Only draw player car if not game over, or draw it differently
    if player_car.alive(): # Check if player_car sprite still exists
        player_screen_x = SCREEN_WIDTH // 2 - player_car.rect.width // 2
        screen.blit(player_car.image, (player_screen_x, player_car.rect.y))

    if game_over:
        display_game_over_message(screen)
        # Optionally, add text for restart/quit here and handle input

    pygame.display.flip()  # Update the full display
    
    clock.tick(60) # Limit to 60 FPS

# Quit Pygame
pygame.quit() 