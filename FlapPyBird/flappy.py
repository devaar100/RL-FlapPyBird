from itertools import cycle
import random
import sys
import numpy as np
import math
import time

import pygame
from pygame.locals import *


print("Flappy file")
show_sensors = True
FPS = 60
SCREENWIDTH  = 288
SCREENHEIGHT = 512
# amount by which base can maximum shift to left
PIPEGAPSIZE  = 100 # gap between upper and lower part of pipe
BASEY        = SCREENHEIGHT * 0.79
# image, sound and hitmask  dicts
IMAGES, SOUNDS, HITMASKS = {}, {}, {}

# list of all possible players (tuple of 3 positions of flap)
PLAYERS_LIST = (
    # red bird
    (
        '/users/aarnavjindal/desktop/rl/FlapPyBird/assets/sprites/redbird-upflap.png',
        '/users/aarnavjindal/desktop/rl/FlapPyBird/assets/sprites/redbird-midflap.png',
        '/users/aarnavjindal/desktop/rl/FlapPyBird/assets/sprites/redbird-downflap.png',
    ),
    # blue bird
    (
        # amount by which base can maximum shift to left
        '/users/aarnavjindal/desktop/rl/FlapPyBird/assets/sprites/bluebird-upflap.png',
        '/users/aarnavjindal/desktop/rl/FlapPyBird/assets/sprites/bluebird-midflap.png',
        '/users/aarnavjindal/desktop/rl/FlapPyBird/assets/sprites/bluebird-downflap.png',
    ),
    # yellow bird
    (
        '/users/aarnavjindal/desktop/rl/FlapPyBird/assets/sprites/yellowbird-upflap.png',
        '/users/aarnavjindal/desktop/rl/FlapPyBird/assets/sprites/yellowbird-midflap.png',
        '/users/aarnavjindal/desktop/rl/FlapPyBird/assets/sprites/yellowbird-downflap.png',
    ),
)

# list of backgrounds
BACKGROUNDS_LIST = (
    '/users/aarnavjindal/desktop/rl/FlapPyBird/assets/sprites/background-day.png',
    '/users/aarnavjindal/desktop/rl/FlapPyBird/assets/sprites/background-night.png',
)

# list of pipes
PIPES_LIST = (
    '/users/aarnavjindal/desktop/rl/FlapPyBird/assets/sprites/pipe-green.png',
    '/users/aarnavjindal/desktop/rl/FlapPyBird/assets/sprites/pipe-red.png',
)


try:
    xrange
except NameError:
    xrange = range

pygame.init()
FPSCLOCK = pygame.time.Clock()
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
pygame.display.set_caption('Flappy Bird')

# numbers sprites for score display
IMAGES['numbers'] = (
    pygame.image.load('/users/aarnavjindal/desktop/rl/FlapPyBird/assets/sprites/0.png').convert_alpha(),
    pygame.image.load('/users/aarnavjindal/desktop/rl/FlapPyBird/assets/sprites/1.png').convert_alpha(),
    pygame.image.load('/users/aarnavjindal/desktop/rl/FlapPyBird/assets/sprites/2.png').convert_alpha(),
    pygame.image.load('/users/aarnavjindal/desktop/rl/FlapPyBird/assets/sprites/3.png').convert_alpha(),
    pygame.image.load('/users/aarnavjindal/desktop/rl/FlapPyBird/assets/sprites/4.png').convert_alpha(),
    pygame.image.load('/users/aarnavjindal/desktop/rl/FlapPyBird/assets/sprites/5.png').convert_alpha(),
    pygame.image.load('/users/aarnavjindal/desktop/rl/FlapPyBird/assets/sprites/6.png').convert_alpha(),
    pygame.image.load('/users/aarnavjindal/desktop/rl/FlapPyBird/assets/sprites/7.png').convert_alpha(),
    pygame.image.load('/users/aarnavjindal/desktop/rl/FlapPyBird/assets/sprites/8.png').convert_alpha(),
    pygame.image.load('/users/aarnavjindal/desktop/rl/FlapPyBird/assets/sprites/9.png').convert_alpha()
)

