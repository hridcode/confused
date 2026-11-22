import pygame
import sys
import random
import math

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

    def rerender(self):
        self._surface = self.font.render(self.text, True, self.color)

class Button:
    def __init__(self, font, text, x, y, width, height, align_x, align_y, text_color, background_color, hover_color = (255, 255, 255), border_color=(0, 0, 0), border_width=0):
        self.rect = pygame.Rect(x - align_x * width / 2, y - align_y * height / 2, width, height)
        self.text = Text(font, text, self.rect.centerx, self.rect.centery, 1, 1, text_color)
        self.background_color = background_color
        self.hovered = False
        self.hover_color = hover_color
        self.border_color = border_color
        self.border_width = border_width

    def display(self):
        pygame.draw.rect(win, self.background_color if not self.hovered else self.hover_color, self.rect)
        pygame.draw.rect(win, self.border_color, self.rect, self.border_width)
        self.text.display()

    def isover(self, x, y):
        return self.rect.collidepoint((x, y))

jump_sound = pygame.mixer.Sound("assets/jump.wav")
jump_sound.set_volume(0.6)

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
        self.fall_acceleration = 0.3
        
        self.x_velocity = 0
        self.x_direction = 1
        self.x_acceleration = 0.2
        self.x_max_velocity = 7

    def update(self):
        if not self.collideany():
            self.is_falling = True
        else:
            collision = self.collideanyreturn()[0]
            if not self.is_jumping:
                if self.y <= collision.y + collision.height / 2:
                    self.y = collision.y - 49
                else:
                    self.y = collision.y + collision.height

        if self.is_falling:
            self.fall_velocity += self.fall_acceleration
            self.y += self.fall_velocity
            if self.collideany() and not self.is_jumping:
                self.is_falling = False
                self.fall_velocity = 0
                self.y = self.collideanyreturn()[0].y - 49

        pygame.draw.rect(win, (255, 255, 0), (self.x, self.y, 50, 50))
        pygame.draw.rect(win, (0, 0, 0), (self.x, self.y, 50, 50), width=2)

    def move(self, direction, stop = False):
        if self.x_direction != direction:
            self.x_direction = direction
            self.x_velocity = 0

        if not stop:
            self.x_velocity += self.x_acceleration
            self.x_velocity = min(self.x_velocity, self.x_max_velocity)
            self.x += self.x_velocity * self.x_direction
            if self.x <= 0:
                self.x = 0
                self.x_velocity = 0
            elif self.x >= WIDTH - 50:
                self.x = WIDTH - 50
                self.x_velocity = 0
        else:
            self.x_velocity = 0

    def jump(self):
        if not self.is_jumping:
            if self.collideany():
                jump_sound.play()
                self.is_jumping = True
        else:
            jump_offset = max(0, (16 / self.fall_acceleration - self.jump_frame) * self.fall_acceleration)
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

                if self.fall_velocity < jump_offset:
                    print("Collision on bottom")
                    self.y = hit_platform.y + hit_platform.height + 1
                else:
                    print("Collision on top")
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

    def die(self):
        player.x = 0
        player.y = HEIGHT - 50

class Platform:
    def __init__(self, x, y, width, height, color = (125, 59, 17), oscillate_x = (0, 1), oscillate_y = (0, 1)):
        self.x = x
        self.y = y
        self.static_x = x
        self.static_y = y
        self.width = width
        self.height = height
        self.color = color
        self.osc_x_length = oscillate_x[0]
        self.osc_x_speed = oscillate_x[1] * 5
        self.osc_y_length = oscillate_y[0]
        self.osc_y_speed = oscillate_y[1] * 5
        self.osc_frame = 0
        self.dir_x = 1
        self.dir_y = 1
        self.last_offset_x = 0
        self.last_offset_y = 0

    def draw(self):
        self.x = self.static_x + int(math.sin(self.osc_frame * math.pi * 2 / (self.osc_x_speed / 2)) * self.osc_x_length)
        self.y = self.static_y + int(math.sin(self.osc_frame * math.pi * 2 / (self.osc_y_speed / 2)) * self.osc_y_length)

        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))

        # Stripes
        num_stripes = self.width // 50
        for i in range(num_stripes):
            point1 = (self.x + i * 50, self.y + self.height - 2)
            point2 = (self.x + i * 50 + 25, self.y)
            point3 = (self.x + i * 50 + 50, self.y)
            point4 = (self.x + i * 50 + 25, self.y + self.height - 2)
            pygame.draw.polygon(win, (212, 152, 83), (point1, point2, point3, point4))

        pygame.draw.rect(win, (0, 0, 0), (self.x, self.y, self.width, self.height), width=2)
        
        self.osc_frame += 1

