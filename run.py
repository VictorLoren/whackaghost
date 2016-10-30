# Whack-A-Ghost
# VictorLoren

import pygame
import pygame.locals as pyglocals
import os
from random import random as rand
from random import shuffle


FPS = 10  # game has very simple animations and requires only slow refreshes
WINDOWWIDTH = 1600  # game will take up whole screen on decent monitor
WINDOWHEIGHT = 900

# Color definitions
BLACK = (0,0,0)

# Levels
LEVELEASY = 0
LEVELMEDI = 1
LEVELHARD = 2

# Lifespan constraints (in ms)
LIFEMIN = 500
LIFEMAX = 1800

GAMETIME = 15

# Timer to check if things have changed in past 1/10th second or 100ms
UPDATETIMER, UPDATETIME = pygame.USEREVENT+1, 100
pygame.time.set_timer(UPDATETIMER, UPDATETIME)


class GameInfo():
    '''Reference to the current game being played.

    Attributes:
        level: Integer saying how hard this game is.
        timeLeft: Integer of how many seconds left in the game.
        score: Integer of the current score. Starts at 0.
        ghostsAlive: List of Ghost objects that are currently alive
    '''
    def __init__(self, level, timeLeft=GAMETIME):
        self.level = level
        self.timeLeft = timeLeft
        self.isGameOver = False
        self.score = 0
        self.ghostsAlive = []

    def getScore(self):
        '''Return the score of current game.'''
        return self.score

    def updateTime(self,timeLeft):
        '''Update game clock to new integer/seconds left.'''
        assert type(timeLeft) == type(0)
        self.timeLeft = timeLeft

    def getTime(self):
        '''Return how much game time is left in seconds (integer).'''
        return self.timeLeft

    def endGame(self):
        '''Game has finished so reset all parts except score.'''
        self.isGameOver = True
        self.ghostsAlive = []

    def startGame(self,level):
        '''Starts game after reseting attributes, thought level can change.'''
        self.level = level
        self.timeLeft = GAMETIME
        self.isGameOver = False
        self.score = 0
        self.ghostsAlive = []

    def whosAlive(self):
        '''Returns which Ghost objects are currently alive.'''
        return self.ghostsAlive

    def ghostBorn(self,ghost,lifespan):
        '''Add newly born ghost to ghostsAlive list.

        Args:
            ghost: Ghost object that was birthed
        '''
        ghost.born(lifespan)
        self.ghostsAlive += [ghost]

    def ghostEscape(self,ghost):
        '''When a ghost escapes because her lifespan is up, (potentially)
        update the score and remove previously living ghost from ghostsAlive
        list. Note a ghost can only escape if it was already alive.

        Args:
            ghost: Ghost object to be killed
        '''
        self.ghostsAlive.remove(ghost)
        # self.score -= ghost.points
        ghost.escape()

    def killGhost(self,ghost):
        '''When a ghost is killed, update the score and remove previously
        living ghost from ghostsAlive list. Note a ghost can only be killed if
        it was already alive.

        Args:
            ghost: Ghost object to be killed
        '''
        self.ghostsAlive.remove(ghost)
        self.score += ghost.points
        ghost.die()


class Ghost(pygame.sprite.Sprite):
    '''A ghost that will born and then escape if her lifespan finishes or dies
    if she is killed.

    Ghost will be associated with a sprite and a physical button. Animations on
    the screen and LED button flashes.

    Attributes:
        color: String for the ghost color and referenced by file
            'ghost_COLOR.png'.
        position: Tuple of two integers to define where the ghost will be
            located on the screen.
        points: Optional integer variable to define the point value rewarded to
            a player's kill.
        isAlive: Boolean to say whether ghost is available to be killed. (False
            when ghost is killed or she escapes.)
    '''

    def __init__(self, color, position, points=1):
        pygame.sprite.Sprite.__init__(self)
        self.color = color
        self.image = pygame.image.load(os.path.join('images','ghostLimbo.png'))
        #TODO: Scale image to fit proper screen size
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.position = position  # tuple of integers
        self.points = points
        self.isAlive = False

    def born(self,lifespan):
        self.lifespan = lifespan
        self.isAlive = True
        self.image = pygame.image.load(
            os.path.join('images','ghost_%s.png' %self.color))
        print('%s Ghost Born - Lifespan: %s' %(self.color,self.lifespan))

    def escape(self):
        self.isAlive = False
        self.image = pygame.image.load(
            os.path.join('images','ghostEscape.png'))
        #TODO: Update score
        print('%s Ghost Escaped' %self.color)

    def die(self):
        self.isAlive = False
        self.image = pygame.image.load(
            os.path.join('images','ghostDie.png'))
        #TODO: Update score
        print('%s Ghost Died' %self.color)

    def limbo(self):
        '''State of ghost when waiting to be born and therefore invisible to
        the screen.'''

        self.isAlive = False
        self.image = pygame.image.load(os.path.join('images','ghostLimbo.png'))
        print('%s Ghost went to Limbo' %self.color)


def posInPercent(x,y):
    '''Defines a vector/position based on the size of the screen.
    Args:
        x: Percent to the right of the screen to define the x-coordinate
        y: Percent to the bottom of the screen to define the y-coordinate
    Returns:
        Tuple of pixels from the top-left corner of the screen
    '''
    return (x*int(WINDOWWIDTH * 0.01), y*int(WINDOWHEIGHT * 0.01))


