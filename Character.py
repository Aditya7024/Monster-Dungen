import pygame
import math
import Constants as cs

class Characters():
    def __init__(self, x, y, health, mob_animation, char_type):
        self.char_type = char_type
        self.score = 0
        self.flip = False
        self.animation_list = mob_animation[char_type]
        self.frame_index = 0
        self.action = 0 # 0-idle 1-run
        self.update_time = pygame.time.get_ticks()
        self.running = False
        self.health = health
        self.alive = True

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = pygame.Rect(0,0, cs.Tile_Size, cs.Tile_Size)
        self.rect.center = (x,y)
    
    def move(self,dx,dy):
        screen_scroll = [0,0]
        self.running = False
        if dx != 0 or dy != 0:
            self.running = True
        if dx < 0 :
            self.flip = True
        if dx > 0 :
            self.flip = False
        if dx != 0 and dy != 0:
            dx = dx * (math.sqrt(2)/2)
            dy = dy * (math.sqrt(2)/2)
        self.rect.x += dx
        self.rect.y += dy

        # only move screen for player not enimies movements
        if self.char_type == 0:

            # move camera left or right
            if self.rect.right > (cs.Screen_Width - cs.Scroll_Thresh):
                screen_scroll[0] = (cs.Screen_Width - cs.Scroll_Thresh) - self.rect.right
                self.rect.right = cs.Screen_Width - cs.Scroll_Thresh
            if self.rect.left < cs.Scroll_Thresh:
                screen_scroll[0] = cs.Scroll_Thresh - self.rect.left
                self.rect.left = cs.Scroll_Thresh

            # move camera up or down
            if self.rect.bottom > (cs.Screen_Hight - cs.Scroll_Thresh):
                screen_scroll[1] = (cs.Screen_Hight - cs.Scroll_Thresh) - self.rect.bottom
                self.rect.bottom = cs.Screen_Hight - cs.Scroll_Thresh
            if self.rect.top < cs.Scroll_Thresh:
                screen_scroll[1] = cs.Scroll_Thresh - self.rect.top
                self.rect.top = cs.Scroll_Thresh

        return screen_scroll

    def ai(self, screen_scroll):
        # reposition the mobs based on screen scroll
        self.rect.x += screen_scroll[0]
        self.rect.y += screen_scroll[1]

    def update(self):
        # check if character is dead
        if self.health <= 0:
            self.health = 0
            self.alive = False
        # check what action is being performed
        if self.running == True:
            self.update_action(1) # run
        else:
            self.update_action(0) # idle
        animation_cooldown = 70
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0

    def update_action(self,new_action):
        # check the action
        if new_action != self.action:
            self.action = new_action
            # update animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()        

    def draw(self,surface):
        flipped_image = pygame.transform.flip(self.image,self.flip,False)
        if self.char_type == 0:
            surface.blit(flipped_image,(self.rect.x,self.rect.y - cs.Scale*cs.Offset))
        else:
            surface.blit(flipped_image,self.rect)
        pygame.draw.rect(surface,cs.Red,self.rect,1)
    
    
