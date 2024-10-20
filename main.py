from typing import Any
import pygame
from pygame import mixer
import csv
import pygame.locals
from pygame.sprite import Group 
import Constants as cs
from Character import Characters
from Weapon import Weapons
from Items import Item
from World import Worlds
from Button import Buttons

mixer.init()
pygame.init()
pygame.font.init()

Screen = pygame.display.set_mode((cs.Screen_Width,cs.Screen_Hight))
pygame.display.set_caption(" Monster Killer !")

# create clock for maintaning frame rate
clock = pygame.time.Clock()

# Define game variables
level = 1
start_game = False
pause_game = False
start_intro = False
screen_scroll = [0,0]

# Player Movement
moving_left = False
moving_right = False
moving_up = False
moving_down = False

# define Font
font = pygame.font.Font(r"assets/fonts/AtariClassic.ttf",20)


def scale_img(image,scale):
    w = image.get_width()
    h = image.get_height()
    return pygame.transform.scale(image,(w * scale, h* scale))

# Load music and sounds
pygame.mixer.music.load("assets/audio/music.wav")
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 5000)
shot_teer = pygame.mixer.Sound("assets/audio/arrow_shot.mp3")
shot_teer.set_volume(0.5)
teer_hit = pygame.mixer.Sound("assets/audio/arrow_hit.wav")
teer_hit.set_volume(0.5)
coin_sou = pygame.mixer.Sound("assets/audio/coin.wav")
coin_sou.set_volume(0.5)
portion_sou = pygame.mixer.Sound("assets/audio/heal.wav")
portion_sou.set_volume(0.5)

# Load button images
restart_img = scale_img(pygame.image.load(r"assets\images\buttons\button_restart.png").convert_alpha(),cs.Button_Scale)
exit_img = scale_img(pygame.image.load(r"assets\images\buttons\button_exit.png").convert_alpha(),cs.Button_Scale)
resume_img = scale_img(pygame.image.load(r"assets\images\buttons\button_resume.png").convert_alpha(),cs.Button_Scale)
start_img = scale_img(pygame.image.load(r"assets\images\buttons\button_start.png").convert_alpha(),cs.Button_Scale)

# Load heart images
heart_empty = scale_img(pygame.image.load(r"assets\images\items\heart_empty.png").convert_alpha(),cs.Item_Scale)
heart_full = scale_img(pygame.image.load(r"assets\images\items\heart_full.png").convert_alpha(),cs.Item_Scale)
heart_half = scale_img(pygame.image.load(r"assets\images\items\heart_half.png").convert_alpha(),cs.Item_Scale)

# load coin images
coin_images = []
for i in range(4):
    img = scale_img(pygame.image.load(f"assets/images/items/coin_f{i}.png").convert_alpha(),cs.Item_Scale)
    coin_images.append(img)

# Load potion image
potion_image = scale_img(pygame.image.load(r"assets\images\items\potion_red.png").convert_alpha(),cs.Potion_Scale)

item_images = []
item_images.append(coin_images)
item_images.append(potion_image)

# Load weapon image
kaman_image = scale_img(pygame.image.load(r"assets\images\weapons\bow.png").convert_alpha(),cs.Weapon_Scale)
teer_image = scale_img(pygame.image.load(r"assets\images\weapons\arrow.png").convert_alpha(),cs.Weapon_Scale)
fireball_image = scale_img(pygame.image.load(r"assets\images\weapons\fireball.png").convert_alpha(),cs.Fireball_Scale)

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
            images = pygame.image.load(f"assets/images/characters/{mob}/{animation}/{i}.png").convert_alpha()
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

# Function to reset level
def reset_level():
    damage_text_group.empty()
    teer_group.empty()
    item_group.empty()
    fireball_group.empty()

    # Creat empty tile list
    data = []
    for row in range(cs.Rows):
        r = [-1] * cs.Columns
        data.append(r)
    
    return data

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

