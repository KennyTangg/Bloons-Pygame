import pygame
from monkey import Monkey
from balloons import Balloons
from map import Map
from monkeyMenu import MonkeyMenu

# --- Constants ---
WIDTH, HEIGHT = 1280, 720
FPS = 60
CAPTION = "Tower Defense Window"

# --- Initialize Pygame ---
pygame.init()
pygame.mixer.init()
pygame.display.set_caption(CAPTION)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font("assets/font/Pixeltype.ttf", 50)

# --- Sounds ---
pop_sound_effect = pygame.mixer.Sound("assets/sound/popSound.mp3") # Sound played when a balloon pops
pop_sound_effect.set_volume(0.5)

# --- Load Map Image ---
map_image = pygame.image.load("assets/Images/Map/map2.png").convert()

# --- Load Monkey Assets ---
monkey_image = pygame.image.load("assets/Images/Monkey/Monkey.png").convert_alpha()
monkey_sheet = pygame.image.load("assets/Images/Monkey/animationMonkey-sheet.png").convert_alpha()
upgrade_monkey_image = pygame.image.load("assets/Images/GameMenu/upgradeMonkey.png").convert_alpha()

# --- Load Balloon Assets ---
balloons_images = {
    "weak": pygame.image.load("assets/Images/Balloons/Balloons_Red.png").convert_alpha(),
    "medium": pygame.image.load("assets/Images/Balloons/Balloons_Blue.png").convert_alpha(),
    "strong": pygame.image.load("assets/Images/Balloons/Balloons_Green.png").convert_alpha(),
    "very strong": pygame.image.load("assets/Images/Balloons/Balloons_Yellow.png").convert_alpha()
}

# --- Load Menu Button Assets ---
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

# --- Game Path ---
GAME_PATH = [
    (-50, 280), (490, 280), (490, 135), (320, 135), (320, 565),
    (150, 565), (150, 415), (650, 415), (650, 260),
    (750, 260), (750, 530), (460, 530), (460, 750)
]

# -----------------------------------------------

