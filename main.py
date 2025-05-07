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

# Load car image
try:
    car_image = pygame.image.load("craftpix-889156-free-racing-game-kit/PNG/Car_1_Main_Positions/Car_1_01.png")
    car_image = pygame.transform.scale(car_image, (100, 200)) # Adjust size as needed
except pygame.error as e:
    print(f"Unable to load car image: {e}")
    # Create a placeholder surface if image loading fails
    car_image = pygame.Surface((50, 100))
    car_image.fill(BLACK) # Fill with a color, e.g., black

# Load obstacle image
try:
    obstacle_image = pygame.image.load("craftpix-889156-free-racing-game-kit/PNG/Game_Props_Items/Barrel_01.png")
    obstacle_image = pygame.transform.scale(obstacle_image, (70, 70)) # Adjust size as needed
except pygame.error as e:
    print(f"Unable to load obstacle image: {e}")
    obstacle_image = pygame.Surface((50, 50))
    obstacle_image.fill(BLACK) # Placeholder

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
    def __init__(self, x, y, speed):
        super().__init__()
        self.image = obstacle_image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill() # Remove obstacle if it goes off screen

player_car = PlayerCar(car_image, (SCREEN_WIDTH - car_image.get_width()) // 2, SCREEN_HEIGHT - car_image.get_height() - 10)
all_sprites = pygame.sprite.Group()
all_sprites.add(player_car)

# Obstacle properties
obstacles = pygame.sprite.Group()
obstacle_spawn_timer = 0
obstacle_spawn_delay = 100 # Adjusted spawn delay
obstacle_speed = 5 # Adjusted obstacle speed

# Game loop
running = True
clock = pygame.time.Clock() # For managing FPS

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Handle key presses
    keys = pygame.key.get_pressed()
    
    # Update player car
    player_car.update(keys) # Call update once with the current keys state

    # Spawn obstacles
    obstacle_spawn_timer += 1
    if obstacle_spawn_timer >= obstacle_spawn_delay:
        obstacle_spawn_timer = 0
        obstacle_x = random.randint(0, SCREEN_WIDTH - obstacle_image.get_width())
        new_obstacle = Obstacle(obstacle_x, -obstacle_image.get_height(), obstacle_speed)
        obstacles.add(new_obstacle)
        all_sprites.add(new_obstacle) # Add obstacles to all_sprites to be drawn

    # Update obstacles
    obstacles.update()

    # Check for collisions
    collided_obstacles = pygame.sprite.spritecollide(player_car, obstacles, True) # True: kill obstacle on collision
    if collided_obstacles:
        print("Collision detected!")
        # For now, let's just remove the car. In a real game, you'd handle game over.
        player_car.kill() 
        running = False # End the game or trigger game over state

    # Drawing
    screen.fill(WHITE)  # Fill screen with white

    all_sprites.draw(screen) # Draw all sprites (player car and obstacles)

    pygame.display.flip()  # Update the full display
    
    clock.tick(60) # Limit to 60 FPS

# Quit Pygame
pygame.quit() 