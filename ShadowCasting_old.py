import pygame
from time import sleep, perf_counter
from threading import Thread

pygame.init()

ON = True

class Game:
    def __init__(self, background_color=(255, 255, 255)):
        self.screen = pygame.display.set_mode((1000, 1000))
        pygame.display.set_caption("Shadow Casting in Pygame")
        self.background_color = background_color
        self.rectangles = []
        self.font = pygame.font.SysFont("Helvetica", 32)
        self.setup()

    def setup(self):
        self.point = self.Point(x=0, y=0)

        for p in range(75, 975, 100):
            self.rectangles.append(self.Rectangle(geometry=(p, p, 75, 75)))

        Thread(target=self.draw_and_update).start()

    def draw_and_update(self):
        sleep(0.25)
        while ON:
            initial_time = perf_counter()
            self.screen.fill(self.background_color)

            for box in self.rectangles:
                self.point.shadow_casting(box)

            for box in self.rectangles:
               box.draw()

            self.point.draw()

            final_time = perf_counter()
            difference = round(final_time - initial_time, 4)
            FPS = round(1 / difference)
            
            self.text = self.font.render(f"FPS: {FPS}", True, (255, 0, 0))
            self.screen.blit(self.text, (0, 0))
            
            pygame.display.flip()


    class Point:
        def __init__(self, x=495, y=495, radius=5, color=(255, 0, 0)):
            self.radius = radius
            self.color = color
            self.x = x
            self.y = y

        def draw(self):
            pygame.draw.circle(game.screen, self.color, (self.x, self.y), self.radius)

        def shadow_casting(self, object, color=(0, 0, 0)):
            # To prevent the ZeroDivisionError...
            c1, c2 = False, False
            if abs(self.x - object.x) == 0:
                object.x += 1
                c1 = True
            if abs(self.x - (object.x + object.width)) == 0:
                object.x += 1
                c1 = True
            if abs(self.y - object.y) == 0:
                object.y += 1
                c2 = True
            if abs(self.y - (object.y + object.height)) == 0:
                object.y += 1
                c2 = True

            # Finding the 2 corners of a box.
            corners = [[0, 0], [0, 0]]
            if self.x < object.x:
                if self.y > object.y + object.height:
                    corners[0] = [object.x, object.y]
                    corners[1] = [object.x + object.width, object.y + object.height]
                elif self.y < object.y:
                    corners[0] = [object.x + object.width, object.y]
                    corners[1] = [object.x, object.y + object.height]
                else:
                    corners[0] = [object.x, object.y]
                    corners[1] = [object.x, object.y + object.height]
            elif self.x > object.x + object.width:
                if self.y > object.y + object.height:
                    corners[0] = [object.x + object.width, object.y]
                    corners[1] = [object.x, object.y + object.height]
                elif self.y < object.y:
                    corners[0] = [object.x, object.y]
                    corners[1] = [object.x + object.width, object.y + object.height]
                else:
                    corners[0] = [object.x + object.width, object.y]
                    corners[1] = [object.x + object.width, object.y + object.height]
            else:
                if self.y < object.y:
                    corners[0] = [object.x, object.y]
                    corners[1] = [object.x + object.width, object.y]
                else:
                    corners[0] = [object.x, object.y + object.height]
                    corners[1] = [object.x + object.width, object.y + object.height]

            x1, y1 = corners[0]
            x2, y2 = corners[1]
            final_1 = [x1, y1]
            final_2 = [x2, y2]

            # First we find the slope of the line.
            # Then we find the final coordinates using the slope.
            # Finding the final coordinates is important,
            # because drawing a large polygon degrades FPS drastically.
            if True:
                m1 = (self.y - y1) / (self.x - x1)
                if x1 < self.x and y1 < self.y:
                    x = (-y1 / m1) + x1
                    y = (-m1 * x1) + y1
                    if abs(0 - x) < abs(0 - y):
                        final_1 = [x, 0]
                    else:
                        final_1 = [0, y]
                elif x1 < self.x and y1 > self.y:
                    x = ((1000 -y1) / m1) + x1
                    y = m1 * (0 - x1) + y1
                    if abs(0 - x) < abs(1000 - y):
                        final_1 = [x, 1000]
                    else:
                        final_1 = [0, y]
                elif x1 > self.x and y1 < self.y:
                    x = (-y1 / m1) + x1
                    y = m1 * (1000 - x1) + y1
                    if abs(1000 - x) < abs(0 - y):
                        final_1 = [x, 0]
                    else:
                        final_1 = [1000, y]
                elif x1 > self.x and y1 > self.y:
                    x = ((1000 - y1) / m1) + x1
                    y = m1 * (1000 - x1) + y1
                    if abs(1000 - x) < abs(1000 - y):
                        final_1 = [x, 1000]
                    else:
                        final_1 = [1000, y]

                m2 = (self.y - y2) / (self.x - x2)
                if x2 < self.x and y2 < self.y:
                    x = (-y2 / m2) + x2
                    y = (-m2 * x2) + y2
                    if abs(0 - x) < abs(0 - y):
                        final_2 = [x, 0]
                    else:
                        final_2 = [0, y]
                elif x2 < self.x and y2 > self.y:
                    x = ((1000 - y2) / m2) + x2
                    y = m2 * (0 - x2) + y2
                    if abs(0 - x) < abs(1000 - y):
                        final_2 = [x, 1000]
                    else:
                        final_2 = [0, y]
                elif x2 > self.x and y2 < self.y:
                    x = (-y2 / m2) + x2
                    y = m2 * (1000 - x2) + y2
                    if abs(1000 - x) < abs(0 - y):
                        final_2 = [x, 0]
                    else:
                        final_2 = [1000, y]
                elif x2 > self.x and y2 > self.y:
                    x = ((1000 - y2) / m2) + x2
                    y = m2 * (1000 - x2) + y2
                    if abs(1000 - x) < abs(1000 - y):
                        final_2 = [x, 1000]
                    else:
                        final_2 = [1000, y]

                final_3 = None
                final_4 = None

                if (final_1[1] == 0 and final_2[0] == 0):
                    final_3 = [0, 0]
                elif (final_1[0] == 0 and final_2[1] == 1000):
                    final_3 = [0, 1000]
                elif (final_1[1] == 0 and final_2[0] == 1000):
                    final_3 = [1000, 0]
                elif (final_1[0] == 1000 and final_2[1] == 1000):
                    final_3 = [1000, 1000]
                elif (final_1[0] == 0 and final_2[1] == 0):
                    final_3 = [0, 0]
                elif (final_1[1] == 1000 and final_2[0] == 1000):
                    final_3 = [1000, 1000]
                elif (final_1[1] == 0 and final_2[1] == 1000):
                    if self.x > x1:
                        final_3 = [0, 0]
                        final_4 = [0, 1000]
                    else:
                        final_3 = [1000, 0]
                        final_4 = [1000, 1000]
                elif (final_1[0] == 0 and final_2[0] == 1000):
                    if self.y < y1:
                        final_3 = [0, 1000]
                        final_4 = [1000, 1000]
                    else:
                        final_3 = [0, 0]
                        final_4 = [1000, 0]
                # Drawing polygon with 4, 5 or 6 corners.
                else:
                    pygame.draw.polygon(game.screen, color, [(x1, y1), (x2, y2), final_2, final_1])
                    final_3 = None
                    final_4 = None

                if final_3 is not None and final_4 is not None:
                    pygame.draw.polygon(game.screen, color, [(x1, y1), (x2, y2), final_2, final_4, final_3, final_1])
                elif final_3 is not None:
                    pygame.draw.polygon(game.screen, color, [(x1, y1), (x2, y2), final_2, final_3, final_1])

                if c1 is True:
                    object.x -= 1
                if c2 is True:
                    object.y -= 1

    class Rectangle:
        def __init__(self, geometry=(0, 0, 100, 100), color=(0, 255, 0)):
            self.x, self.y, self.width, self.height = geometry
            self.Rect = pygame.draw.rect
            self.color = color

        def draw(self):
            pygame.draw.rect(game.screen, self.color, (self.x, self.y, self.width, self.height))


game = Game()

while True:
    sleep(0.01)
    game.point.x, game.point.y = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                ON = False
                sleep(0.25)
                pygame.quit()
                quit()
