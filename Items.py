import pygame

class Item(pygame.sprite.Sprite):
    def __init__(self,x,y, item_type, animation_list, dummy_coin = False):
        pygame.sprite.Sprite.__init__(self)
        # 0-> coins , 1-> portion
        self.item_type = item_type
        self.animtion_list = animation_list
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.image = self.animtion_list[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.dummy_coin = dummy_coin

    def update(self, screen_scroll, player):
        # Doesn't apply to the dummy coin that is displayed at the top
        if not self.dummy_coin:
            # reposition based on screen scroll
            self.rect.x += screen_scroll[0]
            self.rect.y += screen_scroll[1]
        # check to see if item is collected
        if self.rect.colliderect(player.rect):
            # coins
            if self.item_type == 0:
                player.score += 1
            elif self.item_type == 1:
                player.health += 10
                if player.health > 100:
                    player.health = 100
            self.kill()
        # Handle animation
        animation_cooldown = 150
        # update _image
        self.image = self.animtion_list[self.frame_index]
        # Check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        # check if the animation has finished
        if self.frame_index >= len(self.animtion_list):
            self.frame_index = 0

    def draw(self, surface):
        surface.blit(self.image, self.rect)