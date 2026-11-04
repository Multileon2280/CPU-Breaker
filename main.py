from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.core.window import Window
import random

# ==========================================
# НАШ САМОДЕЛЬНЫЙ ПРОЦЕССОР (32-бит)
# ==========================================
memory = [0] * 1000
reg_A = 0
reg_B = 0
pc = 0
running = True

def run_cpu(program):
    global pc, reg_A, reg_B, running
    pc = 0
    reg_A = 0
    reg_B = 0
    running = True
    steps = 0
    
    for i in range(len(program)):
        memory[i] = program[i]
        
    while running and steps < 1000:
        steps += 1
        instruction = memory[pc]
        
        if instruction == 1: 
            pc += 1; reg_A = memory[pc]
        elif instruction == 2: 
            pc += 1; reg_B = memory[pc]
        elif instruction == 3: 
            reg_A += reg_B
        elif instruction == 5: 
            reg_A -= reg_B
        elif instruction == 6:
            pc += 1
            if reg_A > reg_B: pc = memory[pc]; continue
        elif instruction == 7:
            pc += 1
            pc = memory[pc]; continue
        elif instruction == 10:
            pc += 1
            if reg_A == reg_B: pc = memory[pc]; continue
        elif instruction == 0: 
            running = False
        pc += 1
        
    return reg_A

# ==========================================
# ИГРА CPU-BREAKER
# ==========================================
class CPUBreakerGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.ball_x = Window.width / 2
        self.ball_y = Window.height / 2
        self.ball_dx = 4
        self.ball_dy = 4
        
        self.paddle_x = Window.width / 2 - 50
        self.paddle_y = 20
        self.paddle_width = 100
        self.paddle_height = 15
        
        self.bricks = []
        self.create_bricks()
        
        with self.canvas:
            Color(1, 1, 1)
            self.ball = Ellipse(pos=(self.ball_x, self.ball_y), size=(15, 15))
            self.paddle = Rectangle(pos=(self.paddle_x, self.paddle_y), size=(self.paddle_width, self.paddle_height))
            
            self.brick_rects = []
            for b in self.bricks:
                Color(b['r'], b['g'], b['b'])
                rect = Rectangle(pos=(b['x'], b['y']), size=(b['w'], b['h']))
                self.brick_rects.append(rect)
                
        Clock.schedule_interval(self.update, 1.0 / 30.0)

    def create_bricks(self):
        rows = 4
        cols = 6
        brick_w = (Window.width - 40) / cols
        brick_h = 20
        start_x = 20
        start_y = Window.height - 150
        
        colors = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0)]
        
        for row in range(rows):
            for col in range(cols):
                self.bricks.append({
                    'x': start_x + col * brick_w,
                    'y': start_y + row * (brick_h + 5),
                    'w': brick_w - 5,
                    'h': brick_h,
                    'alive': True,
                    'r': colors[row % len(colors)][0],
                    'g': colors[row % len(colors)][1],
                    'b': colors[row % len(colors)][2]
                })

    def update(self, dt):
        program_x = [1, int(self.ball_x), 2, int(self.ball_dx), 3, 0]
        self.ball_x = run_cpu(program_x)
        
        self.ball_y += self.ball_dy
        
        if self.ball_x > Window.width - 15 or self.ball_x < 0:
            self.ball_dx *= -1
        if self.ball_y > Window.height - 15:
            self.ball_dy *= -1
            
        if (self.ball_y < self.paddle_y + self.paddle_height and 
            self.ball_y > self.paddle_y and
            self.ball_x > self.paddle_x - 10 and 
            self.ball_x < self.paddle_x + self.paddle_width):
            self.ball_dy *= -1
            if self.ball_x < self.paddle_x + self.paddle_width / 2:
                self.ball_dx = -abs(self.ball_dx)
            else:
                self.ball_dx = abs(self.ball_dx)
                
        if self.ball_y < 0:
            self.reset_ball()
            
        self.check_brick_collisions()
        
        self.ball.pos = (self.ball_x, self.ball_y)
        self.paddle.pos = (self.paddle_x, self.paddle_y)
        
        for i, b in enumerate(self.bricks):
            if not b['alive']:
                self.brick_rects[i].pos = (-100, -100)

    def check_brick_collisions(self):
        for i, b in enumerate(self.bricks):
            if not b['alive']: continue
            if (self.ball_x + 15 > b['x'] and self.ball_x < b['x'] + b['w'] and
                self.ball_y + 15 > b['y'] and self.ball_y < b['y'] + b['h']):
                b['alive'] = False
                self.ball_dy *= -1
                if self.ball_dy > 0: self.ball_y = b['y'] + b['h'] + 1
                else: self.ball_y = b['y'] - 16
                break

    def reset_ball(self):
        self.ball_x = Window.width / 2
        self.ball_y = Window.height / 2
        self.ball_dx = random.choice([-4, 4])
        self.ball_dy = 4

    def move_paddle(self, x):
        self.paddle_x = x - self.paddle_width / 2
        if self.paddle_x < 0: self.paddle_x = 0
        if self.paddle_x > Window.width - self.paddle_width:
            self.paddle_x = Window.width - self.paddle_width

class CPUBreakerApp(App):
    def build(self):
        game = CPUBreakerGame()
        Window.bind(on_touch_move=self.on_touch_move)
        return game

    def on_touch_move(self, window, touch):
        self.root.move_paddle(touch.x)
        return True

if __name__ == '__main__':
    CPUBreakerApp().run()
