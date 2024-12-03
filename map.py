import random
from balloonsData import balloons_spawn_data 

# Constants for initial health and money
HEALTH = 100
MONEY = 650

class Map:
    def __init__(self, map_image):
        '''Initialize the map with an image, health, money, and other game stats.'''
        self.image = map_image
        self.health = HEALTH
        self.money = MONEY
        self.level = 0
        self.game_speed = 1
        self.balloon_list = []  # List to store spawned balloons
        self.spawned_balloons = 0
        self.killed_balloons = 0
        self.missed_balloons = 0

    def draw(self, screen):
        '''Draw the map image on the screen.'''
        screen.blit(self.image, (0, 0))

    def check_wave_complete(self):
        '''Check if all balloons (killed or missed) are processed for the wave.'''
        if (self.killed_balloons + self.missed_balloons) == len(self.balloon_list):
            return True
        return False

    def reset_wave(self):
        '''Reset the balloon list and stats for a new wave.'''
        self.balloon_list = []
        self.spawned_balloons = 0
        self.killed_balloons = 0
        self.missed_balloons = 0

    def process_balloons(self):
        '''Spawn balloons for the current level.'''
        if self.level < len(balloons_spawn_data):
            balloons = balloons_spawn_data[self.level]
            # Add balloons to the list based on the spawn data
            for balloon_type in balloons:
                spawn_balloons = balloons[balloon_type]
                for balloon in range(spawn_balloons):
                    self.balloon_list.append(balloon_type)
            random.shuffle(self.balloon_list)  # Shuffle balloon spawn order

    @staticmethod
    def valid_position(x, y):
        '''Check if the position (x, y) is valid for placing a monkey.'''
        # Return True if the position is valid based on predefined areas
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
        
        return False  # If no condition matched, return False