def randomBirth(aliveGhosts, allGhosts, lifespan=0):
    '''Birth a random ghost (who isn't alive) with a random lifespan.'''
    if lifespan == 0:
        # Create a lifespan between LIFEMIN and LIFEMAX
        lifespan = int(rand() * (LIFEMAX-LIFEMIN) + LIFEMIN)
        #TODO: Level decides lifespan too
    # Pick random ghost and check she is not alive
    shuffle(allGhosts)
    for ghost in allGhosts:  # shuffles ghosts (references originals)
        if ghost not in aliveGhosts:
            newGhost = ghost
    return newGhost,lifespan

def main():
    # Initialize a black screen
    pygame.init()
    screen = pygame.display.set_mode((WINDOWWIDTH,WINDOWHEIGHT))
    pygame.display.set_caption('Whack-A-Ghost')
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill(BLACK)

    # Create ghosts
    ghosts = [
        Ghost('white', posInPercent(5,15)),
        Ghost('green', posInPercent(15,50)),
        Ghost('yellow', posInPercent(45,70)),
        Ghost('red', posInPercent(65,50)),
        Ghost('blue', posInPercent(75,15))
    ]

    # Time keepers
    clock = pygame.time.Clock()
    msPassed = 0 # Keep time until next second (1000ms)
    ghostLifeClock = {}  # tracks how long ghost is alive
    for i,ghost in enumerate(ghosts):
        ghostLifeClock[ghost] = 0


    # Create game
    game = GameInfo(LEVELMEDI)
    game.startGame(LEVELMEDI)

    # Text for game
    myfont = pygame.font.SysFont("monospace", 50)
    labelScore = myfont.render("Score: %d" %game.getScore(), 1, (255,0,0))
    labelTimer = myfont.render("Timer: %d" %game.getTime(), 1, (255,0,0))
    labelGameOver = myfont.render("GAME OVER", 1, (255,0,0))



    while (not game.isGameOver):
        for event in pygame.event.get():
            if event.type == pyglocals.QUIT or (event.type == pyglocals.KEYUP and event.key == pyglocals.K_ESCAPE):
                pygame.quit()
            # Check every UPDATETIME milliseconds to see if something needs to be checked
            if event.type == UPDATETIMER:
                # Randomly birth ghosts (assuming ghost is in limbo/not alive)
                # Make sure not all ghosts are alive
                if len(game.whosAlive()) != len(ghosts) \
                   and rand() > 0.8:  # only produce a ghost sometimes
                    # Make copy of ghosts so it doesn't get shuffled
                    babyGhost,lifespan = randomBirth(game.whosAlive(),ghosts[:])
                    game.ghostBorn(babyGhost,lifespan)
                #TODO: Check for any ghost killed (update score)
                #TODO: Check for any ghost escapes (update score)
                for ghost in game.whosAlive():
                    ghostLifeClock[ghost] += UPDATETIME
                    if ghostLifeClock[ghost] > ghost.lifespan:  #time to escape
                        game.ghostEscape(ghost)
                        ghostLifeClock[ghost] = 0  # reset life
                #Update the game clock display
                msPassed += UPDATETIME  # increase time passed
                if msPassed >= 1000:  # One second has passed
                    #
                    msPassed = 0
                    game.updateTime(game.getTime()-1)
                    labelTimer = myfont.render("Timer: %d" %game.getTime(), 1, (255,0,0))
                #TODO: Check if game has ended
                if game.getTime() == 0:
                    game.endGame()
                print 'Checked'
            #TEST: births
            elif event.type == pyglocals.KEYUP and event.key == pyglocals.K_1:
                ghosts[0].born(1)
            elif event.type == pyglocals.KEYUP and event.key == pyglocals.K_2:
                ghosts[1].born(1)
            elif event.type == pyglocals.KEYUP and event.key == pyglocals.K_3:
                ghosts[2].born(1)
            elif event.type == pyglocals.KEYUP and event.key == pyglocals.K_4:
                ghosts[3].born(1)
            elif event.type == pyglocals.KEYUP and event.key == pyglocals.K_5:
                ghosts[4].born(1)
            #TEST: deaths
            elif event.type == pyglocals.KEYUP and event.key == pyglocals.K_q:
                ghosts[0].die()
            elif event.type == pyglocals.KEYUP and event.key == pyglocals.K_w:
                ghosts[1].die()
            elif event.type == pyglocals.KEYUP and event.key == pyglocals.K_e:
                ghosts[2].die()
            elif event.type == pyglocals.KEYUP and event.key == pyglocals.K_r:
                ghosts[3].die()
            elif event.type == pyglocals.KEYUP and event.key == pyglocals.K_t:
                ghosts[4].die()

        # Update the screen
        clock.tick(FPS)
        screen.fill(BLACK)
        for ghost in ghosts:
            screen.blit(ghost.image, ghost.position)


        screen.blit(labelScore, posInPercent(5, 2))
        screen.blit(labelTimer, posInPercent(80, 2))
        pygame.display.update()

    #Game Over screen to start over
    while True:
        for event in pygame.event.get():
            if event.type == pyglocals.QUIT or (event.type == pyglocals.KEYUP and event.key == pyglocals.K_ESCAPE):
                pygame.quit()

        screen.fill(BLACK)
        labelFinalScore = myfont.render('Score: %d' %game.getScore(), 1, (255,0,0))
        screen.blit(labelGameOver, posInPercent(40, 30))
        screen.blit(labelFinalScore, posInPercent(40, 40))

        pygame.display.update()


if __name__ == '__main__':
    main()