# game over sprite
IMAGES['gameover'] = pygame.image.load('/users/aarnavjindal/desktop/rl/FlapPyBird/assets/sprites/gameover.png').convert_alpha()
# message sprite for welcome screen
IMAGES['message'] = pygame.image.load('/users/aarnavjindal/desktop/rl/FlapPyBird/assets/sprites/message.png').convert_alpha()
# base (ground) sprite
IMAGES['base'] = pygame.image.load('/users/aarnavjindal/desktop/rl/FlapPyBird/assets/sprites/base.png').convert_alpha()

# sounds
if 'win' in sys.platform:
    soundExt = '.wav'
else:
    soundExt = '.ogg'

SOUNDS['die']    = pygame.mixer.Sound('/users/aarnavjindal/desktop/rl/FlapPyBird/assets/audio/die' + soundExt)
SOUNDS['hit']    = pygame.mixer.Sound('/users/aarnavjindal/desktop/rl/FlapPyBird/assets/audio/hit' + soundExt)
SOUNDS['point']  = pygame.mixer.Sound('/users/aarnavjindal/desktop/rl/FlapPyBird/assets/audio/point' + soundExt)
SOUNDS['swoosh'] = pygame.mixer.Sound('/users/aarnavjindal/desktop/rl/FlapPyBird/assets/audio/swoosh' + soundExt)
SOUNDS['wing']   = pygame.mixer.Sound('/users/aarnavjindal/desktop/rl/FlapPyBird/assets/audio/wing' + soundExt)
    

