import pygame
import sys
import numpy as np
from queue import LifoQueue as Queue

BLACK = (0, 0, 0)
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,200,255)
PINK = (255,192,203)
PURPLE = (255,0,255)
ORANGE = (255,165,0)
GRAY = (100,100,100)
context = [("Clue 1: https://1105042987.github.io/Gift/",GREEN),
           ("Clue 2: Top",BLUE),
           ("Clue 3: Crack and Light",RED)]
class Button:
    def __init__(self, msg, x, y, w, h, c, screen, text_size=20, text_color=(0,0,0)):
        self.button = pygame.Rect(x,y,w,h)
        self.color = c
        self.screen = screen
        Text = pygame.font.SysFont('comicsansms', text_size)
        self.textSurf = Text.render(msg, True, text_color)
        self.textRect = self.textSurf.get_rect()
        self.textRect.center = ( (x+(w/2)), (y+(h/2)))

    def isClick(self, pos):
        return self.button.collidepoint(pos)
    
    def draw(self):
        pygame.draw.rect(self.screen, self.color, self.button)
        self.screen.blit(self.textSurf, self.textRect)

class Text:
    def __init__(self,center_x, center_y, w, h, screen, back_color = WHITE, text_size=20, 
                        text_color=(0,0,0), line_width=0, line_color = None, msg = ['']):
        self.default_msg = msg if type(msg) == list else [msg]
        self.screen = screen
        self.Text = pygame.font.SysFont('comicsansms', text_size)
        self.text_color = text_color
        self.backGround_color = back_color
        self.last = []

        self.text_height = h
        self.text_width = w
        self.center = (center_x,center_y)
        self.line_width = line_width
        self.line_color = text_color if line_color is None else line_color
            
    def get_rects(self,msg):
        num = len(msg)
        x,y = (self.center[0]-self.text_width//2), (self.center[1]-(num*self.text_height)//2)
        self.rect_in = pygame.Rect(x,y,self.text_width,self.text_height*num)
        self.rect_out =  pygame.Rect(x-self.line_width,y-self.line_width,self.text_width+
                            self.line_width*2,self.text_height*num+self.line_width*2)
        self.text_container = []
        for i in range(num):
            if type(msg[i]) is tuple:
                textSurf = self.Text.render(msg[i][0], True, msg[i][1])
            else:
                textSurf = self.Text.render(msg[i], True, self.text_color)
            textRect = textSurf.get_rect()
            textRect.center = ((x+(self.text_width//2)), (y+(self.text_height//2))+i*self.text_height)
            self.text_container.append((textSurf,textRect))
    
    def draw(self, msg=None):
        if self.last != msg:
            self.last = msg
            if msg is None:
                msg = self.default_msg
            elif type(msg) is not list:
                msg = [msg]
            self.get_rects(msg)
        pygame.draw.rect(self.screen, self.line_color, self.rect_out)
        pygame.draw.rect(self.screen, self.backGround_color, self.rect_in)
        for textSurf, textRect in self.text_container:
            self.screen.blit(textSurf, textRect)
    
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Happy Birthday ~')
        self.width, self.height, self.grid = 960, 720, 48
        mid_w = self.width//2
        text_h = self.height//2 - 80
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.width,self.height))
        # 游戏说明
        insText = [
            ("Tips ( I hide a clue in every difficulty of this game ): ",BLACK),
            "Use direction key to move 'you' :)",
            "Use space key to become shiny ~",
            "Use -/= key to change the scopy you shine ~",
        ]
        self.title = Text(mid_w,text_h//2,200,100,self.screen,text_size=50,msg='A Gift For YZX')
        self.ins   = Text(mid_w,text_h,   600, 40,self.screen,text_color=ORANGE,msg=insText,line_width=10,line_color=GRAY)
        self.end_text = Text(mid_w,500,   600, 50,self.screen,line_width=5)
        self.end_cont = None
        self.gift_text  = Text(mid_w,580,600,50,self.screen,text_color=PINK,line_width=5,
                                    msg="You know, I'll come to find you wherever you shine.")
        self.gift_text_ = Text(mid_w,630,610,50,self.screen,back_color=PINK,text_color=WHITE,
                                    msg='Happy Birthday !           My Dear ~')
        # 载入按钮
        self.but1 = Button('Easy',   mid_w-250, 400, 100, 50, GREEN, self.screen)
        self.but2 = Button('Normal', mid_w-50,  400, 100, 50, BLUE,  self.screen)
        self.but3 = Button('Hard',   mid_w+150, 400, 100, 50, RED,   self.screen)
        # MAP
        self.mapH,self.mapW = self.height//self.grid, self.width//self.grid
        # 载入翅膀
        self.fly = pygame.image.load('pic/fly.png')
        self.fly = pygame.transform.scale(self.fly,(40,28))
        self.fly_pos = self.fly.get_rect()
        # 载入Star
        self.star_s = pygame.image.load('pic/star_s.png')
        self.star_s = pygame.transform.scale(self.star_s,(15,15))
        self.star_s_pos = self.star_s.get_rect()
        self.star = pygame.image.load('pic/star.png')
        self.star = pygame.transform.scale(self.star,(30,30))
        self.star_pos = self.star.get_rect()
        # Canvas 
        self.energy_max = 20
        self.draw_gift = False
        self.energy_bar = Button('20',10,30,80,12,(0,255,0),self.screen,8)
        self.cost = 1
        self.Easter_Egg = 0
        self.cost_text = Text(50,15,80,20,self.screen,text_size=18,text_color=WHITE,back_color=BLACK)
        self.reset()

    def reset(self):
        self.light_list = {}
        self.step = 'MENU'
        self.vaild = False
        self.energy = 20
        self.cost = 1
        self.Easter_Egg = 0
        self.star_pos.center = (self.grid//2,self.height-3*self.grid//2)
        self.star_s_pos.center = (self.grid//2,self.height-3*self.grid//2)
        self.fly_pos.center = (self.width-self.grid,3*self.grid//2)

    def pointCheck(self,h,w,next_list):
        if w>=0 and w<self.mapW and h>=0 and h<self.mapH and \
                    not self.map[h,w] and not (h,w) in next_list:
            return True
        return False

    def genLightList(self):
        center = np.array(self.star_pos.center)-self.grid//2
        for i in range(self.mapW):
            for j in range(self.mapH):
                now = np.array([i*self.grid,j*self.grid])
                dis = np.sqrt(((center-now)**2).sum())
                if dis < (self.cost-self.difficulty/2)*self.grid*1.2 and not self.map[j,i]:
                    # ((position),show_time)
                    self.light_list[tuple(now)]= 100*self.cost+100
                    

    def generateMap(self,th):
        self.map = np.random.rand(self.mapH,self.mapW) < th
        self.map[1,self.mapW-1] = False
        self.map[self.mapH-2, 0] = False
        self.map[0,0:2] = True
        path = Queue()
        history = []
        path.put((self.mapH-2,0))
        end = (1,self.mapW-1)
        # DFS
        while not path.empty():
            last = path.get()
            history.append(last)
            nextList = [(last[0],last[1]-1),(last[0],last[1]+1),
                        (last[0]-1,last[1]),(last[0]+1,last[1])]
            for Next in nextList:
                if Next == end:
                    self.vaild = True
                    self.step='GAME'
                    return
                if self.pointCheck(*Next,history):
                    path.put(Next)

    def collision(self,rec):
        if rec.left < 0 or rec.right >= self.width or rec.top < 0 or rec.bottom >= self.height:
            self.end_cont = ("WoW, The fragile little star kissed the hard wall mistakenly.",PURPLE)
            self.end_text.line_color = PURPLE
            self.reset()
            return
        pos = np.array([rec.left,rec.right,rec.top,rec.bottom])//self.grid
        point = ([2,0],[3,0],[2,1],[3,1])
        end = False
        for p in point:
            if tuple(pos[p]) == (1,self.mapW-1):
                end = True
            if self.map[pos[p][0],pos[p][1]]:
                self.end_cont = ("Seemed to encounter with an invisible danger.",PURPLE)
                self.end_text.line_color = PURPLE
                self.reset()
                return
        if end:
            self.end_cont = context[self.difficulty]
            self.end_text.line_color = context[self.difficulty][1]
            self.reset()

    def run(self):
        while True:
            self.clock.tick(60)
            if self.energy <= self.energy_max:
                self.energy += 0.2/60
            for event in pygame.event.get():    # 遍历所有事件
                if event.type == pygame.QUIT:
                    sys.exit()
                if self.step == 'MENU':
                    move_x, move_y = 0,0
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.but1.isClick(pygame.mouse.get_pos()):
                            while not self.vaild: self.generateMap(0.2)
                            self.draw_gift = False
                            self.difficulty = 0
                        if self.but2.isClick(pygame.mouse.get_pos()):
                            while not self.vaild: self.generateMap(0.35)
                            self.draw_gift = False
                            self.difficulty = 1
                        if self.but3.isClick(pygame.mouse.get_pos()):
                            while not self.vaild: self.generateMap(0.5)
                            self.draw_gift = False
                            self.difficulty = 2
                else:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT:
                            move_x = -1
                        elif event.key == pygame.K_RIGHT:
                            move_x = 1
                        elif event.key == pygame.K_UP:
                            move_y = -1
                        elif event.key == pygame.K_DOWN:
                            move_y = 1
                        elif event.key == pygame.K_EQUALS:
                            self.Easter_Egg+=1
                            self.cost+=1
                            if self.cost>5:
                                self.cost = 5
                            if self.Easter_Egg >= 20:
                                self.cost = 20
                        elif event.key == pygame.K_MINUS:
                            self.Easter_Egg = 0
                            self.cost-=1
                            if self.cost > 5:
                                self.cost = 5
                            if self.cost <= 0:
                                self.cost = 1
                            
                        elif event.key == pygame.K_SPACE:
                            if self.energy >= self.cost:
                                self.energy-=self.cost
                                self.genLightList()
                                if self.cost == 20:
                                    self.draw_gift = True
                                    self.step = 'Vedio'

                    elif event.type == pygame.KEYUP:
                        if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                            move_x = 0
                        elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                            move_y = 0
            if self.step == 'GAME':
                self.energy_bar = Button('{}'.format(int(self.energy)),10,30,80*self.energy//self.energy_max,15,
                        (255-255*self.energy//self.energy_max,255*self.energy//self.energy_max,0),self.screen,12)
                self.star_pos = self.star_pos.move((move_x,move_y))
                self.collision(self.star_pos)
                move = [x2-x1 for x1,x2 in zip(self.star_s_pos.center,self.star_pos.center)]
                if np.sqrt(move[0]**2+move[1]**2) > 30:
                    move[0],move[1] = move[0]//10,move[1]//10
                    self.star_s_pos = self.star_s_pos.move(move)
            elif self.step == 'Vedio':
                self.energy_bar = Button('{}'.format(int(self.energy)),10,30,80*self.energy//self.energy_max,15,
                        (255-255*self.energy//self.energy_max,255*self.energy//self.energy_max,0),self.screen,12)
                move = [x2-x1 for x1,x2 in zip(self.fly_pos.center,self.star_pos.center)]
                if np.sqrt(move[0]**2+move[1]**2) < 10:
                    self.end_cont = context[self.difficulty]
                    self.end_text.line_color = context[self.difficulty][1]
                    self.reset()
                move[0] = max(move[0]//100,2) if move[0]>0 else min(move[0]//100,-2)
                move[1] = max(move[1]//100,2) if move[1]>0 else min(move[1]//100,-2)
                self.fly_pos = self.fly_pos.move(move)
            self.draw()
        pygame.quit()

    def draw(self):
        if self.step=='MENU':
            self.screen.fill(WHITE)
            self.title.draw()
            self.ins.draw()
            self.but1.draw()
            self.but2.draw()
            self.but3.draw()
            if self.end_cont is not None:
                self.end_text.draw(self.end_cont)
                if self.draw_gift:
                    self.gift_text.draw()
                    self.gift_text_.draw()
        else:
            self.screen.fill(BLACK)
            self.energy_bar.draw()
            for key,val in self.light_list.items():
                if val>0:
                    self.light_list[key]-=(self.difficulty+2)
                    show = min(max((val-1)//3,0),255)
                    pygame.draw.rect(self.screen, (show,show,0), pygame.Rect(key[0],key[1],self.grid,self.grid))
                else:
                    pass
            pos = pygame.Rect(self.star_pos.center[0]//self.grid*self.grid,self.star_pos.center[1]//self.grid*self.grid,self.grid,self.grid)
            if self.cost>self.difficulty/2:
                pygame.draw.circle(self.screen,(100,100,0),self.star_pos.center,int(self.grid*(self.cost-self.difficulty/2)*1.2),3)
            self.cost_text.draw('Cost: {}'.format(self.cost))
            self.screen.blit(self.star_s, self.star_s_pos)
            self.screen.blit(self.star, self.star_pos)
            self.screen.blit(self.fly, self.fly_pos)
        pygame.display.flip()


move_x, move_y = 0, 0
game = Game()
game.run()

# compile cmd:   pyinstaller -F gift.py
# then copy "pic" folder to "dist/pic"