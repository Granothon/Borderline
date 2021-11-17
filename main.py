#Project Borderline: 2d Space shooter
import pygame as pg
import random as r
import math

class Player(pg.sprite.Sprite):
    def __init__(self, size, image, image_left, image_right, image_thrust, image_thrust2, x, y):
        super().__init__()
        self.image = image
        self.image = pg.transform.scale(self.image, (size, size))
        self.image_left = image_left
        self.image_left = pg.transform.scale(self.image_left, (size, size))
        self.image_right = image_right
        self.image_right = pg.transform.scale(self.image_right, (size, size))
        self.thrust = image_thrust
        self.thrust2 = image_thrust2
        self.thrust = pg.transform.scale(self.thrust, (size // 3, size // 3))
        self.thrust2 = pg.transform.scale(self.thrust2, (size // 3, size // 3))
        self.draw_thrust = self.thrust
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.move_left = False
        self.move_right = False
        self.is_firing = False
        self.bullet_last = pg.time.get_ticks()
        self.bullet_cooldown = 100
        self.weapon = "Left"
        self.vel_x = 0
        self.score = 0
        self.hp = 3
    
    def update(self):
        
        #draw thrust: slow
        self.draw_thrust = self.thrust

        #stop player from moving
        self.vel_x = 0 
        self.vel_y = 0
        self.move_left = False
        self.move_right = False
        self.is_firing = False
        
        #check for key held down
        keystate = pg.key.get_pressed()
        
        #make the player unable to leave the screen while moving
        if keystate[pg.K_LEFT]:
            self.move_left = True
            if self.rect.left - self.vel_x >= 0:
                self.vel_x = -5.3
        if keystate[pg.K_RIGHT]:
            self.move_right = True
            if self.rect.right + self.vel_x <= Game.scr_w:
                self.vel_x = 5.3
        if keystate[pg.K_UP]:
            self.draw_thrust = self.thrust2
            if self.rect.top + self.vel_y >= 0:
                self.vel_y = -4.3
        if keystate[pg.K_DOWN]:
            if self.rect.bottom + self.vel_y <= Game.scr_h:
                self.vel_y = 4.3
        if keystate[pg.K_SPACE]:
            self.is_firing = True

        #move player
        self.rect.x += self.vel_x 
        self.rect.y += self.vel_y

        #attack
        if self.is_firing:
            bullet_y = self.rect.y + 40
            now = pg.time.get_ticks()
            if now - self.bullet_last >= self.bullet_cooldown:
                self.bullet_last = now
                if self.weapon == "Left":
                    Game.bullet_group.add(Bullet(7, Game.bullet_image, self.rect.x + 15, bullet_y))
                    self.weapon = "Right"
                elif self.weapon == "Right":
                    Game.bullet_group.add(Bullet(7, Game.bullet_image, self.rect.x + 64, bullet_y))
                    self.weapon = "Left"

class Bullet(pg.sprite.Sprite):
    def __init__(self, size, image, x, y):
        super().__init__()
        self.image = image
        self.image = pg.transform.scale(self.image, (size, size * 2.6))
        self.rect = self.image.get_rect()
        self.bullet_speed = 5.3 #same as player ship speed
        self.rect.center = (x, y)

    def update(self):
        #check for collisions
        for enemy in Game.e1_group:
            if pg.sprite.collide_rect(self, enemy):
                #collision
                Game.explosion_group.add(Explosion(Game.explosion_sprites, enemy.rect.center[0], enemy.rect.center[1]))
                self.kill()
                enemy.kill()
        
        self.rect.y -= self.bullet_speed

class Bolt(pg.sprite.Sprite):
    def __init__(self, size, image, x, y):
        super().__init__()
        self.image = image
        self.image = pg.transform.scale(self.image, (size, size))
        self.rect = self.image.get_rect()
        self.speed = 5.3 #same as player ship speed
        self.rect.center = (x, y)
        self.angle = math.atan2(Game.p1.rect.y - self.rect.y, Game.p1.rect.x - self.rect.x)
        self.x_vel = math.cos(self.angle) * self.speed
        self.y_vel = math.sin(self.angle) * self.speed
    
    def update(self):
        #check for collisions
        if pg.sprite.collide_rect(self, Game.p1):
            #collision
            Game.explosion_group.add(Explosion(Game.explosion_sprites, Game.p1.rect.center[0], Game.p1.rect.center[1]))
            self.kill()
            #Game.p1.kill() ;)
        
        self.rect.x += self.x_vel
        self.rect.y +=  self.y_vel



class Explosion(pg.sprite.Sprite):
    def __init__(self, images: list, x, y):
        super().__init__()
        self.images = images
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0
    
    def update(self):
        animation_speed = 4
        self.counter += 1

        if self.counter >= animation_speed and self.index < len(self.images) - 1:
            self.counter = 0
            
            #next image
            self.index += 1
            self.image = self.images[self.index]
        
        #if animation is complete the sprite is now removed
        if self.counter >= animation_speed and self.index >= len(self.images) - 1:
            self.kill()
            
class Enemy(pg.sprite.Sprite):
    def __init__(self, size, image, image_left, image_right, x, y):
        super().__init__()
        self.image = image
        self.image = pg.transform.scale(self.image, (size, size))
        self.image_left = image_left
        self.image_left = pg.transform.scale(self.image_left, (size, size))
        self.image_right = image_right
        self.image_right = pg.transform.scale(self.image_right, (size, size))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.move_left = False
        self.move_right = False
        self.is_firing = False
        self.bolt_last = pg.time.get_ticks()
        self.attack_cooldown = 800
        self.vel_x = 0
        self.vel_y = 0
        self.score = 0
        self.hp = 3

    def update(self):
        self.vel_y = 2.5
        
        #move enemy
        self.rect.x += self.vel_x 
        self.rect.y += self.vel_y
        if self.rect.top > 0:
            self.is_firing = True

        #attack
        if self.is_firing:
            bolt_x = self.rect.center[0]
            bolt_y = self.rect.center[1]
            now = pg.time.get_ticks()
            if now - self.bolt_last >= self.attack_cooldown:
                self.bolt_last = now
                Game.bolt_group.add(Bolt(10, Game.bolt_image, bolt_x, bolt_y))

class Main():
    def __init__(self):
        pg.init()
        
        #set screen size
        self.scr = pg.display.set_mode((864, 1080))
        
        #get width and height
        self.scr_w, self.scr_h = pg.display.get_surface().get_size()

        #set game display name and icon
        pg.display.set_caption("Borderline")
        icon = pg.image.load('assets/ships/ship 01/ship.png').convert_alpha()
        pg.display.set_icon(icon)

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

        #load player ship images
        self.p1_image = pg.image.load("assets/ships/ship 01/ship.png").convert_alpha()
        self.p1_image_left = pg.image.load("assets/ships/ship 01/left.png").convert_alpha()
        self.p1_image_right = pg.image.load("assets/ships/ship 01/right.png").convert_alpha()
        self.p1_thrust = pg.image.load("assets/ships/thrust/01/slow.png").convert_alpha()
        self.p1_thrust2 = pg.image.load("assets/ships/thrust/01/fast.png").convert_alpha()

        #load enemy ship images
        self.e1_image = pg.image.load("assets/enemy_ships/fighter/basic.png").convert_alpha()
        self.e1_image_left = pg.image.load("assets/enemy_ships/fighter/left.png").convert_alpha()
        self.e1_image_right = pg.image.load("assets/enemy_ships/fighter/right.png").convert_alpha()
        self.e1_spawn_cooldown = 4000 #4 seconds
        self.e1_spawn_last = pg.time.get_ticks()

        #load bullet image
        self.bullet_image = pg.image.load('assets/bolts/bullet.png').convert_alpha()

        #load bolt image
        self.bolt_image = pg.image.load('assets/bolts/1.png').convert_alpha()

        #load explosion animation
        self.explosion_sprites = []
        for i in range(1,8):
            image = (pg.image.load(f'assets/explosions/{i}.png')).convert_alpha()
            #maybe add scaling here
            self.explosion_sprites.append(image)
          
        #set fps
        self.clock = pg.time.Clock()
        self.fps = 60

        #sprite groups
        self.p1 = Player(80, self.p1_image, self.p1_image_left, self.p1_image_right, self.p1_thrust, self.p1_thrust2, self.scr_w // 2, self.scr_h - (self.scr_h // 10))
        self.p1_group = pg.sprite.Group()
        self.p1_group.add(self.p1)
        self.p1_group.add(self.p1)
        self.e1_group = pg.sprite.Group()
        self.bullet_group = pg.sprite.Group()
        self.bolt_group = pg.sprite.Group()
        self.explosion_group = pg.sprite.Group()

    #main loop
    def run(self):
        while True:
            self.update()
    
    def spawn_e1(self): #TODO: implement scoring for more enemies
        offset = 50
        now = pg.time.get_ticks()
        if now - self.e1_spawn_last >= self.e1_spawn_cooldown:
            self.e1_spawn_last = now
            location = r.choice(range(50, 650, 50))
            self.e1_group.add(Enemy(80, self.e1_image, self.e1_image_left, self.e1_image_right, location, 0 - offset))
            self.e1_group.add(Enemy(80, self.e1_image, self.e1_image_left, self.e1_image_right, location + 200, 0 - offset))
        
    def update(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    exit()

        #draw the parallex background layers
        self.scr.fill((0,0,0))
        
        self.scr.blit(self.bg, (0, self.bg_i))
        self.scr.blit(self.bg, (0, -self.scr_h + self.bg_i))
        
        self.scr.blit(self.bg_back_layer, (0, self.bg_back_i))
        self.scr.blit(self.bg_back_layer, (0, -self.scr_h + self.bg_back_i))

        self.scr.blit(self.bg_middle_layer, (0, self.bg_middle_i))
        self.scr.blit(self.bg_middle_layer, (0, -self.scr_h + self.bg_middle_i))
        
        self.scr.blit(self.bg_front_layer, (0, self.bg_front_i))
        self.scr.blit(self.bg_front_layer, (0, -self.scr_h + self.bg_front_i))

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
        
        self.bg_i += 0 #at the moment looks best when real background is not scrolling
        self.bg_back_i += 0.5
        self.bg_middle_i += 1.5
        self.bg_front_i += 3

        #spawning of enemies
        if self.p1.score <= 100:
            self.spawn_e1()
        #elif self.p1.score > 100: TODO: 
            #self.spawn_e2()
        
        #movement and removing of bullets
        for bullet in self.bullet_group:
            if bullet.rect.bottom < 0:
                bullet.kill()
            #keep bullets moving
            bullet.update()
        
        #movement and removing of bolts
        for bolt in self.bolt_group:
            if bolt.rect.top > self.scr_h:
                bolt.kill()
            #keep bullets moving
            bolt.update()
        
        #movement and removing on enemies
        for enemy in self.e1_group:
            if enemy.rect.top > self.scr_h:
                enemy.kill()
            #keep enemies moving   
            enemy.update()

        #draw player
        if self.p1.move_left:
            self.scr.blit(self.p1.image_left, (self.p1.rect.x, self.p1.rect.y))
        elif self.p1.move_right:
            self.scr.blit(self.p1.image_right, (self.p1.rect.x, self.p1.rect.y))
        else:
            self.p1_group.draw(self.scr)
        
        #draw afterburner
        offset_x = -12.95
        offset_y = 25
        self.scr.blit(self.p1.draw_thrust, (self.p1.rect.center[0] + offset_x, self.p1.rect.center[1] + offset_y))
        
        #keep player moving
        self.p1.update()

        #draw enemies
        self.e1_group.draw(self.scr)

        #draw bullets and bolts
        self.bullet_group.draw(self.scr)
        self.bolt_group.draw(self.scr)

        #draw explosions
        self.explosion_group.draw(self.scr)
        for explosion in self.explosion_group:
            explosion.update()

        
        pg.display.flip()
        
        self.clock.tick(self.fps)

if __name__ == "__main__":
    Game = Main()
    Game.run()


##CODEBANK##