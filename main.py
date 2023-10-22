import subprocess
import pygame
import sys
import random
import pygame.time

pygame.init()

WIDTH, HEIGHT = 800, 600
FPS = 60
TILE = 32
DIRECTION = [[0, -1], [1, 0], [0, 1], [-1, 0]]
transition_delay = 1000

window = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

fontUI = pygame.font.Font(None, 30)

imgBrick = pygame.image.load('brick.png')
img_player_tank = [
    pygame.image.load('player_tank1.png'),
    pygame.image.load('player_tank2.png'),
    pygame.image.load('player_tank3.png'),
]
imgBooms = [
    pygame.image.load('bang1.png'),
    pygame.image.load('bang2.png'),
    pygame.image.load('bang3.png'),
]
imgBase = pygame.image.load('base.png')

img_armor_block = pygame.image.load('block_armor.png')

img_enemy_tank = [
    pygame.image.load('tank1.png'),
    pygame.image.load('tank2.png'),
    pygame.image.load('tank3.png'),
    pygame.image.load('tank4.png'),
    pygame.image.load('tank5.png'),
    pygame.image.load('tank6.png'),
    pygame.image.load('tank7.png'),
    pygame.image.load('tank8.png'),
]
img_water_block = pygame.image.load('water.png')
img_bush_block = pygame.image.load('bush_block.png')
img_health_bonus = pygame.image.load('bonus_tank.png')
img_rank_bonus = pygame.image.load('bonus_star.png')
img_speed_bonus = pygame.image.load('bonus_speed.png')
img_ice_block = pygame.image.load('block_ice.png')

pygame.mixer_music.load('biscuit.mp3')
pygame.mixer_music.set_volume(0.05)
pygame.mixer_music.play(-1)

shot_sound = pygame.mixer.Sound('battle-city-sfx-6.mp3')
shot_sound.set_volume(0.2)


class Tank:
    def __init__(self, color, pos_x, pos_y, direct, key_list, hp, rank):
        objects.append(self)
        self.type = 'tank'
        self.color = color
        self.rect = pygame.Rect(pos_x, pos_y, TILE, TILE)
        self.direct = direct
        self.rank = rank
        self.move_speed = 2
        self.hp = hp
        self.shot_timer = 0
        self.shot_delay = 60
        self.bullet_speed = 5
        self.bullet_damage = 1
        self.max_hp = hp
        self.current_hp = hp
        self.key_left, self.key_right, self.key_up, self.key_down, self.key_shot = key_list

        self.image = pygame.transform.rotate(img_player_tank[self.rank], -self.direct * 90)
        self.rect = self.image.get_rect(center=self.rect.center)

        if self.rank == 1:
            self.move_speed = 2.5
            self.bullet_speed = 5.5

        if self.rank == 2:
            self.move_speed = 3
            self.bullet_speed = 6
            self.bullet_damage = 2

    def update(self):
        self.image = pygame.transform.rotate(img_player_tank[self.rank], -self.direct * 90)
        self.image = pygame.transform.scale(self.image, (self.image.get_width() - 5, self.image.get_height() - 5))
        self.rect = self.image.get_rect(center=self.rect.center)

        oldX, oldY = self.rect.topleft
        if keys[self.key_left] and self.rect.left > 0:
            self.rect.x -= self.move_speed
            self.direct = 3
        elif keys[self.key_right] and self.rect.right < WIDTH:
            self.rect.x += self.move_speed
            self.direct = 1
        elif keys[self.key_up] and self.rect.top > 0:
            self.rect.y -= self.move_speed
            self.direct = 0
        elif keys[self.key_down] and self.rect.bottom < HEIGHT:
            self.rect.y += self.move_speed
            self.direct = 2

        for obj in objects:
            if obj != self and (
                    obj.type == 'block' or obj.type == 'base' or obj.type == 'armor_block'
                    or obj.type == 'enemy' or obj.type == 'water_block') and self.rect.colliderect(obj.rect):
                self.rect.topleft = oldX, oldY

        for obj in enemy_tanks:
            if obj.type == 'enemy' and self.rect.colliderect(obj.rect):
                self.rect.topleft = oldX, oldY

        if keys[self.key_shot] and self.shot_timer == 0:
            shot_sound.play()
            dir_x = DIRECTION[self.direct][0] * self.bullet_speed
            dir_y = DIRECTION[self.direct][1] * self.bullet_speed
            Bullet(self, self.rect.centerx, self.rect.centery, dir_x, dir_y, self.bullet_damage)
            self.shot_timer = self.shot_delay

        if self.shot_timer > 0:
            self.shot_timer -= 1

    def draw(self):
        window.blit(self.image, self.rect)

        hp_bar_width = self.rect.width
        hp_bar_height = 5
        hp_bar_x = self.rect.left
        hp_bar_y = self.rect.bottom + 2
        hp_percentage = self.current_hp / self.max_hp

        if hp_percentage > 0:
            pygame.draw.rect(window, self.color, (hp_bar_x, hp_bar_y, hp_bar_width * hp_percentage, hp_bar_height))

    def damage(self, value):
        self.current_hp -= value
        if self.current_hp <= 0:
            self.current_hp = 0
            objects.remove(self)

    def health_up(self):
        self.max_hp += 1
        self.current_hp += 1

    def rank_up(self):
        self.rank += 1


