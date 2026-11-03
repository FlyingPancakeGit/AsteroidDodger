import pygame
import math
import random
import time


# sprites
class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.original_images = [pygame.transform.scale_by(pygame.image.load(
                                '../images/spaceship/spaceship_stationary.png').convert_alpha(), 0.6),
                                pygame.transform.scale_by(pygame.image.load(
                                '../images/spaceship/spaceship_moving.png').convert_alpha(), 0.6)
                                ]
        self.image = self.original_images[1]
        self.rect = self.image.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.mask = pygame.mask.from_surface(self.image)

        self.image_index = 1

        self.speed = 300
        self.max_speed = 500
        self.min_speed = 100
        self.speed_increment = 10
        self.can_change_speed = True
        self.speed_change_time = 0
        self.speed_cooldown = 50

        self.direction = pygame.math.Vector2(0, 0)
        self.rotation = 0

        self.can_move = True
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.laser_cooldown = 400

        self.speed_powerup_active = False
        self.speed_powerup_time = 0
        self.speed_powerup_life_time = 10000

        self.lives = 3

    def get_input(self):
        keys = pygame.key.get_pressed()
        recent_keys = pygame.key.get_just_pressed()

        if recent_keys[pygame.K_SPACE]:
            self.can_move = not self.can_move
            self.image_index = 1 if self.image_index == 0 else 0

        if keys[pygame.K_w] and self.can_change_speed:
            if self.speed >= self.max_speed:
                self.speed = self.max_speed
            else:
                self.speed += self.speed_increment

            self.speed_change_time = pygame.time.get_ticks()
            self.can_change_speed = False

        if keys[pygame.K_s] and self.can_change_speed:
            if self.speed <=  self.min_speed:
                self.speed = self.min_speed
            else:
                self.speed -= self.speed_increment

            self.speed_change_time = pygame.time.get_ticks()
            self.can_change_speed = False

        if pygame.mouse.get_pressed()[0] and self.can_shoot:
            Laser((all_sprites, laser_sprites), laser_image, self.rect.center, self.rotation)

            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()

            laser_sound.play()

    def get_direction(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.direction.x = mouse_x - self.rect.centerx
        self.direction.y = mouse_y - self.rect.centery
        self.direction = self.direction.normalize() if self.direction else self.direction

    def get_dist_to_mouse(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        distance = pygame.math.Vector2(0, 0)
        distance.x = abs(mouse_x - self.rect.centerx)
        distance.y = abs(mouse_y - self.rect.centery)
        return math.sqrt(distance.x ** 2 + distance.y ** 2)

    def rotate(self):
        self.rotation = math.degrees(math.atan2(-self.direction.y, self.direction.x)) - 90
        self.image = pygame.transform.rotate(self.original_images[self.image_index], self.rotation)
        self.rect = self.image.get_frect(center=self.rect.center)

    def check_laser_timer(self):
        if not self.can_shoot:
            if pygame.time.get_ticks() - self.laser_shoot_time >= self.laser_cooldown:
                self.can_shoot = True

    def check_speed_timer(self):
        if not self.can_change_speed:
            if pygame.time.get_ticks() - self.speed_change_time >= self.speed_cooldown:
                self.can_change_speed = True

    def hit(self):
        self.lives -= 1 if self.lives >= 1 else 0
        life_lost_sound.play()
        explosion_sound.play()

    def check_powerups(self):
        if self.speed_powerup_active:
         if pygame.time.get_ticks() - self.speed_powerup_time >= self.speed_powerup_life_time:
            self.speed_powerup_active = False
            self.max_speed -= 300

            if self.speed > self.max_speed:
                self.speed = self.max_speed

    def update(self, dt):
        self.image = self.original_images[self.image_index]
        self.mask = pygame.mask.from_surface(self.image)

        self.get_input()
        self.check_laser_timer()
        self.check_speed_timer()
        self.check_powerups()
        self.get_direction()
        self.rotate()

        if self.can_move and self.get_dist_to_mouse() > 70:
            self.rect.centerx += dt * self.speed * self.direction.x
            self.rect.centery += dt * self.speed * self.direction.y

class Asteroid(pygame.sprite.Sprite):
    def __init__(self, groups, image):
        super().__init__(groups)
        self.original_image = image
        self.image = self.original_image
        self.rect = self.image.get_frect(center=self.get_pos())


        self.speed = random.randint(300, 500)
        self.direction = self.get_direction()

        self.rotation_speed = random.randint(20, 60)
        self.rotation = 0

        self.life_time = 12000
        self.spawn_time = pygame.time.get_ticks()

    def get_pos(self):
        pos = pygame.math.Vector2(0, 0)
        angle = random.uniform(0, 2 * math.pi)
        pos.x = int(asteroid_circle_center.x + asteroid_circle_radius * math.cos(angle))
        pos.y = int(asteroid_circle_center.y + asteroid_circle_radius * math.sin(angle))
        return pos

    def get_direction(self):
        direction = pygame.math.Vector2(0, 0)
        center_x, center_y = asteroid_circle_center
        direction.x = center_x - self.rect.centerx
        direction.y = center_y - self.rect.centery
        direction = direction.normalize()
        return direction

    def check_age(self):
        age = pygame.time.get_ticks() - self.spawn_time
        if age > self.life_time:
            self.kill()

    def update(self, dt):
        self.check_age()

        self.image = pygame.transform.rotozoom(self.original_image, self.rotation, 1)
        self.rect = self.image.get_frect(center=self.rect.center)

        self.rotation += self.rotation_speed * dt

        self.rect.center += dt * self.speed * self.direction

class Laser(pygame.sprite.Sprite):
    def __init__(self, groups, image, pos, rotation):
        super().__init__(groups)
        self.original_image = image
        self.image = pygame.transform.rotate(self.original_image, rotation)
        self.rect = self.image.get_frect(center=pos)

        self.speed = 700
        self.direction = pygame.math.Vector2(0, -1).rotate(-rotation).normalize()

        self.life_time = 4000
        self.spawn_time = pygame.time.get_ticks()

    def check_age(self):
        age = pygame.time.get_ticks() - self.spawn_time
        if age > self.life_time:
            self.kill()

    def update(self, dt):
        self.check_age()

        movement = dt * self.speed * self.direction

        self.rect.center += dt * self.speed * self.direction

class Life(pygame.sprite.Sprite):
    def __init__(self, groups, image, pos):
        super().__init__(groups)
        self.original_image = image
        self.image = self.original_image
        self.rect = self.image.get_frect(bottomleft=pos)

    def update(self, dt):
        pass

class Powerup(pygame.sprite.Sprite):
    def __init__(self, groups, image):
        super().__init__(groups)
        self.original_image = image
        self.image = self.original_image
        self.rect = self.image.get_frect(center=self.get_pos())

        self.speed = random.randint(400, 500)
        self.direction = self.get_direction()

        self.life_time = 12000
        self.spawn_time = pygame.time.get_ticks()

    def get_pos(self):
        pos = pygame.math.Vector2(0, 0)
        angle = random.uniform(0, 2 * math.pi)
        pos.x = int(asteroid_circle_center.x + asteroid_circle_radius * math.cos(angle))
        pos.y = int(asteroid_circle_center.y + asteroid_circle_radius * math.sin(angle))
        return pos

    def get_direction(self):
        direction = pygame.math.Vector2(0, 0)
        center_x, center_y = asteroid_circle_center
        direction.x = center_x - self.rect.centerx
        direction.y = center_y - self.rect.centery
        direction = direction.normalize()
        return direction

    def check_age(self):
        age = pygame.time.get_ticks() - self.spawn_time
        if age > self.life_time:
            self.kill()

    def hit(self):
        self.kill()

    def update(self, dt):
        self.check_age()

        self.rect.center += dt * self.speed * self.direction

class LifePowerup(Powerup):
    def __init__(self, groups, image):
        super().__init__(groups, image)

    def hit(self):
        player.lives += 1
        self.kill()

class SpeedPowerup(Powerup):
    def __init__(self, groups, image):
        super().__init__(groups, image)

        self.rotate()

    def rotate(self):
        rotation = math.degrees(math.atan2(-self.direction.y, self.direction.x))
        self.image = pygame.transform.rotate(self.original_image, rotation)
        self.rect = self.image.get_frect(center=self.rect.center)

    def hit(self):
        if not player.speed_powerup_active:
            player.speed_powerup_active = True
            player.max_speed += 300
            player.speed_powerup_time = pygame.time.get_ticks()

        self.kill()


# functions
def check_collisions(score):
    for laser in laser_sprites:
        if pygame.sprite.spritecollide(laser, asteroid_sprites, True, pygame.sprite.collide_mask):
            score += 1
            laser.kill()

        powerup_collisions = pygame.sprite.spritecollide(laser, powerup_sprites, False, pygame.sprite.collide_mask)
        if powerup_collisions:
            laser.kill()
            for powerup in powerup_collisions:
                powerup.hit()
                powerup_sound.play()

    player_collisions = pygame.sprite.spritecollide(player, asteroid_sprites, True, pygame.sprite.collide_mask)
    powerup_collisions = pygame.sprite.spritecollide(player, powerup_sprites, False, pygame.sprite.collide_mask)

    if player_collisions:
        player.hit()
    if powerup_collisions:
        for powerup in powerup_collisions:
            powerup.hit()
            powerup_sound.play()

    return score

def check_lives():
    global game_over
    if player.lives <= 0:
        game_over = True

def update_lives(num):
    for life in life_sprites:
        life.kill()

    x_pos = 10
    y_pos = WINDOW_HEIGHT - 10

    for life in range(num):
        if len(life_sprites) != 0:
            x_pos += 60

        Life((all_sprites, life_sprites), life_image, (x_pos, y_pos))

def display_score(score):
    title_surf = font.render(f'Score: ', True, (240, 240, 240))
    title_rect = title_surf.get_frect(bottomleft=(15, WINDOW_HEIGHT - 110))


    score_surf = font.render(f'{score}', True, (240, 240, 240))
    score_rect = score_surf.get_frect(bottomleft=title_rect.bottomright)

    display_surface.blit(title_surf, title_rect)
    display_surface.blit(score_surf, score_rect)

def display_speed():
    speed_colour = (255, 165, 0) if player.speed > 500 else (240, 240, 240)
    title_surf = font.render(f'Speed: ', True, (240, 240, 240))
    title_rect = title_surf.get_frect(bottomleft=(15, WINDOW_HEIGHT - 70))

    speed_surf = font.render(f'{player.speed}', True, (speed_colour))
    speed_rect = speed_surf.get_frect(bottomleft=title_rect.bottomright)

    display_surface.blit(title_surf, title_rect)
    display_surface.blit(speed_surf, speed_rect)

def display_game_over(score):
    colour = (240, 240, 240)
    game_over_surf = menu_font.render('Game Over!', True, colour)
    game_over_rect = game_over_surf.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))

    final_score_surf = font.render(f'Final Score: {score}', True, colour)
    final_score_rect = final_score_surf.get_frect(center=(game_over_rect.centerx, game_over_rect.centery + 80))

    display_surface.blit(game_over_surf, game_over_rect)
    display_surface.blit(final_score_surf, final_score_rect)


