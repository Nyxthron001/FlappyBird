import pygame
import neat
import time 
import os
import random

WIN_WIDTH = 500
WIN_HEIGHT = 750

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird1.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird2.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird3.png")))]
PIPE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")))
BASE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")))
BG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bg.png")))

class Bird:
    IMGS = BIRD_IMGS
    MAX_ROT = 25
    ROT_VEL = 20
    ANIM_TIME = 5

    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.tilt = 0 
        self.vel = 0
        self.tick = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -10.5
        self.tick = 0 
        self.height = self.y

    def move(self):
        self.tick +=1

        d = self.vel*self.tick + 1.5*self.tick**2

        if d>=16:
            d=16

        if d<0:
            d-=2

        self.y = self.y +d

        if d<0 or self.y <self.height + 50:
            if self.tilt < self.MAX_ROT:
                self.tilt = self.MAX_ROT
        else:
            if self.tilt>-90:
                self.tilt -= self.ROT_VEL
    def draw(self,win):
        self.img_count += 1

        if self.img_count < self.ANIM_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIM_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIM_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIM_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIM_TIME*4 +1:
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIM_TIME*2

        rotated_img  = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_img.get_rect(center=self.img.get_rect(topleft = (self.x,self.y)).center) 
        win.blit(rotated_img, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

class Pipe:
    GAP=200
    VEL=5

    def __init__(self,x):
        self.x = x
        self.height = 0
        self.gap = 100

        self.top = 0
        self.bottom=0
        self.PIPE_TOP = pygame.transform.flip(PIPE,False,True)
        self.PIPE_BOTTOM = PIPE

        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50,450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height+self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x,self.top))
        win.blit(self.PIPE_BOTTOM, (self.x,self.bottom))

    def collide(self,bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x-bird.x,self.top-round(bird.y))
        bottom_offset = (self.x-bird.x,self.bottom-round(bird.y))

        b_point = bird_mask.overlap(bottom_mask,bottom_offset) 
        t_point = bird_mask.overlap(top_mask,top_offset)

        if t_point or b_point:
            return True
        return False

class Base:
    VEL = 5
    WIDTH = BASE.get_width()
    IMG  = BASE

    def __init__(self,y):
        self.y = y 
        self.x1 = 0 
        self.x2= self.WIDTH

    def move(self):
        self.x1-=self.VEL
        self.x2-=self.VEL

        if self.x1 + self.WIDTH <0:
            self.x1=self.x2+self.WIDTH

        if self.x2+self.WIDTH<0:
            self.x2 = self.x1+self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def draw_window(win, bird,pipes,base):
    win.blit(BG,(0,0))
    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)

    bird.draw(win)

    pygame.display.update()



def main():
    pygame.init()
    bird = Bird(230,350)
    base = Base(700)
    pipes = [Pipe(550)]
    run = True
    game_over=False
    win = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))
    clock = pygame.time.Clock()
    score =0
    while run:
        clock.tick(30)
        if not game_over:
            bird.move()

            if bird.y + bird.img.get_height()>=700 or bird.y<0:
                game_over = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over:
                    bird.jump()
                if event.key == pygame.K_r and game_over:
                    main()
                    return
        #bird.move()
        rem=[]
        add_pipe  =False
        if not game_over:
            for pipe in pipes:
                if pipe.collide(bird):
                    game_over = True
                    pass
                if pipe.x + pipe.PIPE_TOP.get_width()<0:
                    rem.append(pipe)
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

                pipe.move()

        if add_pipe:
            score +=1
            pipes.append(Pipe(550))

        for r in rem:
            pipes.remove(r)
        if not game_over:
            base.move()

        draw_window(win,bird,pipes,base)
        font = pygame.font.SysFont("comicsans", 40)

        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        win.blit(score_text, (WIN_WIDTH - score_text.get_width() - 10, 10))

        if game_over:
            over_text = font.render("GAME OVER", True, (255, 0, 0))
            win.blit(
            over_text,
            (
            WIN_WIDTH // 2 - over_text.get_width() // 2,
            WIN_HEIGHT // 2
                )
            )

        pygame.display.update()

    pygame.quit()
    quit()

main()

