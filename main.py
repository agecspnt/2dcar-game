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

# Background Tile Constants
DESERT_SPRITESHEET_PATH = "Mini Pixel Pack 2/Levels/Desert_details (16 x 16).png"
TILE_SPRITE_WIDTH = 16
TILE_SPRITE_HEIGHT = 16
SCALED_TILE_WIDTH = 64
SCALED_TILE_HEIGHT = 64
NUM_TILE_TYPES = 4

# Background Scroll Speed
BACKGROUND_SCROLL_SPEED_Y = 2 # Pixels per frame for vertical scroll

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

# Load desert background tiles
desert_tile_images = []
try:
    loaded_desert_spritesheet = pygame.image.load(DESERT_SPRITESHEET_PATH).convert_alpha()
    for i in range(NUM_TILE_TYPES):
        tile_rect = pygame.Rect(i * TILE_SPRITE_WIDTH, 0, TILE_SPRITE_WIDTH, TILE_SPRITE_HEIGHT)
        original_tile = loaded_desert_spritesheet.subsurface(tile_rect)
        scaled_tile = pygame.transform.scale(original_tile, (SCALED_TILE_WIDTH, SCALED_TILE_HEIGHT))
        desert_tile_images.append(scaled_tile)
except pygame.error as e:
    print(f"Unable to load desert tiles: {e}")
    # Create placeholder surfaces if image loading fails
    for _ in range(NUM_TILE_TYPES):
        placeholder_tile = pygame.Surface((SCALED_TILE_WIDTH, SCALED_TILE_HEIGHT))
        placeholder_tile.fill(WHITE) # Fill with white for now, maybe a sand color later
        desert_tile_images.append(placeholder_tile)

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
background_scroll_y = 0 # Initialize vertical scroll offset for background

# Determine number of tiles needed to fill the screen plus a buffer for scrolling
TILES_HIGH = (SCREEN_HEIGHT + SCALED_TILE_HEIGHT - 1) // SCALED_TILE_HEIGHT
TILES_WIDE = (SCREEN_WIDTH + SCALED_TILE_WIDTH - 1) // SCALED_TILE_WIDTH

# For initial static display, we might not need more than what fits the screen.
# For scrolling, we'll need more, typically at least one screen width/height extra.
# Let's make it twice the screen width for horizontal scrolling.
# And twice the screen height for vertical scrolling pattern.
# SCROLL_BUFFER_HORIZONTAL = TILES_WIDE # Number of extra tiles horizontally for smooth scrolling -> incorporated into TILES_WIDE*2
# SCROLL_BUFFER_VERTICAL = 2 # Number of extra tiles vertically, might not be needed for horizontal scroll only -> incorporated into TILES_HIGH*2

background_layout = []
if desert_tile_images: # Ensure tiles are loaded
    tile_weights = [0.5, 0.3, 0.1, 0.1] # Plain, Speckled, Cactus, Rock
    for r in range(TILES_HIGH * 2): # Make the background taller for vertical scrolling
        row = []
        for c in range(TILES_WIDE * 2): # Make the background wider for horizontal scrolling
            if len(tile_weights) == NUM_TILE_TYPES and NUM_TILE_TYPES > 0:
                tile_to_use = random.choices(desert_tile_images, weights=tile_weights, k=1)[0]
            elif desert_tile_images: # Fallback if weights are misconfigured or no tiles
                tile_to_use = random.choice(desert_tile_images)
            else:
                # This case should ideally not be reached if desert_tile_images check at the start is robust
                # Creating a dummy surface to avoid error if all else fails
                tile_to_use = pygame.Surface((SCALED_TILE_WIDTH, SCALED_TILE_HEIGHT))
                tile_to_use.fill(WHITE) # Default to white

            row.append(tile_to_use)
        background_layout.append(row)

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
        camera_x = player_car.rect.centerx - SCREEN_WIDTH // 2
        # Clamp camera (optional, if world boundaries are defined)
        # world_width = TILES_WIDE * 2 * SCALED_TILE_WIDTH # Example world width based on background
        # if camera_x < 0: camera_x = 0
        # if camera_x > world_width - SCREEN_WIDTH: camera_x = world_width - SCREEN_WIDTH
        
        # Update background vertical scroll
        background_scroll_y = (background_scroll_y - BACKGROUND_SCROLL_SPEED_Y) # Changed + to - for downward scroll

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

    # Draw background tiles
    if background_layout and desert_tile_images: # Ensure lists are not empty
        # Calculate the starting column index and the offset within the first visible tile for X
        start_col_idx_in_layout = (camera_x // SCALED_TILE_WIDTH)
        offset_x = camera_x % SCALED_TILE_WIDTH

        # Calculate the starting row index and the offset within the first visible tile for Y
        start_row_idx_in_layout = (background_scroll_y // SCALED_TILE_HEIGHT)
        offset_y = background_scroll_y % SCALED_TILE_HEIGHT

        # Calculate how many tiles to draw horizontally & vertically to fill the screen plus one extra
        num_tiles_to_draw_wide = TILES_WIDE + 1
        num_tiles_to_draw_high = TILES_HIGH + 1
        
        LAYOUT_NUM_ROWS = len(background_layout)
        LAYOUT_NUM_COLS = len(background_layout[0]) if LAYOUT_NUM_ROWS > 0 else 0

        if LAYOUT_NUM_COLS > 0: # Ensure layout is not empty
            for j in range(num_tiles_to_draw_high): # Vertical tile iteration (screen rows)
                actual_layout_row = (start_row_idx_in_layout + j) % LAYOUT_NUM_ROWS
                screen_y_pos = j * SCALED_TILE_HEIGHT - offset_y
                
                for i in range(num_tiles_to_draw_wide): # Horizontal tile iteration (screen columns)
                    actual_layout_col = (start_col_idx_in_layout + i) % LAYOUT_NUM_COLS
                    
                    tile_image = background_layout[actual_layout_row][actual_layout_col]
                    
                    screen_x_pos = i * SCALED_TILE_WIDTH - offset_x
                    screen.blit(tile_image, (screen_x_pos, screen_y_pos))

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