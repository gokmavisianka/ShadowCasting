import pygame
from time import sleep, perf_counter
from threading import Thread
from random import randint
import numpy as np

pygame.init()
ON = True


class Rectangle:
    def __init__(self, position, size, color: tuple = (0, 50, 200)):
        self.x, self.y = position
        self.width, self.height = size
        A = [self.x, self.y]
        B = [self.x + self.width, self.y]
        C = [self.x, self.y + self.height]
        D = [self.x + self.width, self.y + self.height]
        self.corners = np.array([A, B, C, D])
        self.color = color

    def draw(self):
        pygame.draw.rect(game.display, self.color, (self.x, self.y, self.width, self.height))


class LightSource:
    def __init__(self, position, shadow_color: tuple = (0, 0, 0), radius: int = 5):
        self.radius = radius
        self.x, self.y = position
        self.shadow_color = shadow_color
        self.areas = {(1, 1, 1, 1, 1, 1, 1, 1): 0,
                      (0, 1, 0, 1, 1, 1, 1, 1): 1,
                      (0, 0, 0, 0, 1, 1, 1, 1): 2,
                      (1, 1, 1, 1, 0, 0, 1, 1): 3,
                      (0, 1, 0, 1, 0, 0, 1, 1): 4,
                      (0, 0, 0, 0, 0, 0, 1, 1): 5,
                      (1, 1, 1, 1, 0, 0, 0, 0): 6,
                      (0, 1, 0, 1, 0, 0, 0, 0): 7,
                      (0, 0, 0, 0, 0, 0, 0, 0): 8}
        # usage: self.corner_indices[area]
        self.corner_indices = {0: (1, 2),
                               1: (0, 1),
                               2: (0, 3),
                               3: (0, 2),
                               5: (1, 3),
                               6: (0, 3),
                               7: (2, 3),
                               8: (1, 2)}
        # usage: self.border_indices[area][corner_index][case]
        self.border_indices = {0: {1: {0: None, 1: 2, 2: (2, 3)}, 2: {0: 3, 1: None, 2: (2, 3)}},
                               1: {0: {0: 3, 1: 0, 2: (0, 3)}, 1: {0: 3, 1: 2, 2: (2, 3)}},
                               2: {0: {0: None, 1: 0, 2: (0, 3)}, 3: {0: 3, 1: None, 2: (0, 3)}},
                               3: {0: {0: 1, 1: 2, 2: (1, 2)}, 2: {0: 3, 1: 2, 2: (2, 3)}},
                               5: {1: {0: 1, 1: 0, 2: (0, 1)}, 3: {0: 3, 1: 0, 2: (0, 3)}},
                               6: {0: {0: 1, 1: None, 2: (1, 2)}, 3: {0: None, 1: 2, 2: (1, 2)}},
                               7: {2: {0: 1, 1: 0, 2: (0, 1)}, 3: {0: 1, 1: 2, 2: (1, 2)}},
                               8: {1: {0: 1, 1: None, 2: (0, 1)}, 2: {0: None, 1: 0, 2: (0, 1)}}}
        self.additional_points = {(0, 1): (0, 0),
                                  (1, 2): (game.width, 0),
                                  (2, 3): (game.width, game.height),
                                  (3, 4): (0, game.height)}  # (3, 4) can be considered as (3, 0).

    # Line starts from the position of the light source and ends at the corner of the rectangle.
    # The value of the "area" is important to know which corner will be used as the end point.
    def operate(self, rectangle):
        area = self.where_am_i(rectangle)
        # Corners can be shown like this for a rectangle; |A   B|
        #                                                 |C   D|
        # area = 0 or area = 8 : B and C will be used : indices are 1 & 2.
        # area = 2 or area = 6 : A and D will be used : indices are 0 & 3.
        # area = 1             : A and B will be used : indices are 0 & 1.
        # area = 3             : A and C will be used : indices are 0 & 2.
        # area = 5             : B and D will be used : indices are 1 & 3.
        # area = 7             : C and D will be used : indices are 2 & 3.
        # We need to find the collision points where the lines collide with borders.
        corner_points = []
        border_numbers = []
        collision_points = []
        if area != 4:
            corner_indices = self.corner_indices[area]
            for corner_index in corner_indices:
                corner_point = rectangle.corners[corner_index]
                equation = self.find_line_equation(corner_point)
                collision_point, border_number = self.find_collision_point(equation, area, corner_index)
                corner_points.append(corner_point)
                border_numbers.append(border_number)
                collision_points.append(collision_point)
            # Now, we can create polygons by using the collision points and the position of the corners.
            additional_points = self.find_additional_points(corner_indices, border_numbers)
            self.draw_shadow(corner_points, collision_points, additional_points)

    def where_am_i(self, rectangle):
        X = self.x < rectangle.corners[:, 0]
        # X = [self.x < A.x, self.x < B.x, self.x < C.x, self.x < D.x]
        Y = self.y < rectangle.corners[:, 1]
        # Y = [self.y < A.y, self.y < B.y, self.y < C.y, self.y < D.y]
        data = np.concatenate((X, Y), axis=None)
        # Converting it to tuple so we can use a dictionary to determine the value of "area".
        data = tuple(data)
        # Note that 0 means False and 1 means True.
        # data = (1, 1, 1, 1, 1, 1, 1, 1) : top-left     : (0)
        # data = (0, 1, 0, 1, 1, 1, 1, 1) : top          : (1)
        # data = (0, 0, 0, 0, 1, 1, 1, 1) : top-right    : (2)
        # data = (1, 1, 1, 1, 0, 0, 1, 1) : left         : (3)
        # data = (0, 1, 0, 1, 0, 0, 1, 1) : middle       : (4)
        # data = (0, 0, 0, 0, 0, 0, 1, 1) : right        : (5)
        # data = (1, 1, 1, 1, 0, 0, 0, 0) : bottom-left  : (6)
        # data = (0, 1, 0, 1, 0, 0, 0, 0) : bottom       : (7)
        # data = (0, 0, 0, 0, 0, 0, 0, 0) : bottom-right : (8)
        area = self.areas[data]
        return area

    def find_line_equation(self, point):
        X, Y = point
        if self.x == X:
            # if x values are the same of these 2 data points, then there will be a division by zero.
            # So, in this case, we need to create a line "x = Ay + B" where A equals to 0 and B equals to self.x.
            equation = [0, self.x]
            case = 0
        elif self.y == Y:
            # In this case, we need to create a line "y = Ax + B" where A equals to 0 and B equals to self.y.
            equation = [0, self.y]
            case = 1
        else:
            # In this case, we need to create a line "y = Ax + B"
            # Newton's Interpolation can be applied.
            A = (self.y - Y) / (self.x - X)
            B = self.y - (A * self.x)
            equation = [A, B]
            case = 2
        return equation, case

    def find_collision_point(self, equation, area, corner_index):
        points = []
        # We have 4 windows borders and their equations are;
        # left border   : x = 0, find the value of y.
        # top border    : y = 0, find the value of x.
        # right border  : x = window width, find the value of y.
        # bottom border : y = window height. find the value of x.
        coefficients, case = equation
        border_number = []
        border_indices = self.border_indices[area][corner_index][case]
        if type(border_indices) == int:
            border_indices = [border_indices]
        for border_index in border_indices:
            A, B = coefficients
            point = None
            if border_index == 0:
                if (case == 1) or (case == 2):  # y = Ax + B where x = 0, so y = B
                    point = (0, B)
            elif border_index == 1:
                if case == 0:  # x = B and y = 0.
                    point = (B, 0)
                elif case == 2:  # y = Ax + B where y = 0, so x = -(B / A)
                    point = (-(B / A), 0)
            elif border_index == 2:
                if case == 1:  # y = B and x = window width
                    point = (game.width, B)
                elif case == 2:  # y = Ax + B where x = window width, so y = A * (window width) + B
                    point = (game.width, A * game.width + B)
            elif border_index == 3:
                if case == 0:  # x = B and y = window height
                    point = (B, game.height)
                elif case == 2:  # y = Ax + B where y = window height, so x = (window height - B) / A
                    point = ((game.height - B) / A, game.height)
            points.append(point)
            border_number.append(border_index)
        if len(points) == 2:
            x1, y1 = points[0]
            if (0 <= x1 <= game.width) and (0 <= y1 <= game.height):
                return points[0], border_number[0]
            else:
                return points[1], border_number[1]
        else:
            return points[0], border_number[0]

    def draw_shadow(self, corner_points, collision_points, additional_points):
        points = [*corner_points[::-1], collision_points[0], *additional_points, collision_points[1]]
        pygame.draw.polygon(game.display, self.shadow_color, points)

    def find_additional_points(self, corner_indices, border_numbers):
        additional_points = []
        if (corner_indices == (1, 3)) and (border_numbers == [1, 3]):
            additional_points = [(0, 0), (0, game.height)]
        elif (corner_indices == (0, 1)) and (border_numbers == [0, 2]):
            additional_points = [(0, game.height), (game.width, game.height)]
        else:
            start_value = min(border_numbers)
            difference = abs(border_numbers[0] - border_numbers[1])
            if difference == 3:  # 0 - 3 must be considered as 4 - 3
                difference, start_value = 1, 3
            for n in range(start_value, (start_value + difference)):
                transition = (n, (n + 1))
                additional_points.append(self.additional_points[transition])
        return additional_points

    def draw_circle(self):
        pygame.draw.circle(game.display, self.shadow_color, (self.x, self.y), self.radius)


