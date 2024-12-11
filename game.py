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

# --- Define Game Path ---
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
        self.last_balloon_spawn = pygame.time.get_ticks()
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
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_position = pygame.mouse.get_pos()
                    if mouse_position[0] < 950 and mouse_position[1] > 75:
                        print('test1')
                        self.selected_monkey = None
                        self.clear_select()
                        if self.put_monkey:
                            if self.map_instance.money >= self.buy_monkey:
                                if Map.valid_position(mouse_position[0],mouse_position[1]) == True:
                                    monkey = Monkey(monkey_sheet,mouse_position,pop_sound_effect)
                                    self.monkey_group.add(monkey)
                                    self.map_instance.money -= self.buy_monkey
                                else:
                                    self.invalid_time = pygame.time.get_ticks() 
                                    self.draw_text("Invalid Placement","red","black",500,75)
                                    print("Not Valid position")
                        else:
                            self.selected_monkey = self.select_monkey(mouse_position)
                            if self.selected_monkey:
                                print(f"Selected monkey di posisi {mouse_position}")

    def draw_text(self,text, text_color, outline_color, x, y):
        """Draws text with an outline effect."""
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
        if self.map_instance.level <= 19:
            return self.map_instance.level + 1
        else:
            return 20
        
    def process_game_logic(self):
        """Runs core game state logic before rendering and event handling."""
        if not self.game_over:
            # Check for game-over conditions
            if self.map_instance.health <= 0:
                self.game_over = True
                self.game_outcome = -1  # lose outcome
            if self.map_instance.level + 1 > self.total_wave:
                self.game_over = True
                self.game_outcome = 1  # win outcome

            # Update groups
            self.balloons_group.update(self.map_instance)
            self.monkey_group.update(self.balloons_group, self.map_instance)
            
            self.map_instance.draw(screen)
            self.balloons_group.draw(screen)
            
        # Handle balloon spawning logic
        if not self.game_over:
            if not self.wave_started:
                if self.startbutton.draw(screen):
                    self.wave_started = True
            else:
                self.map_instance.game_speed = 1
                if self.fastforwardbutton.draw(screen):
                    self.map_instance.game_speed = 2

                if pygame.time.get_ticks() - self.last_balloon_spawn > (self.spawn_cooldown / self.map_instance.game_speed):
                    if self.map_instance.spawned_balloons < len(self.map_instance.balloon_list):
                        balloon_type = self.map_instance.balloon_list[self.map_instance.spawned_balloons]
                        balloons = Balloons(balloon_type, balloons_images, GAME_PATH)
                        self.balloons_group.add(balloons)
                        self.map_instance.spawned_balloons += 1
                        self.last_balloon_spawn = pygame.time.get_ticks()

            # Handle wave completion logic
            if self.map_instance.check_wave_complete():
                self.map_instance.money += 100
                self.map_instance.level += 1
                self.wave_started = False
                self.last_balloon_spawn = pygame.time.get_ticks()
                self.map_instance.reset_wave()
                self.map_instance.process_balloons()

            for monkey in self.monkey_group:
                monkey.draw(screen)

            if self.monkeymenu.draw(screen):
                self.put_monkey = True
        
            if self.put_monkey:
                if self.cancelmenu.draw(screen):
                    self.put_monkey = False
                    print("Cancel")
                cursor_rect = monkey_image.get_rect()
                cursor_position = pygame.mouse.get_pos()
                cursor_rect.midbottom = cursor_position
                if cursor_position[0] <= 975:
                    screen.blit(monkey_image,cursor_rect)

            if self.selected_monkey:
                if self.selected_monkey.upgrade_level < 4:
                    screen.blit(coin_image,(1140,230))
                    self.draw_text("$100","white","black",1190,240)
                    if self.upgrademonkey.draw(screen):
                        if self.map_instance.money >= self.upgrade_monkey:
                            self.selected_monkey.upgrade()
                            self.map_instance.money -= self.upgrade_monkey
                            print(self.selected_monkey.upgrade_level)
                screen.blit(coin_image,(1140,150))
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
                if self.sellbutton.draw(screen):
                    self.selected_monkey.sell_monkey()
                    self.selected_monkey = None
                    self.map_instance.money += self.sell_monkey
        else:
            pygame.draw.rect(screen,"dodgerblue",(300,200,500,300),border_radius = 30)
            if self.game_outcome == -1:
                self.draw_text("GAME OVER","red","black",470,230)
                self.draw_text("Restart","white","black",490,440)

            elif self.game_outcome == 1:
                self.draw_text(" YOU WIN !","yellow","black",480,230)
                self.draw_text("Restart","white","black",490,440)

            if self.restartbutton.draw(screen):
                self.game_over = False
                self.wave_started = False
                self.put_monkey = False
                self.selected_monkey = None
                self.last_balloon_spawn = pygame.time.get_ticks()
                self.map_instance = Map(map_image)
                self.map_instance.process_balloons()

                self.balloons_group.empty()
                self.monkey_group.empty()

    def update(self):
        """Game logic updates."""
        if self.invalid_time is not None:
            current_time = pygame.time.get_ticks()
            if current_time - self.invalid_time < self.message_duration:
                self.draw_text("Invalid Placement","red","black",450,75)
            else:
                self.invalid_time = None  

    def draw(self):
        screen.blit(health_image,(30,15))
        screen.blit(coin_image,(150,10))
        self.draw_text(str(self.map_instance.health),"white","black",70,20)
        self.draw_text("$"+ str(self.map_instance.money),"white","black",200,20)
        self.draw_text("Wave " + str(self.name()) + " / 20","yellow","black",500,20)
        pygame.draw.lines(screen,"grey0", False, GAME_PATH)

    def main_loop(self):
        """Main game loop."""
        pygame.mixer.music.load("assets/sound/gameMusic.mp3")
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.1)
        
        while self.running:
            self.process_game_logic()
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.update()
            clock.tick(FPS)

        pygame.quit()


# Main execution
if __name__ == "__main__":
    game = TowerDefenseGame()
    game.main_loop()