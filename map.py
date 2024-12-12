import random
from balloonsData import balloons_spawn_data 

# Constants for health and money
HEALTH = 100
MONEY = 650

# Defines the Map class
class Map:
    def __init__(self,map_image):
        # set the image, health, money, wave and speed of the game 
        self.image = map_image
        self.health = HEALTH
        self.money = MONEY
        self.level = 0
        self.game_speed = 1

        # Attributes for list of balloons and counting the balloons
        self.balloon_list = []
        self.spawned_balloons = 0
        self.killed_balloons = 0
        self.missed_balloons = 0

    def draw(self,screen):
        '''Draw the map image to the screen.'''
        screen.blit(self.image,(0,0))

    def check_wave_complete(self):
        '''Check if the wave is complete '''
        if (self.killed_balloons + self.missed_balloons) == len(self.balloon_list):
            return True

    def reset_wave(self):
        '''Reset wave data for next wave.'''
        self.balloon_list = []
        self.spawned_balloons = 0
        self.killed_balloons = 0
        self.missed_balloons = 0


    def process_balloons(self):
        '''Process balloon spawns for the current level using balloon spawn data.'''
        if self.level < len(balloons_spawn_data):
            balloons = balloons_spawn_data[self.level]
            for balloon_type in balloons:
                spawn_balloons = balloons[balloon_type]
                for balloon in range(spawn_balloons):
                    self.balloon_list.append(balloon_type)
            # Randomize the balloons so it is not in order
            random.shuffle(self.balloon_list)


    def valid_position(x,y):
        '''Check if a given (x, y) position is valid for placing a monkey.'''
        if 75 <= y <= 110:
            return True
        
        if x <= 280 and 75 <= y <= 260:
            return True

        if 360 <= x <= 450 and 180 <= y <= 260:
            return True

        if 530 <= x <= 950 and y <= 250:
            return True

        if x <= 270 and 330 <= y <= 390:
            return True

        if 370 <= x <= 600 and 330 <= y <= 390:
            return True

        if 530 <= x <= 600 and y <= 390:
            return True

        if 690 <= x <= 710 and 310 <= y <= 500:
            return True

        if 790 <= x <= 950 and 75 <= y <= 720:
            return True

        if x <= 110 and y >= 330:
            return True

        if 190 <= x <= 270 and 460 <= y <= 540:
            return True
        
        if 360 <= x <= 710 and 460 <= y <= 510:
            return True

        if 360 <= x <= 410 and y >= 460:
            return True

        if x <= 410 and y >= 610:
            return True

        if 510 <= x <= 950 and y >= 590:
            return True
        
        return False # else return false