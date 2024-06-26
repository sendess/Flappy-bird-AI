import pygame
import os
import time
import random
import neat
from neat.config import Config
pygame.font.init()

WIN_WIDTH = 500
WIN_HEIGHT = 900
JUMPER_IMG = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","jumper1.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","jumper2.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","jumper3.png")))]
OBSTACLE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","obstacle.png")))
BGND_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","background.png")))
GND_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","ground.png")))
STAT_FONT = pygame.font.SysFont("jokerman",50)

class jumper:
    IMGS = JUMPER_IMG
    MAX_ROTATION = 25
    ROT_VELOCITY = 20
    ANIMATION_TIME = 5

    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.velocity = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]
        
    def jump(self):
        self.velocity = -10.5
        self.tick_count = 0
        self.height = self.y
    
    def move(self):
        self.tick_count += 1
        d = self.velocity * self.tick_count +1.5*self.tick_count**2
        if d >= 16:
            d = 16
        if d < 0:
            d -= 2
        self.y = self.y + d
        
        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VELOCITY
    
    def draw(self,win):
        self.img_count += 1
        
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]    
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]        
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]       
        elif self.img_count < self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]    
            self.img_count = 0
            
        if self.tilt <= -80:
            self.img = self.IMGS[0]
            self.img_count = self.ANIMATION_TIME*2
            
        rotated_image = pygame.transform.rotate(self.img,self.tilt)
        new_rect = rotated_image.get_rect(center = self.img.get_rect(topleft = (self.x,self.y)).center)
        win.blit(rotated_image,new_rect.topleft)
    
    def get_mask(self):
        return pygame.mask.from_surface(self.img)
    
class obstacle:
        GAP = 200
        VEL = 5
        
        def __init__(self,x):
            self.x = x
            self.height = 0
            self.gap = 0
            
            self.top = 0
            self.bottom = 0
            self.OBSTACLE_TOP = pygame.transform.flip(OBSTACLE_IMG, False,True)
            self.OBSTACLE_BOTTOM = OBSTACLE_IMG
            
            self.passed = False
            self.set_height()
            
        def set_height(self):
            self.height = random.randint(50,450)
            self.top = self.height- self.OBSTACLE_TOP.get_height()
            self.bottom = self.height + self.GAP
            
        def move(self):
            self.x -= self.VEL
    
        def draw(self,win):
            win.blit(self.OBSTACLE_TOP,(self.x,self.top))
            win.blit(self.OBSTACLE_BOTTOM,(self.x,self.bottom))
            
        def collide(self,jumper):
            jumper_mask = jumper.get_mask()
            top_mask = pygame.mask.from_surface(self.OBSTACLE_TOP)
            bottom_mask = pygame.mask.from_surface(self.OBSTACLE_BOTTOM)
            
            top_offset = (self.x-jumper.x,self.top-round(jumper.y))
            bottom_offset = (self.x - jumper.x,self.bottom-round(jumper.y))
            
            b_point = jumper_mask.overlap(bottom_mask,bottom_offset)
            t_point = jumper_mask.overlap(top_mask,top_offset)
            
            if t_point or b_point:
                return True
            
            return False
    
class ground:
    VEL = 5
    WIDTH = GND_IMG.get_width()
    IMG = GND_IMG
    
    def __init__(self,y):
        self.y=y
        self.x1= 0
        self.x2 = self.WIDTH
    def move(self):
        self.x1-= self.VEL
        self.x2-= self.VEL
        
        if self.x1 + self.WIDTH<0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH<0:
            self.x2 = self.x1 + self.WIDTH
            
    def draw(self,win):
        win.blit(self.IMG, (self.x1,self.y)) 
        win.blit(self.IMG, (self.x2,self.y))

def draw_window(win,jumper,obstacle,ground,score):
    win.blit(BGND_IMG,(0,0))
    
    for obs in obstacle:
        obs.draw(win)
    text = STAT_FONT.render("Score : " + str(score), 1, (255,255,255))
    win.blit(text,(WIN_WIDTH-10-text.get_width(),10))
    ground.draw(win)
    for jumping_jack in jumper:
        
        jumping_jack.draw(win)
    pygame.display.update()
    
def main(genomes,config):
    nets = []
    ge = []
    jumping_jacks = []
    
    for _ , g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g,config)
        nets.append(net)
        jumping_jacks.append(jumper(230,350))
        g.fitness = 0
        ge.append(g)
    
    score = 0
    
    grounds = ground(730)
    obstacles = [obstacle(600)]
    run = True
    win = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))
    clock = pygame.time.Clock()
    while run:
        clock.tick(40)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        
        draw_window(win,jumping_jacks,obstacles,grounds,score)
        
        obs_ind = 0

        if len(jumping_jacks) > 0:
            if len(obstacles) >1 and jumping_jacks[0].x > obstacles[0].x + obstacles[0].OBSTACLE_TOP.get_width():
                obs_ind = 1
        else:
            run = False
            break      
          
        for x , jumping_jack in enumerate(jumping_jacks):
            jumping_jack.move()
            ge[x].fitness += 0.1
            
            output = nets[x].activate((jumping_jack.y,abs(jumping_jack.y - obstacles[obs_ind].height), abs(jumping_jack.y - obstacles[obs_ind].bottom)))

            if output[0] > 0.5:
                jumping_jack.jump()

        add_obs = False
        rem = []
        for obs in obstacles:
            for x,jumping_jack in enumerate(jumping_jacks):
                
                if obs.collide(jumping_jack):
                    ge[x].fitness -= 1
                    jumping_jacks.pop(x)
                    nets.pop(x)
                    ge.pop(x)
                
                if not obs.passed and obs.x < jumping_jack.x:
                    obs.passed = True
                    add_obs = True
                    
            if obs.x+obs.OBSTACLE_TOP.get_width() < 0:
                rem.append(obs)
            
                
            obs.move()
        if add_obs:
            score += 1
            
            for g in ge:
                g.fitness += 5

            obstacles.append(obstacle(600))
            
        for r in rem:
            obstacles.remove(r)   
            
        for x,jumping_jack in enumerate(jumping_jacks):
            if jumping_jack.y + jumping_jack.img.get_height() > 730 or jumping_jack.y <0:
                # print ("HIT_GROUND")
                jumping_jacks.pop(x)
                nets.pop(x)
                ge.pop(x)
        
        grounds.move()
        jumping_jack.move()



def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    winner = p.run(main,50)
    
if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir,"config.txt")
    run(config_path)