class Game(object):
    def __init__(self):
        global IMAGES, HITMASKS
        self.randBg = random.randint(0, len(BACKGROUNDS_LIST) - 1)
        IMAGES['background'] = pygame.image.load(BACKGROUNDS_LIST[self.randBg]).convert()

        # select random player sprites
        self.randPlayer = random.randint(0, len(PLAYERS_LIST) - 1)
        IMAGES['player'] = (
            pygame.image.load(PLAYERS_LIST[self.randPlayer][0]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[self.randPlayer][1]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[self.randPlayer][2]).convert_alpha(),
        )

        # select random pipe sprites
        self.pipeindex = random.randint(0, len(PIPES_LIST) - 1)
        IMAGES['pipe'] = (
            pygame.transform.rotate(
            pygame.image.load(PIPES_LIST[self.pipeindex]).convert_alpha(), 180),
            pygame.image.load(PIPES_LIST[self.pipeindex]).convert_alpha(),
        )

        # hismask for pipes
        HITMASKS['pipe'] = (
            getHitmask(IMAGES['pipe'][0]),
            getHitmask(IMAGES['pipe'][1]),
        )

        # hitmask for player
        HITMASKS['player'] = (
            getHitmask(IMAGES['player'][0]),
            getHitmask(IMAGES['player'][1]),
            getHitmask(IMAGES['player'][2]),
        )
        
        for event in pygame.event.get():
            break        
        
    def init_elements(self):
        # index of player to blit on screen
        self.playerIndex = 0
        self.playerIndexGen = cycle([0, 1, 2, 1])
        
        self.playerx = int(SCREENWIDTH * 0.2)
        self.playery = int((SCREENHEIGHT - IMAGES['player'][0].get_height()) / 2)
        pipe_start = self.playerx + SCREENWIDTH/2
        
        self.basex = 0
        # amount by which base can maximum shift to left
        self.baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()
        
        self.score = self.playerIndex = self.loopIter = 0
        self.newPipe1 = getRandomPipe()
        self.newPipe2 = getRandomPipe()

        # list of upper pipes
        self.upperPipes = [
            {'x': pipe_start + 20, 'y': self.newPipe1[0]['y']},
            {'x': pipe_start + (SCREENWIDTH / 2) + 20, 'y': self.newPipe2[0]['y']},
        ]

        # list of lowerpipe
        self.lowerPipes = [
            {'x': pipe_start + 20, 'y': self.newPipe1[1]['y']},
            {'x': pipe_start + (SCREENWIDTH / 2) + 20, 'y': self.newPipe2[1]['y']},
        ]

        self.pipeVelX = -4

        # player velocity, max velocity, downward accleration, accleration on flap
        self.playerVelY    =  -9   # player's velocity along Y, default same as playerFlapped
        self.playerMaxVelY =  10   # max vel along Y, max descend speed
        self.playerMinVelY =  -8   # min vel along Y, max ascend speed
        self.playerAccY    =   1   # players downward accleration
        self.playerFlapAcc =  -9   # players speed on flapping
        self.playerFlapped = False # True when player flaps
                
        
    def frame_step(self,mv):
        reward = 1
        if mv == 1:
            if self.playery > -2 * IMAGES['player'][0].get_height():
                self.playerVelY = self.playerFlapAcc
                self.playerFlapped = True
                SOUNDS['wing'].play()
                
        crashTest = checkCrash({'x': self.playerx, 'y': self.playery, 'index': self.playerIndex},
                               self.upperPipes, self.lowerPipes)
        if crashTest[0]:
            reward = -1000

        # check for score
        playerMidPos = self.playerx + IMAGES['player'][0].get_width() / 2
        for pipe in self.upperPipes:
            pipeMidPos = pipe['x'] + IMAGES['pipe'][0].get_width() / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                self.score += 1
                SOUNDS['point'].play()

        # playerIndex basex change
        if (self.loopIter + 1) % 3 == 0:
            self.playerIndex = next(self.playerIndexGen)
        self.loopIter = (self.loopIter + 1) % 30
        self.basex = -((-self.basex + 100) % self.baseShift)
        

        # player's movement
        if self.playerVelY < self.playerMaxVelY and not self.playerFlapped:
            self.playerVelY += self.playerAccY
        if self.playerFlapped:
            self.playerFlapped = False


        self.playerHeight = IMAGES['player'][self.playerIndex].get_height()
        self.playery += min(self.playerVelY, BASEY - self.playery - self.playerHeight)

        # move pipes to left
        for uPipe, lPipe in zip(self.upperPipes, self.lowerPipes):
            uPipe['x'] += self.pipeVelX
            lPipe['x'] += self.pipeVelX

        # add new pipe when first pipe is about to touch left of screen
        if 0 < self.upperPipes[0]['x'] < 5:
            newPipe = getRandomPipe()
            self.upperPipes.append(newPipe[0])
            self.lowerPipes.append(newPipe[1])

        # remove first pipe if its out of the screen
        if self.upperPipes[0]['x'] < -IMAGES['pipe'][0].get_width():
            self.upperPipes.pop(0)
            self.lowerPipes.pop(0)

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0,0))

        for uPipe, lPipe in zip(self.upperPipes, self.lowerPipes):
            SCREEN.blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
            SCREEN.blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

        SCREEN.blit(IMAGES['base'], (self.basex, BASEY))
        # print score so player overlaps the score
        showScore(self.score)

        
        self.playerSurface = pygame.transform.rotate(IMAGES['player'][self.playerIndex], 0)
        SCREEN.blit(self.playerSurface, (self.playerx, self.playery))

        readings = self.get_sonar_readings(self.playerx,self.playery + self.playerHeight/2,
                                           self.upperPipes, self.lowerPipes)
        
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        reg = -5
        if self.playery > (SCREENHEIGHT - BASEY)/3:
            if self.playery < 2*(SCREENHEIGHT - BASEY)/3:
                reg = 0
            else:
                reg = 5
        
        readings.append(self.playerVelY)
        readings.append(reg)
        return readings, reward
    
    
    def get_sonar_readings(self, x, y, upperPipes, lowerPipes):
        readings = []
        """
        Instead of using a grid of boolean(ish) sensors, sonar readings
        simply return N "distance" readings, one for each sonar
        we're simulating. The distance is a count of the first non-zero
        reading starting at the object. For instance, if the fifth sensor
        in a sonar "arm" is non-zero, then that arm returns a distance of 5.
        """
        # Make our arms.
        arm_small = self.make_sonar_arm(x, y, 8)
        arm_med = self.make_sonar_arm(x, y, 10)
        arm_med2 = self.make_sonar_arm(x, y, 12)
        arm_big = self.make_sonar_arm(x, y, 4)

        # Rotate them and get readings.
        readings.append(self.get_arm_distance(arm_big, x, y, 1.56, upperPipes, lowerPipes))
        readings.append(self.get_arm_distance(arm_med2, x, y, 1, upperPipes, lowerPipes))
        readings.append(self.get_arm_distance(arm_med, x, y, 0.75, upperPipes, lowerPipes))
        readings.append(self.get_arm_distance(arm_small, x, y, 0.45, upperPipes, lowerPipes))
        readings.append(self.get_arm_distance(arm_small, x, y, 0, upperPipes, lowerPipes))
        readings.append(self.get_arm_distance(arm_small, x, y, -0.45, upperPipes, lowerPipes))
        readings.append(self.get_arm_distance(arm_med, x, y, -0.75, upperPipes, lowerPipes))
        readings.append(self.get_arm_distance(arm_med2, x, y, -1, upperPipes, lowerPipes))
        readings.append(self.get_arm_distance(arm_big, x, y, -1.56, upperPipes, lowerPipes))
        
        return readings
    

    def get_arm_distance(self, arm, x, y, offset, upperPipes, lowerPipes):
        # Used to count the distance.
        i = 0

        # Look at each point and see if we've hit something.
        for point in arm:
            i += 1

            # Move the point to the right spot.
            rotated_p = self.get_rotated_point(
                x, y, point[0], point[1], offset
            )

            # Check if we've hit something. Return the current i (distance)
            # if we did.
            if rotated_p[0] <= 0 or rotated_p[1] <= 0 \
                    or rotated_p[0] >= SCREENWIDTH or rotated_p[1] >= SCREENHEIGHT:
                return i  # Sensor is off the screen.
            else:
                if pixelCrash(rotated_p, upperPipes, lowerPipes) == True:
                    return i

            if show_sensors:
                pygame.draw.circle(SCREEN, (0,0,0), (rotated_p), 2)

        # Return the distance for the arm.
        return i
    

    def make_sonar_arm(self, x, y, rng):
        spread = 15  # Default spread.
        distance = 30  # Gap before first sensor.
        arm_points = []
        # Make an arm. We build it flat because we'll rotate it about the
        # center later.
        for i in range(rng):
            arm_points.append((distance + x + (spread * i), y))

        return arm_points
    

    def get_rotated_point(self, x_1, y_1, x_2, y_2, radians):
        # Rotate x_2, y_2 around x_1, y_1 by angle.
        x_change = (x_2 - x_1) * math.cos(radians) + \
            (y_2 - y_1) * math.sin(radians)
        y_change = (y_1 - y_2) * math.cos(radians) - \
            (x_1 - x_2) * math.sin(radians)
        new_x = x_change + x_1
        new_y = (y_change + y_1)
        return int(new_x), int(new_y)


