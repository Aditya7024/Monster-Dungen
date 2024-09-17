from typing import Any
import pygame
import pygame.locals
from pygame.sprite import Group 
import Constants as cs
from Character import Characters
from Weapon import Weapons

pygame.init
pygame.font.init()

Screen = pygame.display.set_mode((cs.Screen_Width,cs.Screen_Hight))
pygame.display.set_caption(" Monster Killer !")

clock = pygame.time.Clock()

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

# Load weapon image
kaman_image = scale_img(pygame.image.load(r"assets\images\weapons\bow.png").convert_alpha(),cs.Weapon_Scale)
teer_image = scale_img(pygame.image.load(r"assets\images\weapons\arrow.png").convert_alpha(),cs.Weapon_Scale)

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

# Damage text class
class DamageText(pygame.sprite.Sprite):
    def __init__(self, x, y, damage, color):
        pygame.sprite.Sprite.__init__(self)
        self.image = font.render(damage, True, color)
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)

    def update(self):
        self.rect.y -= 1
        

# create player
player = Characters(100,100,100,mob_animations,0)

# create enemy
enemy =Characters(200,300,100, mob_animations,1)

# create players weapon
kaman = Weapons(kaman_image, teer_image)

# empty enemy list
enemy_list = []
enemy_list.append(enemy)

# Create sprite group
damage_text_group = pygame.sprite.Group()
teer_group = pygame.sprite.Group()

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
    player.move(dx,dy)

    # Update player 
    for enemy in enemy_list:
        enemy.update()
    player.update()
    
    teer = kaman.update(player)
    if teer:
        teer_group.add(teer)
    for teer in teer_group:
        damage, damage_pos = teer.update(enemy_list)
        if damage:
            damage_text = DamageText(damage_pos.centerx, damage_pos.y, str(damage), cs.Red)
            damage_text_group.add(damage_text)
    damage_text_group.update()
    
    

    # Draw the player on screen
    for enemy in enemy_list:
        enemy.draw(Screen)
    player.draw(Screen)
    kaman.draw(Screen)

    for teer in teer_group:
        teer.draw(Screen)
    
    damage_text_group.draw(Screen)

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