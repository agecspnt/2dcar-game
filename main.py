import pygame
import random

# Initialize Pygame
pygame.init()

# --- Constants ---
# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Sprite and Scaling Constants
CAR_SPRITE_WIDTH = 16
CAR_SPRITE_HEIGHT = 16
SCALED_CAR_WIDTH = 64
SCALED_CAR_HEIGHT = 64

# Background Tile Constants
DESERT_SPRITESHEET_PATH = "Mini Pixel Pack 2/Levels/Desert_details (16 x 16).png"
TILE_SPRITE_WIDTH = 16
TILE_SPRITE_HEIGHT = 16
SCALED_TILE_WIDTH = 64
SCALED_TILE_HEIGHT = 64
NUM_TILE_TYPES = 4 # Should match the number of distinct tile types in the spritesheet (e.g., plain, speckled, cactus, rock)

ROCK_COLLISION_RADIUS = SCALED_TILE_WIDTH // 8 # Adjusted for better collision feel with scaled tiles

# Background Scroll Speed
BACKGROUND_SCROLL_SPEED_Y = 2 # Pixels per frame for vertical scroll

# Invincibility
INVINCIBILITY_DURATION = 2000 # milliseconds (2 seconds)
BLINK_INTERVAL = 200 # milliseconds (for blinking effect)

# Obstacle properties (assuming these might be used if obstacles are re-introduced)
# SCALED_OBSTACLE_WIDTH = 64 # Example, adjust as needed
# SCALED_OBSTACLE_HEIGHT = 64 # Example, adjust as needed
OBSTACLE_SPAWN_DELAY = 100 # Adjusted spawn delay
OBSTACLE_SPEED = 5 # Adjusted obstacle speed


# --- Asset Loading Functions ---
def load_font(font_name, size):
    """Loads a font and returns the font object."""
    try:
        return pygame.font.Font(font_name, size)
    except pygame.error as e:
        print(f"Unable to load font {font_name}: {e}")
        return pygame.font.Font(None, size) # Fallback to default system font

def load_image(path, convert_alpha=True):
    """Loads an image and optionally converts it with alpha transparency."""
    try:
        image = pygame.image.load(path)
        if convert_alpha:
            return image.convert_alpha()
        return image.convert()
    except pygame.error as e:
        print(f"Unable to load image {path}: {e}")
        return None

def extract_sprite(spritesheet, rect, scale_to=None):
    """Extracts a sprite from a spritesheet, optionally scales it."""
    if spritesheet is None:
        return None
    try:
        sprite = spritesheet.subsurface(pygame.Rect(rect))
        if scale_to:
            sprite = pygame.transform.scale(sprite, scale_to)
        return sprite
    except pygame.error as e:
        print(f"Unable to extract sprite from rect {rect}: {e}")
        # Create a placeholder surface if extraction fails
        placeholder_width = scale_to[0] if scale_to else rect[2]
        placeholder_height = scale_to[1] if scale_to else rect[3]
        placeholder_sprite = pygame.Surface((placeholder_width, placeholder_height))
        placeholder_sprite.fill(BLACK) # Fill with a default color
        return placeholder_sprite

# --- Initialization ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2D Car Game")

# Fonts
game_over_font = load_font(None, 74)
restart_quit_font = load_font(None, 36)

# Load car image
car_spritesheet = load_image("Mini Pixel Pack 2/Cars/Player_red (16 x 16).png")
player_car_image_template = extract_sprite(car_spritesheet, (0, 0, CAR_SPRITE_WIDTH, CAR_SPRITE_HEIGHT))
scaled_player_car_image = pygame.transform.scale(player_car_image_template, (SCALED_CAR_WIDTH, SCALED_CAR_HEIGHT)) \
    if player_car_image_template else pygame.Surface((SCALED_CAR_WIDTH, SCALED_CAR_HEIGHT))
if not player_car_image_template: # Fill if placeholder
    scaled_player_car_image.fill(BLACK)


# Load desert background tiles
desert_tile_images = []
rock_tile_image_reference = None
desert_spritesheet = load_image(DESERT_SPRITESHEET_PATH)

