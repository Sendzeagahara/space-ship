import pygame

from os.path import join
from random import randint, uniform


class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.original_image = pygame.image.load(join('images', 'player.png')).convert_alpha()
        self.image = self.original_image
        self.rect = self.image.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT - 100))
        self.direction = pygame.math.Vector2()
        self.speed = 300
        self.rotation = 0

        #laser cooldown
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 500

        #mask
        self.mask = pygame.mask.from_surface(self.image)

    def laser_cooldown_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True

    def update(self, delta_time):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * self.speed * delta_time
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WINDOW_WIDTH:
            self.rect.right = WINDOW_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > WINDOW_HEIGHT:
            self.rect.bottom = WINDOW_HEIGHT

        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser(laser_surf, self.rect.midtop, (all_sprites, laser_sprites))
            laser_sound.play()
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()

        self.laser_cooldown_timer()


class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center=(randint(0, WINDOW_WIDTH - self.image.get_width()),
                                                 randint(0, WINDOW_HEIGHT - self.image.get_height())))


class Laser(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom=pos)
        self.speed = 400

    def update(self, delta_time):
        self.rect.y -= self.speed * delta_time
        if self.rect.bottom < 0:
            self.kill()


class Meteor(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.original_image = surf
        self.image = self.original_image
        self.rect = self.image.get_frect(midbottom=pos)
        self.direction = pygame.math.Vector2(uniform(-0.3, 0.3), 1)
        self.speed = randint(200, 300)
        self.rotation = 0
        self.rotation_speed = randint(-40, 80)

    def update(self, delta_time):
        self.rect.center += self.direction * self.speed * delta_time
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()

        self.rotation += self.rotation_speed * delta_time
        self.image = pygame.transform.rotozoom(self.original_image, self.rotation, 1)
        self.rect = self.image.get_frect(center=self.rect.center)


class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(center=pos)
        explosion_sound.play()

    def update(self, delta_time):
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()
        self.frame_index += 50 * delta_time


def collision_check():
    global score
    global best_score
    global game_state
    if pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask):
        if best_score < score:
            best_score = score
            score = 0
        game_state = False

    for laser_instance in laser_sprites:
        if pygame.sprite.spritecollide(laser_instance, meteor_sprites, True, pygame.sprite.collide_mask):
            laser_instance.kill()
            score += 1
            AnimatedExplosion(explosion_frames, laser_instance.rect.midtop, all_sprites)


def greetings():
    text_surf = font.render('Press "SPACE" to start', True, (220, 220, 220))
    text_rect = text_surf.get_rect(midtop=(WINDOW_WIDTH / 2, 20))
    pygame.draw.rect(display_surface, (120, 100, 120), text_rect.inflate(10, 10).move(0, -3), border_radius=5)
    display_surface.blit(text_surf, text_rect)


def display_score(count):
    text_surf = font.render(str(count), True, (220, 220, 220))
    text_rect = text_surf.get_rect(midbottom=(WINDOW_WIDTH / 2, WINDOW_HEIGHT - 20))
    pygame.draw.rect(display_surface, (120, 100, 120), text_rect.inflate(10, 10).move(0, -3), border_radius=5)
    display_surface.blit(text_surf, text_rect)


def display_best_score(count):
    text_surf = font.render(f'Your best score is: {count}', True, (220, 220, 220))
    text_rect = text_surf.get_rect(midbottom=(WINDOW_WIDTH / 2, WINDOW_HEIGHT - 20))
    pygame.draw.rect(display_surface, (120, 100, 120), text_rect.inflate(10, 10).move(0, -3), border_radius=5)
    display_surface.blit(text_surf, text_rect)


#general setup
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Space Ship')
clock = pygame.time.Clock()
running = True
game_state = False
score = 0
best_score = 0

#imports
star_surf = pygame.image.load(join('images', 'star.png')).convert_alpha()
laser_surf = pygame.image.load(join('images', 'laser.png')).convert_alpha()
meteor_surf = pygame.image.load(join('images', 'meteor.png')).convert_alpha()
font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 20)
explosion_frames = [pygame.image.load(join('images', 'explosion', f'{i}.png')).convert_alpha() for i in range(21)]

laser_sound = pygame.mixer.Sound(join('audio', 'laser.wav'))
laser_sound.set_volume(0.2)
explosion_sound = pygame.mixer.Sound(join('audio', 'explosion.wav'))
explosion_sound.set_volume(0.15)
game_sound = pygame.mixer.Sound(join('audio', 'game_music.wav'))
game_sound.set_volume(0.2)

game_sound.play(loops=-1)


#groups initialisation
all_sprites = pygame.sprite.Group()
star_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()

player = Player(all_sprites)
for i in range(20):
    Star((all_sprites, star_sprites), star_surf)

#custom events
#meteor
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 1000)

while running:
    dt = clock.tick() / 1000
    #event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if game_state:
            if event.type == meteor_event:
                meteor_left_border = int(meteor_surf.get_width() / 2)
                meteor_right_border = WINDOW_WIDTH - int(meteor_surf.get_width() / 2)
                Meteor(meteor_surf,
                       (randint(meteor_left_border, meteor_right_border), 0),
                       (all_sprites, meteor_sprites))
        else:
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    for meteor in meteor_sprites:
                        meteor.kill()
                    for laser in laser_sprites:
                        laser.kill()
                    player.rect.center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT - 100)
                    game_state = True

    if game_state:
        all_sprites.update(dt)

        display_surface.fill('#3a2e3f')

        all_sprites.draw(display_surface)
        display_score(score)

        collision_check()

        pygame.display.update()
    else:
        display_surface.fill('#3a2e3f')

        star_sprites.draw(display_surface)
        greetings()
        display_best_score(best_score)

        pygame.display.update()

pygame.quit()
