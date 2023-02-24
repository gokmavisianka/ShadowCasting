"""
MIT License

Copyright (c) 2023 Rasim Mert YILDIRIM

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import pygame
import numpy as np

pygame.init()
ON = True


class Text:
    def __init__(self, base_string: str, function, color: tuple[int, int, int] = (255, 0, 0)):
        # base_string can be "FPS: " or "Coin: " to represent the remaining part.
        self.base_string = base_string
        self.color = color
        # function is used to get the remaining part (It can be fps value or amount of coins etc.) of the string.
        # So {base_string + remaining} will be shown on the screen.
        self.function = function
        # Size of the font can be changed.
        self.font = pygame.font.SysFont("Helvetica", 32)

    def show(self, display, position, string=None):
        if string is None:
            string = self.base_string
            remaining = self.function()
            # Check if the type of the remaining part is str. If not, Convert it to the str type before merging strings.
            if type(remaining) is str:
                string += remaining
            else:
                string += str(remaining)
        text = self.font.render(string, True, self.color)
        display.blit(text, position)


class Screen:
    def __init__(self, background_color: tuple[int, int, int], resolution: tuple[int, int] = (1000, 1000)):
        self.background_color = background_color
        self.width, self.height = resolution
        self.display = pygame.display.set_mode(resolution)
        self.FPS = self.FPS()

    def fill(self, color=None):
        if color is None:
            color = self.background_color
        # fill the screen with specific color.
        self.display.fill(color)

    @staticmethod
    def update():
        # Update the whole window.
        pygame.display.flip()

    class FPS:
        def __init__(self):
            self.clock = pygame.time.Clock()
            self.text = Text(base_string="FPS: ", function=self.get)

        def set(self, value):
            self.clock.tick(value)

        def get(self):
            return int(self.clock.get_fps())


class Rectangles:
    def __init__(self):
        self.elements = []

    def draw_all(self):
        for rectangle in self.elements:
            rectangle.draw()


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
        pygame.draw.rect(screen.display, self.color, (self.x, self.y, self.width, self.height))


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
                                  (1, 2): (screen.width, 0),
                                  (2, 3): (screen.width, screen.height),
                                  (3, 4): (0, screen.height)}  # (3, 4) can be considered as (3, 0).

    # Draw shadows for every rectangle in the list.
    def draw_shadows(self):
        for rectangle in rectangles.elements:
            self.draw_shadow(rectangle)

    # Line starts from the position of the light source and ends at the corner of the rectangle.
    # The value of the "area" is important to know which corner will be used as the end point.
    def draw_shadow(self, rectangle):
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
            self.draw_polygon(corner_points, collision_points, additional_points)

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
                    point = (screen.width, B)
                elif case == 2:  # y = Ax + B where x = window width, so y = A * (window width) + B
                    point = (screen.width, A * screen.width + B)
            elif border_index == 3:
                if case == 0:  # x = B and y = window height
                    point = (B, screen.height)
                elif case == 2:  # y = Ax + B where y = window height, so x = (window height - B) / A
                    point = ((screen.height - B) / A, screen.height)
            points.append(point)
            border_number.append(border_index)
        if len(points) == 2:
            x1, y1 = points[0]
            if (0 <= x1 <= screen.width) and (0 <= y1 <= screen.height):
                return points[0], border_number[0]
            else:
                return points[1], border_number[1]
        else:
            return points[0], border_number[0]

    # This function is used to draw shadows as polygons.
    def draw_polygon(self, corner_points, collision_points, additional_points):
        points = [*corner_points[::-1], collision_points[0], *additional_points, collision_points[1]]
        pygame.draw.polygon(screen.display, self.shadow_color, points)

    def find_additional_points(self, corner_indices, border_numbers):
        additional_points = []
        if (corner_indices == (1, 3)) and (border_numbers == [1, 3]):
            additional_points = [(0, 0), (0, screen.height)]
        elif (corner_indices == (0, 1)) and (border_numbers == [0, 2]):
            additional_points = [(0, screen.height), (screen.width, screen.height)]
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
        pygame.draw.circle(screen.display, (255, 0, 0), (self.x, self.y), self.radius)


class Game:
    @staticmethod
    def setup():
        for p in range(60, 950, 100):
            rectangles.elements.append(Rectangle(position=(p, p), size=(80, 80)))

    @staticmethod
    def draw_and_update():
        screen.fill()
        light_source.draw_shadows()
        rectangles.draw_all()
        light_source.draw_circle()
        screen.FPS.text.show(screen.display, position=(0, 0))
        screen.update()


game = Game()
rectangles = Rectangles()
screen = Screen(background_color=(255, 255, 255), resolution=(1000, 1000))
light_source = LightSource(position=(500, 500))
game.setup()

while ON:
    light_source.x, light_source.y = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
    keys = pygame.key.get_pressed()
    if keys[pygame.K_q]:
        ON = False
        pygame.quit()
        quit()
    screen.FPS.set(60)
    game.draw_and_update()
    
