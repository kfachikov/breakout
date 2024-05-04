import pygame
from pygame.locals import *

import constants as const

pygame.init()

screen = pygame.display.set_mode((const.SCREEN_WIDTH, const.SCREEN_HEIGHT))
pygame.display.set_caption('Breakout')

font = pygame.font.SysFont('Constantia', 30)

clock = pygame.time.Clock()
live_ball = False
game_over = 0

# function for outputting text onto the screen
def draw_text(text, font, color_text, x, y):
    img = font.render(text, True, color_text)
    screen.blit(img, (x, y))

class Wall():
    """
    A class representing the game blocks.

    Attributes
    ----------
    width : int
        The width of each individual block.
    height : int
        The height of each individual block.
    blocks : list
        A two-dimensional list containing the blocks. Each block is represented by a list containing a rectangle and a strength value.
        The strength indicates the number of hits required to destroy that block.

    Methods
    -------
    create_wall()
        Creates the block instances and stores them in the blocks list.
    draw_wall()
        Draws the blocks on the screen. The block color is determined by each block's strength.
    
    """
    def __init__(self):
        self.width = const.SCREEN_WIDTH // const.COL_NUM # fill the entire screen horizontally
        self.height = 0.5 * const.SCREEN_HEIGHT // const.ROW_NUM # fill only half of the screen vertically

    def create_wall(self):
        self.blocks = []
        for row in range(const.ROW_NUM):
            block_row = []
            for col in range(const.COL_NUM):
                # generate x and y positions for each block and create a rectangle from that
                block_x = col * self.width
                block_y = row * self.height
                rect = pygame.Rect(block_x, block_y, self.width, self.height)

                # assign a strength value to each block based on its row
                if row < 2:
                    strength = 3
                elif row < 4:
                    strength = 2
                elif row < 6:
                    strength = 1

                block_individual = [rect, strength]

                block_row.append(block_individual)    
            self.blocks.append(block_row)

    def draw_wall(self):
        for row in self.blocks:
            for block in row:
                # assign a color based on block strength
                if block[1] == 3:
                    block_col = const.COLOR_BLOCK_BLUE
                elif block[1] == 2:
                    block_col = const.COLOR_BLOCK_GREEN
                elif block[1] == 1:
                    block_col = const.COLOR_BLOCK_RED
                pygame.draw.rect(screen, block_col, block[0])
                pygame.draw.rect(screen, const.COLOR_BACKGROUND, (block[0]), 2)


class Paddle():
    """
    A class representing the player's paddle.

    Attributes
    ----------
    width : int
        The width of the paddle.
    height : int
        The height of the paddle.
    speed : int
        The speed at which the paddle moves.
    x : int
        The x-coordinate of the paddle.
    y : int
        The y-coordinate of the paddle.
    direction : int
        The direction in which the paddle is moving (-1 for left, 1 for right, 0 for no movement)

    Methods
    -------
    move()
        Moves the paddle based on the player's input.
    draw()
        Draws the paddle on the screen.
    reset()
        Resets the paddle to its initial position. Centered at the bottom of the screen.
    """
    def __init__(self):
        self.width = int(const.SCREEN_WIDTH / const.COL_NUM * const.PADDLE_WIDTH_COEF) # the paddle is as wide as a block
        self.height = int(0.5 * const.SCREEN_HEIGHT / const.ROW_NUM * const.PADDLE_HEIGHT_COEF)
        
        self.speed = const.PADDLE_SPEED
        
        self.reset()

    def move(self):
        self.direction = 0
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
            self.direction = -1
        if key[pygame.K_RIGHT] and self.rect.right < const.SCREEN_WIDTH:
            self.rect.x += self.speed
            self.direction = 1

    def draw(self):
        pygame.draw.rect(screen, const.PADDLE_COLOR_FILL, self.rect)
        pygame.draw.rect(screen, const.PADDLE_COLOR_OUTLINE, self.rect, 3)

    def reset(self):
        self.x = int((const.SCREEN_WIDTH / 2) - (self.width / 2))
        self.y = const.SCREEN_HEIGHT - (self.height * 1.5)
        
        self.direction = 0
        
        self.rect = Rect(self.x, self.y, self.width, self.height)