class Orb:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = (0, 255, 0)

    def draw(self):
        pygame.draw.circle(win, self.color, (self.x, self.y), 20)
        pygame.draw.circle(win, (0, 0, 0), (self.x, self.y), 20, width = 2)

    def collision(self, player):
        player_rect = pygame.Rect(player.x, player.y, 50, 50)
        closest_x = max(player_rect.left, min(self.x, player_rect.right))
        closest_y = max(player_rect.top, min(self.y, player_rect.bottom))
        
        dx = self.x - closest_x
        dy = self.y - closest_y
        
        return (dx * dx + dy * dy) <= 400

class Saw:
    def __init__(self, x, y, radius, spin = 0.4):
        self.x = x
        self.y = y
        self.width = radius * 2
        self.height = radius * 2
        self.radius = radius
        self.angle = 0
        self.spin = spin
        self.color = (0, 0, 0)

    def draw(self):
        # Base circle
        pygame.draw.circle(win, self.color, (self.x + self.radius, self.y + self.radius), self.radius / 2)

        # Spikes
        for spike in range(12):
            point1 = (
                self.x + self.radius + math.cos(spike * 30 + self.angle - 15) * self.radius / 2,
                self.y + self.radius + math.sin(spike * 30 + self.angle - 15) * self.radius / 2
            )
            point2 = (
                self.x + self.radius + math.cos(spike * 30 + self.angle + 15) * self.radius / 2,
                self.y + self.radius + math.sin(spike * 30 + self.angle + 15) * self.radius / 2
            )
            point3 = (
                self.x + self.radius + math.cos(spike * 30 + self.angle) * self.radius,
                self.y + self.radius + math.sin(spike * 30 + self.angle) * self.radius
            )
            pygame.draw.polygon(win, self.color, (point1, point2, point3))

        self.angle += self.spin

class Acid:
    def __init__(self, y):
        self.y = y
        self.particles = []

    def draw(self):
        for particle in self.particles:
            pygame.draw.circle(win, (190, 220, 0), particle["coords"], 5)
            pygame.draw.circle(win, (0, 0, 0), particle["coords"], 7, 2)
            particle["coords"][1] += particle["velocity"]
            particle["velocity"] += particle["acceleration"]

    def spawn(self):
        self.particles.append({
            "coords": [random.randint(20, WIDTH - 20), self.y],
            "velocity": 0.2,
            "acceleration": random.uniform(0.1, 0.2)
        })

    def collide(self, object):
        for particle in self.particles:
            particle_rect = pygame.Rect(particle[0] - 5, particle[1] - 5, 10, 10)
            object_rect = pygame.Rect(object.x, object.y, object.width, object.height)
            if particle_rect.colliderect(object_rect):
                return True

        return False

game_parameters = {
    'gravity': 0.4
}

class Pickup:
    def __init__(self, x, y, effect):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.effect = effect
        self.icon_text = Text(JBMONO_16, "?", self.x, self.y, 1, 1, (200, 0, 0))

    def draw(self):
        pygame.draw.rect(win, (200, 200, 0), (self.x - self.width / 2, self.y - self.height / 2, self.width, self.height), border_radius = 5)
        pygame.draw.rect(win, (0, 0, 0), (self.x - self.width / 2, self.y - self.height / 2, self.width, self.height), border_radius = 5, width = 3)
        self.icon_text.display()

    def trigger_effect(self):
        if self.effect == "gravity":
            game_parameters[self.effect] = random.randint(2, 18) / 50

        print(f"{self.effect} = {game_parameters[self.effect]}")

