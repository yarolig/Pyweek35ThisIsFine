#!/usr/bin/env python
import pyglet
import pyglet.gl as gl
import pyglet.font
from pyglet.graphics.shader import Shader, ShaderProgram


class GameWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fps_display = pyglet.window.FPSDisplay(self)
        self.set_caption("Pyweek35 This is fine")
        self.keys = pyglet.window.key.KeyStateHandler()
        self.push_handlers(self.keys)
        self.started = False
        self.ticks = 0

        #pyglet.font.add_directory("data/fonts")
        #self.font = pyglet.font.load("Funtype", 8, False, False)
        #print (self.font)


        #self.label = pyglet.text.Label('Hello, world', x=10, y=10)
        #                                font_name="Constantine",
        #                                font_size=12,x=10, y=10)

    def on_maybe_start(self):
        if self.started:
            return
        self.started = True

        self.main = Main()
        self.level = Level()

        self.level.cell(3, 3).front_entity = SnakeHead()
        self.level.cell(3, 3).front_entity.connection = 'W'

        self.level.cell(3, 4).front_entity = SnakeBody()
        self.level.cell(3, 4).front_entity.connection = 'W'

        self.level.cell(3, 5).front_entity = SnakeTail()

        self.level.cell(6,7).front_entity = Apple()


    def on_draw(self, dt=0):
        self.on_maybe_start()
        self.ticks += 1

        self.main.micro_tick(self.level, self.keys)
        if self.ticks % 20 == 0:
            self.main.macro_tick(self.level, self.keys)


        gl.glClearColor(0.2, 0.3, 0.4, 1.0)
        self.clear()
        self.main.draw_level(self.level)
        self.fps_display.draw()



    def on_resize(self, width, height):
        gl.glViewport(0, 0, width, height)

all_images = {}
def get_image(name):
    global  all_images
    if name in all_images:
        return all_images[name]
    all_images[name] = pyglet.image.load(name)
    return all_images[name]

DIRECTIONS = 'WDSA'
DIRECTIONS_XY = {
    "W" : (0, 1),
    "S" : (0, -1),
    "A" : (-1, 0),
    "D" : (1, 0),
}
DIRECTIONS_XY_R = {
    (0, 1) : "W",
    (0, -1) : "S",
    (-1, 0) : "A",
    (1, 0) : "D",
}




class Entity:
    x = 0
    y = 0
    image_template = ''

    # points to moving direction or connected head-side body part
    direction = ''

    # points to tail-side connected body part
    connection = ''
    def get_image_name(self):
        return self.image_template.replace('X', self.direction)

class SnakeHead(Entity):
    direction = 'W'
    image_template = 'data/pics/snake_headX.png'
    tail_x = 0
    tail_y = 0

class SnakeBody(Entity):
    direction = 'W'
    image_template = 'data/pics/snake_bodyX.png'

class SnakeTail(Entity):
    direction = 'W'
    image_template = 'data/pics/snake_tailX.png'

class Apple(Entity):
    direction = 'W'
    image_template = 'data/pics/apple.png'

class Lamp(Entity):
    direction = 'W'
    image_template = 'data/pics/lamp.png'


class Cell:
    x = 0
    y = 0
    back_entity = None
    front_entity = None
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Level:
    def __init__(self):
        self.w = 8
        self.h = 8
        self.cells = [Cell(a,b)
            for b in range(self.h)
            for a in range(self.w)]
        self.player_head = None

    def cell(self, x ,y) -> Cell:
        if (0 <= x < self.w) and (0 <= y < self.h):
            return self.cells[x+y*self.w]
        return  None

    def enum_cells(self):
        for b in range(self.h):
            for a in range(self.w):
                yield a, b, self.cell(a,b)