class EnemyTank:
    def __init__(self, pos_x, pos_y, rank=0):
        self.current_hp = None
        self.type = 'enemy'
        self.rect = pygame.Rect(pos_x, pos_y, TILE, TILE)
        self.rank = rank
        self.move_speed = 1
        self.hp = 1
        self.shot_timer = 0
        self.shot_delay = 120

    def update(self):
        pass

    def draw(self):
        pass

    def damage(self, value):
        self.hp -= value
        if self.hp <= 0:
            self.current_hp = 0
            enemy_tanks.remove(self)


class SimpleEnemyTank(EnemyTank):
    def __init__(self, pos_x, pos_y, direct):
        super().__init__(pos_x, pos_y)
        self.direct = direct
        self.rank = 0
        self.move_direction = random.choice([0, 1, 2, 3])
        self.move_timer = random.randint(50, 150)
        self.shoot_timer = 50
        self.bullet_speed = 3
        self.bullet_damage = 1
        enemy_tanks.append(self)
        self.image = pygame.transform.rotate(img_enemy_tank[self.rank], -self.direct * 90)
        self.rect = self.image.get_rect(center=self.rect.center)

    def update(self):
        oldX, oldY = self.rect.topleft

        if self.move_timer <= 0:
            self.move_direction = random.choice([0, 1, 2, 3])
            self.move_timer = random.randint(50, 200)
        else:
            self.move_timer -= 1

        self.image = pygame.transform.rotate(img_enemy_tank[self.rank], -self.direct * 90)
        self.image = pygame.transform.scale(self.image, (self.image.get_width() - 5, self.image.get_height() - 5))
        self.rect = self.image.get_rect(center=self.rect.center)

        if self.move_direction == 3 and self.rect.left > 0:
            self.rect.x -= self.move_speed
            self.direct = 3
        elif self.move_direction == 1 and self.rect.right < WIDTH:
            self.rect.x += self.move_speed
            self.direct = 1
        elif self.move_direction == 0 and self.rect.top > 0:
            self.rect.y -= self.move_speed
            self.direct = 0
        elif self.move_direction == 2 and self.rect.bottom < HEIGHT:
            self.rect.y += self.move_speed
            self.direct = 2

        for obj in objects:
            collision_types = ('block', 'base', 'armor_block', 'tank', 'water_block')
            if obj != self and obj.type in collision_types and self.rect.colliderect(obj.rect):
                self.rect.topleft = oldX, oldY
        for obj in enemy_tanks:
            if obj != self and (obj.type == 'enemy') and self.rect.colliderect(obj.rect):
                self.rect.topleft = oldX, oldY

        if self.shoot_timer == 0:
            dir_x = DIRECTION[self.direct][0] * self.bullet_speed
            dir_y = DIRECTION[self.direct][1] * self.bullet_speed
            Bullet(self, self.rect.centerx, self.rect.centery, dir_x, dir_y, self.bullet_damage)
            self.shoot_timer = random.randint(90, 100)

        if self.shoot_timer > 0:
            self.shoot_timer -= 1

    def draw(self):
        self.image = pygame.transform.rotate(img_enemy_tank[self.rank], -self.direct * 90)
        self.image = pygame.transform.scale(self.image, (self.image.get_width() - 5, self.image.get_height() - 5))
        window.blit(self.image, self.rect)


