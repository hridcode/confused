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
    def __init__(self, x = 0, y = 0, platforms = []):
        self.x = x
        self.y = y

        self.platforms = platforms
        
        self.is_jumping = False
        self.jump_frame = 0
        self.jump_length = 36
        
        self.is_falling = False
        self.fall_velocity = 0
        self.fall_acceleration = 1
        
        self.x_velocity = 0
        self.x_direction = 1
        self.x_acceleration = 0.4
        self.x_max_velocity = 5

    def update(self):
        if not self.collideany():
            self.is_falling = True

        if self.is_falling:
            self.fall_velocity += self.fall_acceleration
            self.y += self.fall_velocity
            if self.collideany():
                self.is_falling = False
                self.fall_velocity = 0

        print(f"{self.is_falling=}, {self.fall_velocity=}")

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

    def jump(self):
        if not self.is_jumping:
            if self.collideany():
                self.is_jumping = True
        else:
            jump_offset = max(0, 25 - self.jump_frame)
            self.y -= jump_offset
            self.jump_frame += 1
            if self.jump_frame == self.jump_length:
                self.is_jumping = False
                self.jump_frame = 0
                return

            if self.collideany():
                self.is_jumping = False
                self.jump_frame = 0

                hit_platform = self.collideanyreturn()[0]

                if self.fall_velocity <= jump_offset:
                    self.y = hit_platform.y + hit_platform.height + 1
                else:
                    self.y = hit_platform.y - 50
                    self.is_falling = False

                print(f"{self.fall_velocity=}, {jump_offset=}, {hit_platform=}")

                return

    def collide(self, platform):
        player_rect = pygame.Rect(self.x, self.y, 50, 50)
        platform_rect = pygame.Rect(platform.x, platform.y, platform.width, platform.height)

        return player_rect.colliderect(platform_rect)

    def collideany(self):
        return any([self.collide(platform) for platform in self.platforms])

    def collideanyreturn(self):
        return [platform for platform in self.platforms if self.collide(platform)]

class Platform:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def draw(self):
        pygame.draw.rect(win, (125, 59, 17), (self.x, self.y, self.width, self.height))

platform1 = Platform(0, 400, 300, 30)
platform2 = Platform(500, 500, 300, 30)
ground = Platform(0, HEIGHT, WIDTH, 10)

platforms = [platform1, platform2, ground]

player = Player(0, HEIGHT - 50, platforms)

while True:
    clock.tick_busy_loop(120)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                player.jump()

    keys = pygame.key.get_pressed()

    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        player.move(-1)
    elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        player.move(1)
    else:
        player.move(1, stop = True)

    if player.is_jumping:
        player.jump()

    win.fill((255, 255, 255))

    for platform in platforms:
        platform.draw()

    player.update()

    pygame.display.update()