levels = [
    [
        Platform(0, 400, 400, 30),
        Platform(500, 500, 300, 30),
        Platform(200, 300, 400, 30),
        Orb(400, 200)
    ],
    [
        Platform(0, 500, 300, 30),
        Platform(500, 400, 300, 30),
        Platform(0, 300, 300, 30),
        Platform(500, 200, 300, 30),
        Saw(600, 350, 20, spin = 0.1),
        Orb(400, 100)
    ],
    [
        Platform(300, 500, 200, 30, oscillate_x=(100, 100)),
        Platform(300, 400, 200, 30, oscillate_x=(100, 99)),
        Platform(300, 300, 200, 30, oscillate_x=(100, 98)),
        Platform(300, 200, 200, 30, oscillate_x=(100, 97)),
        Orb(400, 100)
    ],
    [
        Platform(100, 300, 200, 30, oscillate_y=(200, 100)),
        Platform(500, 300, 200, 30, oscillate_y=(200, 100)),
        Saw(200, 50, 10, spin = 0.1),
        Saw(600, 50, 10, spin = 0.1),
        Orb(400, 100)
    ],
    [
        Platform(0, 500, 125, 30),
        Platform(225, 500, 150, 30),
        Saw(300, 450, 20, spin = 0.1),
        Platform(400, 250, 400, 30, oscillate_y=(150, 150)),
        Saw(500, 200, 10, spin = 0.1),
        Saw(600, 100, 10, spin = 0.1),
        Orb(500, 50)
    ],
    [
        Platform(200, 400, 100, 30, oscillate_x=(200, 100), oscillate_y=(100, 100)),
        Platform(600, 300, 30, 150),
        Orb(700, 400),
        Acid(100)
    ],
    [
        Platform(100, 500, 300, 30),
        Platform(100, 400, 300, 30),
        Platform(400, 300, 300, 30),
        Platform(400, 200, 300, 30),
        Saw(300, 600, 30),
        Acid(100),
        Orb(700, 100)
    ],
    [
        Platform(0, 400, 50, 50, oscillate_x=(25, 105), oscillate_y=(100, 100)),
        Platform(375, 400, 50, 50, oscillate_x=(25, 110), oscillate_y=(100, 95)),
        Platform(750, 400, 50, 50, oscillate_x=(25, 115), oscillate_y=(100, 90)),
        Saw(200, 200, 30),
        Saw(200, 600, 30),
        Saw(600, 200, 30),
        Saw(600, 600, 30),
        Orb(400, 100)                
    ]
]

def get_platforms(level):
    return [game_object for game_object in level if type(game_object) == Platform]

def get_orb(level):
    return [game_object for game_object in level if type(game_object) == Orb][0]

def get_fatal_objects(level):
    return [game_object for game_object in level if type(game_object) in [Saw,]]

def get_acid(level):
    return ([game_object for game_object in level if type(game_object) == Acid] or [None,])[0]

ground = Platform(0, HEIGHT, WIDTH, 10)

player = Player(0, HEIGHT - 50, [])

JBMONO_16 = pygame.font.Font("fonts/JetBrains Mono.ttf", 16)
JBMONO_40 = pygame.font.Font("fonts/JetBrains Mono.ttf", 40)

