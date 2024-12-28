import pygame 
import math
from monkeyData import monkey_data

# Constants for animation speed and monkey damage
animation_delay = 110
monkey_damage = 5

# Defines the Monkey class and inherit the pygame.sprite.Sprite
class Monkey(pygame.sprite.Sprite):
    def __init__(self,sprite_sheet,position,sound):
        '''Initialize the monkey sprite '''
        super().__init__() # Initialize the sprite using pygame Sprite class.

        # set the range and cooldown for monkey depends on the upgrade level
        self.upgrade_level = 1
        self.range = monkey_data[self.upgrade_level - 1].get("range")
        self.cooldown = monkey_data[self.upgrade_level - 1].get("cooldown")
        
        # tracking the time for the last attack and time for frame update
        self.last_attack = pygame.time.get_ticks()
        self.update_time = pygame.time.get_ticks()

        # set attributes for set of monkey images for animation , 
        # monkey position and sound effect
        self.sprite_sheet = sprite_sheet
        self.position = position
        self.sound = sound

        # attribute for list of monkey frames for animation and 
        # attribute for image from the list of frames and 
        # track the frames using a frame_index attribute 
        self.animation_list = self.load_images()
        self.frame_index = 0
        self.image = self.animation_list[self.frame_index]

        # attribute for checking if monkey is selected and 
        # attribute for current target and a rectangle for the monkey 
        self.selected = False
        self.target = None
        self.rect = self.image.get_rect(midbottom = position)

        # Attribute to show surface of the monkey attack range
        self.range_image = pygame.Surface((self.range * 2,self.range * 2))
        self.range_image.fill((0,0,0))
        self.range_image.set_colorkey((0,0,0))
        self.range_image.set_alpha(60)
        self.range_rect = self.range_image.get_rect()
        self.range_rect.center = self.rect.center
        pygame.draw.circle(self.range_image,"grey100",(self.range,self.range),self.range)

    def load_images(self):
        '''Load the monkey's animation frames from the sprite sheet.'''
        size  = self.sprite_sheet.get_height() 
        animation_list = []
        # looping 8 times because the frames is 8 frames 
        for i in range(8):
            temp_image = self.sprite_sheet.subsurface(i * size,0,size,size)
            animation_list.append(temp_image)
        return animation_list
    
    def pick_target(self,balloons_group):
        '''Pick a balloon within the monkey range and deal damage to it.'''
        x_distance = 0
        y_distance = 0
        for balloons in balloons_group:
            # if the balloon is still alive 
            if balloons.health > 0: 
                # Calculating the distance from the monkey to the balloon
                x_distance = balloons.position[0] - self.position[0]
                y_distance = balloons.position[1] - self.position[1]
                distance = math.sqrt(x_distance ** 2 + y_distance ** 2 )
                if distance < self.range:
                    self.target = balloons
                    self.target.health -= monkey_damage
                    self.sound.play()
                    break # make sure monkey can only target one balloon at a time
    
    def play_animation(self):
        '''Play the monkey attack animation and reset the animation after.'''
        self.image = self.animation_list[self.frame_index]
        # change frames with delay
        if pygame.time.get_ticks() - self.update_time > animation_delay:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
            if self.frame_index >= len(self.animation_list):
                # reset animation, target, and timer for last attack 
                self.frame_index = 0
                self.last_attack = pygame.time.get_ticks()
                self.target = None

    def upgrade(self):
        ''' Upgrade the monkey stats '''

        # upgrading the level and change the range and 
        # cooldown according to the monkeydata 
        self.upgrade_level += 1
        self.range = monkey_data[self.upgrade_level - 1].get("range")
        self.cooldown = monkey_data[self.upgrade_level - 1].get("cooldown")

        # setting a new range according to the upgraded range 
        self.range_image = pygame.Surface((self.range * 2,self.range * 2))
        self.range_image.fill((0,0,0))
        self.range_image.set_colorkey((0,0,0))
        self.range_image.set_alpha(60)
        self.range_rect = self.range_image.get_rect()
        self.range_rect.center = self.rect.center
        pygame.draw.circle(self.range_image,"grey100",(self.range,self.range),self.range)

    def sell_monkey(self):
        # remove the monkey
        self.kill()

    def update(self,balloons_group, map):
        ''' Update the monkey state '''
        # if the target is picked, it will play the animation
        if self.target:
            self.play_animation()
        else:
            # if the cooldown has passed, it will pick a new target 
            if pygame.time.get_ticks() - self.last_attack > (self.cooldown / map.game_speed):
                self.pick_target(balloons_group)

    def draw(self,screen):
        '''Draw the monkey and range on the screen.'''
        screen.blit(self.image,self.rect)
        if self.selected:
            # show the range if the monkey is selected
            screen.blit(self.range_image,self.range_rect)
