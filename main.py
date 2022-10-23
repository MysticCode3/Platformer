import pygame
from pygame import *
import Bullet
import random


def load_map(path):
    f = open(path + '.txt', 'r')
    data = f.read()
    f.close()
    data = data.split('\n')
    game_map = []
    for row in data:
        game_map.append(list(row))
    return game_map


def collision_test(rect, tiles):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)

    return hit_list


def move(rect, movement, tiles):
    collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}

    rect.x += movement[0]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[0] > 0:
            rect.right = tile.left
            collision_types['right'] = True
        elif movement[0] < 0:
            rect.left = tile.right
            collision_types['left'] = True
    rect.y += movement[1]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_types['bottom'] = True
        elif movement[1] < 0:
            rect.top = tile.bottom
            collision_types['top'] = True

    return rect, collision_types


def render_fog():
    fog.blit(light_mask, (400, 225))
    screen.blit(fog, (0, 0), special_flags=pygame.BLEND_MULT)


def load_animation(path, frame_duration):
    global slice_animation_frames
    animation_name = path.split('/')[-1]
    animation_frame_data = []
    n = 1
    for frame in frame_duration:
        animation_frame_id = animation_name + '_' + str(n)
        img_loc = path + '/' + animation_frame_id + '.png'
        print(img_loc)
        animation_image = pygame.image.load(img_loc)
        slice_animation_frames[animation_frame_id] = animation_image.copy()
        for i in range(frame):
            animation_frame_data.append(animation_frame_id)
        n += 1
    return animation_frame_data

def circle_surf(radius, color):
    surf = pygame.Surface((radius *2, radius * 2))
    pygame.draw.circle(surf, color, (radius, radius), radius)
    surf.set_colorkey((0, 0, 0))
    return surf

# Window Size
WINDOW_SIZE = (1350, 900)
# WINDOW_SIZE = (1920, 1080)

# Display
display = pygame.Surface((450, 300))
background_color = (25, 25, 51)

# Multiply Number
multiply_number = WINDOW_SIZE[0] / display.get_width()

# Animations
# slice_animation_frames = {}
# animation_database = {}
# animation_database['slice'] = load_animation('slash', [1, 1, 1, 1, 1, 1])
# slice_frame = 0
# slice_animation = False
# slice_duration = 3

# Import Images
player_img = pygame.image.load("player_1.png")
player_left_img = pygame.image.load("player_1_left.png")
grass_img = pygame.image.load("grass_1.png")
grass_facing_right_img = pygame.image.load("grass_facing_right.png")
grass_facing_left_img = pygame.image.load("grass_facing_left.png")
grass_right_img = pygame.image.load("grass_right.png")
grass_left_img = pygame.image.load("grass_left.png")
dirt_img = pygame.image.load("dirt_1.png")
water_img = pygame.image.load('water.png')
whole_water_img = pygame.image.load('whole_water.png')
light_mask = pygame.image.load("light_350_med.png")
enemy_tower = pygame.image.load("enemy_tower.png")
score_border = pygame.image.load("score_border_2.png")
torch_right = pygame.image.load("torch_right.png")
torch_left = pygame.image.load("torch_left.png")

# Dark Effect
dark_color = (15, 15, 15)
fog = pygame.Surface((WINDOW_SIZE[0], WINDOW_SIZE[1]))
light_radius = (550, 550)
light_mask = pygame.transform.scale(light_mask, light_radius)

# Read game map from txt
game_map = load_map('map_2')

# Tile Size
TILE_SIZE = 16

# Player
player_y_momentum = 0
moving_right = False
moving_left = False
air_timer = 0
defend = False
defend_timer = 40

player_direction = 'right'

player_rect = pygame.Rect(300, 300, player_img.get_width(), player_img.get_height())
defend_rect = None

health = 100

# Cursor
cx, cy = 0, 0

# Scroll
true_scroll = [0, 0]
scroll = [0, 0]

# Enemy
enemy_list = []
enemy_timer = 20
did_shoot = False

# Bullet
bullet_list = []
bullet_player_list = []

#Points
points = 0

#Torch
torch_radius = 23
torch_change = 0