# Class for handling screen fade
class Screenfade():
    def __init__(self, direction, colors, speed):
        self.directionn = direction
        self.color = colors
        self.speed = speed
        self.fade_counter = 0

    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed
        if self.directionn == 1:
            pygame.draw.rect(Screen, self.color, (0 - self.fade_counter, 0, cs.Screen_Width // 2, cs.Screen_Hight))
            pygame.draw.rect(Screen, self.color, (cs.Screen_Width // 2 + self.fade_counter, 0, cs.Screen_Width, cs.Screen_Hight))
            pygame.draw.rect(Screen, self.color, (0, 0 - self.fade_counter, cs.Screen_Width,cs.Screen_Hight // 2))
            pygame.draw.rect(Screen, self.color, (0, cs.Screen_Hight // 2 + self.fade_counter, cs.Screen_Width, cs.Screen_Hight))
        
        elif self.directionn == 2:
            pygame.draw.rect(Screen, self.color,(0,0,cs.Screen_Width, 0 + self.fade_counter))

        if self.fade_counter >= cs.Screen_Width:
            fade_complete = True
        
        return fade_complete
 
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
fireball_group = pygame.sprite.Group()

score_coin = Item(cs.Screen_Width-115, 23, 0, coin_images, True)
item_group.add(score_coin)
# Add the items from the level data
for item in world.item_list:
    item_group.add(item)

# Create screen fade
intro_fade = Screenfade(1, cs.Black, 4)
death_fade = Screenfade(2, cs.Pink, 4)

# Create Button
restart_button = Buttons(cs.Screen_Width // 2 - 175, cs.Screen_Hight // 2 - 50, restart_img)
start_button = Buttons(cs.Screen_Width // 2 - 145, cs.Screen_Hight // 2 - 150, start_img)
exit_button = Buttons(cs.Screen_Width // 2 - 110, cs.Screen_Hight // 2 + 50, exit_img)
resume_button = Buttons(cs.Screen_Width // 2 - 175, cs.Screen_Hight // 2 - 150, resume_img)

# main game loop
run = True
while run:
    
    clock.tick(cs.FPS)
    
    if start_game == False:
        Screen.fill(cs.Menu_BG)
        if start_button.draw(Screen):
            start_game = True
            start_intro = True

        if exit_button.draw(Screen):
            run = False

    else:
        if pause_game == True:
            Screen.fill(cs.Menu_BG)
            if resume_button.draw(Screen):
                pause_game = False
            if exit_button.draw(Screen):
                run = False
        
        else:
            Screen.fill(cs.Back_Ground)

            # player movement calculation
            if player.alive:
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
                screen_scroll, level_complete = player.move(dx, dy, world.obstacle_tile, world.exit_tile)

                # Update all objects 
                world.update(screen_scroll)

                for enemy in enemy_list:
                    fireball = enemy.ai(player, world.obstacle_tile, screen_scroll, fireball_image)
                    if fireball:
                        fireball_group.add(fireball)
                    if enemy.alive:
                        enemy.update()
                player.update()
                
                teer = kaman.update(player)
                if teer:
                    teer_group.add(teer)
                    shot_teer.play()
                for teer in teer_group:
                    damage, damage_pos = teer.update(screen_scroll,world.obstacle_tile, enemy_list)
                    if damage:
                        damage_text = DamageText(damage_pos.centerx, damage_pos.y, str(damage), cs.Red)
                        damage_text_group.add(damage_text)
                        teer_hit.play()
                damage_text_group.update()
                fireball_group.update(screen_scroll, player)
                item_group.update(screen_scroll, player, coin_sou, portion_sou)
            

            # Draw the player on screen
            world.draw(Screen)
            for enemy in enemy_list:
                enemy.draw(Screen)
            player.draw(Screen)
            kaman.draw(Screen)

            for teer in teer_group:
                teer.draw(Screen)
            
            for fireball in fireball_group:
                fireball.draw(Screen)
                
            damage_text_group.draw(Screen)
            item_group.draw(Screen)
            draw_info()
            score_coin.draw(Screen)

            # Check level completer
            if level_complete == True:
                start_intro = True
                level += 1
                world_data = reset_level()
                # Loading level data to create world
                with open(f"Levels/level{level}_data.csv",newline = "") as csvfile:
                    reader = csv.reader(csvfile, delimiter= ",")
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            world_data[x][y] = int(tile)

                world = Worlds()
                world.process_data(world_data, tile_list, item_images, mob_animations)

                temp_hp = player.health
                temp_score = player.score
                player = world.player
                player.health = temp_hp
                player.score = temp_score
                enemy_list = world.enemies
                score_coin = Item(cs.Screen_Width - 155, 23, 0, coin_images, True)
                item_group.add(score_coin)
                for item in world.item_list:
                    item_group.add(item)

            # Show Intro
            if start_intro == True:
                if intro_fade.fade():
                    start_intro = False
                    intro_fade.fade_counter = 0   

            # show Death screen
            if player.alive == False:
                if death_fade.fade():
                    if restart_button.draw(Screen):
                        death_fade.fade_counter = 0
                        start_intro = True 
                        world_data = reset_level()
                        # Loading level data to create world
                        with open(f"Levels/level{level}_data.csv",newline = "") as csvfile:
                            reader = csv.reader(csvfile, delimiter= ",")
                            for x, row in enumerate(reader):
                                for y, tile in enumerate(row):
                                    world_data[x][y] = int(tile)

                        world = Worlds()
                        world.process_data(world_data, tile_list, item_images, mob_animations)

                        
                        player = world.player
                        enemy_list = world.enemies
                        score_coin = Item(cs.Screen_Width - 155, 23, 0, coin_images, True)
                        item_group.add(score_coin)
                        for item in world.item_list:
                            item_group.add(item)


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
            if event.key == pygame.K_ESCAPE:
                pause_game = True  
        
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