class Main:
    def __init__(self):
        self.foreground_batch = pyglet.graphics.Batch()
        self.foreground_batch_sprites = []

    def draw_level(self, level):
        self.foreground_batch_sprites = []
        for a, b, c in level.enum_cells():
            assert isinstance(c, Cell)
            if c.front_entity:
                assert isinstance(c.front_entity, Entity)
                img_name = c.front_entity.get_image_name()
                s = pyglet.sprite.Sprite(get_image(img_name), a*64, b*64)
                s.draw()
        self.foreground_batch.draw()

    def move_bodypart(self, sc, tc, level):
        fe = sc.front_entity
        if not fe or not fe.direction:
            return

        old_dir = fe.direction
        old_conn = fe.connection
        tc.front_entity = sc.front_entity
        sc.front_entity = None

        if fe and isinstance(fe, Entity) and fe.connection:

            odx, ody = DIRECTIONS_XY[fe.connection]
            ox = sc.x + odx
            oy = sc.y + ody
            oc = level.cell(ox, oy)
            if oc:
                self.move_bodypart(oc, sc, level)

            if sc.front_entity:
                sc.front_entity.direction = old_dir
                sc.front_entity.connection = old_conn


    def move_snake(self, hx, hy, level):
        c = level.cell(hx, hy)
        dd = c.front_entity.direction
        cc = c.front_entity.connection

        dx, dy = DIRECTIONS_XY[dd]
        newx, newy = hx + dx, hy + dy
        tgt_cell = level.cell(newx, newy)
        if tgt_cell and not tgt_cell.front_entity:
            self.move_bodypart(c, tgt_cell, level)

            tgt_cell.front_entity.connection = DIRECTIONS_XY_R[(-dx, -dy)]
        if c and c.front_entity:
            c.front_entity.direction = dd
            c.front_entity.connection = cc

    def micro_tick(self, level, keys):
        head_cell = None
        for a, b, c in level.enum_cells():
            #            print (b,a,c.front_entity)
            if c.front_entity and isinstance(c.front_entity, SnakeHead):
                head_cell = c
                level.player_head = c
                print('head is at', a, b)
                break

        if head_cell:
            if keys[pyglet.window.key.W]:
                head_cell.front_entity.direction = 'W'
            if keys[pyglet.window.key.S]:
                head_cell.front_entity.direction = 'S'
            if keys[pyglet.window.key.A]:
                head_cell.front_entity.direction = 'A'
            if keys[pyglet.window.key.D]:
                head_cell.front_entity.direction = 'D'

    def macro_tick(self, level, keys):
        # find snake's head
        # try to move head in its direction
        # pull conected body parts :)
        # update body parts location
        print('macro tick')
        head_cell = None
        for a, b, c in level.enum_cells():
    #            print (b,a,c.front_entity)
             if c.front_entity and isinstance(c.front_entity, SnakeHead):
                 head_cell = c
                 level.player_head = c
                 print('head is at', a, b)
                 break

        if head_cell:
             if keys[pyglet.window.key.W]:
                 head_cell.front_entity.direction = 'W'
             if keys[pyglet.window.key.S]:
                 head_cell.front_entity.direction = 'S'
             if keys[pyglet.window.key.A]:
                 head_cell.front_entity.direction = 'A'
             if keys[pyglet.window.key.D]:
                 head_cell.front_entity.direction = 'D'
             dd = head_cell.front_entity.direction

             self.move_snake(head_cell.x, head_cell.y, level)

             '''
                dx, dy = DIRECTIONS_XY[dd]
                newx, newy = head_cell.x + dx, head_cell.y + dy
                tgt_cell = level.cell(newx, newy)
                if tgt_cell and not tgt_cell.front_entity:
                    tgt_cell.front_entity = c.front_entity
                    c.front_entity = None
                #else:
                #    print("can't move to", newx, newy, tgt_cell, tgt_cell.front_entity)
             '''
        else:
            print('no head')

def main():
    print('qwe')
    pyglet.options['shadow_window'] = False
    config = gl.Config(double_buffer=True,
                       vsync=False,
                       major_version=2,
                       minor_version=0,
                       #forward_compatible=True,
                       opengl_api="gl",
                       debug=True)
    print (config)
    gw = GameWindow(config=config, vsync=False, resizable=True)
    print(gw.context)
    pyglet.app.run()
