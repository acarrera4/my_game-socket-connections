#file created by Alec Carrera
# sources : http://kidscancode.org/blog/2016/08/pygame_1-1_getting-started/ and Mr. Cozort


'''
My goal is:

to add a health system 
*when you touch particles you lose life*
health bar^
add sound when touch particles
add a second player 

'''

import pygame as pg
import os

# import settings 
from settings import *
from sprites import *

import sys
import socket
import pickle
import select
import random


BUFFERSIZE = 100000


#initializing sound  
pg.mixer.init()

#set up assets folders
game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, "images")

sound_folder = os.path.join(game_folder, "sounds")
#damage_se = pg.mixer.Sound("punch_SE.mp3")


# create game class in order to pass properties to the sprites file

class Game:
    def __init__(self):
        serverAddr = '127.0.0.1'
        if len(sys.argv) == 2:
            serverAddr = sys.argv[1]

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((serverAddr, 4321))

        self.playerid = 1

        # init game window etc.
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption("my game")
        self.clock = pg.time.Clock()
        self.running = True
        # print(self.screen)

    def new(self):
        # starting a new game
        #sets variabels for classe created in other game files
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.player = Player(self)
        self.player_2 = Player2(self)
        self.plat1 = Platform(WIDTH, 50, 0, HEIGHT-50, (150,150,150), "normal")

        #prepares python to add sprites from given variables
        self.all_sprites.add(self.plat1)
        self.platforms.add(self.plat1)
        self.all_sprites.add(self.player_2)


        #adds platforms and mobs to screen 
        self.all_sprites.add(self.player)
        for plat in PLATFORM_LIST:
            p = Platform(*plat) 
            self.all_sprites.add(p)
            self.platforms.add(p)
        for i in range(0,12):
            m = Mob(20,20,(0,255,0))
            self.all_sprites.add(m)
            self.enemies.add(m)
        self.run()

    #sets method that runs the different components of the game, including the frame rate
    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.check()
            self.events()
            self.update()
            self.draw()

    def check(self):
        ins, outs, ex = select.select([self.s], [], [], 0)
        for inm in ins: 
            gameEvent = pickle.loads(inm.recv(BUFFERSIZE))
            # print(gameEvent)
            if gameEvent[0] == 'id update':
                self.playerid = gameEvent[1]
                print("Player ID:",self.playerid)
                self.player.id = self.playerid
                self.player_2.id = self.playerid
                self.player.s = self.s
                self.player_2.s = self.s
            if gameEvent[0] == 'move update':
                gameEvent.pop(0)
                if gameEvent[0][0] != self.playerid and gameEvent[0][1] == "UP":
                    if self.playerid == 1:self.player.jump()
                    elif self.playerid == 2:self.player_2.jump()
                if gameEvent[0][0] != self.playerid and gameEvent[0][1] != "UP":
                    # self.update(gameEvent[0][1])
                    move = gameEvent[0][1]

                    if self.playerid == 1:self.player.value = float(move)
                    elif self.playerid == 2:self.player_2.value = float(move)
                    # print("Tried Update", move)
            if gameEvent[0] == 'health update' and self.playerid == 2:
                gameEvent.pop(0)
                self.player.health = float(gameEvent[0][1][0])
                self.player_2.health = float(gameEvent[0][1][1])
            if gameEvent[0] == 'mob update' and self.playerid == 2:
                gameEvent.pop(0)
                for mob, mob_pos in zip(self.enemies, gameEvent[0][1]):
                    mob.pos = mob_pos[0]
                    mob.rect.center = mob_pos[0]
                    mob.vel = mob_pos[1]



    #method that loads the images and moves them to desired location 
    def load_data(self):
        self.player1img = pg.image.load(os.path.join(img_folder, 'player_1_life_image.jpg')).convert()
        self.player1img_rect = self.player1img.get_rect()
        self.player1img_rect.x = 15
        self.player1img_rect.y = 545
        self.screen.blit(self.player1img, self.player1img_rect)
        self.player2img = pg.image.load(os.path.join(img_folder, 'player_2_life_image.jpg')).convert()
        self.player2img_rect = self.player2img.get_rect()
        self.player2img_rect.x = 500
        self.player2img_rect.y = 545
        self.screen.blit(self.player2img, self.player2img_rect)

        
    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            # if event.type == pg.KEYDOWN:
            #     if event.key == pg.K_w:
            #         self.player.jump()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    if self.playerid == 1:self.player_2.jump()
                    elif self.playerid == 2:self.player.jump()
                    ge = ['move update', self.playerid, "UP"]
                    self.s.send(pickle.dumps(ge))


    # computer checking for updates, method
    def update(self, move=None):
        self.all_sprites.update()

        if random.random() < 0.3 and self.playerid == 1:
            positions = []

            for mob in self.enemies:
                positions.append([mob.pos, mob.vel])

            ge = ['mob update', self.playerid, positions]
            self.s.send(pickle.dumps(ge))


        # if player hits particles health is removed, used later for health bar
        #printed in terminal to make sure computer registers collosions
        player_death = pg.sprite.spritecollide(self.player, self.enemies, False)
        if player_death:
            self.player.health -= 4
            # print("PLayer1 Health:", self.player.health)

        player2_death = pg.sprite.spritecollide(self.player_2, self.enemies, False)
        if player2_death:
            self.player_2.health -= 4
            # print("PLayer2 Health:", self.player_2.health)

        # plays sound when players collide with particles 
        #p1hits = pg.sprite.spritecollide(self.player, self.enemies, False)
        #if p1hits:
            #damage_se.play()
        
        #p2hits = pg.sprite.spritecollide(self.player_2, self.enemies, False)
        #if p2hits:
            #damage_se.play()

        
        # sets up output if player collides with a specific platform
        # jump sets player to jump if collide with bouncey platform
        if self.player.vel.y > 0:
            hits = pg.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                if hits[0].variant == "bouncey":
                    self.player.pos.y = hits[0].rect.top
                    self.player.vel.y = -PLAYER_JUMP
                else:
                    self.player.pos.y = hits[0].rect.top
                    self.player.vel.y = 0
        if self.player_2.vel.y > 0:
            hits = pg.sprite.spritecollide(self.player_2, self.platforms, False)
            if hits:
                if hits[0].variant == "bouncey":
                    self.player_2.pos.y = hits[0].rect.top
                    self.player_2.vel.y = -PLAYER_JUMP
                else:
                    self.player_2.pos.y = hits[0].rect.top
                    self.player_2.vel.y = 0

    #draws the screen by filling background, adding sprites, loading the photos and health bars
    def draw(self):
        self.screen.fill(BLACK)
        self.all_sprites.draw(self.screen)
        self.load_data()
        self.draw_health_bar(self.screen, 120, 560, self.player.health)
        self.draw_health_bar(self.screen, 590, 560, self.player_2.health)

        # Generate a random number between 0 and 1
        random_number = random.random()

        if self.playerid == 1 and random_number<0.1:
            ge = ['health update', self.playerid, [self.player.health, self.player_2.health]]
            self.s.send(pickle.dumps(ge))

        pg.display.flip()

    # method for drawing health bar
    #credit to Mr. Cozort
    def draw_health_bar(self, surf, x, y, pct):
        if pct < 0:
            pct = 0
        BAR_LENGTH = 200
        BAR_HEIGHT = 20
        fill = (pct / 100) * BAR_LENGTH
        outline_rect = pg.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
        fill_rect = pg.Rect(x, y, fill, BAR_HEIGHT)
        pg.draw.rect(surf, CYAN, fill_rect)
        pg.draw.rect(surf, BLACK, outline_rect, 2)
    

    clock = pg.time.Clock()
 


# instantiate the game class
g = Game()

# kick off the game loop
while g.running:
    g.new()

pg.quit()