class TowerDefenseGame:
    def __init__(self):
        # --- Game state variables ---
        self.running = True
        self.game_over = False
        self.wave_started = False
        self.put_monkey = False
        self.selected_monkey = None
        self.invalid_time = None
        self.last_balloon_spawn = pygame.time.get_ticks() # track the time since the game start 
        self.buy_monkey = 150
        self.upgrade_monkey = 100
        self.sell_monkey = 120
        self.spawn_cooldown = 500
        self.message_duration = 2000
        self.total_wave = 20
        self.game_outcome = 0

        # Map and groups
        self.map_instance = Map(map_image)
        self.map_instance.process_balloons() 
        self.balloons_group = pygame.sprite.Group()
        self.monkey_group = pygame.sprite.Group()

        # Set up menus
        self.monkeymenu = MonkeyMenu(monkeymenu_button, 1000, 10, True)
        self.cancelmenu = MonkeyMenu(cancelmenu_button, 1150, 60, True)
        self.upgrademonkey = MonkeyMenu(upgrade_monkey_button, 1010, 240, True)
        self.sellbutton = MonkeyMenu(sell_button, 1030, 160, True)
        self.startbutton = MonkeyMenu(start_button, 1150, 620, True)
        self.fastforwardbutton = MonkeyMenu(fast_forward_button, 1150, 620, False)
        self.restartbutton = MonkeyMenu(restart_button, 500, 330, True)


    def handle_events(self):
        """Handle user input and quit events."""
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # Stop the game loop when closing the game
                    self.running = False
                # if mouse button is pressed and the mouse button 
                # that is getting pressed is Left mouse button
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_position = pygame.mouse.get_pos()
                    if mouse_position[0] < 950 and mouse_position[1] > 75:
                        self.clear_select()
                        if self.put_monkey:
                            # able to put monkey if there is enough money
                            if self.map_instance.money >= self.buy_monkey:
                                if Map.valid_position(mouse_position[0],mouse_position[1]) == True:
                                    monkey = Monkey(monkey_sheet,mouse_position,pop_sound_effect)
                                    self.monkey_group.add(monkey)
                                    self.map_instance.money -= self.buy_monkey
                                else:
                                    self.invalid_time = pygame.time.get_ticks() 
                                    self.draw_text("Invalid Placement","red","black",500,75)
                        else:
                            self.selected_monkey = self.select_monkey(mouse_position)

    def draw_text(self,text, text_color, outline_color, x, y):
        """Draws text with an outline effect."""
        # the width of the outline
        outline_width = 2
        for i in range(-outline_width, outline_width + 1):
            for j in range(-outline_width, outline_width + 1):
                if i != 0 or j != 0:
                    outline_text = font.render(text, True, outline_color)
                    screen.blit(outline_text, (x + i, y + j))
        txt = font.render(text, True, text_color)
        screen.blit(txt, (x, y))

    def select_monkey(self, mouse_position):
        """Selects a monkey at the given mouse position."""
        for monkey in self.monkey_group:
            # if the mouse position is inside the monkey rectangle, it returns true
            if monkey.rect.collidepoint(mouse_position):
                monkey.selected = True 
                return monkey
        return None

    def clear_select(self):
        """Clears selection from all monkeys."""
        for monkey in self.monkey_group:
            monkey.selected = False

    def name(self):
        """Determines the wave number for display."""
        # showing current wave number
        if self.map_instance.level <= 19:
            return self.map_instance.level + 1
        else:
            return 20
        
    def process_game_logic(self):
        """Runs core game state logic before rendering and event handling."""
        if self.game_over == False:
            # Check for game-over conditions
            # if the health is 0 , game over
            if self.map_instance.health <= 0:
                self.game_over = True
                self.game_outcome = -1  # lose outcome
            # if complete all the wave, win
            if self.map_instance.level + 1 > self.total_wave:
                self.game_over = True
                self.game_outcome = 1  # win outcome

            # Update groups
            self.balloons_group.update(self.map_instance)
            self.monkey_group.update(self.balloons_group, self.map_instance)
            
            # display map and balloons
            self.map_instance.draw(screen)
            self.balloons_group.draw(screen)
            
        # Handle balloon spawning 
        if self.game_over == False:
            if self.wave_started != True:
                # show start button if wave is not start yet
                if self.startbutton.draw(screen):
                    self.wave_started = True
            else:
                # normal game speed and if the fastforward button is hold the game will fast forward
                self.map_instance.game_speed = 1
                if self.fastforwardbutton.draw(screen):
                    self.map_instance.game_speed = 2
    
                # cooldown before next balloon come out
                if pygame.time.get_ticks() - self.last_balloon_spawn > (self.spawn_cooldown / self.map_instance.game_speed):
                    # displaying all the balloons inside the list
                    if self.map_instance.spawned_balloons < len(self.map_instance.balloon_list):
                        # get the balloon with the balloon stats from the map balloon list
                        balloon_type = self.map_instance.balloon_list[self.map_instance.spawned_balloons]
                        balloons = Balloons(balloon_type, balloons_images, GAME_PATH)
                        self.balloons_group.add(balloons)
                        self.map_instance.spawned_balloons += 1

                        # update to a new time, to restart the cooldown 
                        self.last_balloon_spawn = pygame.time.get_ticks()

            # Handle wave completion 
            if self.map_instance.check_wave_complete():
                # rewarding player with money
                self.map_instance.money += 100
                self.map_instance.level += 1

                # make sure every wave player, can prepare before the next wave
                self.wave_started = False

                self.last_balloon_spawn = pygame.time.get_ticks()
                self.map_instance.reset_wave()
                self.map_instance.process_balloons()

            # monkey in the monkey group
            for monkey in self.monkey_group:
                monkey.draw(screen)

            # the monkey menu is clicked , player can put the monkey
            if self.monkeymenu.draw(screen):
                self.put_monkey = True

            # if the player can place the monkey, they can sell the monkey as well
            if self.put_monkey:
                if self.cancelmenu.draw(screen):
                    self.put_monkey = False
                cursor_rect = monkey_image.get_rect()
                cursor_position = pygame.mouse.get_pos()
                cursor_rect.midbottom = cursor_position
                # displaying the monkey following the cursor position
                if cursor_position[0] <= 975:
                    screen.blit(monkey_image,cursor_rect)

            # if monkey is selected show range and monkey can be upgrade
            if self.selected_monkey:
                # if the level is not maxed the button, it will appear and show its cost
                if self.selected_monkey.upgrade_level < 4:
                    screen.blit(coin_image,(1140,230))
                    self.draw_text("$100","white","black",1190,240)
                    # if the upgrade button is pressed , upgrade the monkey by one level and reduce the money 
                    if self.upgrademonkey.draw(screen):
                        if self.map_instance.money >= self.upgrade_monkey:
                            self.selected_monkey.upgrade()
                            self.map_instance.money -= self.upgrade_monkey
                screen.blit(coin_image,(1140,150))
                # The money get increase the higher the level 
                match self.selected_monkey.upgrade_level:
                        case 1:
                            self.sell_monkey = 120
                        case 2:
                            self.sell_monkey = 200
                        case 3:
                            self.sell_monkey = 280
                        case 4:
                            self.sell_monkey = 360
                self.draw_text(f"${self.sell_monkey}","white","black",1190,160)
                # if the sell button is clicked, monkey get remove and player get money
                if self.sellbutton.draw(screen):
                    self.selected_monkey.sell_monkey()
                    self.selected_monkey = None
                    self.map_instance.money += self.sell_monkey
        else:
            # a box with a blue color to display text more 
            pygame.draw.rect(screen,"dodgerblue",(300,200,500,300),border_radius = 30)
            # Game over screen
            if self.game_outcome == -1:
                self.draw_text("GAME OVER","red","black",470,230)
                self.draw_text("Restart","white","black",490,440)
            # Win screen
            elif self.game_outcome == 1:
                self.draw_text(" YOU WIN !","yellow","black",480,230)
                self.draw_text("Restart","white","black",490,440)

            if self.restartbutton.draw(screen):
                # if the restart button is clicked restarting the game
                self.game_over = False
                self.wave_started = False
                self.put_monkey = False
                self.selected_monkey = None
                self.last_balloon_spawn = pygame.time.get_ticks()
                self.map_instance = Map(map_image)
                self.map_instance.process_balloons()

                # empty the group for balloon and monkey
                self.balloons_group.empty()
                self.monkey_group.empty()

    def update(self):
        """ Text delay """
        # give some time for the text before stop displaying on the screen 
        if self.invalid_time != None:
            current_time = pygame.time.get_ticks()
            if current_time - self.invalid_time < self.message_duration:
                self.draw_text("Invalid Placement","red","black",450,75)
            else:
                self.invalid_time = None  

    def draw(self):
        # displaying health and coin images 
        screen.blit(health_image,(30,15))
        screen.blit(coin_image,(150,10))

        # displaying the value of health and coin as well as the number of wave
        self.draw_text(str(self.map_instance.health),"white","black",70,20)
        self.draw_text("$"+ str(self.map_instance.money),"white","black",200,20)
        self.draw_text("Wave " + str(self.name()) + " / 20","yellow","black",500,20)

        # # a line showing the game path 
        # pygame.draw.lines(screen,"grey0", False, GAME_PATH)

    def main_loop(self):
        """Main game loop."""
        pygame.mixer.music.load("assets/sound/gameMusic.mp3")
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.1)
        # Loop the game 
        while self.running:
            self.process_game_logic()
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.update()
            # limit the screen to have 60 FPS
            clock.tick(FPS)
        # if the loop is quit / break, close the game 
        pygame.quit()


# Checking if the script is run directly or imported as a module
if __name__ == "__main__":
    game = TowerDefenseGame()
    game.main_loop()