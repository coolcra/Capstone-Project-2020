
import pygame as pg
import numpy as np
import sys
import pickle
from os import path
from settings import *
from sprites import *
from tilemap import *
class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.numGames = 0



        self.load_data()

    def load_data(self):
        game_folder = path.dirname(__file__)
        img_folder = path.join(game_folder, 'img')
        self.map = Map(path.join(game_folder, 'map.txt'))
        self.coin_img = pg.image.load(path.join(img_folder, COIN_IMG)).convert_alpha()
        self.player_img = pg.image.load(path.join(img_folder, PLAYER_IMG)).convert_alpha()
        self.zomb_img = pg.image.load(path.join(img_folder, ZOMB_IMG)).convert_alpha()
        self.wall_img = pg.image.load(path.join(img_folder, WALL_IMG)).convert_alpha()
        self.wall_img = pg.transform.scale(self.wall_img, (TILESIZE, TILESIZE))

    def new(self):
        # initialize all variables and do setup for a new game
        self.end_screen()
        self.health = 100
        self.score = 0
        self.numGames += 1
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.zombs = pg.sprite.Group()
        self.coins = pg.sprite.Group()
        for row, tiles in enumerate(self.map.data):
            for col, tile in enumerate(tiles):
                if tile == '1':
                    Wall(self, col, row)
                if tile == 'Z':
                    Zomb(self, col, row)
                if tile == 'P':
                    self.player = Player(self, col, row)
                if tile == '.':
                    Coins(self, col, row)



    def run(self):
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000.0  # fix for Python 2.x
            self.events()
            self.update()
            self.draw()
            #print(self.reward)

            if self.health == 0:
                self.reward += 5
                self.end_screen()
                self.new()
            if self.score == 30:
                self.end_screen()
                self.reward -= 1
                self.new()


    def health_bar(self, x, y, cool):
        if cool < 0:
            cool = 0
        BAR_LENGTH = 200
        BAR_HEIGHT = 25
        fill = (cool / 100) * BAR_LENGTH
        outline_rect = pg.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
        fill_rect = pg.Rect(x, y, fill, BAR_HEIGHT)
        pg.draw.rect(self.screen, PURPLE, fill_rect)
        pg.draw.rect(self.screen, BLACK, outline_rect, 2)

    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        # update portion of the game loop
        self.all_sprites.update()

        #my main backend lies here
        # model hyperparameters
        ALPHA = 1.0
        GAMMA = 0.5
        EPS = 1.0
        #Q = {}
        with open('Q.pickle', 'rb') as f:
           Q = pickle.load(f)

        #for zomb in self.zombs:
        #    for state in zomb.stateSpace:
        #        for action in zomb.possibleActions:
        #           Q[state, action] = 0
        totalRewards = np.zeros(self.numGames)

        epRewards = 0

        rand = np.random.random()
        for zomb in self.zombs:
            observation = zomb.state
            #state
            action = maxAction(Q, observation, zomb.possibleActions) if rand < (1-EPS) \
                                                        else zomb.actionSpaceSample()
            #choosing the best action possible


            observationnew, reward, done, info = zomb.step(action)

            #print(action)
        epRewards = reward
        #print(self.reward)
        for zomb in self.zombs:
            possible_actions = zomb.possibleActions
            action_ = maxAction(Q, observationnew, possible_actions)
            #print(action_)

        Q[observation,action] = Q[observation,action] + ALPHA*(self.reward + \
                    GAMMA*Q[observationnew,action_] - Q[observation,action])
        observation = observationnew
        if EPS - 2 / self.numGames > 0:
            EPS -= 2 / self.numGames
        else:
            EPS = 0
        for i in range(self.numGames):
            totalRewards[i] = epRewards
            #print(totalRewards)
        with open('Q.pickle', 'wb') as f:
            # Pickle the 'data' dictionary using the highest protocol available.
            pickle.dump(Q, f, pickle.HIGHEST_PROTOCOL)

    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))

    def draw(self):
        pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))
        self.screen.fill(BGCOLOR)
        self.all_sprites.draw(self.screen)
        font = pg.font.SysFont('Arial', 30, True, False)
        text = font.render("Coins = " + str(self.score), True, BLACK)
        self.screen.blit(text, [500, 5] )
        self.health_bar(150, 5, self.health)
        font = pg.font.SysFont('Arial', 30, True, False)
        text = font.render("Health = ", True, BLACK)
        self.screen.blit(text, [25, 5] )
        pg.display.flip()



    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()


    def end_screen(self):
        self.screen.fill(YELLOW)
        font = pg.font.SysFont('Arial', 30, True, False)
        text = font.render("~ Dungeon Escape ~" , True, BLUE)
        self.screen.blit(text, [150, 100])
        font = pg.font.SysFont('Arial', 20, True, False)
        text = font.render("Controls: R/L arrows:Turn, U/D arrows:Move", True, BLUE)
        self.screen.blit(text, [100, 300])
        font = pg.font.SysFont('Arial', 30, True, False)
        text = font.render("Start by pressing a key", True, BLUE)
        self.screen.blit(text, [150, 600])
        pg.display.flip()
        waiting = True
        while waiting:
            pg.init()
            self.clock.tick(60)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    sys.exit()
                if event.type == pg.KEYDOWN:
                    waiting = False

# create the game object
g = Game()
def maxAction(Q, state, actions):
    try:
        values = np.array([Q[state,a] for a in actions])
        action = np.argmax(values)
        #print(action)
        return actions[action]

    except KeyError:
        print(state)
        sys.exit()




g.new()
g.run()
