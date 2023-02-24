import pygame
import numpy as np
from shadow_casting import LightSource

pygame.init()


class Rectangle:
    def __init__(self, position, size, color: tuple = (0, 50, 200)):
        self.x, self.y = position
        self.width, self.height = size
        # Define all the corners by using x, y, width and height.
        A = [self.x, self.y]
        B = [self.x + self.width, self.y]
        C = [self.x, self.y + self.height]
        D = [self.x + self.width, self.y + self.height]
        # Note that, corners need to be in numpy array instead of usual list.
        self.corners = np.array([A, B, C, D])
        # Define the color of the rectangle.
        self.color = color

    def draw(self):
        # draw the rectangle
        pygame.draw.rect(display, self.color, (self.x, self.y, self.width, self.height))


def setup():
    # Create the rectangles and append them to the list.
    for x in range(60, 950, 100):
        y = x
        rectangles.append(Rectangle(position=(x, y), size=(80, 80)))


def draw_and_update():
    # Fill the background with the white color (255, 255, 255).
    display.fill((255, 255, 255))

    for rectangle in rectangles:
        # Get the array of the corners/vertices of the rectangle.
        corners = rectangle.corners
        light_source.draw_shadow(corners)
        # corners = np.array([[x, y], [x + width, y], [x, y + height], [x + width, y + height]])

    # Draw the rectangles.
    for rectangle in rectangles:
        rectangle.draw()

    # Show the light source.
    light_source.show()
    
    # Update the game window.
    pygame.display.flip()


# Create a list for rectangles.
rectangles = []

# Run the setup() to create and append the rectangles to the list.
setup()

# Create the display with the resolution of 1000x1000.
display = pygame.display.set_mode((1000, 1000))

# Create the clock to set maximum limit for the FPS.
clock = pygame.time.Clock()

# Create a LightSource object.
light_source = LightSource(position=(400, 400), shadow_color=(0, 0, 0), display=display)

while True:
    # Update the position of the light_source with the mouse position.
    light_source.x, light_source.y = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_q]:
        # if Q is pressed, quit.
        ON = False
        pygame.quit()
        quit()

    # Limit the maximum FPS.
    clock.tick(60)

    # Draw the things and update the game window.
    draw_and_update()
    