def playerShm(playerShm):
    """oscillates the value of playerShm['val'] between 8 and -8"""
    if abs(playerShm['val']) == 8:
        playerShm['dir'] *= -1

    if playerShm['dir'] == 1:
         playerShm['val'] += 1
    else:
        playerShm['val'] -= 1


def getRandomPipe():
    """returns a randomly generated pipe"""
    # y of gap between upper and lower pipe
    gapY = random.randrange(0, int(BASEY * 0.6 - PIPEGAPSIZE))
    gapY += int(BASEY * 0.2)
    pipeHeight = IMAGES['pipe'][0].get_height()
    pipeX = SCREENWIDTH + 10

    return [
        {'x': pipeX, 'y': gapY - pipeHeight},  # upper pipe
        {'x': pipeX, 'y': gapY + PIPEGAPSIZE}, # lower pipe
    ]


def showScore(score):
    """displays score in center of screen"""
    scoreDigits = [int(x) for x in list(str(score))]
    totalWidth = 0 # total width of all numbers to be printed

    for digit in scoreDigits:
        totalWidth += IMAGES['numbers'][digit].get_width()

    Xoffset = (SCREENWIDTH - totalWidth) / 2

    for digit in scoreDigits:
        SCREEN.blit(IMAGES['numbers'][digit], (Xoffset, SCREENHEIGHT * 0.1))
        Xoffset += IMAGES['numbers'][digit].get_width()

        
