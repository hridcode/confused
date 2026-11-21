import pygame
import sys

pygame.init()
pygame.font.init()

WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))

clock = pygame.time.Clock()

class Text:
    def __init__(self, font, text, x, y, x_align, y_align, color):
        self.font = font
        self.text = text
        self.x = x
        self.y = y
        self.x_align = x_align
        self.y_align = y_align
        self.color = color

        self._last_text = ""
        self._surface = None

    def display(self):
        if self._last_text != self.text:
            self._surface = self.font.render(self.text, True, self.color)

        text_width, text_height = self.font.size(self.text)
        adj_x, adj_y = self.x - text_width * (self.x_align) / 2, self.y - text_height * (self.y_align) / 2
        
        win.blit(self._surface, (adj_x, adj_y))

COMIC_SANS_16 = pygame.font.Font("fonts/Comic Sans MS.ttf", 16)
COMIC_SANS_40 = pygame.font.Font("fonts/Comic Sans MS.ttf", 40)

class Player:
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y
        
        self.is_jumping = False
        self.jump_frame = 0
        self.is_falling = False
        self.fall_height = 0
        
        self.x_velocity = 0
        self.x_direction = 1
        self.x_acceleration = 0.4
        self.x_max_velocity = 5

    def draw(self):
        pygame.draw.rect(win, (255, 255, 0), (self.x, self.y, 50, 50))

    def move(self, direction, stop = False):
        if self.x_direction != direction:
            self.x_direction = direction
            self.x_velocity = 0

        if not stop:
            self.x_velocity += self.x_acceleration
            self.x_velocity = min(self.x_velocity, self.x_max_velocity)
            self.x += self.x_velocity * self.x_direction
        else:
            self.x_velocity = 0

player = Player(0, HEIGHT - 50)

while True:
    clock.tick_busy_loop(120)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()

    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        player.move(-1)
    elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        player.move(1)
    else:
        player.move(1, stop = True)

    win.fill((255, 255, 255))

    player.draw()

    pygame.display.update()