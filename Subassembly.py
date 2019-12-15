import pygame
import numpy as np

BLACK = (0, 0, 0)
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,200,255)
PINK = (255,192,203)
PURPLE = (255,0,255)
ORANGE = (255,165,0)
GRAY = (100,100,100)

class Button:
    def __init__(self, msg, x, y, w, h, c, screen, text_size=20, text_color=BLACK):
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
                        text_color=BLACK, line_width=0, line_color = None, msg = ['']):
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
            
    def __get_rects(self,msg):
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
            self.__get_rects(msg)
        pygame.draw.rect(self.screen, self.line_color, self.rect_out)
        pygame.draw.rect(self.screen, self.backGround_color, self.rect_in)
        for textSurf, textRect in self.text_container:
            self.screen.blit(textSurf, textRect)

class Slider:
    def __init__(self,x,y,length,height,max_num,msg_template,screen,msg_func=int,full_color=GREEN,
                                            empty_color=None,text_size=20,text_color=BLACK):
        self.x,self.y,self.h,self.l,self.screen = x,y,height,length,screen
        self.temp,self.func,self.text_size,self.text_color =  msg_template,msg_func,text_size,text_color
        self.full = np.array(full_color)
        self.max = max_num
        self.Text = pygame.font.SysFont('comicsansms', text_size)
        self.empty = self.full if empty_color is None else np.array(empty_color)

    def draw(self,val):
        ratio = min(max(val/self.max,0),1)
        tmp_color = tuple(((1-ratio)*self.empty+ratio*self.full).astype(int))
        pygame.draw.rect(self.screen, tmp_color, pygame.Rect(self.x,self.y,int(ratio*self.l),self.h))

        textSurf = self.Text.render(self.temp.format(self.func(val)), True, self.text_color)
        textRect = textSurf.get_rect()
        textRect.center = (self.x+int(ratio*self.l/2), self.y+self.h//2)
        self.screen.blit(textSurf, textRect)