class Ball():
    """
    A class representing the ball in the game.

    Attributes
    ----------
    ball_rad : int
        The radius of the ball.
    speed_max : int
        The maximum speed of the ball.
    x : int
        The x-coordinate of the ball.
    y : int
        The y-coordinate of the ball.
    speed_x : int
        The speed of the ball in the x-direction.
    speed_y : int
        The speed of the ball in the y-direction.
    game_over : int
        The game state (0 for ongoing, 1 for win, -1 for loss).
    rect : Rect
        A rectangle representing the ball.

    Methods
    -------
    move()
        Moves the ball and checks for collisions with the paddle, blocks, and walls.
    draw()
        Draws the ball on the screen.
    reset(x, y)
        Resets the ball to its initial position.
    """
    def __init__(self, x, y, speed_max = 10):
        self.ball_rad = int(0.5 * const.SCREEN_HEIGHT / const.ROW_NUM * const.BALL_SIZE_COEF)
        self.speed_max = speed_max

        self.reset(x, y)

    def move(self):

        # collision threshold
        collision_thresh_x = self.speed_max
        collision_thresh_y = abs(self.speed_y)

        wall_destroyed = 1
        
        for row_idx, row in enumerate(wall.blocks):
            for col_ixd, item in enumerate(row):
                # check whether the ball collides with a block
                if self.rect.colliderect(item[0]):
                    # object above
                    if abs(self.rect.bottom - item[0].top) < collision_thresh_y and self.speed_y > 0:
                        self.speed_y *= -1
                    # object below
                    elif abs(self.rect.top - item[0].bottom) < collision_thresh_y and self.speed_y < 0:
                        self.speed_y *= -1
                    # object on the right
                    elif abs(self.rect.right - item[0].left) < collision_thresh_x and self.speed_x > 0:
                        self.speed_x *= -1
                    # object on the left
                    elif abs(self.rect.left - item[0].right) < collision_thresh_x and self.speed_x < 0:
                        self.speed_x *= -1

                    if wall.blocks[row_idx][col_ixd][1] > 1:
                        wall.blocks[row_idx][col_ixd][1] -= 1
                    else:
                        wall.blocks[row_idx][col_ixd][0] = (0, 0, 0, 0)

                # if a block still exists, the wall is not destroyed
                if wall.blocks[row_idx][col_ixd][0] != (0, 0, 0, 0):
                    wall_destroyed = 0

        if wall_destroyed == 1:
            self.game_over = 1

        if self.rect.left < 0 or self.rect.right > const.SCREEN_WIDTH:
            self.speed_x *= -1

        if self.rect.top < 0:
            self.speed_y *= -1
        if self.rect.bottom > const.SCREEN_HEIGHT:
            self.game_over = -1

        if self.rect.colliderect(player_paddle):
            if abs(self.rect.bottom - player_paddle.rect.top) < collision_thresh_y and self.speed_y > 0:
                self.speed_y *= -1
                self.speed_x += player_paddle.direction # the paddle direction influences the ball's speed
                if self.speed_x > self.speed_max:
                    self.speed_x = self.speed_max
                elif self.speed_x < 0 and self.speed_x < -self.speed_max:
                    self.speed_x = -self.speed_max

        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        return self.game_over

    def draw(self):
        pygame.draw.circle(screen, const.PADDLE_COLOR_FILL, (self.rect.x + self.ball_rad, self.rect.y + self.ball_rad),
                           self.ball_rad)
        pygame.draw.circle(screen, const.PADDLE_COLOR_OUTLINE, (self.rect.x + self.ball_rad, self.rect.y + self.ball_rad),
                           self.ball_rad, 3)

    def reset(self, x, y):
        self.x = x - self.ball_rad
        self.y = y - 2 * self.ball_rad
        
        self.speed_x = int(self.speed_max * const.BALL_SPEED_INITIAL_COEF)
        self.speed_y = -(self.speed_max * const.BALL_SPEED_INITIAL_COEF)

        self.game_over = 0
        
        self.rect = Rect(self.x, self.y, self.ball_rad * 2, self.ball_rad * 2)

wall = Wall()
wall.create_wall()

player_paddle = Paddle()

ball = Ball(player_paddle.x + (player_paddle.width // 2), player_paddle.y) 

run = True
while run:

    clock.tick(const.FPS)

    screen.fill(const.COLOR_BACKGROUND)

    wall.draw_wall()
    player_paddle.draw()
    ball.draw()

    if live_ball:
        # draw paddle
        player_paddle.move()
        # draw ball
        game_over = ball.move()
        if game_over != 0:
            live_ball = False

    # print player instructions
    if not live_ball:
        if game_over == 0:
            draw_text('CLICK ANYWHERE TO START', font, const.COLOR_TEXT, 100, const.SCREEN_HEIGHT // 2 + 100)
        elif game_over == 1:
            draw_text('YOU WON!', font, const.COLOR_TEXT, 240, const.SCREEN_HEIGHT // 2 + 50)
            draw_text('CLICK ANYWHERE TO START', font, const.COLOR_TEXT, 100, const.SCREEN_HEIGHT // 2 + 100)
        elif game_over == -1:
            draw_text('YOU LOST!', font, const.COLOR_TEXT, 240, const.SCREEN_HEIGHT // 2 + 50)
            draw_text('CLICK ANYWHERE TO START', font, const.COLOR_TEXT, 100, const.SCREEN_HEIGHT // 2 + 100)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and live_ball == False:
            live_ball = True
            ball.reset(player_paddle.x + (player_paddle.width // 2), player_paddle.y - player_paddle.height)
            player_paddle.reset()
            wall.create_wall()

    pygame.display.update()

pygame.quit()