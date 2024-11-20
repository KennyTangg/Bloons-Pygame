import pygame 
from monkey import Monkey
from balloons import Balloons
from map import Map
from monkeyMenu import MonkeyMenu

WIDTH,HEIGHT = 1280,720
pygame.init()
pygame.display.set_caption("Tower Defense Window")
screen = pygame.display.set_mode((1280,720))
clock = pygame.time.Clock()
font = pygame.font.Font("assets/font/Pixeltype.ttf",50)

#variables
put_monkey = False
buy_monkey = 0
upgrade_monkey = 1
spawn_cooldown = 400
message_duration = 2000
last_balloon_spawn = pygame.time.get_ticks()
selected_monkey = None
invalid_time = None
wave_started = False
running = True

#Map
map_image = pygame.image.load("assets/Images/Map/map2.png").convert()
map = Map(map_image)
map.process_balloons()

#Monkeys
monkey_image = pygame.image.load("assets/Images/Monkey/Monkey.png").convert_alpha()
monkey_sheet = pygame.image.load("assets/Images/Monkey/animationMonkey-sheet.png").convert_alpha()
upgrade_monkey_image = pygame.image.load("assets/Images/GameMenu/upgradeMonkey.png").convert_alpha()

#Balloons
path = [
    (-50,270),(490,270),(490,130),(320,130),(320,550),
    (150,550),(150,410),(650,410),(650,260),
    (750,260),(750,530),(460,530),(460,750)]

balloons_images ={
    "weak":pygame.image.load("assets/Images/Balloons/Balloons_Red.png").convert_alpha(),
    "medium":pygame.image.load("assets/Images/Balloons/Balloons_Blue.png").convert_alpha(),
    "strong":pygame.image.load("assets/Images/Balloons/Balloons_Green.png").convert_alpha(),
    "very strong":pygame.image.load("assets/Images/Balloons/Balloons_Yellow.png").convert_alpha()
}

#groups
balloons_group = pygame.sprite.Group()
monkey_group = pygame.sprite.Group()

#monkey menu
monkeymenu_button = pygame.image.load("assets/Images/GameMenu/buyMonkey.png").convert()
cancelmenu_button = pygame.image.load("assets/Images/GameMenu/cancelMenu.png").convert_alpha()
upgrade_monkey_button = pygame.image.load("assets/Images/GameMenu/upgradeMonkey.png").convert_alpha()
start_button = pygame.image.load("assets/Images/GameMenu/upgradeMonkey.png").convert_alpha()

monkeymenu = MonkeyMenu(monkeymenu_button,1000,10,True)
cancelmenu = MonkeyMenu(cancelmenu_button,1000,150,True)
upgrademonkey = MonkeyMenu(upgrade_monkey_button,1000,250,True)
startbutton = MonkeyMenu(start_button,1150,650,True) 

def draw_text(text, text_color, outline_color, x, y):
    outline_width = 2  

    for i in range(-outline_width, outline_width+1):
        for j in range(-outline_width, outline_width+1):
            if i != 0 or j != 0: 
                outline_text = font.render(text, True, outline_color)
                screen.blit(outline_text, (x + i, y + j))
    
    txt = font.render(text, True, text_color)
    screen.blit(txt, (x, y))

def select_monkey(mouse_position):
    for monkey in monkey_group:
        if monkey.rect.collidepoint(mouse_position):
            monkey.selected = True
            return monkey
    return None

def clear_select():
    for monkey in monkey_group:
        monkey.selected = False

while running:
    balloons_group.update(map)
    monkey_group.update(balloons_group)

    map.draw(screen)
    balloons_group.draw(screen)

    if wave_started != True:
        if startbutton.draw(screen):
            wave_started = True
    else:
        if pygame.time.get_ticks() - last_balloon_spawn > spawn_cooldown:
            if map.spawned_balloons < len(map.balloon_list):
                balloon_type = map.balloon_list[map.spawned_balloons]
                balloons = Balloons(balloon_type,balloons_images,path)
                balloons_group.add(balloons)
                map.spawned_balloons += 1
                last_balloon_spawn = pygame.time.get_ticks()

    if map.check_wave_complete() :
        map.level += 1
        wave_started = False
        last_balloon_spawn = pygame.time.get_ticks()
        map.reset_wave()
        map.process_balloons()

    for monkey in monkey_group:
        monkey.draw(screen)

    if monkeymenu.draw(screen):
        put_monkey = True
   
    if put_monkey:
        if cancelmenu.draw(screen):
            put_monkey = False
            print("Cancel")
        cursor_rect = monkey_image.get_rect()
        cursor_position = pygame.mouse.get_pos()
        cursor_rect.midbottom = cursor_position
        if cursor_position[0] <= 975:
            screen.blit(monkey_image,cursor_rect)

    if selected_monkey:
        if selected_monkey.upgrade_level < 4:
            if upgrademonkey.draw(screen):
                if map.money >= upgrade_monkey:
                    selected_monkey.upgrade()
                    map.money -= upgrade_monkey


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_position = pygame.mouse.get_pos()
            if mouse_position[0] < 950 and mouse_position[1] > 75:
                print('test1')
                selected_monkey = None
                clear_select()
                if put_monkey:
                    if map.money >= buy_monkey:
                        if Map.valid_position(mouse_position[0],mouse_position[1]) == True:
                            monkey = Monkey(monkey_sheet,mouse_position)
                            monkey_group.add(monkey)
                            map.money -= buy_monkey
                        else:
                            invalid_time = pygame.time.get_ticks() 
                            draw_text("Invalid Placement","red","black",500,75)
                            print("Not Valid position")
                else:
                    selected_monkey = select_monkey(mouse_position)
                    if selected_monkey:
                        print(f"Selected monkey di posisi {mouse_position}")

    if invalid_time is not None:
        current_time = pygame.time.get_ticks()
        if current_time - invalid_time < message_duration:
            draw_text("Invalid Placement","red","black",500,75)
        else:
            invalid_time = None  
    
    draw_text(str(map.health),"white","black",70,20)
    draw_text("$"+ str(map.money),"white","black",200,20)
    draw_text("Wave "+ str(map.level),"yellow","black",500,20)
    # pygame.draw.lines(screen,"grey0", False, path)
    pygame.display.update()
    clock.tick(60)

pygame.quit()