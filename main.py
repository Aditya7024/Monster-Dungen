from typing import Any
import pygame
import csv
import pygame.locals
from pygame.sprite import Group 
import Constants as cs
from Character import Characters
from Weapon import Weapons
from Items import Item
from World import Worlds

pygame.init
pygame.font.init()

Screen = pygame.display.set_mode((cs.Screen_Width,cs.Screen_Hight))
pygame.display.set_caption(" Monster Killer !")

# create clock for maintaning frame rate
clock = pygame.time.Clock()

# Define game variables
level = 3
screen_scroll = [0,0]

# Player Movement
moving_left = False
moving_right = False
moving_up = False
moving_down = False

# define Font
font = pygame.font.Font(r"assets\fonts\AtariClassic.ttf",20)


def scale_img(image,scale):
    w = image.get_width()
    h = image.get_height()
    return pygame.transform.scale(image,(w * scale, h* scale))

# Load heart images
heart_empty = scale_img(pygame.image.load(r"assets\images\items\heart_empty.png").convert_alpha(),cs.Item_Scale)
heart_full = scale_img(pygame.image.load(r"assets\images\items\heart_full.png").convert_alpha(),cs.Item_Scale)
heart_half = scale_img(pygame.image.load(r"assets\images\items\heart_half.png").convert_alpha(),cs.Item_Scale)

# load coin images
coin_images = []
for i in range(4):
    img = scale_img(pygame.image.load(f"assets\images\items\coin_f{i}.png").convert_alpha(),cs.Item_Scale)
    coin_images.append(img)

# Load potion image
potion_image = scale_img(pygame.image.load(r"assets\images\items\potion_red.png").convert_alpha(),cs.Potion_Scale)

item_images = []
item_images.append(coin_images)
item_images.append(potion_image)

# Load weapon image
kaman_image = scale_img(pygame.image.load(r"assets\images\weapons\bow.png").convert_alpha(),cs.Weapon_Scale)
teer_image = scale_img(pygame.image.load(r"assets\images\weapons\arrow.png").convert_alpha(),cs.Weapon_Scale)

# Load tile map images
tile_list = []
for x in range(cs.Tile_Types):
    tile_image = pygame.image.load(f"assets/images/tiles/{x}.png").convert_alpha()
    tile_image = pygame.transform.scale(tile_image, (cs.Tile_Size, cs.Tile_Size))
    tile_list.append(tile_image)

# load character images
mob_animations = []
mob_types = ["elf","imp","skeleton","goblin","muddy","tiny_zombie","big_demon"]

animation_types = ['idle','run']
for mob in mob_types:
    # load image
    animation_list = []
    for animation in animation_types:
        temp_list = []
        for i in range(4):
            images = pygame.image.load(f"assets\images\characters\{mob}\{animation}\{i}.png").convert_alpha()
            images = scale_img(images,cs.Scale)
            temp_list.append(images)
        animation_list.append(temp_list)
    mob_animations.append(animation_list)    

# function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    Screen.blit(img, (x,y)) 

# function for displaying game info
def draw_info ():
    pygame.draw.rect(Screen, cs.Panel, (0, 0, cs.Screen_Width, 50))
    pygame.draw.line(Screen, cs.White, (0,50),(cs.Screen_Width,50))

    # Draw lives
    half_heart_draw = False
    for i in range(5):
        if player.health >= ((i + 1) *20):
            Screen.blit(heart_full,(10 + i * 50, 0))
        elif (player.health % 20 > 0) and half_heart_draw == False:
            Screen.blit(heart_half,(10 + i * 50, 0))
            half_heart_draw = True
        else:
            Screen.blit(heart_empty,(10 + i * 50, 0))

    # level
    draw_text("Level: " + str(level), font, cs.White, cs.Screen_Width / 2, 15)

    # show Score
    draw_text(f"X{player.score}", font, cs.White, cs.Screen_Width - 100, 15)

# create empty tile list
world_data = [  ]
for row in range(cs.Rows):
    r = [-1] * cs.Columns
    world_data.append(r)

# Loading level data to create world
with open(f"Levels/level{level}_data.csv",newline = "") as csvfile:
    reader = csv.reader(csvfile, delimiter= ",")
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)


world = Worlds()
world.process_data(world_data, tile_list, item_images, mob_animations)

# Damage text class
class DamageText(pygame.sprite.Sprite):
    def __init__(self, x, y, damage, color):
        pygame.sprite.Sprite.__init__(self)
        self.image = font.render(damage, True, color)
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.counter = 0

    def update(self):
        # reposition based on screen scroll
        self.rect.x += screen_scroll[0]
        self.rect.y += screen_scroll[1] 
        # damage text moving up
        self.rect.y -= 1
        # delete the char after few sec
        self.counter += 1
        if self.counter > 30:
            self.kill()


# create player
player = world.player

# create players weapon
kaman = Weapons(kaman_image, teer_image)

# Extract enemies from world data
enemy_list = world.enemies


# Create sprite group
damage_text_group = pygame.sprite.Group()
teer_group = pygame.sprite.Group()
item_group = pygame.sprite.Group()

score_coin = Item(cs.Screen_Width-115, 23, 0, coin_images, True)
item_group.add(score_coin)
# Add the items from the level data
for item in world.item_list:
    item_group.add(item)

# main game loop
run = True
while run:
    
    clock.tick(cs.FPS)

    Screen.fill(cs.Back_Ground)

    dx = 0
    dy = 0
    if moving_right == True:
        dx = cs.Speed
    if moving_left == True:
        dx = cs.Down_Speed
    if moving_up == True:
        dy = cs.Down_Speed
    if moving_down == True:
        dy = cs.Speed

    # Move of player at dx,dy  
    screen_scroll = player.move(dx,dy, world.obstacle_tile)

    # Update all objects 
    world.update(screen_scroll)

    for enemy in enemy_list:
        enemy.ai(player, world.obstacle_tile, screen_scroll)
        if enemy.alive:
            enemy.update()
    player.update()
    
    teer = kaman.update(player)
    if teer:
        teer_group.add(teer)
    for teer in teer_group:
        damage, damage_pos = teer.update(screen_scroll,world.obstacle_tile, enemy_list)
        if damage:
            damage_text = DamageText(damage_pos.centerx, damage_pos.y, str(damage), cs.Red)
            damage_text_group.add(damage_text)
    damage_text_group.update()
    item_group.update(screen_scroll, player)
    

    # Draw the player on screen
    world.draw(Screen)
    for enemy in enemy_list:
        enemy.draw(Screen)
    player.draw(Screen)
    kaman.draw(Screen)

    for teer in teer_group:
        teer.draw(Screen)
    
    damage_text_group.draw(Screen)
    item_group.draw(Screen)
    draw_info()
    score_coin.draw(Screen)

    # Event Handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        # Keyboar Input
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_w:
                moving_up = True
            if event.key == pygame.K_s:
                moving_down = True    
        
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right =False
            if event.key == pygame.K_w:
                moving_up = False
            if event.key == pygame.K_s:
                moving_down = False    
    
    pygame.display.update()

pygame.quit()