if desert_spritesheet:
    for i in range(NUM_TILE_TYPES):
        tile_rect = (i * TILE_SPRITE_WIDTH, 0, TILE_SPRITE_WIDTH, TILE_SPRITE_HEIGHT)
        scaled_tile = extract_sprite(desert_spritesheet, tile_rect, (SCALED_TILE_WIDTH, SCALED_TILE_HEIGHT))
        if scaled_tile:
            desert_tile_images.append(scaled_tile)
    # Assuming rock is the 4th tile (index 3) based on weights and NUM_TILE_TYPES
    if NUM_TILE_TYPES == 4 and len(desert_tile_images) == 4:
        rock_tile_image_reference = desert_tile_images[3]
else:
    # Create placeholder surfaces if spritesheet loading failed
    for _ in range(NUM_TILE_TYPES):
        placeholder_tile = pygame.Surface((SCALED_TILE_WIDTH, SCALED_TILE_HEIGHT))
        placeholder_tile.fill(WHITE) # Fill with white for now
        desert_tile_images.append(placeholder_tile)


# --- Helper Functions ---
# Function to display Game Over message
def display_game_over_message(surface):
    text_surface = game_over_font.render('Game Over', True, RED)
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
    surface.blit(text_surface, text_rect)

    restart_text = restart_quit_font.render('Press R to Restart or Q to Quit', True, BLACK)
    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
    surface.blit(restart_text, restart_rect)

