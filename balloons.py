import pygame 
from balloonsData import balloons_data

# Defines the Balloons class and inherit the pygame.sprite.Sprite
class Balloons(pygame.sprite.Sprite):
    def __init__(self, balloon_type, images, checkpoints):
        '''
        Represents balloon in the game. Balloons move along a defined path and
        interact with the game map by either reaching the end or being destroyed by the player.
        '''
        super().__init__()  # Initialize the sprite using pygame Sprite class.
        
        # Set the balloon image 
        self.image = images.get(balloon_type)
        
        # Store the path checkpoints and next checkpoint
        self.checkpoints = checkpoints
        self.next_checkpoint = 1
        
        # Set the balloon health and speed from balloons_data
        self.health = balloons_data.get(balloon_type)["health"]
        self.speed = balloons_data.get(balloon_type)["speed"]
        
        # Set the initial position of the balloon and create a rectangle
        self.position = pygame.Vector2(self.checkpoints[0])
        self.rect = self.image.get_rect(center=self.position)

    def update(self, map):
        '''
        Updates the balloon's state during each game frame:
        - Moves the balloon along its path.
        - Checks if the balloon is still alive (has health left).
        
        '''
        self.move(map)  
        self.check_alive(map) 

    def check_alive(self, map):
        ''' 
        Checks if the balloon's health is zero. 
        If so, it rewards the player and remove the balloon from the game.

        '''
        if self.health <= 0:
            # Remove balloon, reward the player with money 
            # and increment the killed balloons count
            map.money += 3
            map.killed_balloons += 1
            self.kill()
    
    def move(self, map):
        ''' 
        Moves the balloon along the path defined by checkpoints. If it reaches the end,
        it decreases the player's health and increments the missed balloon count.

        '''
        # Check if the balloon has more checkpoints to reach
        if self.next_checkpoint < len(self.checkpoints):
            # Set the target to the next checkpoint and 
            # calculate the distance from current position to target
            self.target = pygame.Vector2(self.checkpoints[self.next_checkpoint])
            self.movement = self.target - self.position
        else:
            # If the balloon reaches the last checkpoint,
            # remove balloon, decrease player health and increase missed balloons count
            self.kill()  
            map.health -= 1  
            map.missed_balloons += 1  


        distance = self.movement.length()
        
        # Move the balloon towards the next checkpoint
        if distance >= (self.speed * map.game_speed):
            self.position += self.movement.normalize() * self.speed * map.game_speed
        else:
            # If the balloon is close enough to the checkpoint, 
            # move directly to it and set the next checkpoint
            if distance != 0:
                self.position += self.movement.normalize() * distance
            self.next_checkpoint += 1
        
        self.rect.center = self.position