# setup
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1260, 840
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Asteroid Dodger')
running = True
game_over = False
score = 0
clock = pygame.time.Clock()

# imports
space_image = pygame.image.load('../images/space.png').convert_alpha()
life_image = pygame.transform.scale_by(pygame.image.load('../images/life.png').convert_alpha(), 0.2)

asteroid_images = [pygame.transform.scale_by(pygame.image.load(f'../images/asteroids/{i}.png').convert_alpha(), 0.5)for i in range(2)]
laser_image = pygame.transform.scale_by(pygame.image.load('../images/laser.png'), 0.2).convert_alpha()

life_powerup_image = pygame.transform.scale_by(pygame.image.load('../images/powerups/life_powerup.png').convert_alpha(), 0.3)
speed_powerup_image = pygame.transform.scale_by(pygame.image.load('../images/powerups/speed_powerup.png').convert_alpha(), 0.3)

laser_sound = pygame.mixer.Sound('../audio/laser.wav')
laser_sound.set_volume(0.3)

explosion_sound = pygame.mixer.Sound('../audio/explosion.wav')
life_lost_sound = pygame.mixer.Sound('../audio/life_lost.mp3')
powerup_sound = pygame.mixer.Sound('../audio/powerup.wav')

font = pygame.font.Font('../fonts/comic_sans.ttf', 30)
menu_font = pygame.font.Font('../fonts/comic_sans.ttf', 120)

