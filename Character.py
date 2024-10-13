import pygame
import math
import Constants as cs
import Weapon as wp

class Characters():
    def __init__(self, x, y, health, mob_animation, char_type, boss, size):
        self.char_type = char_type
        self.boss = boss
        self.score = 0
        self.flip = False
        self.animation_list = mob_animation[char_type]
        self.frame_index = 0
        self.action = 0 # 0-idle 1-run
        self.update_time = pygame.time.get_ticks()
        self.running = False
        self.health = health
        self.alive = True
        self.hit = False
        self.last_hit = pygame.time.get_ticks()
        self.last_attack = pygame.time.get_ticks()
        self.stunned = False

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = pygame.Rect(0,0, cs.Tile_Size * size, cs.Tile_Size * size)
        self.rect.center = (x,y)
    
    def move(self,dx,dy, obstacle_tile, exit_tile = None):
        screen_scroll = [0,0]
        level_complete = False
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
        
        # Ckeck for collision with map in x direction
        self.rect.x += dx
        for obst in obstacle_tile:
            # Ckeck for collision
            if obst[1].colliderect(self.rect):
                # check the side of collision
                if dx > 0:
                    self.rect.right = obst[1].left
                if dx < 0:
                    self.rect.left = obst[1].right    
        
        # Ckeck for collision with map in x direction
        self.rect.y += dy
        for obst in obstacle_tile:
            # Ckeck for collision
            if obst[1].colliderect(self.rect):
                # check the side of collision
                if dy > 0:
                    self.rect.bottom = obst[1].top
                if dy < 0:
                    self.rect.top = obst[1].bottom

        # only move screen for player not enimies movements
        if self.char_type == 0:
            # Check collision with exit ladder
            if exit_tile[1].colliderect(self.rect):
                # ensure player is close to exit ladder
                exit_dist = dist = math.sqrt(((self.rect.centerx - exit_tile[1].centerx) ** 2) + ((self.rect.centery - exit_tile[1].centery) ** 2))
                if exit_dist < 20 :
                    level_complete = True

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

        return screen_scroll, level_complete

    def ai(self, player, obstacle_tile, screen_scroll, fireball_img):
        clipped_line = ()
        stun_cooldown = 100
        ai_dx = 0
        ai_dy = 0
        fireball = None
        
        # reposition the mobs based on screen scroll
        self.rect.x += screen_scroll[0]
        self.rect.y += screen_scroll[1]
        
        # Create a line os sight from enemy to the player
        line_of_sight = ((self.rect.centerx, self.rect.centery), (player.rect.centerx, player.rect.centery))
        
        # Check if line of sight passes through an obstacle tile
        for obsta in obstacle_tile:
            if obsta[1].clipline(line_of_sight):
                clipped_line = obsta[1].clipline(line_of_sight)

        # Check distance  to player
        dist = math.sqrt(((self.rect.centerx - player.rect.centerx) ** 2) + ((self.rect.centery - player.rect.centery) ** 2))
        if not clipped_line and dist > cs.Range:
            if self.rect.centerx > player.rect.centerx:
                ai_dx = -cs.Enemy_Speed
        
            if self.rect.centerx < player.rect.centerx:
                ai_dx = cs.Enemy_Speed    

            if self.rect.centery > player.rect.centery:
                ai_dy = -cs.Enemy_Speed        
        
            if self.rect.centery < player.rect.centery:
                ai_dy = cs.Enemy_Speed      
        
        if self.alive:
            if not self.stunned:              
                # Move towards the player
                self.move(ai_dx, ai_dy, obstacle_tile)
                # Attack Player
                if dist < cs.Attack_Range and player.hit == False:
                    player.health -= 10
                    player.hit = True
                    player.last_hit = pygame.time.get_ticks()

                # Boss enemy shoot fireball
                fireball_cooldown = 700
                if self.boss:
                    if dist < 500:
                        if pygame.time.get_ticks() - self.last_attack >= fireball_cooldown:
                            fireball = wp.Fireball(fireball_img, self.rect.centerx, self.rect.centery, player.rect.centerx, player.rect.centery)
                            self.last_attack = pygame.time.get_ticks()

            # Check if hit
            if self.hit == True:
                self.hit = False
                self.last_hit = pygame.time.get_ticks()
                self.stunned = True
                self.running = False
                self.update_action(0)

            if (pygame.time.get_ticks() - self.last_hit > stun_cooldown):
                self.stunned = False
        
        return fireball

    def update(self):
        # check if character is dead
        if self.health <= 0:
            self.health = 0
            self.alive = False

        # timer to reset player taking a hit
        hit_cooldown = 1000
        if self.char_type == 0:
            if self.hit == True:
                if pygame.time.get_ticks() - self.last_hit > hit_cooldown:
                    self.hit = False
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
      
    
    
