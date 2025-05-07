import pygame
import os # Added to construct paths

# Define asset paths relative to the script's location or project root
# Assuming the script is in the project root and 'craftpix-...' folder is also there.
ASSET_BASE_PATH = "craftpix-889156-free-racing-game-kit"
CAR_IMAGE_PATH = os.path.join(ASSET_BASE_PATH, "PNG", "Car_1_Main_Positions", "Car_1_01.png")
OBSTACLE_IMAGE_PATH = os.path.join(ASSET_BASE_PATH, "PNG", "Game_Props_Items", "Barrel_01.png")

def main():
    pygame.init()
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Pygame Test - Load Assets")

    try:
        print(f"Loading car image from: {CAR_IMAGE_PATH}")
        car_img = pygame.image.load(CAR_IMAGE_PATH)
        print(f"Loading obstacle image from: {OBSTACLE_IMAGE_PATH}")
        obstacle_img = pygame.image.load(OBSTACLE_IMAGE_PATH)
        
        # For demonstration, let's scale them if they are too big
        # Adjust size as needed, ensure these are reasonable defaults
        car_rect = car_img.get_rect()
        if car_rect.width > 150 or car_rect.height > 150: # Check if scaling is likely needed
            car_img = pygame.transform.scale(car_img, (min(car_rect.width, 100), min(car_rect.height,100)))
        
        obstacle_rect = obstacle_img.get_rect()
        if obstacle_rect.width > 100 or obstacle_rect.height > 100: # Check if scaling is likely needed
             obstacle_img = pygame.transform.scale(obstacle_img, (min(obstacle_rect.width, 50), min(obstacle_rect.height,50)))


    except pygame.error as e:
        print(f"Error loading images: {e}")
        pygame.quit()
        return

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        screen.fill((200, 200, 200))  # Fill screen with light gray

        # Display images
        screen.blit(car_img, (screen_width // 2 - car_img.get_width() // 2, screen_height - car_img.get_height() - 20)) # Car at bottom center
        screen.blit(obstacle_img, (screen_width // 2 - obstacle_img.get_width() // 2, screen_height // 2 - obstacle_img.get_height() // 2)) # Obstacle in middle

        pygame.display.flip()   # Update the full display

    pygame.quit()
    print("Pygame asset loading test executed successfully. Window closed.")

if __name__ == '__main__':
    main() 