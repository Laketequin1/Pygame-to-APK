# -------- Setup
import pygame, pyautogui, sys, random
pygame.init()

# ------- Constant variables
MIDDLE_WIDTH = 80

GAME_WIDTH, GAME_HEIGHT = 1280, 720
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()
SCREEN_WIDTH, SCREEN_HEIGHT = (960, 540)
FPS = 120

WIDTH_MULTI = SCREEN_WIDTH/GAME_WIDTH
HEIGHT_MULTI = SCREEN_HEIGHT/GAME_HEIGHT

# Colors
class Color:
    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)
    white = (255, 255, 255)
    black = (0, 0, 0)
    grey = (150, 150, 150)

# -------- Variables
display = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
clock = pygame.time.Clock()

background_color = Color.white

# -------- Functions
def relative_image(image):
    return pygame.transform.smoothscale(image, (image.get_width() * WIDTH_MULTI, image.get_height() * HEIGHT_MULTI))

def relative_rect(rect):
    rect[0] *= WIDTH_MULTI
    rect[1] *= HEIGHT_MULTI
    rect[2] *= WIDTH_MULTI
    rect[3] *= HEIGHT_MULTI
    return rect

def invert_rect(rect):
    rect[0] /= WIDTH_MULTI
    rect[1] /= HEIGHT_MULTI
    rect[2] /= WIDTH_MULTI
    rect[3] /= HEIGHT_MULTI
    return rect

def invert_pos(pos):
    pos = list(pos)
    pos[0] /= WIDTH_MULTI
    pos[1] /= HEIGHT_MULTI
    return pos

def reflect_balls(ball, mallet):
    mallet_direction = mallet.get_direction()
    x, y = ball.pos[0] + ball.size[0] / 2, ball.pos[1] + ball.size[1] / 2
    v1 = pygame.math.Vector2((x, y))
    x, y = mallet.pos[0] + mallet.size[0] / 2, mallet.pos[1] + mallet.size[1] / 2
    v2 = pygame.math.Vector2((x, y))
    r1 = ball.size[0] // 2
    r2 = mallet.size[0] // 2
    d = v1.distance_to(v2)
    if d < r1 + r2 - 2:
        dnext = (v1 + ball.direction).distance_to(v2 + mallet_direction)
        nv = v2 - v1
        if dnext < d and nv.length() > 0:
            ball.reflect(nv)

            #if mallet_direction[0]:
            ball.direction[0] += abs(mallet_direction[0]) * 3 #########
            #if mallet_direction[1]:
            ball.direction[1] += abs(mallet_direction[1]) * 3##########

# --------- Class's
class Item:
    def __init__(self, rect, color=None):
        self.rect = relative_rect(rect)
        self.color = color
    
    def display(self, screen):
        if self.color:
            pygame.draw.rect(screen, self.color, self.rect)


class Mallet:
    def __init__(self, start_pos, image_path, play_area, size = (50, 50)):
        self.pos = list(start_pos)
        self.image = relative_image(pygame.transform.smoothscale(pygame.image.load(image_path), size))
        self.play_area = play_area
        self.size = size

        self.direction = pygame.math.Vector2((1, 1)).normalize()
        self.previous_pos = self.pos
    
    def get_direction(self):
        x = self.pos[0] - self.previous_pos[0]
        y = self.pos[1] - self.previous_pos[1]

        return (x, y)

    def set_pos(self, pos):
        self.pos[0] = pos[0] - (self.size[0] / 2)
        self.pos[1] = pos[1] - (self.size[1] / 2)

    def update(self, mouse_pos):
        self.previous_pos = self.pos
        if relative_rect(pygame.Rect(self.play_area)).collidepoint(mouse_pos):
            self.set_pos(invert_pos(mouse_pos))

    def display(self, screen):
        screen.blit(self.image, (self.pos[0] * WIDTH_MULTI, self.pos[1] * HEIGHT_MULTI))


class Ball:
    def __init__(self, start_pos, image_path, start_direction = (100, 100), start_velocity = 0, size = (50, 50)):
        self.pos = pygame.math.Vector2(start_pos)
        self.image = relative_image(pygame.transform.smoothscale(pygame.image.load(image_path), size))
        self.direction = pygame.math.Vector2(start_direction).normalize()
        self.velocity = start_velocity
        self.size = size

    def reflect(self, NV):
        self.direction = self.direction.reflect(pygame.math.Vector2(NV))

    def set_pos(self, pos):
        self.pos[0] = pos[0] - (self.size[0] / 2)
        self.pos[1] = pos[1] - (self.size[1] / 2)

    def update(self):
        self.pos += self.direction * self.velocity

        if self.pos[0] <= 0:
            self.reflect((1, 0))
            self.pos[0] = 0
        if self.pos[0] + self.size[0] >= GAME_WIDTH:
            self.reflect((-1, 0))
            self.pos[0] = GAME_WIDTH - self.size[0]
        if self.pos[1] <= 0:
            self.reflect((0, 1))
            self.pos[1] = 0
        if self.pos[1] + self.size[1] >= GAME_HEIGHT:
            self.reflect((0, -1))
            self.pos[1] = GAME_HEIGHT - self.size[1]

    def display(self, screen):
        screen.blit(self.image, (self.pos[0] * WIDTH_MULTI, self.pos[1] * HEIGHT_MULTI))


goals = [Item([0, 150, 50, GAME_HEIGHT - 300], Color.green), Item([GAME_WIDTH - 50, 150, 50, GAME_HEIGHT - 300], Color.blue)]
half = Item([GAME_WIDTH / 2 - MIDDLE_WIDTH / 2, 0, MIDDLE_WIDTH, GAME_HEIGHT], Color.grey)
mallets = [Mallet((50, 50), "Ball64.png", (0, 0, GAME_WIDTH / 2 - MIDDLE_WIDTH / 2, GAME_HEIGHT)), Mallet((200, 200), "Ball64.png", (GAME_WIDTH / 2 + MIDDLE_WIDTH / 2, 0, (GAME_WIDTH / 2) - MIDDLE_WIDTH / 2, GAME_HEIGHT))]
ball = Ball((50, 50), "Ball64.png", start_velocity = 3)

# --------- Main
def main():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        
        # Update
        mouse_pos = pygame.mouse.get_pos()

        ball.update()

        for mallet in mallets:
            mallet.update(mouse_pos)
            reflect_balls(ball, mallet)

        # Render
        display.fill(background_color)

        half.display(display)

        for goal in goals:
            goal.display(display)

        for mallet in mallets:
            mallet.display(display)
        
        ball.display(display)

        pygame.display.flip()
        clock.tick(FPS)

# -------- Start
if __name__ == "__main__":
    main()