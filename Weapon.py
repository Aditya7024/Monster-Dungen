import pygame
import math
import Constants as cs
import random

from pygame.sprite import Group

class Weapons():
    def __init__(self,image ,teer_image):
        self.original_image = image
        self.angle = 0
        self.image = pygame.transform.rotate(self.original_image,self.angle)
        self.teer_image = teer_image
        self.rect = self.image.get_rect()
        self.fired = False
        self.last_shot = pygame.time.get_ticks()

    def update(self,player):
        shot_cooldown = 300
        teer = None
        self.rect.center = player.rect.center
        pos = pygame.mouse.get_pos()
        x_dist = pos[0] - self.rect.centerx
        y_dist = -(pos[1] - self.rect.centery) # -ve denn pygame y cordinates increase downstream
        self.angle = math.degrees(math.atan2(y_dist,x_dist))

        # Get mouse click
        if pygame.mouse.get_pressed()[0] and self.fired == False and (pygame.time.get_ticks() - self.last_shot) >= shot_cooldown:
            teer = Teer(self.teer_image, self.rect.centerx,self.rect.centery,self.angle)
            self.fired = True
            self.last_shot = pygame.time.get_ticks()
        # reset mouse click
        if pygame.mouse.get_pressed()[0] == False:
            self.fired = False
        return teer

    def draw(self,surface):
        self.image = pygame.transform.rotate(self.original_image,self.angle)
        surface.blit(self.image,((self.rect.centerx - int(self.image.get_width()/2)),self.rect.centery - int(self.image.get_height()/2)))
    
class Teer(pygame.sprite.Sprite):
    def __init__(self,image,x,y,angle):
        pygame.sprite.Sprite.__init__(self)
        self.original_image = image
        self.angle = angle
        self.image = pygame.transform.rotate(self.original_image, self.angle - 90)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        # Calculate the vertical and horizontal speed on the angle
        self.dx = math.cos(math.radians(self.angle)) * cs.Teer_speed
        self.dy = -(math.sin(math.radians(self.angle)) * cs.Teer_speed)


    def update(self,screen_scroll,enemy_list):
        # reset variable
        damage = 0
        damage_pos = None

        # reposition based on speed
        self.rect.x += screen_scroll[0] + self.dx
        self.rect.y += screen_scroll[1] + self.dy

        # check isf arrow gone out of the screen
        if self.rect.right < 0 or self.rect.left > cs.Screen_Width or self.rect.bottom < 0 or self.rect.top > cs.Screen_Hight:
            self.kill()

        # check collision between teer and enemy
        for enemy in enemy_list:
            if enemy.rect.colliderect(self.rect) and enemy.alive:
                damage = 10 + random.randint(-5,5)
                damage_pos = enemy.rect
                enemy.health -= damage
                self.kill()
                break
        
        return damage , damage_pos

    def draw(self,surface):
        surface.blit(self.image,((self.rect.centerx - int(self.image.get_width()/2)),self.rect.centery - int(self.image.get_height()/2)))