class Game:
    def __init__(self, size=(1000, 1000), background_color=(255, 255, 255)):
        self.width, self.height = size
        self.display = pygame.display.set_mode(size)
        pygame.display.set_caption("Shadow Casting in Pygame")
        self.background_color = background_color
        self.rectangles = []
        self.font = pygame.font.SysFont("Helvetica", 32)

    def setup(self):
        self.LightSource = LightSource(position=(500, 500))
        for p in range(60, 950, 100):
            self.rectangles.append(Rectangle(position=(p, p), size=(80, 80)))
        Thread(target=self.draw_and_update).start()

    def draw_and_update(self):
        sleep(0.25)
        while ON:
            initial_time = perf_counter()
            self.display.fill(self.background_color)
            for rectangle in self.rectangles:
                self.LightSource.operate(rectangle)
            for rectangle in self.rectangles:
                rectangle.draw()
            self.LightSource.draw_circle()
            final_time = perf_counter()
            difference = round(final_time - initial_time, 4)
            FPS = round(1 / difference)
            self.text = self.font.render(f"FPS: {FPS}", True, (255, 0, 0))
            self.display.blit(self.text, (0, 0))
            pygame.display.flip()


game = Game()
game.setup()

while True:
    sleep(0.01)
    game.LightSource.x, game.LightSource.y = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
    keys = pygame.key.get_pressed()
    if keys[pygame.K_q]:
        ON = False
        pygame.quit()
        quit()
