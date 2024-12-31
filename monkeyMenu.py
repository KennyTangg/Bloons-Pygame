import pygame 

# Defines the MonkeyMenu class
class MonkeyMenu(pygame.sprite.Sprite):
    def __init__(self,image,x,y,single_click):
        super().__init__()
        # Set the attributes
        self.image = image
        self.rect = self.image.get_rect(topleft = (x,y))
        self.click = False
        self.single_click = single_click

    def draw(self,screen):
        position = pygame.mouse.get_pos()
        active = False
        # if mouse position is in the rectangle the condition will be True
        if self.rect.collidepoint(position) == True:
            # if left click is press it will return True
            if pygame.mouse.get_pressed()[0] == 1 and self.click == False:
                # check if it is toggle or hold 
                if self.single_click == True:
                    self.click = True
                active = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.click = False

        screen.blit(self.image,self.rect)
        
        return active
    
    def remove_menu(self):
        ''' remove the menu '''
        self.kill()