class FastChasingTank(EnemyTank):
    def __init__(self, pos_x, pos_y, direct):
        super().__init__(pos_x, pos_y)
        self.direct = direct
        self.rank = 0
        self.move_direction = random.choice([0, 1, 2, 3])
        self.move_timer = random.randint(50, 150)
        self.shoot_timer = 50
        self.bullet_speed = 3
        self.bullet_damage = 1

        enemy_tanks.append(self)
        self.image = pygame.transform.rotate(img_enemy_tank[6], -self.direct * 90)
        self.rect = self.image.get_rect(center=self.rect.center)

    def update(self):
        player_tank = None
        for obj in objects:
            if obj.type == 'tank':
                player_tank = obj
                break

        oldX, oldY = self.rect.topleft

        if player_tank:
            target_x = player_tank.rect.centerx
            target_y = player_tank.rect.centery

            if target_y > self.rect.centery:
                self.rect.y += self.move_speed
                self.direct = 2
            elif target_x < self.rect.centerx:
                self.rect.x -= self.move_speed
                self.direct = 3
            elif target_x > self.rect.centerx:
                self.rect.x += self.move_speed
                self.direct = 1
            elif target_y < self.rect.centery:
                self.rect.y -= self.move_speed
                self.direct = 0

        for obj in objects:
            collision_types = ('block', 'base', 'armor_block', 'tank', 'water_block')
            if obj != self and obj.type in collision_types and self.rect.colliderect(obj.rect):
                self.rect.topleft = oldX, oldY

        for obj in enemy_tanks:
            if obj != self and (obj.type == 'enemy') and self.rect.colliderect(obj.rect):
                self.rect.topleft = oldX, oldY

        if self.shoot_timer == 0:
            dir_x = DIRECTION[self.direct][0] * self.bullet_speed
            dir_y = DIRECTION[self.direct][1] * self.bullet_speed
            Bullet(self, self.rect.centerx, self.rect.centery, dir_x, dir_y, self.bullet_damage)
            self.shoot_timer = random.randint(90, 100)

        if self.shoot_timer > 0:
            self.shoot_timer -= 1

    def draw(self):
        self.image = pygame.transform.rotate(img_enemy_tank[6], -self.direct * 90)
        self.image = pygame.transform.scale(self.image, (self.image.get_width() - 5, self.image.get_height() - 5))
        window.blit(self.image, self.rect)


