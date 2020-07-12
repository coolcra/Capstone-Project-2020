import pygame as pg
import numpy as np
from itertools import product
from settings import *
from tilemap import collide_hit_rect
vec = pg.math.Vector2


class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.player_img
        self.rect = self.image.get_rect()
        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center
        self.vel = vec(0, 0)
        self.pos = vec(x, y) * TILESIZE
        self.x = x
        self.y = y
        self.rotate = 0

    def get_keys(self):
        self.rot_speed = 0
        self.vel = vec(0, 0)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.rot_speed = PLAYER_ROT_SPEED
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.rot_speed = -PLAYER_ROT_SPEED
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.vel = vec(PLAYER_SPEED, 0).rotate(-self.rotate)
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.vel = vec(-PLAYER_SPEED / 2, 0).rotate(-self.rotate)

    def collide_with_walls(self, dir):
        if dir == 'x':
            hits = pg.sprite.spritecollide(self, self.game.walls, False, collide_hit_rect)
            if hits:
                if self.vel.x > 0:
                    self.pos.x = hits[0].rect.left - self.hit_rect.width / 2
                if self.vel.x < 0:
                    self.pos.x = hits[0].rect.right + self.hit_rect.width / 2
                self.vel.x = 0
                self.hit_rect.centerx = self.pos.x
        if dir == 'y':
            hits = pg.sprite.spritecollide(self, self.game.walls, False, collide_hit_rect)
            if hits:
                if self.vel.y > 0:
                    self.pos.y = hits[0].rect.top - self.hit_rect.height / 2
                if self.vel.y < 0:
                    self.pos.y = hits[0].rect.bottom + self.hit_rect.height / 2
                self.vel.y = 0
                self.hit_rect.centery = self.pos.y

    def collect_coins(self, dir):
        if dir == 'x':
            hits = pg.sprite.spritecollide(self, self.game.coins, True, collide_hit_rect)
            if hits:
                self.game.score += 1
                self.game.reward -= 1
        if dir == 'y':
            hits = pg.sprite.spritecollide(self, self.game.coins, True, collide_hit_rect)
            if hits:
                self.game.score += 1
                self.game.reward -= 1


    def get_injured(self, direction):
        if direction == 'x':
            hits = pg.sprite.spritecollide(self, self.game.zombs, False, collide_hit_rect)
            if hits:
                if self.game.health > 0:
                    self.game.health -= 1

        if direction == 'y':
            hits = pg.sprite.spritecollide(self, self.game.zombs, False, collide_hit_rect)
            if hits:
                if self.game.health > 0:
                    self.game.health -= 1


    def update(self):
        self.get_keys()
        self.rotate = (self.rotate + self.rot_speed * self.game.dt) % 360
        self.image = pg.transform.rotate(self.game.player_img, self.rotate)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.pos += self.vel * self.game.dt
        self.hit_rect.centerx = self.pos.x
        self.collide_with_walls('x')
        self.collect_coins('x')
        self.get_injured('x')
        self.hit_rect.centery = self.pos.y
        self.collide_with_walls('y')
        self.collect_coins('y')
        self.get_injured('y')
        self.rect.center = self.hit_rect.center

