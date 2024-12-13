import pygame
from monkey import Monkey
from balloons import Balloons
from map import Map
from monkeyMenu import MonkeyMenu

# --- Constants ---
WIDTH, HEIGHT = 1280, 720
FPS = 60
CAPTION = "Tower Defense Window"
FONT_SIZE = 50
POP_SOUND_VOLUME = 0.5
MUSIC_VOLUME = 0.1
BUY_MONKEY_COST = 150
UPGRADE_MONKEY_COST = 100
SELL_MONKEY_BASE_COST = 120
SELL_MONKEY_LVL2_COST = 200
SELL_MONKEY_LVL3_COST = 280
SELL_MONKEY_LVL4_COST = 360
SPAWN_COOLDOWN = 500
MESSAGE_DURATION = 2000
TOTAL_WAVE = 20
GAME_OUTCOME = 0
LOSE = -1
WIN = 1
GAME_PATH = [
    (-50, 280), (490, 280), (490, 135), (320, 135), (320, 565),
    (150, 565), (150, 415), (650, 415), (650, 260),
    (750, 260), (750, 530), (460, 530), (460, 750)
]

# --- Initialize Pygame ---
pygame.init()
pygame.mixer.init()
pygame.display.set_caption(CAPTION)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font("assets/font/Pixeltype.ttf", FONT_SIZE)

# --- Sounds ---
pop_sound_effect = pygame.mixer.Sound("assets/sound/popSound.mp3") 
pop_sound_effect.set_volume(POP_SOUND_VOLUME)

# --- Load Map Image ---
map_image = pygame.image.load("assets/Images/Map/map2.png").convert()

# --- Load Monkey Assets ---
monkey_image = pygame.image.load("assets/Images/Monkey/Monkey.png").convert_alpha()
monkey_sheet = pygame.image.load("assets/Images/Monkey/animationMonkey-sheet.png").convert_alpha()
upgrade_monkey_image = pygame.image.load("assets/Images/GameMenu/upgradeMonkey.png").convert_alpha()

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
music_on = pygame.image.load("assets/Images/GameMenu/musicOn.png").convert_alpha()
music_off = pygame.image.load("assets/Images/GameMenu/musicOff.png").convert_alpha()