class FastShootEnemyTank(EnemyTank):
    def __init__(self, pos_x, pos_y, direct):
        super().__init__(pos_x, pos_y)
        self.move_direction = None
        self.direction = None
        self.direct = direct
        self.rank = 0
        self.move_timer = random.randint(50, 200)
        self.shoot_timer = 60
        self.bullet_speed = 3
        self.bullet_damage = 1
        self.target_base = ((WIDTH - TILE) // 2, HEIGHT - TILE)
        enemy_tanks.append(self)
        self.image = pygame.transform.rotate(img_enemy_tank[7], -self.direct * 90)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.move_timer_base = 120
        self.move_timer_rand = 0

    def update(self):
        oldX, oldY = self.rect.topleft

        if self.move_timer_base > 0:
            target_x, target_y = self.target_base[0] - 5, self.target_base[1]

            if target_y > self.rect.centery:
                self.rect.y += self.move_speed
                self.direct = 2
            elif target_x < self.rect.centerx:
                self.rect.x -= self.move_speed
                self.direct = 3
            elif target_x > self.rect.centerx:
                self.rect.x += self.move_speed
                self.direct = 1
            elif target_y < self.rect.centery:
                self.rect.y -= self.move_speed
                self.direct = 0
            self.move_timer_base -= 1
            if self.move_timer_base == 0:
                self.move_timer_rand = 60
                self.direction = random.choice([0, 1, 2, 3])
        if self.move_timer_rand > 0:
            if self.direction == 3 and self.rect.left > 0:
                self.rect.x -= self.move_speed
                self.direct = 3
            elif self.direction == 1 and self.rect.right < WIDTH:
                self.rect.x += self.move_speed
                self.direct = 1
            elif self.direction == 0 and self.rect.top > 0:
                self.rect.y -= self.move_speed
                self.direct = 0
            elif self.direction == 2 and self.rect.bottom < HEIGHT:
                self.rect.y += self.move_speed
                self.direct = 2
            self.move_timer_rand -= 1
            if self.move_timer_rand == 0:
                self.move_timer_base = 120

        for obj in objects:
            collision_types = ('block', 'base', 'armor_block', 'tank', 'water_block')
            if obj != self and (obj.type in collision_types) and self.rect.colliderect(obj.rect):
                self.rect.topleft = oldX, oldY

        for obj in enemy_tanks:
            if obj != self and (obj.type == 'enemy') and self.rect.colliderect(obj.rect):
                self.rect.topleft = oldX, oldY

        if self.shoot_timer == 0:
            dir_x = DIRECTION[self.direct][0] * self.bullet_speed
            dir_y = DIRECTION[self.direct][1] * self.bullet_speed
            Bullet(self, self.rect.centerx, self.rect.centery, dir_x, dir_y, self.bullet_damage)
            self.shoot_timer = 60

        if self.shoot_timer > 0:
            self.shoot_timer -= 1

        if self.shoot_timer > 0:
            self.shoot_timer -= 1

    def randomize_direction(self):
        self.move_direction = random.choice([0, 1, 2, 3])

    def draw(self):
        self.image = pygame.transform.rotate(img_enemy_tank[4], -self.direct * 90)
        self.image = pygame.transform.scale(self.image, (self.image.get_width() - 5, self.image.get_height() - 5))
        window.blit(self.image, self.rect)


class Bullet:
    def __init__(self, from_who, pos_x, pos_y, dir_x, dir_y, damage):
        bullets.append(self)
        self.from_who = from_who
        self.pos_x, self.pos_y = pos_x, pos_y
        self.dir_x, self.dir_y = dir_x, dir_y
        self.damage = damage

    def update(self):
        self.pos_x += self.dir_x
        self.pos_y += self.dir_y

        if self.pos_x < 0 or self.pos_x > WIDTH or self.pos_y < 0 or self.pos_y > HEIGHT:
            bullets.remove(self)
        else:
            for obj in objects:
                collision_types = ('boom', 'water_block', 'bush_block', 'bonus')
                if obj != self.from_who and obj.type not in collision_types\
                        and obj.rect.collidepoint(self.pos_x, self.pos_y):
                    if obj.type == "armor_block":
                        if self.from_who.rank >= 1:
                            objects.remove(obj)
                    else:
                        obj.damage(self.damage)
                    bullets.remove(self)
                    big_boom(self.pos_x, self.pos_y)
                    break
            for obj in enemy_tanks:
                if obj != self.from_who and obj.type != 'boom' and obj.rect.collidepoint(self.pos_x, self.pos_y):
                    if self.from_who.type != 'enemy':
                        obj.damage(self.damage)
                        big_boom(self.pos_x, self.pos_y)
                    bullets.remove(self)
                    break

    def draw(self):
        pygame.draw.circle(window, 'white', (self.pos_x, self.pos_y), 2)


class Block:
    def __init__(self, pos_x, pos_y, size):
        objects.append(self)
        self.type = 'block'
        self.rect = pygame.Rect(pos_x, pos_y, size, size)
        self.hp = 1

    def update(self):
        pass

    def draw(self):
        window.blit(imgBrick, self.rect)

    def damage(self, value):
        self.hp -= value
        if self.hp <= 0:
            objects.remove(self)


class ConcreteBlock:
    def __init__(self, pos_x, pos_y, size):
        objects.append(self)
        self.rect = pygame.Rect(pos_x, pos_y, size, size)
        self.type = 'armor_block'

    def update(self):
        pass

    def draw(self):
        window.blit(img_armor_block, self.rect)


class WaterBlock:
    def __init__(self, pos_x, pos_y, size):
        objects.append(self)
        self.type = 'water_block'
        self.rect = pygame.Rect(pos_x, pos_y, size, size)

    def update(self):
        pass

    def draw(self):
        window.blit(img_water_block, self.rect)

    def damage(self, value):
        pass


def draw():
    i = 0
    for obj in objects:
        if obj.type == 'tank':
            pygame.draw.rect(window, obj.color, (5 + i * 70, 5, 22, 22))
            text = fontUI.render(str(obj.current_hp), 1, obj.color)
            rect = text.get_rect(center=(5 + i * 70 + 32, 5 + 11))
            window.blit(text, rect)
            i += 1


class UI:
    def __init__(self):
        pass

    def update(self):
        pass


class Base:
    def __init__(self, pos_x, pos_y, size):
        objects.append(self)
        self.type = 'base'
        self.rect = pygame.Rect(pos_x, pos_y, size, size)
        self.hp = 1

    def update(self):
        pass

    def draw(self):
        window.blit(imgBase, self.rect)

    def damage(self, value):
        self.hp -= value
        if self.hp <= 0:
            objects.remove(self)


class BushBlock(Block):
    def __init__(self, pos_x, pos_y, size):
        super().__init__(pos_x, pos_y, size)
        self.type = 'bush_block'

    def draw(self):
        window.blit(img_bush_block, self.rect)


class HealthBonus:
    def __init__(self, pos_x, pos_y):
        objects.append(self)
        self.type = 'bonus'
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.rect = pygame.Rect(pos_x, pos_y, TILE, TILE)

    def update(self):
        for obj in objects:
            if obj.type == 'tank' and obj.rect.colliderect(self.rect):
                obj.health_up()
                objects.remove(self)
                break

    def draw(self):
        window.blit(img_health_bonus, self.rect)


class LVLBonus:
    def __init__(self, pos_x, pos_y):
        objects.append(self)
        self.type = 'bonus'
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.rect = pygame.Rect(pos_x, pos_y, TILE, TILE)

    def update(self):
        for obj in objects:
            if obj.type == 'tank' and obj.rect.colliderect(self.rect):
                obj.rank_up()
                objects.remove(self)
                break

    def draw(self):
        window.blit(img_rank_bonus, self.rect)


class SpeedBonus:
    def __init__(self, pos_x, pos_y):
        objects.append(self)
        self.type = 'bonus'
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.rect = pygame.Rect(pos_x, pos_y, TILE, TILE)

    def update(self):
        for obj in objects:
            if obj.type == 'tank' and obj.rect.colliderect(self.rect):
                obj.move_speed *= 1.5
                objects.remove(self)
                break

    def draw(self):
        window.blit(img_speed_bonus, self.rect)


class big_boom:
    def __init__(self, pos_x, pos_y):
        objects.append(self)
        self.type = 'boom'

        self.pos_x, self.pos_y = pos_x, pos_y
        self.frame = 0

    def update(self):
        self.frame += 0.15
        if self.frame >= 3:
            objects.remove(self)

    def draw(self):
        image = imgBooms[int(self.frame)]
        rect = image.get_rect(center=(self.pos_x, self.pos_y))
        window.blit(image, rect)


def show_menu():
    global number_players
    font = pygame.font.Font(None, 36)
    text = font.render("Выберите количество игроков. Нажмите 1 или 2:", True, (255, 255, 255))
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    window.blit(text, text_rect)
    pygame.display.flip()

    while number_players is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.unicode == '1':
                    number_players = 1
                elif event.unicode == '2':
                    number_players = 2


def find_free_coord():
    x = random.randint(0, WIDTH // TILE - 1) * TILE
    y = random.randint(1, HEIGHT // TILE - 1) * TILE
    rect = pygame.Rect(x, y, TILE, TILE)
    fined = False
    for obj in objects:
        if rect.colliderect(obj.rect):
            fined = True
    return x, y, fined


def setup_level_1(number_players):
    clear_objects()
    if number_players == 1:
        Tank('blue', 250, 560, 0, (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_SPACE), tank1_hp,
             tank1_rank)
    if number_players == 2:
        Tank('blue', 250, 560, 0, (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_SPACE), tank1_hp,
             tank1_rank)
        Tank('red', 525, 560, 0, (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_KP_ENTER),
             tank2_hp, tank2_rank)

    Base((WIDTH - TILE) // 2 - TILE, HEIGHT - TILE, TILE)

    Block((WIDTH - TILE) // 2 - TILE * 2, HEIGHT - TILE, TILE)
    Block((WIDTH - TILE) // 2, HEIGHT - TILE, TILE)
    Block((WIDTH - TILE) // 2 - TILE * 2, HEIGHT - TILE - TILE, TILE)
    Block((WIDTH - TILE) // 2, HEIGHT - TILE - TILE, TILE)
    Block((WIDTH - TILE) // 2 - TILE, HEIGHT - TILE - TILE, TILE)

    ConcreteBlock(96, 192, TILE), ConcreteBlock(96, 192, TILE), ConcreteBlock(64, 192, TILE), ConcreteBlock(
        64, 224, TILE)
    ConcreteBlock(64, 256, TILE), ConcreteBlock(64, 288, TILE), ConcreteBlock(64, 320, TILE), ConcreteBlock(
        96, 288, TILE)
    ConcreteBlock(32, 288, TILE), ConcreteBlock(64, 352, TILE), ConcreteBlock(320, 192, TILE), ConcreteBlock(
        320, 256, TILE)
    ConcreteBlock(320, 288, TILE), ConcreteBlock(320, 320, TILE), ConcreteBlock(320, 352, TILE), ConcreteBlock(
        416, 192, TILE)
    ConcreteBlock(416, 256, TILE), ConcreteBlock(704, 256, TILE), ConcreteBlock(416, 288, TILE), ConcreteBlock(
        416, 320, TILE)
    ConcreteBlock(416, 352, TILE), ConcreteBlock(704, 352, TILE), ConcreteBlock(704, 320, TILE), ConcreteBlock(
        704, 288, TILE)
    ConcreteBlock(704, 224, TILE), ConcreteBlock(736, 192, TILE), ConcreteBlock(672, 192, TILE), ConcreteBlock(
        704, 192, TILE)

    SimpleEnemyTank(30, 0, 0)

    for _ in range(60):
        while True:
            params = find_free_coord()
            if not params[2]:
                break
        Block(params[0], params[1], TILE)

    while True:
        params = find_free_coord()
        if not params[2]:
            break
    SpeedBonus(params[0], params[1])

    while True:
        params = find_free_coord()
        if not params[2]:
            break
    HealthBonus(params[0], params[1])


def setup_level_2(number_players):
    clear_objects()
    if number_players == 1:
        Tank('blue', 250, 560, 0, (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_SPACE), tank1_hp,
             tank1_rank)
    if number_players == 2:
        Tank('blue', 250, 560, 0, (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_SPACE), tank1_hp,
             tank1_rank)
        Tank('red', 525, 560, 0, (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_KP_ENTER),
             tank2_hp, tank2_rank)

    Base((WIDTH - TILE) // 2 - TILE, HEIGHT - TILE, TILE)

    Block((WIDTH - TILE) // 2 - TILE * 2, HEIGHT - TILE, TILE)
    Block((WIDTH - TILE) // 2, HEIGHT - TILE, TILE)
    Block((WIDTH - TILE) // 2 - TILE * 2, HEIGHT - TILE - TILE, TILE)
    Block((WIDTH - TILE) // 2, HEIGHT - TILE - TILE, TILE)
    Block((WIDTH - TILE) // 2 - TILE, HEIGHT - TILE - TILE, TILE)

    WaterBlock(320, 320, TILE), WaterBlock(352, 320, TILE), WaterBlock(384, 320, TILE), WaterBlock(416, 320, TILE)
    WaterBlock(288, 320, TILE), WaterBlock(320, 320, TILE), WaterBlock(160, 256, TILE), WaterBlock(128, 256, TILE)
    WaterBlock(96, 256, TILE), WaterBlock(64, 256, TILE), WaterBlock(544, 256, TILE), WaterBlock(576, 256, TILE)
    WaterBlock(608, 256, TILE), WaterBlock(640, 256, TILE), ConcreteBlock(416, 128, TILE), ConcreteBlock(384, 128,
                                                                                                         TILE)
    ConcreteBlock(352, 128, TILE), ConcreteBlock(320, 128, TILE), ConcreteBlock(288, 128, TILE), ConcreteBlock(
        0, 384, TILE)
    ConcreteBlock(32, 384, TILE), ConcreteBlock(64, 384, TILE), ConcreteBlock(768, 288, TILE), ConcreteBlock(
        736, 288, TILE)

    FastShootEnemyTank(750, 0, 0)
    SimpleEnemyTank(30, 0, 0)

    for _ in range(60):
        while True:
            params = find_free_coord()
            if not params[2]:
                break
        Block(params[0], params[1], TILE)

    while True:
        params = find_free_coord()
        if not params[2]:
            break
    LVLBonus(params[0], params[1])

    while True:
        params = find_free_coord()
        if not params[2]:
            break
    HealthBonus(params[0], params[1])


def setup_level_3(number_players):
    clear_objects()
    if number_players == 1:
        Tank('blue', 250, 560, 0, (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_SPACE), tank1_hp,
             tank1_rank)
    if number_players == 2:
        Tank('blue', 250, 560, 0, (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_SPACE), tank1_hp,
             tank1_rank)
        Tank('red', 525, 560, 0, (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_KP_ENTER),
             tank2_hp, tank2_rank)

    Base((WIDTH - TILE) // 2 - TILE, HEIGHT - TILE, TILE)

    Block((WIDTH - TILE) // 2 - TILE * 2, HEIGHT - TILE, TILE)
    Block((WIDTH - TILE) // 2, HEIGHT - TILE, TILE)
    Block((WIDTH - TILE) // 2 - TILE * 2, HEIGHT - TILE - TILE, TILE)
    Block((WIDTH - TILE) // 2, HEIGHT - TILE - TILE, TILE)
    Block((WIDTH - TILE) // 2 - TILE, HEIGHT - TILE - TILE, TILE)

    SimpleEnemyTank(30, 0, 0)

    for _ in range(40):
        while True:
            params = find_free_coord()
            if not params[2]:
                break
        Block(params[0], params[1], TILE)

    for _ in range(40):
        while True:
            params = find_free_coord()
            if not params[2]:
                break
        BushBlock(params[0], params[1], TILE)

    while True:
        params = find_free_coord()
        if not params[2]:
            break
    LVLBonus(params[0], params[1])


def setup_level_4(number_players):
    clear_objects()
    if number_players == 1:
        Tank('blue', 250, 560, 0, (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_SPACE), tank1_hp,
             tank1_rank)
    if number_players == 2:
        Tank('blue', 250, 560, 0, (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_SPACE), tank1_hp,
             tank1_rank)
        Tank('red', 525, 560, 0, (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_KP_ENTER),
             tank2_hp, tank2_rank)

    Base((WIDTH - TILE) // 2 - TILE, HEIGHT - TILE, TILE)

    Block((WIDTH - TILE) // 2 - TILE * 2, HEIGHT - TILE, TILE)
    Block((WIDTH - TILE) // 2, HEIGHT - TILE, TILE)
    Block((WIDTH - TILE) // 2 - TILE * 2, HEIGHT - TILE - TILE, TILE)
    Block((WIDTH - TILE) // 2, HEIGHT - TILE - TILE, TILE)
    Block((WIDTH - TILE) // 2 - TILE, HEIGHT - TILE - TILE, TILE)

    enemy = SimpleEnemyTank(30, 0, 0)
    enemy.rank = 7
    enemy.hp = 2

    for _ in range(20):
        while True:
            params = find_free_coord()
            if not params[2]:
                break
        WaterBlock(params[0], params[1], TILE)

    for _ in range(20):
        while True:
            params = find_free_coord()
            if not params[2]:
                break
        ConcreteBlock(params[0], params[1], TILE)

    for _ in range(20):
        while True:
            params = find_free_coord()
            if not params[2]:
                break
        Block(params[0], params[1], TILE)

    for _ in range(10):
        while True:
            params = find_free_coord()
            if not params[2]:
                break
        BushBlock(params[0], params[1], TILE)

    for i in range(2):
        while True:
            params = find_free_coord()
            if not params[2]: break
        HealthBonus(params[0], params[1])


def clear_objects():
    global objects, bullets, enemy_tanks
    objects = []
    bullets = []
    enemy_tanks = []


def show_game_over_menu():
    global base_exist
    font = pygame.font.Font(None, 36)
    if not base_exist:
        text = font.render("Игра завершена (база сломана). Нажмите Q для выхода.", True, (255, 0, 0))
    else:
        text = font.render("Игра завершена (танки уничтожены). Нажмите Q для выхода.", True, (255, 0, 0))
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    window.blit(text, text_rect)
    pygame.display.flip()

    game_over = True
    while game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()


levels = [setup_level_1, setup_level_2, setup_level_3, setup_level_4]
current_level = 0
is_first_level = False

tank1_hp = 3
tank2_hp = 3
tank1_rank = 0
tank2_rank = 0


def spawn_tanks_0_lvl():
    for obj in enemy_tanks:
        x = random.randint(30, 770)
        rect = pygame.Rect(x, 0, TILE, TILE)
        if not rect.colliderect(obj.rect) and obj.type != 'boom':
            SimpleEnemyTank(rect.x, 0, 0)
            break


def spawn_tanks_1_lvl():
    for obj in enemy_tanks:
        x = random.randint(30, 770)
        rect = pygame.Rect(x, 0, TILE, TILE)
        if not rect.colliderect(obj.rect) and obj.type != 'boom':
            SimpleEnemyTank(rect.x, 0, 0)
            break

    for obj in enemy_tanks:
        x = random.randint(30, 770)
        rect = pygame.Rect(x, 0, TILE, TILE)
        if not rect.colliderect(obj.rect) and obj.type != 'boom':
            tank = FastShootEnemyTank(rect.x, 0, 0)
            tank.rank = 0
            break


def spawn_tanks_2_lvl():
    for obj in enemy_tanks:
        x = random.randint(30, 770)
        rect = pygame.Rect(x, 0, TILE, TILE)
        if not rect.colliderect(obj.rect) and obj.type != 'boom':
            FastChasingTank(rect.x, 0, 0)
            break

    for obj in enemy_tanks:
        x = random.randint(30, 770)
        rect = pygame.Rect(x, 0, TILE, TILE)
        if not rect.colliderect(obj.rect) and obj.type != 'boom':
            SimpleEnemyTank(rect.x, 0, 0)
            break


def spawn_tanks_3_lvl():
    for obj in enemy_tanks:
        x = random.randint(30, 770)
        rect = pygame.Rect(x, 0, TILE, TILE)
        if not rect.colliderect(obj.rect) and obj.type != 'boom':
            tank = SimpleEnemyTank(rect.x, 0, 0)
            tank.hp = 2
            tank.rank = 7
            tank.bullet_damage = 2
            break

    for obj in enemy_tanks:
        x = random.randint(30, 770)
        rect = pygame.Rect(x, 0, TILE, TILE)
        if not rect.colliderect(obj.rect) and obj.type != 'boom':
            FastShootEnemyTank(rect.x, 0, 0)
            break


def pause_menu():
    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    paused = False

        font = pygame.font.Font(None, 36)
        text = font.render("Пауза", True, (255, 255, 255))
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        instruction = font.render("Нажмите Enter для продолжения", True, (255, 255, 255))
        instruction_rect = instruction.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        window.blit(text, text_rect)
        window.blit(instruction, instruction_rect)
        pygame.display.update()


def show_congratulations_menu():
    global is_first_level, current_level, count_enemy_tanks_on_lvl

    menu_font = pygame.font.Font(None, 36)
    text = menu_font.render("Поздравляем! Вы прошли игру!", True, (255, 255, 255))
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))

    start_again_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50)
    start_again_text = menu_font.render("Начать заново", True, (0, 0, 0))
    start_again_text_rect = start_again_text.get_rect(center=start_again_button.center)

    close_game_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 100, 200, 50)
    close_game_text = menu_font.render("Закрыть игру", True, (0, 0, 0))
    close_game_text_rect = close_game_text.get_rect(center=close_game_button.center)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_again_button.collidepoint(event.pos):
                    subprocess.Popen([sys.executable, "main.py"], creationflags=subprocess.CREATE_NEW_CONSOLE)
                    sys.exit()
                elif close_game_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

        window.fill((0, 0, 0))
        pygame.draw.rect(window, (255, 255, 255), start_again_button)
        pygame.draw.rect(window, (255, 255, 255), close_game_button)

        window.blit(text, text_rect)
        window.blit(start_again_text, start_again_text_rect)
        window.blit(close_game_text, close_game_text_rect)

        pygame.display.update()


def main():
    global objects, bullets, enemy_tanks, number_players, keys, current_level, is_first_level, tank1_hp, tank2_hp, tank1_rank, tank2_rank, base_exist

    number_players = None
    enemy_tanks = []
    objects = []
    bullets = []
    ui = UI()
    spawn_timer = 250
    count_enemy_tanks_on_lvl = [0, 0, 0, 0]
    paused = False

    show_menu()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = not paused
                    if paused:
                        pause_menu()
                if event.key == pygame.K_1:
                    current_level = 0
                    levels[current_level](number_players)
                elif event.key == pygame.K_2:
                    current_level = 1
                    levels[current_level](number_players)
                elif event.key == pygame.K_3:
                    current_level = 2
                    levels[current_level](number_players)
                elif event.key == pygame.K_4:
                    current_level = 3
                    levels[current_level](number_players)
                elif event.key == pygame.K_5:
                    for obj in objects:
                        if obj.type == "tank":
                            obj.current_hp += 1

        spawn_timer -= 1
        if spawn_timer <= 0:
            if current_level == 0 and count_enemy_tanks_on_lvl[0] < 5:
                spawn_tanks_0_lvl()
                count_enemy_tanks_on_lvl[0] += 1
                spawn_timer = 300
            if current_level == 1 and count_enemy_tanks_on_lvl[1] < 4:
                spawn_tanks_1_lvl()
                count_enemy_tanks_on_lvl[1] += 1
                spawn_timer = 400
            if current_level == 2 and count_enemy_tanks_on_lvl[2] < 4:
                spawn_tanks_2_lvl()
                count_enemy_tanks_on_lvl[2] += 1
                spawn_timer = 400
            if current_level == 3 and count_enemy_tanks_on_lvl[3] < 5:
                spawn_tanks_3_lvl()
                count_enemy_tanks_on_lvl[3] += 1
                spawn_timer = 400

        keys = pygame.key.get_pressed()

        for bullet in bullets:
            bullet.update()
        for obj in objects:
            obj.update()
        for enemy_tank in enemy_tanks:
            enemy_tank.update()
        ui.update()

        window.fill('black')

        for obj in objects:
            if obj.type != "bush_block":
                obj.draw()
        for bullet in bullets:
            bullet.draw()

        for enemy_tank in enemy_tanks:
            enemy_tank.draw()

        for obj in objects:
            if obj.type == "bush_block":
                obj.draw()

        draw()

        if not is_first_level:
            levels[current_level](number_players)
            is_first_level = True

        enemy_exist = any(obj.type == 'enemy' for obj in enemy_tanks)
        base_exist = any(obj.type == 'base' for obj in objects)
        tank_exist = any(obj.type == 'tank' for obj in objects)

        if not enemy_exist and current_level == 3:
            show_congratulations_menu()

        if not enemy_exist:
            current_level += 1
            if current_level < len(levels):
                pygame.time.delay(transition_delay)
                levels[current_level](number_players)

        if not base_exist:
            show_game_over_menu()

        if not tank_exist:
            show_game_over_menu()

        for obj in objects:
            if obj.type == 'tank':
                if obj.color == 'blue':
                    tank1_hp = obj.current_hp
                    tank1_rank = obj.rank
                elif obj.color == 'red':
                    tank2_hp = obj.current_hp
                    tank2_rank = obj.rank

        pygame.display.update()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
