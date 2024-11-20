import pygame 
import math
from monkeyData import monkey_data

animation_delay = 110
monkey_damage = 100

class Monkey(pygame.sprite.Sprite):
    def __init__(self,sprite_sheet,position):
        super().__init__()
        self.upgrade_level = 1
        self.range = monkey_data[self.upgrade_level - 1].get("range")
        self.cooldown = monkey_data[self.upgrade_level - 1].get("cooldown")
        self.last_attack = pygame.time.get_ticks()
        self.selected = False
        self.target = None
        self.sprite_sheet = sprite_sheet
        self.animation_list = self.load_images()
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.image = self.animation_list[self.frame_index]
        self.position = position
        self.rect = self.image.get_rect(midbottom = position)
        self.range_image = pygame.Surface((self.range * 2,self.range * 2))
        self.range_image.fill((0,0,0))
        self.range_image.set_colorkey((0,0,0))
        self.range_image.set_alpha(60)
        self.range_rect = self.range_image.get_rect()
        self.range_rect.center = self.rect.center
        pygame.draw.circle(self.range_image,"grey100",(self.range,self.range),self.range)


    def load_images(self):
        size  = self.sprite_sheet.get_height()
        animation_list = []
        for i in range(8):
            temp_image = self.sprite_sheet.subsurface(i * size,0,size,size)
            animation_list.append(temp_image)
        return animation_list
    
    def pick_target(self,balloons_group):
        x_distance = 0
        y_distance = 0
        for balloons in balloons_group:
            if balloons.health > 0:
                x_distance = balloons.position[0] - self.position[0]
                y_distance = balloons.position[1] - self.position[1]
                distance = math.sqrt(x_distance ** 2 + y_distance ** 2 )
                if distance < self.range:
                    self.target = balloons
                    self.target.health -= monkey_damage
                    break
    
    def play_animation(self):
        self.image = self.animation_list[self.frame_index]
        if pygame.time.get_ticks() - self.update_time > animation_delay:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
            if self.frame_index >= len(self.animation_list):
                self.frame_index = 0
                self.last_attack = pygame.time.get_ticks()
                self.target = None

    def upgrade(self):
        self.upgrade_level += 1
        self.range = monkey_data[self.upgrade_level - 1].get("range")
        self.cooldown = monkey_data[self.upgrade_level - 1].get("cooldown")
        self.range_image = pygame.Surface((self.range * 2,self.range * 2))
        self.range_image.fill((0,0,0))
        self.range_image.set_colorkey((0,0,0))
        self.range_image.set_alpha(60)
        self.range_rect = self.range_image.get_rect()
        self.range_rect.center = self.rect.center
        pygame.draw.circle(self.range_image,"grey100",(self.range,self.range),self.range)

    def update(self,balloons_group):
        if self.target:
            self.play_animation()
        else:
            if pygame.time.get_ticks() - self.last_attack > self.cooldown:
                self.pick_target(balloons_group)

    def draw(self,screen):
        screen.blit(self.image,self.rect)
        if self.selected:
            screen.blit(self.range_image,self.range_rect)
