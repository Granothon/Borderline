#Project Borderline: 2d Space shooter
import pygame as pg
from pygame import Color
import random as r
import math
from time import time

from pygame.constants import BLEND_RGB_ADD

class Main():
    def __init__(self):
        self.reset()
    
    def reset(self):
        pg.init()
        #set screen size
        #game screen
        self.scr = pg.display.set_mode((864, 1080))
        #whole screen including gui
        #self.display = pg.display.set_mode((1980, 1080))
        
        #get width and height
        self.scr_w, self.scr_h = pg.display.get_surface().get_size()

        #set game display name and icon
        pg.display.set_caption("Borderline")
        icon = pg.image.load('assets/ships/ship 01/1.png').convert_alpha()
        pg.display.set_icon(icon)

        #set fps
        self.clock = pg.time.Clock()
        self.last_time = time()
        self.fps = 60
        
        #set background
        self.bg = pg.image.load('assets/background/stage-back.png').convert()
        self.bg_back_layer = pg.image.load('assets/background/layer_back.png').convert_alpha()
        self.bg_middle_layer = pg.image.load('assets/background/layer_mid.png').convert_alpha()
        self.bg_front_layer = pg.image.load('assets/background/layer_front.png').convert_alpha()
        self.bg = pg.transform.scale(self.bg, (self.scr_w, self.scr_h))
        self.bg_back_layer = pg.transform.scale(self.bg_back_layer, (self.scr_w, self.scr_h))
        self.bg_middle_layer = pg.transform.scale(self.bg_middle_layer, (self.scr_w, self.scr_h))
        self.bg_front_layer = pg.transform.scale(self.bg_front_layer, (self.scr_w, self.scr_h))

        #position of background layers at the beginning
        self.bg_i = 0 
        self.bg_back_i = 0
        self.bg_middle_i = 0
        self.bg_front_i = 0

        #set game state
        self.game_over = False
        self.game_end = False
        
        #sprite groups
        self.menu_group = pg.sprite.Group()
        self.p1_group = pg.sprite.Group()
        self.enemy_group = pg.sprite.Group()
        self.boss_group = pg.sprite.Group()
        self.bullet_group = pg.sprite.Group()
        self.bolt_group = pg.sprite.Group()
        self.eyes_of_ra_group = pg.sprite.Group()
        self.explosion_group = pg.sprite.Group()
        self.power_up_group = pg.sprite.Group()

        #particle groups
        self.particle_bullet_group = []

        #load player ship images
        p1_size = 58
        thrust_size = 24
        self.p1_sprites = []
        self.p1_thrust_sprites = []

        for i in range(1,4):
            image = pg.image.load(f"assets/ships/ship 01/{i}.png").convert_alpha()
            image = pg.transform.scale(image, (p1_size, p1_size))
            self.p1_sprites.append(image)
        
        for i in range(1,3):
            image = pg.image.load(f"assets/ships/thrust/01/{i}.png").convert_alpha()
            image = pg.transform.scale(image, (thrust_size, thrust_size))
            self.p1_thrust_sprites.append(image)
        
        self.p1_image_menu = pg.image.load("assets/ships/ship 01/ship_menu.png").convert_alpha()
        self.p1_image_menu = pg.transform.scale(self.p1_image_menu, (150, 150))
        self.hp_heart = pg.image.load("assets/player/heart.png").convert_alpha()
        self.hp_heart = pg.transform.scale(self.hp_heart, (30 * 1.22, 30))
        
        #init player
        p1_starting_coords = (self.scr_w // 2, self.scr_h - (self.scr_h // 10))
        self.p1 = Player(self.p1_sprites, p1_starting_coords)

        #init player thrusters
        offset_x = -11.95
        offset_y = 9.5
        p1_thrust_coords = (self.p1.rect.center[0] + offset_x, self.p1.rect.center[1] + offset_y)
        self.p1_thrusters = P1_thrusters(self.p1_thrust_sprites, p1_thrust_coords)
        #add to sprite group
        self.p1_group.add(self.p1, self.p1_thrusters)

        #add start animation
        self.menu_animation = Ship_animation_menu(self.p1_image_menu, -100, (self.scr_w // 2) - 200)
        self.menu_group.add(self.menu_animation)
        #instructions page
        self.instructions = True
        self.game_begin = False #this will wait for instructions to be passed first
        self.instructions_start_cd = 1600
        self.inst_txt_idx = 0 
        self.inst_cd = 5000
        
        #load enemy ship images
        #fighter:
        self.e1_sprites = []
        e1_size = 90
        for i in range(1,4):
            image = pg.image.load(f'assets/enemy_ships/fighter/{i}.png').convert_alpha()
            image = pg.transform.scale(image, (e1_size, e1_size))
            self.e1_sprites.append(image)
        self.e1_spawn_cooldown = 2750
        self.e1_spawn_last = pg.time.get_ticks()
        self.e1_spawn_last_coords = None

        #worm:
        self.e2_sprites = []
        e2_size = 90
        for i in range(1,5):
            image = pg.image.load(f'assets/enemy_ships/worm/{i}.png').convert_alpha()
            image = pg.transform.scale(image, (e2_size, e2_size))
            self.e2_sprites.append(image)
        self.e2_spawn_cooldown = 2000
        self.e2_spawn_last = pg.time.get_ticks()

        #droid:
        self.e3_sprites = []
        e3_size = 90
        for i in range(1,5):
            image = pg.image.load(f'assets/enemy_ships/droid/{i}.png').convert_alpha()
            image = pg.transform.scale(image, (e3_size, e3_size))
            self.e3_sprites.append(image)
        self.e3_spawn_cooldown = 1000
        self.e3_spawn_last = pg.time.get_ticks()

        #boss:
        self.boss_spawned = False
        self.escape_pod = None
        self.boss_dead = False
        self.boss_ship_sprites = []
        self.boss_ray_sprites = []
        self.boss_thrust_sprites = []
        self.boss_color = (184, 31, 11)
        boss_size = 400
        ray_size = 262
        thrust_size = 262
        self.boss_escape_pod_img = pg.image.load(f'assets/enemy_ships/boss/ship/escape_pod.png').convert_alpha()
        self.boss_escape_pod_img = pg.transform.scale(self.boss_escape_pod_img, (boss_size // 10, (boss_size // 10) * 2))
        self.boss_pattern_2_damaged_img = pg.image.load(f'assets/enemy_ships/boss/ship/2_damaged.png').convert_alpha()
        self.boss_pattern_2_damaged_img = pg.transform.scale(self.boss_pattern_2_damaged_img, (boss_size, boss_size))
        for i in range(1,6):
            image = pg.image.load(f'assets/enemy_ships/boss/ship/{i}.png').convert_alpha()
            image = pg.transform.scale(image, (boss_size, boss_size))
            self.boss_ship_sprites.append(image)
        for i in range(1,12):
            image = pg.image.load(f'assets/enemy_ships/boss/rays/{i}.png').convert_alpha()
            image = pg.transform.scale(image, (ray_size, ray_size * 3.5))
            self.boss_ray_sprites.append(image)
        for i in range(1,3):
            image = pg.image.load(f'assets/enemy_ships/boss/thrust/{i}.png').convert_alpha()
            image = pg.transform.scale(image, (thrust_size, thrust_size * 0.375))
            self.boss_thrust_sprites.append(image)

        #add boss
        self.e_boss = Boss(self.boss_ship_sprites, self.scr_w // 2, -180)
        
        #load bullet image
        bullet_size = 6
        self.bullet_sprites = []
        for i in range(1,3):
            image = pg.image.load(f'assets/bolts/bullet_{i}.png').convert_alpha()
            image = pg.transform.scale(image, (bullet_size, bullet_size * 2.6))
            self.bullet_sprites.append(image)
    
        #load bolt image
        bolt_size = 15
        self.bolt_sprites = []
        for i in range(1,3):
            image = pg.image.load(f'assets/bolts/{i}.png').convert_alpha()
            image = pg.transform.scale(image, (bolt_size, bolt_size))
            self.bolt_sprites.append(image)

        #load explosion animation
        self.explosion_sprites = []
        for i in range(1,8):
            image = (pg.image.load(f'assets/explosions/{i}.png')).convert_alpha()
            #maybe add scaling here
            self.explosion_sprites.append(image)
        
        #load weapon upgrade animation
        weapon_up_size = 50
        self.weapon_up_spawned = False
        self.weapon_up_spawned_2 = False
        self.weapon_up_sprites = []
        for i in range(1,3):
            image = (pg.image.load(f'assets/power_up/{i}.png')).convert_alpha()
            image = pg.transform.scale(image, (weapon_up_size, weapon_up_size))
            self.weapon_up_sprites.append(image)

        #set required score for different enemy spawnings
        self.e_spawn_points = [1000, 2500, 3500, 7000, 14000]

        #load font
        font_size = 30
        font_scores_size = 25
        font_credits_size = 35
        self.font = pg.font.Font("assets/fonts/Audiowide.ttf", font_size)
        self.font_scores = pg.font.Font("assets/fonts/Audiowide.ttf", font_scores_size)
        self.font_credits = pg.font.Font("assets/fonts/Audiowide.ttf", font_credits_size)

        #load highscore
        self.p1_highscore = self.highscore()
               
        #texts
        self.inst_txt = ["Welcome to Borderline, Commander", "Instructions:", "Movement: Arrow Keys", "Fire: Spacebar", "Good Luck!"]
        self.p1_score_text = self.font_scores.render(f"Score: {self.p1.score}", True, (255, 255, 255))
        self.p1_highscore_text = self.font_scores.render(f"Highscore: {self.p1_highscore}", True, (255, 255, 255))
        self.txt_escape_pod = "I'll get you later!!"
        self.txt_escape_pod_display = self.font_scores.render(self.txt_escape_pod, True, (255, 255, 255))
        self.txt_escape_pod_length = self.font_scores.size(f'{self.txt_escape_pod}')[0] // 2
        self.txt_game_over = "GAME OVER"
        self.txt_game_over_2 = "R - Restart"
        self.txt_game_over_display = self.font.render(self.txt_game_over, True, Color("white"))
        self.txt_game_over_2_display = self.font.render(self.txt_game_over_2, True, Color("white"))
        self.end_credits_txt = ["You Are Victorious!", "Game by:", "Risto Ruuskanen / Granothon#0892", "Assets by:", "Luis Zuno / @ansimuz", "Thank You For Playing!"]
        
        #end credits
        self.final_animation = False
        self.final_animation_last = None
        self.final_animation_cd = 1600
        self.final_animation_stop_player_movement = False
        self.end_credits = False
        self.end_credits_start_cd = 1600
        self.end_credits_txt_idx = 0 
        self.end_credits_cd = 7000
        self.game_over_last = None
        self.game_over_cd = 2000

        #sounds
        self.sound_flight = pg.mixer.Sound('assets/sounds/flight.wav')
        self.sound_bullet = pg.mixer.Sound('assets/sounds/bullet.wav')
        self.sound_bullet.set_volume(0.5)
        self.sound_weapon_up = pg.mixer.Sound('assets/sounds/weapon_up.wav')
        self.sound_explosion = pg.mixer.Sound('assets/sounds/explosion.wav')
        self.sound_escape_pod = pg.mixer.Sound('assets/sounds/escape_pod.wav')
        self.sound_victory = pg.mixer.Sound('assets/sounds/victory.wav')
        self.sound_victory_played = False

    #main menu
    def menu(self):
        while True:
            self.menu_process_events()
            self.menu_update()
        
    def menu_update(self):
        self.dt = self.clock.tick(self.fps) 
        self.scr.fill((0,0,0))
        self.scr.blit(self.bg, (0, 0))
        if len(self.menu_group) != 0:
            #start animation
            self.menu_group.draw(self.scr)
            self.menu_animation.update()
        
        else:
            self.run()       

        pg.display.flip()

    def menu_process_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    exit()
                elif event.key == pg.K_SPACE:
                    #skip the animation and start the game
                    self.run()

    #main loop
    def run(self):
        
        #background music
        pg.mixer.music.load('assets/sounds/patrol.wav')
        pg.mixer.music.play(0, 0.0, 0)

        #set time for instruction text
        self.instructions_start = pg.time.get_ticks()
        self.inst_last = pg.time.get_ticks()

        #set time for end credits text
        self.end_credits_start = None
        self.end_credits_last = pg.time.get_ticks()

        while True:
            self.process_events()
            self.update()
            self.draw()

    def highscore(self) ->str:
        '''to be used to check what highscore is at the beginning of the game and also to determine if a player made highscore at the end of the game'''
        try:
            with open ("assets/player/data.txt", "r") as hi:
                hscore = hi.read().strip()
                if self.p1.score > int(hscore):
                    hi.close()
                    #write new highscore to file
                    hscore = f"{self.p1.score}"
                    with open ("assets/player/data.txt", "w") as hi:
                        hi.write(hscore)
        except IOError:
            print ("The file doesn't exist. Creating a new file.")
            with open ("assets/player/data.txt", "w") as hi:
                hscore = "0"
                hi.write(hscore)
        return hscore

    def spawn_e1(self):
        offset_y = 50
        now = pg.time.get_ticks()
        if now - self.e1_spawn_last >= self.e1_spawn_cooldown:
            self.e1_spawn_last = now
            x_coords = self.p1.rect.center[0]
            if x_coords == self.e1_spawn_last_coords and x_coords + 150 < self.scr_w and x_coords -150 > 0:
                x_coords += r.choice([-150, 150])
            self.enemy_group.add(Fighter(self.e1_sprites, x_coords, - offset_y))
            self.e1_spawn_last_coords = x_coords

    def spawn_e2(self):
        offset_y = 50
        worm_size = 80
        now = pg.time.get_ticks()
        if now - self.e2_spawn_last >= self.e2_spawn_cooldown:
            self.e2_spawn_last = now
            location = r.choice(range(worm_size * 2, self.scr_w - worm_size, worm_size))
            self.enemy_group.add(Worm(self.e2_sprites, location, 0 - offset_y))
                
    def spawn_e3(self):
        now = pg.time.get_ticks()
        if now - self.e3_spawn_last >= self.e3_spawn_cooldown:
            self.e3_spawn_last = now
            location = r.choice([-50, self.scr_h + 50])
            if location < 0: spawn = "Left"
            else:
                spawn = "Right"
            self.enemy_group.add(Droid(self.e3_sprites, spawn, location, self.scr_h // 9))

    def spawn_boss(self): #\o/
        #spawns only once lol
        if not self.boss_spawned:
            self.boss_spawned = True
            self.boss_group.add(Boss_thrusters(self.boss_thrust_sprites), self.e_boss)
    
    def spawn_weapon_up(self):
        now = pg.time.get_ticks()
        if now - self.e2_spawn_last >= self.e2_spawn_cooldown:
            self.e2_spawn_last = now
            location = r.choice([-50,self.scr_w + 50])
            self.power_up_group.add(Weapon_up(self.weapon_up_sprites, location, self.scr_h // 4))

    def update_fps(self):
        fps = str(int(self.clock.get_fps()))
        fps_text = self.font_scores.render(f"{fps} fps", 1, pg.Color("white"))
        return fps_text
        
    def process_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    exit()
                if not Game.p1.alive:
                    if event.key == pg.K_r:
                        self.reset()
                        self.run()

    def update(self):
        self.dt = self.clock.tick(self.fps) 
        
        #setting delay for instruction text
        if not self.instructions and not self.game_begin:
            now = pg.time.get_ticks()
            if now - self.instructions_start >= self.instructions_start_cd:
                self.instructions = True

        #spawning of enemies
        if self.game_begin:
            if self.p1.score <= self.e_spawn_points[0]:
                self.spawn_e1()
            elif self.p1.score <= self.e_spawn_points[1]:
                if not self.weapon_up_spawned:
                    self.weapon_up_spawned = True
                    self.spawn_weapon_up() #spawn power u
                self.spawn_e2()
            if self.p1.score >= self.e_spawn_points[2] and self.p1.weapon_lvl == 0 and not self.weapon_up_spawned_2:
                    self.spawn_weapon_up() #second chance :D
                    self.weapon_up_spawned_2 = True
            elif self.p1.score <= self.e_spawn_points[2]:
                self.spawn_e1()
            elif self.p1.score <= self.e_spawn_points[3]:
                self.spawn_e2()
            elif self.p1.score <= self.e_spawn_points[4]:
                self.spawn_e1()
                self.spawn_e2()
            else:
                self.spawn_boss() #\o/
    
        #movement and removing of bullets
        for bullet in self.bullet_group:
            if bullet.rect.bottom < 0:
                bullet.kill()
            bullet.update()
        
        #movement and removing of bolts
        for bolt in self.bolt_group:
            if bolt.rect.top > self.scr_h:
                bolt.kill()
            bolt.update()
        
        #movement (animation) of eyes of Ra
        if self.boss_spawned and not self.boss_dead: 
            for bolt in self.eyes_of_ra_group:
                bolt.update()
        
        #movement and removing on enemies
        for enemy in self.enemy_group:
            if enemy.rect.top > self.scr_h: 
                enemy.kill()
            if enemy.name == "Escape pod":
                if enemy.rect.bottom + enemy.rect.height * 2 < 0:
                    self.final_animation_last = pg.time.get_ticks() #add for end animation / credits
                    enemy.kill()
            enemy.update()
       
        #movement and removing of boss(enemy)
        if self.boss_spawned:
            for enemy in self.boss_group:
                enemy.update()
        
        #movement and removing of player
        for player in self.p1_group:
            player.update()
            
        #explosions
        for explosion in self.explosion_group:
            explosion.update()
        
        #powerups
        for powerup in self.power_up_group:
            powerup.update()
    
    def circle_surf(self, color, radius):
        print (radius)
        surf = pg.Surface((radius * 2, radius * 2 ), pg.SRCALPHA) #make it transparent
        #make a glow circle
        pg.draw.circle(surf, color, (radius, radius), radius)
        return surf

    def draw(self):
        #draw the parallex background layers
        self.scr.fill((0,0,0))
        
        self.scr.blit(self.bg, (0, self.bg_i * self.dt))
        self.scr.blit(self.bg, (0, -self.scr_h + self.bg_i * self.dt))
        
        self.scr.blit(self.bg_back_layer, (0, self.bg_back_i * self.dt))
        self.scr.blit(self.bg_back_layer, (0, -self.scr_h + self.bg_back_i * self.dt))

        self.scr.blit(self.bg_middle_layer, (0, self.bg_middle_i * self.dt))
        self.scr.blit(self.bg_middle_layer, (0, -self.scr_h + self.bg_middle_i * self.dt))
        
        self.scr.blit(self.bg_front_layer, (0, self.bg_front_i * self.dt))
        self.scr.blit(self.bg_front_layer, (0, -self.scr_h + self.bg_front_i * self.dt))

        #get background scrolling
        if self.bg_i == self.scr_h:
            self.bg_i = 0
        if self.bg_back_i == self.scr_h:
            self.bg_back_i = 0
        if self.bg_middle_i == self.scr_h:
            self.bg_middle_i = 0
        if self.bg_front_i == self.scr_h:
            self.bg_front_i = 0

        #set scrolling speed for each layer: 
        #the screen size has to divide evenly with speed 
        #width / length: 864, 1080
        
        self.bg_i += 0  #at the moment it looks best when the real background is not scrolling
        if not self.boss_spawned:
            self.bg_back_i += 0.5 * self.dt
            self.bg_middle_i += 1 * self.dt
            self.bg_front_i += 2.5 * self.dt

        #draw player
        self.p1_group.draw(self.scr)

        #draw enemies
        if self.boss_spawned:
            if len(self.boss_group) > 0:
                self.boss_group.draw(self.scr)
        self.enemy_group.draw(self.scr)
        
        #draw bullets and bolts
        self.bullet_group.draw(self.scr)
        self.bolt_group.draw(self.scr)
        if self.boss_spawned and not self.boss_dead:
            self.eyes_of_ra_group.draw(self.scr)

        #draw particles
        for particle in self.particle_bullet_group[:]:
            color = r.choice(["#a9420f", "#f0d5bc", "#6d412e", "#dfae7f", "#e87e0d", "#fbcf85", "#293d43", "#f9b631", "#7c9ca5", "#a6693d", "#d9894d", "#3c5964"])
            pg.draw.circle(self.scr, Color(color), (particle.x, particle.y), particle.time)
            particle.update()
            if particle.time <= 0:
                self.particle_bullet_group.remove(particle)
        
        #keeping scoretext updated inside loop 
        self.p1_highscore_text = self.font_scores.render(f"Highscore: {self.p1_highscore}", True, (255, 255, 255))
        self.p1_score_text = self.font_scores.render(f"Score: {self.p1.score}", True, (255, 255, 255))

        #instructions text rendering
        if self.instructions:
            now = pg.time.get_ticks()
            txt = self.inst_txt[self.inst_txt_idx]
            self.inst_txt_display = self.font.render(txt, True, (255, 255, 255))
            self.inst_txt_length = self.font.size(f"{self.inst_txt[self.inst_txt_idx]}")[0] // 2 #returns width, height
            
            #display text
            self.scr.blit(self.inst_txt_display, (self.scr_w // 2 - self.inst_txt_length, self.scr_h - 350))
            
            if now - self.inst_last >= self.inst_cd:
                self.inst_last = now    
                #moving on to next text
                self.inst_txt_idx += 1 
            
            if self.inst_txt_idx >= len(self.inst_txt) - 1:
                #all texts have been displayed. Start spawning of enemies.
                self.instructions = False
        self.game_begin = True #TODO: is this here? or animations..?
        
        #draw scores
        self.scr.blit(self.p1_highscore_text, (20, 40))
        self.scr.blit(self.p1_score_text, (20, 40 + self.p1_score_text.get_height()))

        #escape pod text
        if self.escape_pod is not None:
            self.scr.blit(self.txt_escape_pod_display, (self.escape_pod.rect.center[0] - self.txt_escape_pod_length, self.escape_pod.rect.center[1] - self.escape_pod.rect.height))
        
        #draw player hp
        if not self.game_end:
            hp_offset_x = 12.5
            hp_offset_y = 70
            hp_length = self.p1.image.get_size() [0] * 0.20 * self.p1.hp
            for _ in range(self.p1.hp):
                pg.draw.line(self.scr, Color("green"), (self.p1.rect.x + hp_offset_x, self.p1.rect.y + hp_offset_y), (self.p1.rect.x + hp_length, self.p1.rect.y + hp_offset_y), width = 5)

        #draw player lives
        offset_lives = 15
        offset_lives_2 = 0
        for _ in range(self.p1.lives):
            self.scr.blit(self.hp_heart, (self.scr_w - 100 - offset_lives * self.p1.lives + offset_lives_2, 40))
            offset_lives_2 += 40
        
        #draw boss hp
        if len(self.boss_group) > 0 and self.e_boss.in_position:
            boss_hp_y = 35 + self.hp_heart.get_height() // 2
            boss_hp_length = self.e_boss.image.get_size() [0] * 0.0010 * self.e_boss.hp
            boss_hp_orig_length = self.e_boss.image.get_size() [0] * 0.0010 * self.e_boss.max_hp
            pg.draw.line(self.scr, self.boss_color, (self.scr_w // 2 - boss_hp_orig_length // 2, boss_hp_y), 
                        (self.scr_w // 2 - boss_hp_orig_length // 2 + boss_hp_length, boss_hp_y), width = 5)
        
        #draw explosions
        self.explosion_group.draw(self.scr)
       
        #add glow to powerups
        for powerup in self.power_up_group:
            radius = powerup.rect.width * 0.6
            color = (0, 120, 0)
            self.scr.blit(self.circle_surf(color, radius), (powerup.rect.center[0] - radius, powerup.rect.center[1] - radius), special_flags=BLEND_RGB_ADD) 
        
        #draw powerups
        self.power_up_group.draw(self.scr)
 
        #draw fps 
        self.scr.blit(self.update_fps(), (self.scr_w - 125,self.scr_h - 100))

        #draw game over
        if not self.p1.alive: 
            self.game_over = True
        
        if self.game_over:
            self.scr.blit(self.txt_game_over_display, (self.scr_w // 2 -self.font.size(f'{self.txt_game_over}')[0] // 2, self.scr_h // 2))
            self.scr.blit(self.txt_game_over_2_display, (self.scr_w // 2 -self.font.size(f'{self.txt_game_over_2}')[0] // 2, self.scr_h // 2 + self.font.size(f'{self.txt_game_over}')[1] * 2))
        
        #draw game clear
        if self.p1.alive and self.boss_dead:
            self.game_end = True
            if not self.final_animation_stop_player_movement:
                self.p1.vel_x = 0
                self.p1.vel_y = 0
                self.p1.is_firing = False
                self.final_animation_stop_player_movement = True

            if self.final_animation:
                #move player out from the screen
                self.p1.vel_y = -3.5
            if self.p1.rect.bottom + self.p1.rect.height * 2 < 0:
                if len(self.p1_group) > 0:
                    self.end_credits_start = pg.time.get_ticks()
                    self.end_credits_last = pg.time.get_ticks()
                self.p1_group.empty()
            
            #check for final animation timer
            if self.final_animation_last is not None:
                now = pg.time.get_ticks()
                if now - self.final_animation_last > self.final_animation_cd:
                    self.final_animation = True #add for end credits
                
        #draw end credits
        now = pg.time.get_ticks()
        if self.end_credits_start is not None and self.game_over_last is None:
            if now - self.end_credits_start > self.end_credits_start_cd:
                self.end_credits = True

        if self.end_credits:
            #init text
            txt = self.end_credits_txt[self.end_credits_txt_idx]
            self.end_credits_txt_display = self.font_credits.render(txt, True, (255, 255, 255))
            self.end_credits_txt_length = self.font_credits.size(f"{self.end_credits_txt[self.end_credits_txt_idx]}")[0] // 2
            
            #play victory sound
            if not self.sound_victory_played:
                self.sound_victory_played = True
                self.sound_victory.play()

            #display text
            self.scr.blit(self.end_credits_txt_display, (self.scr_w // 2 - self.end_credits_txt_length, self.scr_h // 2))

            if now - self.end_credits_last > self.end_credits_cd:
                self.end_credits_last = now    
                #moving on to next text
                self.end_credits_txt_idx += 1 

            if self.end_credits_txt_idx >= len(self.end_credits_txt) - 1:
                #all texts have been displayed. 
                self.end_credits = False
                if self.game_over_last is None:
                    self.game_over_last = pg.time.get_ticks()

        if not self.end_credits and self.game_over_last is not None:
            now = pg.time.get_ticks()
            if now - self.game_over_last > self.game_over_cd:
                self.game_over = True

        pg.display.flip()

class Ship_animation_menu(pg.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.name = "Start animation"
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.vel_x = 17
        self.vel_y = 0
        self.turned_1 = False
        self.turned_2 = False
        self.play_1 = True

    def update(self):
        #move ship
        self.rect.x += self.vel_x * Game.dt
        self.rect.y += self.vel_y * Game.dt

        #sound
        if self.play_1:
            Game.sound_flight.play()
            self.play_1 = False
        
        print (self.rect.center)
        #destroy sprite when leaving screens
        if self.rect.x > 1080 and not self.turned_1:
            Game.sound_flight.play()
            self.rect.y += 300
            self.vel_x = -self.vel_x
            self.image = pg.transform.rotate(self.image, 180)
            self.turned_1 = True
        if self.rect.x < -350 and self.turned_1:
            Game.sound_flight.play()
            self.rect.y += 300
            self.vel_x = -self.vel_x
            self.image = pg.transform.rotate(self.image, 180)
            self.turned_2 = True
        if self.rect.x > 1080 + 150 and self.turned_2:
            self.kill()

class Player(pg.sprite.Sprite):
    def __init__(self, images: list, coords: tuple):
        super().__init__()
        self.name = "Player"
        self.alive = True
        self.images = images
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = coords
        self.radius = self.rect.width * 0.3
        self.is_firing = False
        self.bullet_last = pg.time.get_ticks()
        self.attack_cooldown = 200
        self.weapon_lvl = 0
        self.vel_x = 0
        self.vel_y = 0
        self.score = 900
        self.lives = 3
        self.max_hp = 4
        self.hp = 4
    
    def update(self):
        #stop player from moving
        if not Game.game_end:
            self.vel_x = 0 
            self.vel_y = 0
                    
        #check for key held down
        keystate = pg.key.get_pressed()
        
        #make the player unable to leave the screen while moving
        if self.alive and not Game.game_end:
            if keystate[pg.K_LEFT]:
                if self.rect.left - self.vel_x >= 0:
                    self.vel_x = -5.3
            if keystate[pg.K_RIGHT]:
                if self.rect.right + self.vel_x <= Game.scr_w:
                    self.vel_x = 5.3
            if keystate[pg.K_UP]:
                if self.rect.top + self.vel_y >= 0:
                    self.vel_y = -4.3
            if keystate[pg.K_DOWN]:
                if self.rect.bottom + self.vel_y <= Game.scr_h:
                    self.vel_y = 4.3
            if keystate[pg.K_SPACE]:
                self.is_firing = True   
            else:
                self.is_firing = False             
        
        #animation
        self.image = self.images[self.index]
        
        if self.vel_x < 0:
            self.index = 1
        elif self.vel_x > 0:
            self.index = 2
        else:
            self.index = 0

        #move player
        self.rect.x += self.vel_x 
        self.rect.y += self.vel_y

        #attack
        if self.is_firing:
            self.attack()
    
    def attack(self):
        bullet_y = self.rect.y + 4
        bullet_y_up = self.rect.y + 10
        offset_x = 0
        now = pg.time.get_ticks()
        
        if now - self.bullet_last >= self.attack_cooldown:
            self.bullet_last = now
            Game.sound_bullet.play()
            Game.bullet_group.add(Bullet(Game.bullet_sprites, self.rect.x + 13, bullet_y))
            Game.bullet_group.add(Bullet(Game.bullet_sprites, self.rect.x + 44, bullet_y))

            if self.weapon_lvl > 0:
                for _ in range(self.weapon_lvl):
                    Game.bullet_group.add(Bullet(Game.bullet_sprites, self.rect.x + 3 - offset_x, bullet_y_up))
                    Game.bullet_group.add(Bullet(Game.bullet_sprites, self.rect.x + 52 + offset_x, bullet_y_up))
                    offset_x += 8
                    bullet_y_up += 6

class P1_thrusters(pg.sprite.Sprite):
    def __init__(self, images: list, coords: tuple):
        super().__init__()
        self.name = "P1 thrusters"
        self.images = images
        self.index = 0
        self.offset_x = -11.95
        self.offset_y = 9.5
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = coords

    def update(self):
        #animation
        if Game.p1.vel_y < 0:
            self.index = 1
        else:
            self.index = 0
        
        self.image = self.images[self.index]
        
        self.rect.x = Game.p1.rect.center[0] + self.offset_x
        self.rect.y = Game.p1.rect.center[1] + self.offset_y

class Bullet(pg.sprite.Sprite):
    def __init__(self, images: list, x, y):
        super().__init__()
        self.images = images
        self.image = self.images[0]
        self.counter = 0
        self.index = 0
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.radius = self.rect.width * 0.5
        self.speed = 5.3 

    def update(self):
        #check for collisions: normal enemies
        for enemy in Game.enemy_group:
            if enemy.name != "Escape pod":
                if pg.sprite.collide_circle(self, enemy):
                    #collision
                    self.kill()
                    Game.particle_bullet_group.append(Particle(self.rect.center[0], self.rect.center[1] + self.speed))

                    enemy.hp -= 1
                    if enemy.hp < 1:
                        enemy.kill()
                        Game.explosion_group.add(Explosion(Game.explosion_sprites, (enemy.rect.center[0] + enemy.vel_x, enemy.rect.center[1] + enemy.vel_y)))
                        #add scores
                        Game.p1.score += enemy.points

        #check for collisions: boss
        if Game.boss_spawned and not Game.boss_dead:
            for enemy in Game.boss_group:
                if enemy.name == "Boss":
                    #make boss unable to take damage while moving to position
                    if Game.e_boss.in_position and not Game.e_boss.is_firing_2 and not Game.e_boss.pattern_3_moving_down:
                        if pg.sprite.collide_circle(self, enemy):

                            #collision
                            self.kill()
                            Game.particle_bullet_group.append(Particle(self.rect.center[0], self.rect.center[1] + self.speed))

                            enemy.hp -= 1
                            if enemy.hp < 1:
                                Game.escape_pod = Escape_pod(Game.boss_escape_pod_img, enemy.rect.center)
                                Game.enemy_group.add(Game.escape_pod)
                                Game.boss_group.empty()
                                Game.boss_dead = True
                                Game.sound_explosion.play()
                                Game.explosion_group.add(Explosion(Game.explosion_sprites, enemy.rect.center))
                                #add scores
                                Game.p1.score += enemy.points
                                #check highscore
                                Game.p1_highscore = Game.highscore()

        #kill sprites that left the screen
        if self.rect.y > Game.scr_h or self.rect.x > Game.scr_w or self.rect.x < 0:
            self.kill()
        
        #animation
        fps = 6 #bigger number means it stays longer in one frame -> slower animation
        self.counter += 1

        if self.counter >= fps and self.index < len(self.images) - 1:
            self.counter = 0
            
            #next image
            self.index += 1
            self.image = self.images[self.index]
        
        #animation is complete, all images have been used -> restart animation
        if self.counter >= fps and self.index >= len(self.images) - 1:
            self.index = 0
            self.counter = 0
            self.image = self.images[self.index]

        #move bullets
        self.rect.y -= self.speed

class Particle():
    def __init__(self, x, y, time = r.randint(3, 6)):
        self.x = x
        self.y = y
        self.vel_x = r.randint(0, 20) / 10 - 1
        self.vel_y = 2
        self.time = time #also acts as radius

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.time -= 0.1

class Bolt(pg.sprite.Sprite):
    def __init__(self, images: list, coords, dx = 0, dy = 0, speed = 0): 
        super().__init__()
        self.images = images
        self.image = self.images[0]
        self.index = 0
        self.counter = 0
        self.rect = self.image.get_rect()
        self.rect.center = coords
        self.speed = speed
        self.dx = dx
        self.dy = dy
    
    def update(self):
        #check for collisions
        if Game.p1.alive and not Game.game_end:
            if pg.sprite.collide_circle(self, Game.p1):
                #collision
                self.kill()
                Game.p1.hp -= 1
                if Game.p1.hp < 1:
                    Game.explosion_group.add(Explosion(Game.explosion_sprites, (Game.p1.rect.center[0] + Game.p1.vel_x, Game.p1.rect.center[1] + Game.p1.vel_y)))
                    if Game.p1.lives > 0:
                        Game.p1.lives -= 1
                        Game.p1.hp = Game.p1.max_hp
                    else:    
                        Game.p1.alive = False
                        Game.p1.kill() 

        self.rect.x += self.speed * self.dx
        self.rect.y += self.speed * self.dy

        #kill sprites that left the screen
        if self.rect.y > Game.scr_h or self.rect.x > Game.scr_w or self.rect.x < 0:
            self.kill()

        #animation
        fps = 6 #bigger number means it stays longer in one frame -> slower animation
        self.counter += 1

        if self.counter >= fps and self.index < len(self.images) - 1:
            self.counter = 0
            
            #next image
            self.index += 1
            self.image = self.images[self.index]
        
        #animation is complete, all images have been used -> restart animation
        if self.counter >= fps and self.index >= len(self.images) - 1:
            self.index = 0
            self.counter = 0
            self.image = self.images[self.index]

class Boss_ray(pg.sprite.Sprite):
    def __init__(self, images: list, coords):
        super().__init__()
        self.images = images
        self.image = images[0]
        self.rect = self.image.get_rect()
        self.rect.center = (coords[0], coords[1]+self.rect.height // 2)
        self.hitbox = pg.Rect(self.rect.left + ((self.rect.width // 5) * 2), self.rect.top, self.rect.width - ((self.rect.width // 5) * 4), self.rect.height)
        self.counter = 0
        self.index = 0
        
    def update(self):
        #check for collisions
        if Game.p1.alive:
            if self.index >=8: #ray is active
                if self.hitbox.colliderect(Game.p1): #using colliderect [instead of sprite.collide_rect] since hitbox is not of sprite class
                    #collision
                    self.kill()
                    Game.p1.hp -= 10
                    if Game.p1.hp < 1:
                        Game.explosion_group.add(Explosion(Game.explosion_sprites, (Game.p1.rect.center[0] + Game.p1.vel_x, Game.p1.rect.center[1] + Game.p1.vel_y)))
                        if Game.p1.lives > 0:
                            Game.p1.lives -= 1
                            Game.p1.hp = Game.p1.max_hp
                        else:    
                            Game.p1.alive = False
                            Game.p1.kill() 

        #animation
        fps = 8 #bigger number means it stays longer in one frame -> slower animation
        self.counter += 1

        if self.counter >= fps and self.index < len(self.images) - 1:
            self.counter = 0
            
            #next image
            self.index += 1
            self.image = self.images[self.index]
        
        #animation is complete, all images have been used -> kill the sprite
        if self.counter >= fps and self.index >= len(self.images) - 1:
            self.kill()

class Explosion(pg.sprite.Sprite):
    def __init__(self, images: list, coords: tuple):
        super().__init__()
        self.images = images
        self.index = 0
        self.image = self.images[self.index]
        if Game.boss_spawned:
            self.rect = self.image.get_rect(topleft=coords)
        else:
            self.rect = self.image.get_rect()
            self.rect.center = coords
        self.counter = 0
        
        #play the sound
        Game.sound_explosion.play()
    
    def update(self):
        fps = 4 #bigger number means it stays longer in one frame -> slower animation
        self.counter += 1

        if self.counter >= fps and self.index < len(self.images) - 1:
            self.counter = 0
            
            #next image
            self.index += 1
            self.image = self.images[self.index]
        
        #animation is complete, all images have been used -> kill the sprite
        if self.counter >= fps and self.index >= len(self.images) - 1:
            self.kill()

class Weapon_up(pg.sprite.Sprite):
    def __init__(self, images: list, x, y):
        super().__init__()
        self.images = images
        self.index = 0
        self.counter = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.radius = self.rect.width * 0.2
        self.vel_x = 5
        self.vel_y = 3
        self.speed = 10
        self.ani_last = pg.time.get_ticks()
        self.ani_cd = 400

        #if spawned to the right side of the screen
        if self.rect.x > Game.scr_w:
            self.vel_x = -self.vel_x
    
    def update(self):
        if pg.sprite.collide_circle(self, Game.p1):
            #collision
            Game.sound_weapon_up.play()
            Game.p1.weapon_lvl += 1 #yay!
            Game.p1.attack_cooldown -= 50
            self.kill()

        #kill if leaving the screen
        if self.rect.top > Game.scr_h:
            self.kill()

        #animation
        fps = 5 #bigger number means it stays longer in one frame -> slower animation
        self.counter += 1

        if self.counter >= fps and self.index < len(self.images) - 1:
            self.counter = 0
            
            #next image
            self.index += 1
            self.image = self.images[self.index]
        
        #animation is complete, all images have been used -> restart animation
        if self.counter >= fps and self.index >= len(self.images) - 1:
            self.index = 0
            self.counter = 0
            self.image = self.images[self.index]

        #target player if player is close
        if abs(self.rect.center[0] - Game.p1.rect.center[0]) <= self.rect.width * 3 and abs(self.rect.center[1] - Game.p1.rect.center[1]) <= self.rect.height * 3:
            angle = math.atan2(Game.p1.rect.y - self.rect.y, Game.p1.rect.x - self.rect.x)
            dx = math.cos(angle) 
            dy = math.sin(angle) 
            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed

        else:
            #move normally
            self.rect.x += self.vel_x
            self.rect.y += self.vel_y

class Fighter(pg.sprite.Sprite):
    def __init__(self, images: list, x, y):
        super().__init__()
        self.name = "Fighter"
        self.images = images
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.radius = self.rect.width * 0.3
        self.is_firing = False
        self.bolt_last = pg.time.get_ticks()
        self.attack_last = pg.time.get_ticks()
        self.attack_cooldown = 2200
        self.shots_cooldown = 190
        self.shot_count = 0
        self.no_of_shots = 3
        self.vel_x = 0
        self.vel_y = 3.5
        self.points = 180
        self.hp = 4

    def update(self):    
         #move enemy
        self.rect.x += self.vel_x 
        self.rect.y += self.vel_y
        if self.rect.top >= 0:
            self.is_firing = True

        #attack
        if self.is_firing:
            dx = 0
            dy = 1
            now = pg.time.get_ticks()
            if now - self.bolt_last >= self.shots_cooldown and self.shot_count < self.no_of_shots:
                self.bolt_last = now
                Game.bolt_group.add(Bolt(Game.bolt_sprites, (self.rect.center[0] + self.vel_x, self.rect.center[1] + self.vel_y), dx, dy, 5.3))
                self.shot_count +=1
            if now - self.attack_last >= self.attack_cooldown:
                self.attack_last = now
                self.shot_count = 0
    
class Droid(pg.sprite.Sprite):
    def __init__(self, images: list, spawn, x, y):
        super().__init__()
        self.name = "Droid"
        self.images = images
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.radius = self.rect.width * 0.3
        self.counter = 0
        self.is_firing = False
        self.bolt_last = pg.time.get_ticks()
        self.attack_cooldown = 800
        self.vel_x = 1
        self.vel_y = 1
        self.points = 225
        self.hp = 5
        self.spawn = spawn
        if self.spawn == "Right":
            self.vel_x = -self.vel_x

    def update(self):
        #animation
        fps = 8 #bigger number means it stays longer in one frame -> slower animation
        self.counter += 1

        if self.counter >= fps and self.index < len(self.images) - 1:
            self.counter = 0
            
            #next image
            self.index += 1
            self.image = self.images[self.index]
        
        #animation is complete, all images have been used -> restart animation
        if self.counter >= fps and self.index >= len(self.images) - 1:
            self.index = 0
            self.counter = 0
            self.image = self.images[self.index]

        #start firing
        if self.spawn == "Left" and self.rect.x >= 0 or self.spawn == "Right" and self.rect.x <= Game.scr_w:
            self.is_firing = True
        
        #movement
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        
        #attack
        if self.is_firing:
            now = pg.time.get_ticks()
            if now - self.bolt_last >= self.attack_cooldown:
                self.bolt_last = now
                angle = math.atan2(Game.p1.rect.y - self.rect.y, Game.p1.rect.x - self.rect.x)
                dx = math.cos(angle) 
                dy = math.sin(angle) 
                Game.bolt_group.add(Bolt(Game.bolt_sprites, (self.rect.center[0] + self.vel_x, self.rect.center[1] + self.vel_y), dx, dy, 5.3))

class Worm(pg.sprite.Sprite):
    def __init__(self, images: list, x, y):
        super().__init__()
        self.name = "Worm"
        self.images = images
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.radius = self.rect.width * 0.3
        self.move_left = False
        self.move_right = False
        
        #movement pattern
        self.vel_x = 1.5
        self.vel_y = 2
        self.midpoint = x 
        self.travel = self.rect.width
        if self.rect.x < Game.scr_w // 2:
            self.move_left = True
        else:
            self.move_right = True
        
        #animation
        self.counter = 0
        self.bolt_last = pg.time.get_ticks()
        
        #attack
        self.is_firing = False
        self.attack_cooldown = 800
        
        self.points = 900
        self.hp = 8

    def update(self):
        #animation
        fps = 8 #bigger number means it stays longer in one frame -> slower animation
        self.counter += 1

        if self.counter >= fps and self.index < len(self.images) - 1:
            self.counter = 0
            
            #next image
            self.index += 1
            self.image = self.images[self.index]
        
        #animation is complete, all images have been used -> restart animation
        if self.counter >= fps and self.index >= len(self.images) - 1:
            self.index = 0
            self.counter = 0
            self.image = self.images[self.index]
    
        #movement pattern
        if self.move_left:
            if self.rect.center[0] >= self.midpoint - self.travel:
                self.vel_x = -abs(self.vel_x)
            else:
                self.move_left = False
                self.move_right = True
                self.vel_x = abs(self.vel_x)
        elif self.move_right:
            if self.rect.center[0] <= self.midpoint + self.travel:
                self.vel_x = abs(self.vel_x)
            else:
                self.move_right = False
                self.move_left = True
                self.vel_x = -abs(self.vel_x)

        #start firing
        if self.rect.top > 0:
            self.is_firing = True
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        
        #attack
        if self.is_firing:
            now = pg.time.get_ticks()
            if now - self.bolt_last >= self.attack_cooldown:
                self.bolt_last = now
                angle_step = 360 // 12
                for angle in range(0, 360, angle_step):
                    radians = math.radians(angle)
                    dir_x = math.cos(radians)
                    dir_y = math.sin(radians)
                    Game.bolt_group.add(Bolt(Game.bolt_sprites, (self.rect.center[0] + self.vel_x, self.rect.center[1] + self.vel_y), dir_x, dir_y, 5.3))

class Boss(pg.sprite.Sprite):
    def __init__(self, img_ship: list, x, y):
        super().__init__()
        self.name = "Boss"
        self.img_ship = img_ship
        self.idx_ship = 0
        self.image = self.img_ship[self.idx_ship]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.radius = self.rect.width * 0.4
        self.in_position = False
    
        #speed at start
        self.vel_x = 0
        self.vel_y = 1
        self.points = 15000
        self.max_hp = 600 # ship maximum health
        self.hp = 600 # ship current health
        self.stages = 5 
        self.explosions_cooldown = 200
        self.stage_last = 0

        #hand out power ups
        self.spawn_power_ups = True
    
        #pattern 1 (bolts)
        self.is_firing_1 = False 
        self.pattern_1_cooldown = 5000
        self.pattern_1_atk_last = pg.time.get_ticks()
        self.pattern_1_last = pg.time.get_ticks()
        self.pattern_1_atk_speed = 300
        self.pattern_1_no_of_shots = 5
        self.pattern_1_shot_count = 1
        
        #pattern 2 (ray, droids)
        self.is_firing_2 = False
        self.pattern_2_cooldown = 7000
        self.pattern_2_last = pg.time.get_ticks()
        self.pattern_2_finished = False
        self.pattern_2_pick_location_x = True
        self.pattern_2_moving_up = True
        self.pattern_2_score = None

        #pattern 3 (megaboemb)
        self.is_firing_3 = False
        self.pattern_3_cooldown = 50
        self.pattern_3_last = pg.time.get_ticks() 
        self.pattern_3_moving_up = True
        self.pattern_3_moving_down = False
        self.pattern_3_in_position = False

        #random explosions
        self.r_explosion_cooldown = 450
        self.r_explosion_last = pg.time.get_ticks()

    def explosions(self):
        boss_x, boss_y = self.rect.center
        #left, right
        self.explosion_coords_1 = [ (boss_x - 155, boss_y + 20), (boss_x - 125, boss_y + 60), 
        (boss_x + 83, boss_y + 20), (boss_x + 53, boss_y + 60) ]
        #mid
        self.explosion_coords_2 = [ (boss_x - 51, boss_y + 2), (boss_x - 16, boss_y + 2),
        (boss_x - 51, boss_y - 32), (boss_x - 51, boss_y - 67), (boss_x - 16, boss_y - 32), (boss_x - 16, boss_y - 67) ]
        #around
        self.explosion_coords_3 = [ (boss_x - 34, boss_y + 110), (boss_x - 74, boss_y + 90), 
        (boss_x + 6, boss_y + 90), (boss_x - 155, boss_y - 80), (boss_x - 155, boss_y - 40), 
        (boss_x - 195, boss_y - 60), (boss_x + 83, boss_y - 80), (boss_x + 83, boss_y - 40), (boss_x + 123, boss_y - 60) ]

        if self.idx_ship == 1:
            for coords in self.explosion_coords_1:
                Game.explosion_group.add(Explosion(Game.explosion_sprites, coords))
        elif self.idx_ship == 2:
            for coords in self.explosion_coords_2:
                Game.explosion_group.add(Explosion(Game.explosion_sprites, coords))
        elif self.idx_ship == 3 or self.idx_ship == 4:
            for coords in self.explosion_coords_3:
                Game.explosion_group.add(Explosion(Game.explosion_sprites, coords))
            if self.idx_ship == 4:
                for coords in self.explosion_coords_1:
                    Game.explosion_group.add(Explosion(Game.explosion_sprites, coords))

    @property
    def idx_ship_get(self):
        return self.stages - (-(-self.hp // (self.max_hp // self.stages))) #might require wrapping all in min() if hp == 0

    def update(self):
        #get p1 score and store it for later use
        if self.pattern_2_score is None:
            self.pattern_2_score = Game.p1.score
       
        #update ship image
        self.idx_ship = self.idx_ship_get

        #explosions between stages
        if self.idx_ship != self.stage_last:
            self.explosions()

        self.stage_last = self.idx_ship 
        self.image = self.img_ship[self.idx_ship]

        #start patterns
        if not self.in_position:
            if self.rect.y < Game.scr_h // 5:
                self.rect.y += self.vel_y

        if self.rect.y >= Game.scr_h // 5:
            self.in_position = True

        if self.in_position:
            if self.idx_ship == 0:
                self.is_firing_1 = True
                #stop moving
                self.vel_y = 0
            elif self.idx_ship == 1:
                self.is_firing_1 = False
                self.is_firing_2 = True
            elif self.idx_ship == 2:
                self.is_firing_2 = False
                self.is_firing_3 = True
            if self.idx_ship >= 3:
                self.is_firing_3 = False
                Game.eyes_of_ra_group.empty()
                now = pg.time.get_ticks()
                if now - self.r_explosion_last > self.r_explosion_cooldown:
                    self.r_explosion_last = now
                    pick_list = r.choice([self.explosion_coords_1, self.explosion_coords_2, self.explosion_coords_3])
                    coords = r.choice(pick_list)
                    Game.explosion_group.add(Explosion(Game.explosion_sprites, coords))
            if self.idx_ship == 4:
                self.r_explosion_cooldown = 350  
        
        #movement
        self.rect.y += self.vel_y
        self.rect.x += self.vel_x

        #attack
        if self.is_firing_1:
            self.pattern_1()
                    
        if self.is_firing_2:
            Game.spawn_e3()
            self.pattern_2()

            #cooldown for ray-attack
            now = pg.time.get_ticks()
            if now - self.pattern_2_last >= self.pattern_2_cooldown:
                self.pattern_2_last = now
                self.pattern_2_finished = False
            
            #damage boss from droids
            if Game.p1.score - self.pattern_2_score >= 225: #points from droids
                self.pattern_2_score = Game.p1.score
                self.hp -= 10
                self.image = Game.boss_pattern_2_damaged_img
            
        if self.is_firing_3:
            self.pattern_3()
    
    def pattern_1(self):
            now = pg.time.get_ticks()
            if now - self.pattern_1_atk_last >= self.pattern_1_atk_speed and self.pattern_1_shot_count < self.pattern_1_no_of_shots:
                self.pattern_1_atk_last = now
                angle_step = 360 // 24
                for angle in range(0, 180 + 1, angle_step): #half a circle
                    radians = math.radians(angle)
                    dir_x = math.cos(radians)
                    dir_y = math.sin(radians)
                    Game.bolt_group.add(Bolt(Game.bolt_sprites, (self.rect.center[0] + self.vel_x, self.rect.center[1] + self.vel_y), dir_x, dir_y, 5.3))
                self.pattern_1_shot_count +=1
            if now - self.pattern_1_last >= self.pattern_1_cooldown:
                self.pattern_1_last = now
                self.pattern_1_shot_count = 0
            else:
                if self.spawn_power_ups:
                    Game.spawn_weapon_up()
                    self.spawn_power_ups = False
    
    def pattern_2(self):
        if not self.pattern_2_finished:
            
            #moving up
            if self.pattern_2_moving_up:
                if self.rect.bottom > -1:
                    self.vel_y = -5
                else:
                    self.vel_y = 0
                    self.pattern_2_moving_up = False
            
            else: 
                #pick a spot to descend from
                if self.pattern_2_pick_location_x: 
                    location_x = r.choice([10 + self.rect.width // 2, Game.scr_w // 2, Game.scr_w - 10 - self.rect.width // 2])
                    location_y = -50
                    self.rect.center = (location_x, location_y)
                    self.pattern_2_pick_location_x = False
            
                #in position: fire the ray
                self.vel_y = 0    
                coords = (self.rect.center[0], self.rect.center[1] + 100)
                Game.bolt_group.add(Boss_ray(Game.boss_ray_sprites, coords))

                #time to cool down. stop the pattern
                self.pattern_2_finished = True

                #init next time
                self.pattern_2_pick_location_x = True
                self.pattern_2_moving_up = True
    
    def pattern_3(self):
        #moving up
        if self.pattern_3_moving_up:
            if self.rect.bottom > -1:
                self.vel_y = -5
            else:
                self.vel_y = 0
                self.pattern_3_moving_up = False
                self.rect.center = (Game.scr_w // 2, self.rect.center[1])
                self.pattern_3_moving_down = True
        
        #moving to position (center)
        if self.pattern_3_moving_down:
            if self.rect.y < Game.scr_h // 9:
                self.vel_y = 5
            else:
                self.vel_y = 0
                self.pattern_3_moving_down = False

        if self.rect.y >= Game.scr_h // 9:
            self.pattern_3_in_position = True
        
        #start the attack
        if self.pattern_3_in_position:
            
            #draw the eyes
            if len(Game.eyes_of_ra_group) <= 22: #the amount of bolts in the eyes
                b_w = Game.bolt_sprites[0].get_width()
                b_h = Game.bolt_sprites[0].get_height()
                #top
                for i in range(4):
                    Game.eyes_of_ra_group.add(Bolt(Game.bolt_sprites, (Game.scr_w // 2 - 300 - b_w * i, Game.scr_h // 5))) #left
                    Game.eyes_of_ra_group.add(Bolt(Game.bolt_sprites, (Game.scr_w // 2 + 300 - b_w * i, Game.scr_h // 5))) #right
                for i in range(1,4):
                    Game.eyes_of_ra_group.add(Bolt(Game.bolt_sprites, (Game.scr_w // 2 - 300 + b_w * i, Game.scr_h // 5))) #left
                    Game.eyes_of_ra_group.add(Bolt(Game.bolt_sprites, (Game.scr_w // 2 + 300 + b_w * i, Game.scr_h // 5))) #right
                #triangle
                Game.eyes_of_ra_group.add(Bolt(Game.bolt_sprites, (Game.scr_w // 2 - 300, Game.scr_h // 5 + b_h)) )#left
                Game.eyes_of_ra_group.add(Bolt(Game.bolt_sprites, (Game.scr_w // 2 + 300, Game.scr_h // 5 + b_h))) #right
                for _ in range(2):
                    Game.eyes_of_ra_group.add(Bolt(Game.bolt_sprites, (Game.scr_w // 2 - 300 + b_w, Game.scr_h // 5 + b_h * 2))) #left
                    Game.eyes_of_ra_group.add(Bolt(Game.bolt_sprites, (Game.scr_w // 2 + 300 + b_w, Game.scr_h // 5 + b_h * 2))) #right
                Game.eyes_of_ra_group.add(Bolt(Game.bolt_sprites, (Game.scr_w // 2 - 300 - b_w, Game.scr_h // 5 + b_h * 2))) #left
                Game.eyes_of_ra_group.add(Bolt(Game.bolt_sprites, (Game.scr_w // 2 + 300 - b_w, Game.scr_h // 5 + b_h * 2))) #right
                Game.eyes_of_ra_group.add(Bolt(Game.bolt_sprites, (Game.scr_w // 2 - 300, Game.scr_h // 5 + b_h * 3))) #left
                Game.eyes_of_ra_group.add(Bolt(Game.bolt_sprites, (Game.scr_w // 2 + 300, Game.scr_h // 5 + b_h * 3))) #right

            #fire the eyes
            self.pattern_3_shoot()
    
    def pattern_3_shoot(self):
            b_w = Game.bolt_sprites[0].get_width()
            b_h = Game.bolt_sprites[0].get_height()
            
            starting_points = [(Game.scr_w // 2 - 300, Game.scr_h // 5), (Game.scr_w // 2 - 300 - b_w, Game.scr_h // 5), (Game.scr_w // 2 - 300 - b_w * 2, Game.scr_h // 5), (Game.scr_w // 2 - 300 - b_w * 3, Game.scr_h // 5),
            (Game.scr_w // 2 + 300, Game.scr_h // 5), (Game.scr_w // 2 + 300 - b_w, Game.scr_h // 5), (Game.scr_w // 2 + 300 - b_w * 2, Game.scr_h // 5), (Game.scr_w // 2 + 300 - b_w * 3, Game.scr_h // 5),
            (Game.scr_w // 2 - 300 + b_w, Game.scr_h // 5), (Game.scr_w // 2 - 300 + b_w * 2, Game.scr_h // 5), (Game.scr_w // 2 - 300 + b_w * 3, Game.scr_h // 5), 
            (Game.scr_w // 2 + 300 + b_w, Game.scr_h // 5), (Game.scr_w // 2 + 300 + b_w * 2, Game.scr_h // 5), (Game.scr_w // 2 + 300 + b_w * 3, Game.scr_h // 5),
            (Game.scr_w // 2 - 300, Game.scr_h // 5 + b_h),  (Game.scr_w // 2 + 300, Game.scr_h // 5 + b_h),
            (Game.scr_w // 2 - 300 + b_w, Game.scr_h // 5 + b_h * 2), (Game.scr_w // 2 + 300 + b_w, Game.scr_h // 5 + b_h * 2),
            (Game.scr_w // 2 - 300 - b_w, Game.scr_h // 5 + b_h * 2), (Game.scr_w // 2 + 300 - b_w, Game.scr_h // 5 + b_h * 2),
            (Game.scr_w // 2 - 300, Game.scr_h // 5 + b_h * 3), (Game.scr_w // 2 + 300, Game.scr_h // 5 + b_h * 3)]
            coords = r.choice(starting_points)
            target_x = r.randint(b_w, Game.scr_w - b_w)
            target_y = Game.scr_h - b_h
            angle = math.atan2(target_y - coords[1], target_x - coords[0])
            dx = math.cos(angle) 
            dy = math.sin(angle) 
            now = pg.time.get_ticks()
            if now - self.pattern_3_last >= self.pattern_3_cooldown:
                self.pattern_3_last = now
                Game.bolt_group.add(Bolt(Game.bolt_sprites, coords, dx, dy, 5.3))
                
class Boss_thrusters(pg.sprite.Sprite):
    def __init__(self, images: list):
        super().__init__()
        self.name = "Thrust"
        self.images = images
        self.index = 0
        self.counter = 0
        self.offset_x = -131
        self.offset_y = -185
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = Game.e_boss.rect.center
        self.ani_last = pg.time.get_ticks()
        self.ani_cd = 400

    def update(self):
          #animation
        fps = 10 #bigger number means it stays longer in one frame -> slower animation
        self.counter += 1

        if self.counter >= fps and self.index < len(self.images) - 1:
            self.counter = 0
            
            #next image
            self.index += 1
            self.image = self.images[self.index]
        
        #animation is complete, all images have been used -> restart animation
        if self.counter >= fps and self.index >= len(self.images) - 1:
            self.index = 0
            self.counter = 0
            self.image = self.images[self.index]

        self.rect.x = Game.e_boss.rect.center[0] + self.offset_x
        self.rect.y = Game.e_boss.rect.center[1] + self.offset_y

class Escape_pod(pg.sprite.Sprite):
    def __init__(self, image, coords):
        super().__init__()
        self.name = "Escape pod"
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = coords
        self.cooldown = 700
        self.last = pg.time.get_ticks()
        self.is_moving = False
        self.speed = 5.3 #same as player ship speed
        self.vel_x = self.speed
        self.vel_y = -self.speed
        self.sound_played = False
    
    def update(self):
        now = pg.time.get_ticks()
        if now - self.last >= self.cooldown:
            self.is_moving = True
        if self.is_moving:
            self.rect.x += self.vel_x
            self.rect.y += self.vel_y
            if not self.sound_played:
                Game.sound_escape_pod.play()
                self.sound_played = True       

if __name__ == "__main__":
    Game = Main()
    Game.menu()

#CODEBANK
if False:
    class Game:
        def __init__(self):
            # set the desired window size
            self.window_size = Vector2(512)
            self.window = pygame.display.set_mode(self.window_size, pygame.DOUBLEBUF|pygame.HWSURFACE, 32)
            pygame.display.set_caption('playground')
            
            self.screen_scale = 3
            self.screen_size = Vector2(self.window_size/self.screen_scale)
            
            self.clock = pygame.time.Clock()
            
        ...
            
        def draw(self):
            # fill the window with our background color to clear the screen
            self.window.fill((60,50,60))

            # create a new surface which is the size of the canvas we want
            screen = pygame.Surface(self.screen_size, pygame.SRCALPHA)

            # all drawing/blitting gets applied to the "screen" surface
            
            # resize the "screen" to the same size of the window
            # and blit it to the window surface
            self.window.blit(pygame.transform.scale(screen, self.window_size),Vector2())

            # update the window surface
            pygame.display.flip()