pygame.init()
#print(pygame.display.Info().current_w, pygame.display.Info().current_h)
screen = pygame.display.set_mode((WINDOW_SIZE[0], WINDOW_SIZE[1]))
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            # slice_animation = True
            cx, cy = pygame.mouse.get_pos()
            bullet_player_list.append(Bullet.bullet_class(player_rect.x + player_rect.width/2, player_rect.y + player_rect.height/2, cx/multiply_number + scroll[0], cy/multiply_number + scroll[1], 2))
            if defend_timer == 40:
                pass
                #defend = True
            print(cx, cy)
        if event.type == KEYDOWN:
            if event.key == K_d:
                moving_right = True
                player_direction = 'right'
            if event.key == K_a:
                moving_left = True
                player_direction = 'left'
            if event.key == K_w or event.key == K_SPACE:
                if air_timer < 6:
                    player_y_momentum = -5
        if event.type == KEYUP:
            if event.key == K_d:
                moving_right = False
            if event.key == K_a:
                moving_left = False

    # Displays, Surfaces
    display.fill(background_color)
    fog.fill(dark_color)

    # Font
    font = pygame.font.SysFont("comicsansms", 50)
    font_small = pygame.font.SysFont("comicsansms", 20)

    # Scroll
    true_scroll[0] += (player_rect.x - true_scroll[0] - display.get_width() / 2) / 20
    true_scroll[1] += (player_rect.y - true_scroll[1] - display.get_height() / 2) / 20
    scroll = true_scroll.copy()
    scroll[0] = int(scroll[0])
    scroll[1] = int(scroll[1])

    # Render The Ground
    tile_rects = []
    y = 0
    for row in game_map:
        x = 0
        for tile in row:
            if tile == '1':
                display.blit(dirt_img, (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))
            if tile == '2':
                display.blit(grass_img, (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))
            if tile == '3':
                display.blit(grass_right_img, (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))
            if tile == '4':
                display.blit(grass_left_img, (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))
            if tile == '5':
                display.blit(torch_right, (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))
            if tile == '6':
                display.blit(torch_left, (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))
            if tile == '5' or tile == '6':
                display.blit(circle_surf(5, (44, 49, 15)), (x * TILE_SIZE - scroll[0] + 4, y * TILE_SIZE - scroll[1] - 3), special_flags=BLEND_RGB_ADD)
                display.blit(circle_surf(12, (44, 49, 15)), (x * TILE_SIZE - scroll[0] - 3, y * TILE_SIZE - scroll[1] - 10), special_flags=BLEND_RGB_ADD)
                display.blit(circle_surf(torch_radius, (44, 49, 15)), (x * TILE_SIZE - scroll[0] - (torch_radius-9), y * TILE_SIZE - scroll[1] - (torch_radius-2)), special_flags=BLEND_RGB_ADD)
            # Enemy
            if tile == '7':
                #pygame.draw.rect(display, (255, 0, 0),
                                 #(x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1], TILE_SIZE, TILE_SIZE))
                enemy_list.append(
                    pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            if tile == '8':
                display.blit(grass_facing_right_img, (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))
            if tile == '9':
                display.blit(grass_facing_left_img, (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))
            if tile != '0' and tile != '5' and tile != '6' and tile != '7':
                tile_rects.append(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            x += 1
        y += 1

    # Player
    player_movement = [0, 0]
    if moving_right:
        player_movement[0] += 2
    if moving_left:
        player_movement[0] -= 2
    player_movement[1] += player_y_momentum
    player_y_momentum += 0.2
    if player_y_momentum > 5:
        player_y_momentum = 5

    if player_direction == 'right':
        display.blit(player_img, (player_rect.x - scroll[0], player_rect.y - scroll[1]))
    else:
        display.blit(player_left_img, (player_rect.x - scroll[0], player_rect.y - scroll[1]))

    player_rect, collisions = move(player_rect, player_movement, tile_rects)
    if collisions['bottom']:
        player_y_momentum = 0
        air_timer = 0
    else:
        air_timer += 1
    if collisions['top']:
        player_y_momentum = 0

    if defend:
        pygame.draw.circle(display, (255, 255, 255), (player_rect.x - scroll[0] + player_rect.width / 2, player_rect.y - scroll[1] + player_rect.height / 2), 25, 1)
        display.blit(circle_surf(28, (20, 20, 20)), (player_rect.x - scroll[0] + player_rect.width / 2 - 28, player_rect.y - scroll[1] + player_rect.height / 2 - 28), special_flags=BLEND_RGB_ADD)
        defend_timer -= 0.5

    if defend_timer <= 0:
        defend = False
        defend_timer = 40

    defend_rect = pygame.Rect(player_rect.x - player_rect.width / 2, player_rect.y - player_rect.height / 2, 50, 50)

    for bullet in bullet_player_list:
        pygame.draw.circle(display, (17, 103, 177), (bullet.x - scroll[0], bullet.y - scroll[1]), 2)
        display.blit(circle_surf(3, (20, 20, 40)), (bullet.x - scroll[0] - 3, bullet.y - scroll[1] - 3), special_flags=BLEND_RGB_ADD)
        display.blit(circle_surf(6, (20, 20, 40)), (bullet.x - scroll[0] - 6, bullet.y - scroll[1] - 6), special_flags=BLEND_RGB_ADD)
        display.blit(circle_surf(9, (20, 20, 40)), (bullet.x - scroll[0] - 9, bullet.y - scroll[1] - 9), special_flags=BLEND_RGB_ADD)
        display.blit(circle_surf(12, (20, 20, 40)), (bullet.x - scroll[0] - 12, bullet.y - scroll[1] - 12), special_flags=BLEND_RGB_ADD)
        bullet.update()
        for enemy in enemy_list:
            if bullet.rect.colliderect(enemy):
                points += 1
        if bullet.x < 0 or bullet.x > WINDOW_SIZE[0]:
            bullet_player_list.remove(bullet)
        if bullet.y < 0 or bullet.y > WINDOW_SIZE[1]:
            bullet_player_list.remove(bullet)

    # Enemy
    for enemy in enemy_list:
        if defend:
            if enemy.colliderect(defend_rect):
                points += 1
        display.blit(enemy_tower, (enemy.x - scroll[0], enemy.y - scroll[1]))
        if enemy_timer == 20:
            did_shoot = True
            bullet_list.append(
                Bullet.bullet_class(enemy.x + TILE_SIZE/2, enemy.y + TILE_SIZE/2, player_rect.x + player_rect.width/2, player_rect.y + player_rect.height/2, 2))

    if did_shoot:
        enemy_timer -= 0.2

    if enemy_timer <= 0:
        did_shoot = False
        enemy_timer = 20
        enemy_list.clear()

    for bullet in bullet_list:
        pygame.draw.circle(display, (255, 255, 255), (bullet.x - scroll[0], bullet.y - scroll[1]), 2)
        display.blit(circle_surf(3, (20, 20, 20)), (bullet.x - scroll[0] - 3, bullet.y - scroll[1] - 3), special_flags=BLEND_RGB_ADD)
        display.blit(circle_surf(6, (20, 20, 20)), (bullet.x - scroll[0] - 6, bullet.y - scroll[1] - 6), special_flags=BLEND_RGB_ADD)
        display.blit(circle_surf(9, (20, 20, 20)), (bullet.x - scroll[0] - 9, bullet.y - scroll[1] - 9), special_flags=BLEND_RGB_ADD)
        display.blit(circle_surf(12, (20, 20, 20)), (bullet.x - scroll[0] - 12, bullet.y - scroll[1] - 12), special_flags=BLEND_RGB_ADD)
        bullet.update()
        if defend:
            if bullet.rect.colliderect(defend_rect):
                bullet_list.remove(bullet)
        else:
            if bullet.rect.colliderect(player_rect):
                bullet_list.remove(bullet)
                health -= 5
        if bullet.x < 0 or bullet.x > WINDOW_SIZE[0]:
            bullet_list.remove(bullet)
        if bullet.y < 0 or bullet.y > WINDOW_SIZE[1]:
            bullet_list.remove(bullet)

    # Slice Animation/Sword Animation
    """if slice_animation:
        slice_frame += 1
        if slice_frame >= len(animation_database['slice']):
            slice_frame = 0
            slice_duration -= 1
        slice_img_id = animation_database['slice'][slice_frame]
        slice_img = slice_animation_frames[slice_img_id]
        display.blit(slice_img, (player_rect.x - scroll[0] + 4, player_rect.y - scroll[1]))
        if slice_duration <= 0:
            slice_animation = False

    if slice_animation == False:
        slice_duration = 3"""

    # Player Health Bar
    pygame.draw.rect(display, (203, 247, 161), (14, 21, 100, 16))
    pygame.draw.rect(display, (1, 200, 32), (14, 21, health, 16))
    display.blit(score_border, (10, 10))

    #Torch
    if torch_change == 0:
        if torch_radius < 27:
            torch_radius += 0.3
    else:
        if torch_radius > 19:
            torch_radius -= 0.3
    torch_change = random.randint(0, 1)

    # Render half size surface
    surf = pygame.transform.scale(display, WINDOW_SIZE)
    screen.blit(surf, (0, 0))

    # Draw dark effect
    # render_fog()

    #Draw Points
    points_text = font.render(str(points), True, (173, 216, 230))
    screen.blit(points_text, (WINDOW_SIZE[0]/2 - points_text.get_width()/2, 20))

    # Draw the FPS
    fps = font_small.render(f"FPS: {round(clock.get_fps())}", True, (173, 216, 230))
    screen.blit(fps, (WINDOW_SIZE[0]/2 - fps.get_width()/2, 0))
    pygame.display.update()
    clock.tick(120)