class Coins(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.coins
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.coin_img
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

class Zomb(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.zombs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.zomb_img
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
        #image = image provided in game
        self.x = x
        self.y = y
        self.player_x = self.game.player.x
        self.player_y = self.game.player.y
        self.pos = (self.x, self.y)
        #print(self.pos)
        self.hit_rect = AI_HIT_RECT
        self.hit_rect.center = self.rect.center
        zombie_pos = self.pos
        self.state = ((self.player_x, self.player_y), zombie_pos)
        #print(self.pos)
        initstate = 0
        self.stateSpace = {}
        # Q = {coord: initstate for coord in product(range(GRIDWIDTH),range(GRIDHEIGHT))})
        for player_pos in product(range(int(GRIDWIDTH) + 1), range(int(GRIDHEIGHT) + 1)):
           for zombie_pos in product(range(int(GRIDWIDTH) + 1), range(int(GRIDHEIGHT) + 1)):
                  self.stateSpace[(player_pos, zombie_pos)] = 0

                  #possible states
                  # initialise the Q-value for each state to be 0
        self.actionSpace = {'U': - 2, 'D': 2,
                            'L': - 1, 'R': 1}
        #corresponding adjustments
        self.possibleActions = ['U', 'D', 'L', 'R']
        #list of possible actions
        self.vel_x = 0
        self.vel_y = 0
        self.acc_x = 0
        self.acc_y = 0
        self.rect.center = (self.x, self.y)
        self.rotate = 0
#collision detection
    def ai_collide_with_walls(self, dir, action):
        if dir == 'x':
            hits = pg.sprite.spritecollide(self, self.game.walls, False, collide_hit_rect)
            if hits:
                if self.actionSpace[action] == -1:
                    self.rect.x = hits[0].rect.left - self.hit_rect.width / 2
                if self.actionSpace[action] == 1:
                    self.rect.x = hits[0].rect.right + self.hit_rect.width / 2
                self.hit_rect.centerx = self.rect.x
        if dir == 'y':
            hits = pg.sprite.spritecollide(self, self.game.walls, False, collide_hit_rect)
            if hits:
                if self.actionSpace[action] == -2:
                    self.rect.y = hits[0].rect.top - self.hit_rect.height / 2
                if self.actionSpace[action] == 2:
                    self.rect.y = hits[0].rect.bottom + self.hit_rect.height / 2
                self.hit_rect.centery = self.rect.y

    def zombiehandling(self):
        return self.pos


#set new state as current state
    def setState(self):
        zombie_pos = self.zombiehandling()
        self.state = ((self.player_x, self.player_y), zombie_pos)
        #print(self.state)


#state at which the reward changes
    def TerminalState(self, state):
        if pg.sprite.spritecollide(self.game.player, self.game.zombs, False, collide_hit_rect):
            #print("yeh")  (haha why not)
            return True
        else:
            return False
#step function determines next course of action + state change
    def step(self, action):
        x, y = self.x, self.y
        #print(self.actionSpace[action])
#move as per action chosen
        if self.actionSpace[action] == 2 and self.rect.y < GRIDHEIGHT:
            self.y = self.y + 1
            #to prevent errors 0.5 * TILESIZE is a suitable number
            self.rect.y = self.rect.y + 0.5 * TILESIZE

            #print("DOWN" , (self.x, self.y))


        elif self.actionSpace[action] == -2 and self.rect.y > 0:
            self.y = self.y - 1
            self.rect.y = self.rect.y - 0.5 * TILESIZE

            #print("UP", (self.x, self.y))


        elif self.actionSpace[action] == 1 and self.rect.x < GRIDWIDTH:
            self.x = self.x + 1
            self.rect.x = self.rect.x + 0.5 * TILESIZE

            #print("RIGHT", (self.x, self.y))

        elif self.actionSpace[action] == -1 and self.rect.x > 0.5 * TILESIZE:
            #print("hi")
            self.x = self.x - 1
            self.rect.x = self.rect.x - 0.5 * TILESIZE
        lol = self.zombiehandling()
        resultingState = ((self.player_x, self.player_y), lol)
        #checks if the current state is a terminal one
        self.game.reward = -1 if not self.TerminalState(resultingState) else + 1
        #print(self.game.reward)
        #set the new state as the current state
        self.setState()
        #prevents crossing through the walls (the agent)
        self.hit_rect.centerx = self.rect.x
        self.ai_collide_with_walls('x', action)
        self.hit_rect.centery = self.rect.y
        self.ai_collide_with_walls('y', action)
        return resultingState, self.game.reward,\
            self.TerminalState(resultingState), None


#random initialiser action (ie at the start choose a random action
    def actionSpaceSample(self):
        return np.random.choice(self.possibleActions)



    def update(self):
        pass







class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.wall_img
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