home_title = Text(JBMONO_40, "confused", WIDTH // 2, HEIGHT // 2 - 100, 1, 1, (0, 0, 0))
instructions_title = Text(JBMONO_40, "Instructions", WIDTH // 2, 100, 1, 1, (0, 0, 0))
current_level_display = Text(JBMONO_16, "Level: 1", 30, 30, 0, 0, (0, 0, 0))
money_display = Text(JBMONO_16, "$25", WIDTH - 30, 30, 2, 0, (0, 180, 0))

lose_heading = Text(JBMONO_40, "You Lose!", WIDTH // 2, HEIGHT // 2 - 100, 1, 1, (255, 0, 0))
lose_subtext = Text(JBMONO_16, "get better nerd", WIDTH // 2, HEIGHT // 2 + 100, 1, 1, (0, 0, 0))

win_heading = Text(JBMONO_40, "You Win!", WIDTH // 2, HEIGHT // 2 - 100, 1, 1, (0, 200, 0))
win_subtext = Text(JBMONO_16, "the government has been destroyed. congratulations.", WIDTH // 2, HEIGHT // 2 + 100, 1, 1, (0, 0, 0))

play_button = Button(
    font = JBMONO_16, 
    text = "Play", 
    x = WIDTH // 2 - 170, 
    y = HEIGHT // 2 + 100, 
    width = 150, 
    height = 50, 
    align_x = 1, 
    align_y = 1, 
    text_color = (0, 0, 0), 
    background_color = (255, 255, 255),
    hover_color = (200, 200, 200), 
    border_color = (0, 0, 0), 
    border_width = 3
)

instructions_button = Button(
    font = JBMONO_16, 
    text = "Instructions", 
    x = WIDTH // 2 + 170, 
    y = HEIGHT // 2 + 100, 
    width = 150, 
    height = 50, 
    align_x = 1, 
    align_y = 1, 
    text_color = (0, 0, 0), 
    background_color = (255, 255, 255), 
    hover_color = (200, 200, 200),
    border_color = (0, 0, 0), 
    border_width = 3
)

buttons = [play_button, instructions_button]

game_started = False
level = 1
last_level = 0
screen = "home"
transition_frame = 0
money = 25

pickups = []

while True:
    clock.tick_busy_loop(120)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                player.jump()
                money -= 1
        elif event.type == pygame.MOUSEMOTION:
            for button in buttons:
                button.hovered = button.isover(*event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if play_button.isover(*event.pos):
                screen = "playing"

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

    if screen == "home":
        # Home screen
        home_title.display()
        for button in buttons:
            button.display()
    elif screen == "instructions":
        instructions_title.display()
    elif screen == "playing" or screen == "transition":
        player.fall_acceleration = game_parameters["gravity"]

        current_level = levels[level - 1]
        platforms = get_platforms(current_level) + [ground, ]
        orb = get_orb(current_level)
        fatals = get_fatal_objects(current_level)
        acid = get_acid(current_level)

        if random.randint(0, 1000) == 1:
            platform = random.choice(platforms)
            parameter = random.choice(list(game_parameters.keys()))
            pickup_x = random.randint(platform.x, platform.x + platform.width)
            pickup_y = platform.y - 20
            print(parameter)
            pickup = Pickup(pickup_x, pickup_y, parameter)
            pickups.append(pickup)
            if len(pickups) > 3:
                pickups.pop(0)

        for object in current_level:
            object.draw()

        if acid and random.randint(0, 40) == 1:
            acid.spawn()

        if acid:
            if acid.collide(player):
                player.die()
                money -= 2

        for pickup_index, pickup in enumerate(pickups):
            pickups[pickup_index].draw()
            if player.collide(pickups[pickup_index]):
                pickups[pickup_index].trigger_effect()
                money += random.randint(-200, 200) / 100
                pickups[pickup_index] = None

        pickups = [i for i in pickups if i]

        player.platforms = platforms
        player.update()

        current_level_display.text = f"Level: {level}"
        current_level_display.display()

        money_display.text = f"${money:.2f}"
        money_display.display()

        if orb.collision(player):
            last_level = level
            screen = "transition"

        if any(player.collide(fatal) for fatal in fatals):
            player.die()
            money -= 5

        if screen == "transition":
            transition_frame += 0.2
            if transition_frame >= 30:
                screen = "playing"
                transition_frame = 0

            transition_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

            if transition_frame <= 10:
                transition_surface.fill((0, 0, 0, (transition_frame / 10) * 255))
            elif 10 < transition_frame < 20:
                transition_surface.fill((0, 0, 0))
            else:
                last_level_value = level
                level = last_level + 1
                if level != last_level_value:
                    money += 5
                player.x = 0
                player.y = HEIGHT - 50
                if last_level == len(levels):
                    screen = "win"
                transition_surface.fill((0, 0, 0, ((30 - transition_frame) / 10) * 255))

            win.blit(transition_surface, (0, 0))
    elif screen == "win":
        win_heading.display()
        win_subtext.display()
    elif screen == "lose":
        lose_heading.display()
        lose_subtext.display()

    if money < 0:
        screen = "lose"

    pygame.display.update()