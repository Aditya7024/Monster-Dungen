import pygame
from Character import Characters
import Constants as cs
from Items import Item

class Worlds():
    def __init__(self):
        self.map_tiles = []
        self.obstacle_tile = []
        self.exit_tile = None
        self.item_list = []
        self.player = None
        self.enemies  = []

    def process_data(self, data, tile_list, item_images, mob_animations):
        self.level_length = len(data)
        # iterate through each value in level data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                image  = tile_list[ tile ]
                image_rect = image.get_rect()
                image_x = x * cs.Tile_Size
                image_y = y * cs.Tile_Size
                
                image_rect.center = (image_x, image_y)
                tile_data = [image, image_rect, image_x, image_y]
                
                if tile == 7:
                    self.obstacle_tile.append(tile_data)

                elif tile == 8:
                    self.exit_tile = tile_data
                
                elif tile == 9:
                    coin = Item(image_x, image_y, 0, item_images[0])
                    self.item_list.append(coin)
                    tile_data[0] = tile_list[0]
                
                elif tile == 10:
                    portion = Item(image_x, image_y, 1, [item_images[1]])
                    self.item_list.append(portion)
                    tile_data[0] = tile_list[0]

                elif tile == 11:
                    player = Characters(image_x, image_y, 20, mob_animations,0, False, 1)
                    self.player = player
                    tile_data[0] = tile_list[0]

                elif tile >= 12 and tile <= 16:
                    enemy = Characters(image_x, image_y, 100, mob_animations,tile - 11, False, 1)
                    self.enemies.append(enemy)
                    tile_data[0] = tile_list[0]
                
                elif tile == 17 :
                    enemy = Characters(image_x, image_y, 100, mob_animations, 6, True, 2)
                    self.enemies.append(enemy)
                    tile_data[0] = tile_list[0]
                
                # Add image data to main tile list
                if tile >= 0:
                    self.map_tiles.append(tile_data)
    
    def update(self, screen_scroll):
        for tile in self.map_tiles:
            tile[2] += screen_scroll[0]
            tile[3] += screen_scroll[1]
            tile[1].center  =(tile[2], tile[3])

    def draw (self, surface):
        for tile in self.map_tiles:
            surface.blit(tile[0], tile[1])