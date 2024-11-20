import pygame 
from balloonsData import balloons_data

class Balloons(pygame.sprite.Sprite):
    def __init__(self,balloon_type,images,checkpoints):
        super().__init__()
        self.image = images.get(balloon_type)
        self.checkpoints = checkpoints
        self.health = balloons_data.get(balloon_type)["health"]
        self.speed = balloons_data.get(balloon_type)["speed"]
        self.position = pygame.Vector2(self.checkpoints[0])
        self.next_checkpoint = 1
        self.rect = self.image.get_rect(center = self.position)

    def update(self,map):
        self.move(map)
        self.check_alive(map)

    def check_alive(self,map):
        if self.health <= 0:
            map.money += 1
            map.killed_balloons += 1
            self.kill()
    
    def move(self,map):
        if self.next_checkpoint < len(self.checkpoints):
            self.target = pygame.Vector2(self.checkpoints[self.next_checkpoint])
            self.movement = self.target - self.position
        else:
            self.kill()
            map.health -= 1
            map.missed_balloons += 1

        distance = self.movement.length()
        if distance >= self.speed:
            self.position += self.movement.normalize() * self.speed
        else:
            if distance != 0 :
                self.position += self.movement.normalize() * distance
            self.next_checkpoint += 1
        self.rect.center = self.position
    