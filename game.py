import pygame
from monkey import Monkey
from balloons import Balloons
from map import Map
from monkeyMenu import MonkeyMenu


WIDTH,HEIGHT = 1280,720
pygame.init()
pygame.mixer.init()
pygame.display.set_caption("Tower Defense Window")
screen = pygame.display.set_mode((1280,720))
clock = pygame.time.Clock()
font = pygame.font.Font("assets/font/Pixeltype.ttf",50)

# Sound
pop_sound_effect = pygame.mixer.Sound("assets/sound/popSound.mp3")
pop_sound_effect.set_volume(0.5)
game_music = pygame.mixer.Sound("assets/sound/gameMusic.mp3")
game_music.play(-1)
game_music.set_volume(0.1)

#Map
map_image = pygame.image.load("assets/Images/Map/map2.png").convert()

#Monkeys
monkey_image = pygame.image.load("assets/Images/Monkey/Monkey.png").convert_alpha()
monkey_sheet = pygame.image.load("assets/Images/Monkey/animationMonkey-sheet.png").convert_alpha()
upgrade_monkey_image = pygame.image.load("assets/Images/GameMenu/upgradeMonkey.png").convert_alpha()

#Balloons
balloons_images ={
    "weak":pygame.image.load("assets/Images/Balloons/Balloons_Red.png").convert_alpha(),
    "medium":pygame.image.load("assets/Images/Balloons/Balloons_Blue.png").convert_alpha(),
    "strong":pygame.image.load("assets/Images/Balloons/Balloons_Green.png").convert_alpha(),
    "very strong":pygame.image.load("assets/Images/Balloons/Balloons_Yellow.png").convert_alpha()
}
path = [
    (-50,280),(490,280),(490,135),(320,135),(320,565),
    (150,565),(150,415),(650,415),(650,260),
    (750,260),(750,530),(460,530),(460,750)]

#monkey menu
monkeymenu_button = pygame.image.load("assets/Images/GameMenu/buyMonkey.png").convert()
cancelmenu_button = pygame.image.load("assets/Images/GameMenu/cancelMenu.png").convert_alpha()
upgrade_monkey_button = pygame.image.load("assets/Images/GameMenu/upgradeMonkey.png").convert_alpha()
sell_button = pygame.image.load("assets/Images/GameMenu/sell.png").convert_alpha()
start_button = pygame.image.load("assets/Images/GameMenu/beginButton.png").convert_alpha()
fast_forward_button = pygame.image.load("assets/Images/GameMenu/FastForward.png").convert_alpha()
restart_button = pygame.image.load("assets/Images/GameMenu/restartButton.png").convert_alpha()
health_image = pygame.image.load("assets/Images/GameMenu/Health.png").convert_alpha()
coin_image = pygame.image.load("assets/Images/GameMenu/Coin.png").convert_alpha()
play_image = pygame.image.load("assets/Images/GameMenu/playButton.png").convert_alpha()

def draw_text(text, text_color, outline_color, x, y):
    outline_width = 2 
    for i in range(-outline_width, outline_width+1):
        for j in range(-outline_width, outline_width+1):
            if i != 0 or j != 0: 
                outline_text = font.render(text, True, outline_color)
                screen.blit(outline_text, (x + i, y + j))
    
    txt = font.render(text, True, text_color)
    screen.blit(txt, (x, y))