# --- Drawing Functions ---
def draw_background(surface, layout, tile_images, camera_x_offset, scroll_y_offset):
    """Draws the scrolling background."""
    if not layout or not tile_images:
        surface.fill(WHITE) # Fallback to white if no layout/tiles
        return

    # Calculate the starting column index and the offset within the first visible tile for X
    start_col_idx_in_layout = (camera_x_offset // SCALED_TILE_WIDTH)
    offset_x = camera_x_offset % SCALED_TILE_WIDTH

    # Calculate the starting row index and the offset within the first visible tile for Y
    start_row_idx_in_layout = (scroll_y_offset // SCALED_TILE_HEIGHT)
    offset_y = scroll_y_offset % SCALED_TILE_HEIGHT

    # Calculate how many tiles to draw horizontally & vertically to fill the screen plus one extra
    num_tiles_to_draw_wide = (SCREEN_WIDTH // SCALED_TILE_WIDTH) + 2 # +2 for safety margin
    num_tiles_to_draw_high = (SCREEN_HEIGHT // SCALED_TILE_HEIGHT) + 2 # +2 for safety margin
    
    LAYOUT_NUM_ROWS = len(layout)
    LAYOUT_NUM_COLS = len(layout[0]) if LAYOUT_NUM_ROWS > 0 else 0

    if LAYOUT_NUM_COLS == 0:
        surface.fill(WHITE) # Fallback if layout is empty
        return

    for j in range(num_tiles_to_draw_high): # Vertical tile iteration (screen rows)
        actual_layout_row = (start_row_idx_in_layout + j) % LAYOUT_NUM_ROWS
        screen_y_pos = j * SCALED_TILE_HEIGHT - offset_y
        
        for i in range(num_tiles_to_draw_wide): # Horizontal tile iteration (screen columns)
            actual_layout_col = (start_col_idx_in_layout + i) % LAYOUT_NUM_COLS
            
            tile_image = layout[actual_layout_row][actual_layout_col]
            
            screen_x_pos = i * SCALED_TILE_WIDTH - offset_x
            surface.blit(tile_image, (screen_x_pos, screen_y_pos))

def draw_obstacles(surface, obstacle_group, camera_x_offset):
    """Draws all obstacles in the group, adjusted by camera offset."""
    for obstacle in obstacle_group:
        obstacle_draw_rect = obstacle.rect.move(-camera_x_offset, 0)
        surface.blit(obstacle.image, obstacle_draw_rect)

def draw_player(surface, player_sprite, is_visible):
    """Draws the player car if it's alive and visible."""
    if player_sprite.alive() and is_visible:
        player_screen_x = SCREEN_WIDTH // 2 - player_sprite.rect.width // 2
        surface.blit(player_sprite.image, (player_screen_x, player_sprite.rect.y))


# --- Game Object Classes ---
# Player Car Class
class PlayerCar(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 5 # Adjusted speed for better control without background scroll reference
        self.player_visible = True

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

# Invincibility state
player_invincible = False
invincibility_timer = 0
blink_timer = 0
player_visible = True # Controls if the player car is drawn

# Function to reset the game state
def reset_game():
    global player_car, all_sprites, game_over, camera_x, \
           player_invincible, invincibility_timer, blink_timer, player_visible
    player_car = PlayerCar(scaled_player_car_image, (SCREEN_WIDTH - SCALED_CAR_WIDTH) // 2, SCREEN_HEIGHT - SCALED_CAR_HEIGHT - 10)
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player_car)
    camera_x = 0
    game_over = False
    
    # Always grant invincibility on reset
    player_invincible = True
    invincibility_timer = 0
    blink_timer = 0
    player_visible = True

    # Clear rocks from player's starting area
    if background_layout and rock_tile_image_reference and desert_tile_images:
        player_center_x = player_car.rect.centerx # This is world coordinate, but car starts centered
        player_center_y = player_car.rect.centery

        # Since player starts centered on screen and camera_x is initially 0,
        # screen coordinates for player center are SCREEN_WIDTH // 2, player_car.rect.centery.
        # We need to find the tile indices in the background_layout that correspond to this starting screen area.
        # Effective camera_x for starting position before any movement is 0.
        # Effective background_scroll_y for starting position before any movement is 0.

        # Convert player's starting *world* coordinates to layout tile indices.
        # Note: camera_x and background_scroll_y are 0 at the start of reset_game.
        start_cam_x = player_car.rect.centerx - SCREEN_WIDTH // 2 # This will be 0 if player is centered
        start_scroll_y = 0 # Assuming background scroll y starts at 0 or is reset

        center_tile_col_world = (player_car.rect.centerx + start_cam_x) // SCALED_TILE_WIDTH
        center_tile_row_world = (player_car.rect.centery + start_scroll_y) // SCALED_TILE_HEIGHT
 
        safe_zone_radius = 1 # Clear a 3x3 area (1 tile around the center tile)
        safe_tile = desert_tile_images[0] if desert_tile_images else None # Assuming this is a plain, safe tile

        LAYOUT_NUM_ROWS = len(background_layout)
        LAYOUT_NUM_COLS = len(background_layout[0]) if LAYOUT_NUM_ROWS > 0 else 0

        if LAYOUT_NUM_COLS > 0 and safe_tile:
            for dr in range(-safe_zone_radius, safe_zone_radius + 1):
                for dc in range(-safe_zone_radius, safe_zone_radius + 1):
                    # Calculate indices in the world layout
                    r_world = center_tile_row_world + dr
                    c_world = center_tile_col_world + dc

                    # Apply modulo for wrapping around the layout array
                    r_layout = r_world % LAYOUT_NUM_ROWS
                    c_layout = c_world % LAYOUT_NUM_COLS
                    
                    if background_layout[r_layout][c_layout] is rock_tile_image_reference:
                        if rock_tile_image_reference is not safe_tile: 
                            background_layout[r_layout][c_layout] = safe_tile

# --- Game Logic Functions ---
def handle_events(current_game_over_state):
    """Handles all Pygame events and returns running state and game over state."""
    global game_over # Allow modification of global game_over
    running_state = True
    new_game_over_state = current_game_over_state

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running_state = False
        if event.type == pygame.KEYDOWN:
            if new_game_over_state:
                if event.key == pygame.K_r:
                    reset_game()
                    new_game_over_state = False # Game is no longer over after reset
                if event.key == pygame.K_q:
                    running_state = False
            # Potentially other non-game-over key events could be handled here
    return running_state, new_game_over_state

def update_game_state(keys, current_dt):
    """Updates all game objects and game logic."""
    global game_over, camera_x, background_scroll_y, player_invincible, invincibility_timer, blink_timer, player_visible

    if game_over:
        return # Don't update game state if game is over

    # Update player car
    player_car.update(keys)

    # Update camera based on player's position
    camera_x = player_car.rect.centerx - SCREEN_WIDTH // 2
    # Consider clamping camera_x if you have defined world boundaries:
    # world_width = len(background_layout[0]) * SCALED_TILE_WIDTH if background_layout and background_layout[0] else 0
    # if camera_x < 0: camera_x = 0
    # if world_width > SCREEN_WIDTH and camera_x > world_width - SCREEN_WIDTH:
    #     camera_x = world_width - SCREEN_WIDTH
    
    # Update background vertical scroll
    background_scroll_y = (background_scroll_y - BACKGROUND_SCROLL_SPEED_Y)

    # Handle invincibility and blinking
    if player_invincible:
        invincibility_timer += current_dt
        if invincibility_timer >= INVINCIBILITY_DURATION:
            player_invincible = False
            player_visible = True # Ensure player is visible when invincibility ends
        else:
            blink_timer += current_dt
            if blink_timer >= BLINK_INTERVAL:
                player_visible = not player_visible
                blink_timer = 0
    else:
        # If not invincible and car is alive, it should be visible
        if player_car.alive(): # This check might be redundant if game_over handles it
            player_visible = True

    # Update obstacles (if any)
    obstacles.update() # This will call the update method of each sprite in the group

    # Check for collisions with obstacles (if any)
    # collided_with_obstacles = pygame.sprite.spritecollide(player_car, obstacles, True) # True: kill obstacle
    # if collided_with_obstacles:
    #     print("Collision with an obstacle detected!")
    #     if player_car.alive() and not player_invincible: # Only lose if not invincible
    #         player_car.kill()
    #         game_over = True
    #         return # Stop further updates this frame if game over

    # Collision logic with background rock tiles
    if not player_invincible and rock_tile_image_reference and player_car.alive():
        # Player's collision rectangle in screen coordinates (since car is drawn centered)
        player_screen_rect_collision = pygame.Rect(
            SCREEN_WIDTH // 2 - player_car.rect.width // 2, 
            player_car.rect.y, 
            player_car.rect.width, 
            player_car.rect.height
        )

        start_col_idx_in_layout_collision = (camera_x // SCALED_TILE_WIDTH)
        offset_x_collision = camera_x % SCALED_TILE_WIDTH
        start_row_idx_in_layout_collision = (background_scroll_y // SCALED_TILE_HEIGHT)
        offset_y_collision = background_scroll_y % SCALED_TILE_HEIGHT
        
        num_tiles_to_check_wide = (SCREEN_WIDTH // SCALED_TILE_WIDTH) + 2
        num_tiles_to_check_high = (SCREEN_HEIGHT // SCALED_TILE_HEIGHT) + 2
        
        LAYOUT_NUM_ROWS_COLLISION = len(background_layout) if background_layout else 0
        LAYOUT_NUM_COLS_COLLISION = len(background_layout[0]) if LAYOUT_NUM_ROWS_COLLISION > 0 and background_layout[0] else 0

        collision_detected_this_frame = False
        if LAYOUT_NUM_COLS_COLLISION > 0:
            for j_coll in range(num_tiles_to_check_high):
                if collision_detected_this_frame: break
                actual_layout_row_coll = (start_row_idx_in_layout_collision + j_coll) % LAYOUT_NUM_ROWS_COLLISION
                
                for i_coll in range(num_tiles_to_check_wide):
                    actual_layout_col_coll = (start_col_idx_in_layout_collision + i_coll) % LAYOUT_NUM_COLS_COLLISION
                    tile_image_to_check = background_layout[actual_layout_row_coll][actual_layout_col_coll]
                    
                    if tile_image_to_check is rock_tile_image_reference:
                        rock_screen_x_pos = i_coll * SCALED_TILE_WIDTH - offset_x_collision
                        rock_screen_y_pos = j_coll * SCALED_TILE_HEIGHT - offset_y_collision

                        rock_circle_center_x = rock_screen_x_pos + SCALED_TILE_WIDTH // 2
                        rock_circle_center_y = rock_screen_y_pos + SCALED_TILE_HEIGHT // 2

                        # Find closest point on car_rect to rock_circle_center
                        closest_x = max(player_screen_rect_collision.left, min(rock_circle_center_x, player_screen_rect_collision.right))
                        closest_y = max(player_screen_rect_collision.top, min(rock_circle_center_y, player_screen_rect_collision.bottom))

                        distance_x = rock_circle_center_x - closest_x
                        distance_y = rock_circle_center_y - closest_y
                        distance_squared = (distance_x ** 2) + (distance_y ** 2)

                        if distance_squared < (ROCK_COLLISION_RADIUS ** 2):
                            print("Collision with rock tile detected!")
                            if player_car.alive(): player_car.kill()
                            game_over = True
                            collision_detected_this_frame = True
                            break

def draw_game_elements():
    """Draws all game elements onto the screen."""
    screen.fill(WHITE)  # Clear screen

    draw_background(screen, background_layout, desert_tile_images, camera_x, background_scroll_y)
    draw_obstacles(screen, obstacles, camera_x) # Draw obstacles (if any)
    draw_player(screen, player_car, player_visible)

    if game_over:
        display_game_over_message(screen)

    pygame.display.flip() # Update the full display

# --- Game Initialization --- 
# (This section might be better named or integrated into a main function)
# Initialize game variables and objects before the loop starts
clock = pygame.time.Clock()
camera_x = 0
background_scroll_y = 0
game_over = False
player_invincible = False
invincibility_timer = 0
blink_timer = 0
player_visible = True # This is also in PlayerCar init and reset_game

# Setup player car and sprite groups
player_car = PlayerCar(scaled_player_car_image, (SCREEN_WIDTH - SCALED_CAR_WIDTH) // 2, SCREEN_HEIGHT - SCALED_CAR_HEIGHT - 10)
all_sprites = pygame.sprite.Group() # May not be strictly needed if not drawing all_sprites directly
all_sprites.add(player_car)
obstacles = pygame.sprite.Group() # Initialize obstacle group

# Create background layout
background_layout = []
if desert_tile_images: 
    tile_weights = [0.5, 0.3, 0.1, 0.1] # Plain, Speckled, Cactus, Rock
    # Ensure TILES_HIGH and TILES_WIDE are defined if they are used here, or derive them.
    # For scrolling, the layout needs to be larger than the screen.
    # Let's define them based on screen size for clarity, assuming they were meant for this.
    EFFECTIVE_TILES_HIGH = (SCREEN_HEIGHT // SCALED_TILE_HEIGHT) * 2 # Twice screen height for vertical scroll
    EFFECTIVE_TILES_WIDE = (SCREEN_WIDTH // SCALED_TILE_WIDTH) * 2   # Twice screen width for horizontal scroll

    for r in range(EFFECTIVE_TILES_HIGH):
        row = []
        for c in range(EFFECTIVE_TILES_WIDE):
            tile_to_use = None
            if len(tile_weights) == NUM_TILE_TYPES and NUM_TILE_TYPES > 0 and desert_tile_images:
                try:
                    tile_to_use = random.choices(desert_tile_images, weights=tile_weights, k=1)[0]
                except IndexError: # If desert_tile_images is empty despite checks
                    pass 
            elif desert_tile_images: # Fallback if weights are misconfigured or NUM_TILE_TYPES is 0
                tile_to_use = random.choice(desert_tile_images)
            
            if tile_to_use is None: # Ultimate fallback if all fails
                tile_to_use = pygame.Surface((SCALED_TILE_WIDTH, SCALED_TILE_HEIGHT))
                tile_to_use.fill(WHITE)
            row.append(tile_to_use)
        background_layout.append(row)

reset_game() # Initialize game state, including invincibility and clearing start area

# --- Main Game Loop ---
running = True
while running:
    # 1. Handle Events
    keys = pygame.key.get_pressed() # Get key states once per frame
    running, game_over = handle_events(game_over) # game_over can be modified by handle_events
    
    # 2. Update Game State
    dt = clock.get_time() # Delta time for frame-rate independent movement/timers
    update_game_state(keys, dt)

    # 3. Draw Everything
    draw_game_elements()
    
    clock.tick(60) # Limit to 60 FPS

# --- Cleanup --- 
pygame.quit() 