def checkCrash(player, upperPipes, lowerPipes):
    """returns True if player collders with base or pipes."""
    pi = player['index']
    player['w'] = IMAGES['player'][0].get_width()
    player['h'] = IMAGES['player'][0].get_height()

    # if player crashes into ground
    if player['y'] + player['h'] >= BASEY - 1:
        return [True, 0]
    elif player['y'] <= 0:
        return [True, 1]
    else:

        playerRect = pygame.Rect(player['x'], player['y'],
                      player['w'], player['h'])
        pipeW = IMAGES['pipe'][0].get_width()
        pipeH = IMAGES['pipe'][0].get_height()

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            # upper and lower pipe rects
            uPipeRect = pygame.Rect(uPipe['x'], uPipe['y'], pipeW, pipeH)
            lPipeRect = pygame.Rect(lPipe['x'], lPipe['y'], pipeW, pipeH)

            # player and upper/lower pipe hitmasks
            pHitMask = HITMASKS['player'][pi]
            uHitmask = HITMASKS['pipe'][0]
            lHitmask = HITMASKS['pipe'][1]

            # if bird collided with upipe or lpipe
            uCollide = pixelCollision(playerRect, uPipeRect, pHitMask, uHitmask)
            lCollide = pixelCollision(playerRect, lPipeRect, pHitMask, lHitmask)

            if uCollide :
                return [True, 1]
            elif lCollide :
                return [True, 0]

    return [False, 2]


def pixelCrash(point, upperPipes, lowerPipes):
    if point[0] >= BASEY - 1:
        return True
    elif point[0] <= 0:
        return True
    else:
        pipeW = IMAGES['pipe'][0].get_width()
        pipeH = IMAGES['pipe'][0].get_height()

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            # upper and lower pipe rects
            if point[0] >= uPipe['x'] and point[0] <= uPipe['x']+pipeW :
                if point[1] >= uPipe['y'] and point[1] <= uPipe['y']+pipeH :
                    return True
            
            if point[0] >= lPipe['x'] and point[0] <= lPipe['x']+pipeW :
                if point[1] >= lPipe['y'] and point[1] <= lPipe['y']+pipeH :
                    return True
    return False
    
    
def pixelCollision(rect1, rect2, hitmask1, hitmask2):
    """Checks if two objects collide and not just their rects"""
    rect = rect1.clip(rect2)

    if rect.width == 0 or rect.height == 0:
        return False

    x1, y1 = rect.x - rect1.x, rect.y - rect1.y
    x2, y2 = rect.x - rect2.x, rect.y - rect2.y

    for x in xrange(rect.width):
        for y in xrange(rect.height):
            if hitmask1[x1+x][y1+y] and hitmask2[x2+x][y2+y]:
                return True
    return False

def getHitmask(image):
    """returns a hitmask using an image's alpha."""
    mask = []
    for x in xrange(image.get_width()):
        mask.append([])
        for y in xrange(image.get_height()):
            mask[x].append(bool(image.get_at((x,y))[3]))
    return mask

if __name__ == '__main__':
    game = Game()
    while True:
        game.init_elements()
        while True:
            game.frame_step(1)
            for ix in range(18):
                game.frame_step(0)
            view = pygame.surfarray.array3d(SCREEN)[:,:404,:]
            print(view.shape)
            time.sleep(1)