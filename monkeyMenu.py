import pygame 

class MonkeyMenu():
    def __init__(self,image,x,y,single_click):
        self.image = image
        self.rect = self.image.get_rect(topleft = (x,y))
        self.click = False
        self.single_click = single_click

    def draw(self,screen):
        position = pygame.mouse.get_pos()
        active = False
        if self.rect.collidepoint(position):
            if pygame.mouse.get_pressed()[0] == 1 and self.click == False:
                if self.single_click == True:
                    self.click = True
                active = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.click = False

        screen.blit(self.image,self.rect)
        
        return active