def game():
    def select_monkey(mouse_position):
        for monkey in monkey_group:
            if monkey.rect.collidepoint(mouse_position):
                monkey.selected = True
                return monkey
        return None

    def clear_select():
        for monkey in monkey_group:
            monkey.selected = False
        
    monkeymenu = MonkeyMenu(monkeymenu_button,1000,10,True)
    cancelmenu = MonkeyMenu(cancelmenu_button,1150,60,True)
    upgrademonkey = MonkeyMenu(upgrade_monkey_button,1010,240,True)
    sellbutton = MonkeyMenu(sell_button,1030,160,True)
    startbutton = MonkeyMenu(start_button,1150,620,True) 
    fastforwardbutton = MonkeyMenu(fast_forward_button,1150,620,False) 
    restartbutton = MonkeyMenu(restart_button,500,330,True)

    map = Map(map_image)
    map.process_balloons()

    #groups
    balloons_group = pygame.sprite.Group()
    monkey_group = pygame.sprite.Group()

    #variables
    put_monkey = False
    buy_monkey = 150
    upgrade_monkey = 100
    sell_monkey = 120
    spawn_cooldown = 500
    message_duration = 2000
    game_outcome = 0
    total_wave = 20
    last_balloon_spawn = pygame.time.get_ticks()
    selected_monkey = None
    invalid_time = None
    wave_started = False
    game_over = False
    running = True

    while running:
        pygame.mixer.music.load("assets/sound/gameMusic.mp3")
        pygame.mixer.music.play(-1)
        if game_over == False:
            if map.health <= 0:
                game_over = True
                game_outcome = -1 #lose
            if map.level + 1 > total_wave:
                game_over = True
                game_outcome = 1 #win

            balloons_group.update(map)
            monkey_group.update(balloons_group,map)

            map.draw(screen)
            balloons_group.draw(screen)

        if game_over == False:
            if wave_started != True:
                if startbutton.draw(screen):
                    wave_started = True
            else:
                map.game_speed = 1
                if fastforwardbutton.draw(screen):
                    map.game_speed = 2


                if pygame.time.get_ticks() - last_balloon_spawn > (spawn_cooldown / map.game_speed):
                    if map.spawned_balloons < len(map.balloon_list):
                        balloon_type = map.balloon_list[map.spawned_balloons]
                        balloons = Balloons(balloon_type,balloons_images,path)
                        balloons_group.add(balloons)
                        map.spawned_balloons += 1
                        last_balloon_spawn = pygame.time.get_ticks()

            if map.check_wave_complete() :
                map.money += 100
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
                    screen.blit(coin_image,(1140,230))
                    draw_text("$100","white","black",1190,240)
                    if upgrademonkey.draw(screen):
                        if map.money >= upgrade_monkey:
                            selected_monkey.upgrade()
                            map.money -= upgrade_monkey
                            print(selected_monkey.upgrade_level)
                screen.blit(coin_image,(1140,150))
                match selected_monkey.upgrade_level:
                        case 1:
                            sell_monkey = 120
                        case 2:
                            sell_monkey = 200
                        case 3:
                            sell_monkey = 280
                        case 4:
                            sell_monkey = 360
                draw_text(f"${sell_monkey}","white","black",1190,160)
                if sellbutton.draw(screen):
                    selected_monkey.sell_monkey()
                    selected_monkey = None
                    map.money += sell_monkey
        else:
            pygame.draw.rect(screen,"dodgerblue",(300,200,500,300),border_radius = 30)
            if game_outcome == -1:
                draw_text("GAME OVER","red","black",470,230)
                draw_text("Restart","white","black",490,440)

            elif game_outcome == 1:
                draw_text(" YOU WIN !","yellow","black",480,230)
                draw_text("Restart","white","black",490,440)

            if restartbutton.draw(screen):
                game_over = False
                wave_started = False
                put_monkey = False
                selected_monkey = None
                last_balloon_spawn = pygame.time.get_ticks()
                map = Map(map_image)
                map.process_balloons()

                balloons_group.empty()
                monkey_group.empty()

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
                                monkey = Monkey(monkey_sheet,mouse_position,pop_sound_effect)
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
                draw_text("Invalid Placement","red","black",450,75)
            else:
                invalid_time = None  
        
        def name():
            if map.level <= 19:
                return map.level + 1
            else:
                return 20

        screen.blit(health_image,(30,15))
        screen.blit(coin_image,(150,10))
        draw_text(str(map.health),"white","black",70,20)
        draw_text("$"+ str(map.money),"white","black",200,20)
        draw_text("Wave " + str(name()) + " / 20","yellow","black",500,20)
        # pygame.draw.lines(screen,"grey0", False, path)
        pygame.display.update()
        clock.tick(60)

    pygame.quit()

game()