import pygame 
import math
from monkeyData import monkey_data

# Constants
animation_delay = 110
monkey_damage = 5

class Monkey(pygame.sprite.Sprite):
    def __init__(self, sprite_sheet, position, sound):
        '''Initialize the monkey sprite with its properties (range, cooldown, animation, etc.).'''
        super().__init__()
        self.upgrade_level = 1  # Initial upgrade level
        self.range = monkey_data[self.upgrade_level - 1].get("range")
        self.cooldown = monkey_data[self.upgrade_level - 1].get("cooldown")
        self.last_attack = pygame.time.get_ticks()  # Track time of last attack
        self.selected = False  # Whether the monkey is selected
        self.target = None  # Current target balloon
        self.sprite_sheet = sprite_sheet  # Sprite sheet for animation
        self.animation_list = self.load_images()  # Load animation frames
        self.frame_index = 0  # Index for current animation frame
        self.update_time = pygame.time.get_ticks()  # Time tracker for frame updates
        self.image = self.animation_list[self.frame_index]
        self.position = position
        self.sound = sound  # Sound effect for attack
        self.rect = self.image.get_rect(midbottom=position)

        # Create a surface to show the monkey's attack range
        self.range_image = pygame.Surface((self.range * 2, self.range * 2))
        self.range_image.fill((0, 0, 0))  # Make the circle black
        self.range_image.set_colorkey((0, 0, 0))  # Make black transparent
        self.range_image.set_alpha(60)  # Set transparency level
        self.range_rect = self.range_image.get_rect()
        self.range_rect.center = self.rect.center
        pygame.draw.circle(self.range_image, "grey100", (self.range, self.range), self.range)  # Draw the attack range circle

    def load_images(self):
        '''Load the monkey's animation frames from the sprite sheet.'''
        size = self.sprite_sheet.get_height()  # Assuming sprite sheet frames are square
        animation_list = []
        for i in range(8):  # Assuming 8 frames for animation
            temp_image = self.sprite_sheet.subsurface(i * size, 0, size, size)
            animation_list.append(temp_image)
        return animation_list
    
    def pick_target(self, balloons_group):
        '''Find a balloon within the monkey's range and deal damage to it.'''
        for balloon in balloons_group:
            if balloon.health > 0:  # Skip dead balloons
                # Calculate the distance from the monkey to the balloon
                x_distance = balloon.position[0] - self.position[0]
                y_distance = balloon.position[1] - self.position[1]
                distance = math.sqrt(x_distance ** 2 + y_distance ** 2)
                
                # If the balloon is within range, select it as the target and apply damage
                if distance < self.range:
                    self.target = balloon
                    self.target.health -= monkey_damage  # Deal damage
                    self.sound.play()  # Play the attack sound effect
                    break
    
    def play_animation(self):
        '''Play the monkey's attack animation and reset after completion.'''
        self.image = self.animation_list[self.frame_index]
        # Update animation frame at the specified delay
        if pygame.time.get_ticks() - self.update_time > animation_delay:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
            if self.frame_index >= len(self.animation_list):
                self.frame_index = 0  # Restart animation
                self.last_attack = pygame.time.get_ticks()  # Reset attack timer
                self.target = None  # Reset target after attack

    def upgrade(self):
        '''Upgrade the monkey's stats (range, cooldown, etc.).'''
        self.upgrade_level += 1  # Increase the upgrade level
        self.range = monkey_data[self.upgrade_level - 1].get("range")
        self.cooldown = monkey_data[self.upgrade_level - 1].get("cooldown")
        # Update the range image for the new range
        self.range_image = pygame.Surface((self.range * 2, self.range * 2))
        self.range_image.fill((0, 0, 0))
        self.range_image.set_colorkey((0, 0, 0))  # Transparent background
        self.range_image.set_alpha(60)
        self.range_rect = self.range_image.get_rect()
        self.range_rect.center = self.rect.center
        pygame.draw.circle(self.range_image, "grey100", (self.range, self.range), self.range)

    def sell_monkey(self):
        '''Remove the monkey from the game (sell it).'''
        self.kill()  # Remove the monkey from all sprite groups

    def update(self, balloons_group, map):
        '''Update the monkey's state (target picking, cooldown, and animation).'''
        if self.target:
            self.play_animation()  # Play animation if there is a target
        else:
            # If cooldown has passed, pick a new target from the balloon group
            if pygame.time.get_ticks() - self.last_attack > (self.cooldown / map.game_speed):
                self.pick_target(balloons_group)

    def draw(self, screen):
        '''Draw the monkey and its range indicator on the screen.'''
        screen.blit(self.image, self.rect)  # Draw the current animation frame
        if self.selected:
            screen.blit(self.range_image, self.range_rect)  # Draw range circle if monkey is selected