# --- Load Balloon Assets ---
balloons_images = {
    "weak": pygame.image.load("assets/Images/Balloons/Balloons_Red.png").convert_alpha(),
    "medium": pygame.image.load("assets/Images/Balloons/Balloons_Blue.png").convert_alpha(),
    "strong": pygame.image.load("assets/Images/Balloons/Balloons_Green.png").convert_alpha(),
    "very strong": pygame.image.load("assets/Images/Balloons/Balloons_Yellow.png").convert_alpha()
}


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
        self.music_state = None

        # Track the time when game start 
        self.last_balloon_spawn = pygame.time.get_ticks() 

        self.buy_monkey = BUY_MONKEY_COST
        self.upgrade_monkey = UPGRADE_MONKEY_COST
        self.sell_monkey = SELL_MONKEY_BASE_COST
        self.spawn_cooldown = SPAWN_COOLDOWN
        self.message_duration = MESSAGE_DURATION
        self.total_wave = TOTAL_WAVE
        self.game_outcome = GAME_OUTCOME
        self.music_volume = MUSIC_VOLUME

        # Set up map and processing balloons
        self.map_instance = Map(map_image)
        self.map_instance.process_balloons() 

        # Set the groups
        self.balloons_group = pygame.sprite.Group()
        self.monkey_group = pygame.sprite.Group()

        # Set up menus
        self.monkeymenu = MonkeyMenu(monkeymenu_button, 1000, 10, True)
        self.cancelmenu = MonkeyMenu(cancelmenu_button, 1150, 60, True)
        self.upgrademonkey = MonkeyMenu(upgrade_monkey_button, 1010, 240, True)
        self.sellbutton = MonkeyMenu(sell_button, 1030, 160, True)
        self.restartbutton = MonkeyMenu(restart_button, 500, 330, True)
        self.startbutton = MonkeyMenu(start_button, 1150, 620, True)
        self.fastforwardbutton = MonkeyMenu(fast_forward_button, 1150, 620, False)
        self.musicon = MonkeyMenu(music_on,930,10,True)
        self.musicoff = MonkeyMenu(music_off,930,10,True)
        


    def handle_events(self):
        """Handle user input and quit events."""
        for event in pygame.event.get():
                # Stop the game loop when closing the game
                if event.type == pygame.QUIT:
                    self.running = False

                # If mouse button is pressed and the mouse button that is getting pressed is Left mouse button
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_position = pygame.mouse.get_pos() # Getting mouse cursor Position
                    if mouse_position[0] < 950 and mouse_position[1] > 75:
                        self.clear_select()
                        if self.put_monkey == True:

                            # Able to put monkey if there is enough money
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

        # The width of the outline
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
        
    def handle_main_game(self):
        """Runs core game state logic before rendering and event handling."""

        # Check for game-over conditions
        if self.game_over == False:

            # If the health is 0 , game over
            if self.map_instance.health <= 0:
                self.game_over = True
                self.game_outcome = LOSE 

            # If complete all the wave, win
            if self.map_instance.level + 1 > self.total_wave:
                self.game_over = True
                self.game_outcome = WIN 

            # Update groups
            self.balloons_group.update(self.map_instance)
            self.monkey_group.update(self.balloons_group, self.map_instance)
            
            # Display map and balloons
            self.map_instance.draw(screen)
            self.balloons_group.draw(screen)
            
        # Handle balloon spawning 
        if self.game_over == False:
            if self.wave_started != True:
                # Show start button if wave is not start yet
                if self.startbutton.draw(screen):
                    self.wave_started = True

            else:
                # Normal game speed and if the fastforward button is hold the game will fast forward
                self.map_instance.game_speed = 1
                if self.fastforwardbutton.draw(screen):
                    self.map_instance.game_speed = 2
    
                # Cooldown before next balloon come out
                if pygame.time.get_ticks() - self.last_balloon_spawn > (self.spawn_cooldown / self.map_instance.game_speed):
                    
                    # Displaying all the balloons inside the list
                    if self.map_instance.spawned_balloons < len(self.map_instance.balloon_list):

                        # Get the balloon with the balloon stats from the map balloon list
                        balloon_type = self.map_instance.balloon_list[self.map_instance.spawned_balloons]
                        balloons = Balloons(balloon_type, balloons_images, GAME_PATH)
                        self.balloons_group.add(balloons)
                        self.map_instance.spawned_balloons += 1

                        # Update to a new time, to restart the cooldown 
                        self.last_balloon_spawn = pygame.time.get_ticks()

            # Handle wave completion 
            if self.map_instance.check_wave_complete():

                # Rewarding player with money
                self.map_instance.money += 100
                self.map_instance.level += 1

                # Making sure player can prepare before the next wave
                # self.wave_started = False

                # Reset time tracking, wave and processing balloons 
                self.last_balloon_spawn = pygame.time.get_ticks()
                self.map_instance.reset_wave()
                self.map_instance.process_balloons()

            # If the sound image is pressed the music will mute 
            if self.music_state == None:
                if self.musicon.draw(screen):
                    # mute music
                    self.music_volume = 0
                    pygame.mixer.music.set_volume(self.music_volume)
                    pop_sound_effect.set_volume(self.music_volume)
                    
                    # remove the music on image
                    self.musicon.remove_menu()

                    # displaying the music off image
                    self.musicoff.draw(screen)
                    self.music_state = False

            # If the sound image is pressed the music will unmute 
            elif self.music_state == False:
                if self.musicoff.draw(screen):
                    # unmute music
                    self.music_volume = 0.1
                    pygame.mixer.music.set_volume(self.music_volume)
                    pop_sound_effect.set_volume(self.music_volume * 5)

                    # remove the music off image
                    self.musicoff.remove_menu()

                    # displaying the music on image
                    self.musicon.draw(screen)
                    self.music_state = None

            # Displaying each monkey from the monkey group to the screen
            for monkey in self.monkey_group:
                monkey.draw(screen)

            # When the menu is clicked, player can place the monkey
            if self.monkeymenu.draw(screen):
                self.put_monkey = True

            # When the player can place the monkey, they can sell the monkey as well
            if self.put_monkey == True:
                if self.cancelmenu.draw(screen) == True:
                    self.put_monkey = False
                cursor_rect = monkey_image.get_rect()
                cursor_position = pygame.mouse.get_pos()
                cursor_rect.midbottom = cursor_position
                # Displaying the monkey 
                if cursor_position[0] <= 975:
                    screen.blit(monkey_image,cursor_rect)

            # When monkey is selected, range is visible and monkey can be upgraded
            if self.selected_monkey != None:

                # If the level is not maxed the button, it will appear and show its cost
                if self.selected_monkey.upgrade_level < 4:
                    screen.blit(coin_image,(1140,230))
                    self.draw_text("$100","white","black",1190,240)

                    # If the upgrade button is pressed , upgrade the monkey by one level and reduce the money 
                    if self.upgrademonkey.draw(screen):
                        if self.map_instance.money >= self.upgrade_monkey:
                            self.selected_monkey.upgrade()
                            self.map_instance.money -= self.upgrade_monkey

                # Displaying coin image to the screen
                screen.blit(coin_image,(1140,150))

                # The money get increase the higher the level 
                match self.selected_monkey.upgrade_level:
                        case 1:
                            self.sell_monkey = SELL_MONKEY_BASE_COST
                        case 2:
                            self.sell_monkey = SELL_MONKEY_LVL2_COST
                        case 3:
                            self.sell_monkey = SELL_MONKEY_LVL3_COST
                        case 4:
                            self.sell_monkey = SELL_MONKEY_LVL4_COST

                # Displaying the cost to the screen
                self.draw_text(f"${self.sell_monkey}","white","black",1190,160)

                # If the sell button is clicked, monkey get remove and player get money
                if self.sellbutton.draw(screen):
                    self.selected_monkey.sell_monkey()
                    self.selected_monkey = None
                    self.map_instance.money += self.sell_monkey

        else:
            pygame.draw.rect(screen,"dodgerblue",(300,200,500,300),border_radius = 30)

            # Game over screen
            if self.game_outcome == -1:
                self.draw_text("GAME OVER","red","black",470,230)
                self.draw_text("Restart","white","black",490,440)

            # Win screen
            elif self.game_outcome == 1:
                self.draw_text(" YOU WIN !","yellow","black",480,230)
                self.draw_text("Restart","white","black",490,440)

            # If player click the restart button, it will restart the game
            if self.restartbutton.draw(screen):
                
                # Restarting Attributes
                self.game_over = False
                self.wave_started = False
                self.put_monkey = False
                self.selected_monkey = None
                self.last_balloon_spawn = pygame.time.get_ticks()
                self.map_instance = Map(map_image)
                self.map_instance.process_balloons()

                # Empty the group for balloon and monkey
                self.balloons_group.empty()
                self.monkey_group.empty()

    def handle_text_delay(self):
        """ Handling text delay """

        # checking if the time has value or not 
        if self.invalid_time != None:
            current_time = pygame.time.get_ticks()

            #give delay before the text stop displaying
            if current_time - self.invalid_time < self.message_duration:
                self.draw_text("Invalid Placement","red","black",450,75)
            else:
                self.invalid_time = None  

    def render_ui(self):
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
        pygame.mixer.music.set_volume(self.music_volume)

        # Loop the game 
        while self.running:
            self.handle_main_game()
            self.handle_events()
            self.handle_text_delay()
            self.render_ui()
            pygame.display.update()

            # limit the screen to have 60 FPS
            clock.tick(FPS)

        pygame.quit()


# Checking if the script is run directly or imported as a module
if __name__ == "__main__":
    game = TowerDefenseGame()
    game.main_loop()