# groups
all_sprites = pygame.sprite.Group()

asteroid_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()
powerup_sprites = pygame.sprite.Group()
life_sprites = pygame.sprite.Group()

player_group = pygame.sprite.Group()


player = Player((all_sprites, player_group))

# custom events
asteroid_event = pygame.event.custom_type()
pygame.time.set_timer(asteroid_event, 1000)

powerup_event = pygame.event.custom_type()
pygame.time.set_timer(powerup_event, 8000)

# asteroid circle
asteroid_circle_center = pygame.math.Vector2(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
asteroid_circle_radius = math.sqrt(WINDOW_WIDTH ** 2 + WINDOW_HEIGHT ** 2)

# secondary setup
update_lives(player.lives)


# main loop
while running and not game_over:
    dt = clock.tick() / 1000

    # event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == asteroid_event:
            Asteroid((all_sprites, asteroid_sprites), random.choice(asteroid_images))
        if event.type == powerup_event:
            LifePowerup((all_sprites, powerup_sprites), life_powerup_image)
            SpeedPowerup((all_sprites, powerup_sprites), speed_powerup_image)

    # update
    update_lives(player.lives)
    score = check_collisions(score)

    all_sprites.update(dt)

    check_lives()

    # draw
    display_surface.blit(space_image, (0, 0))

    if game_over:
        update_lives(player.lives)
        display_game_over(score)
        pygame.display.update()
        time.sleep(3)
    else:
        display_score(score)
        display_speed()
        all_sprites.draw(display_surface)
        player_group.draw(display_surface)
        pygame.display.update()

pygame.quit()