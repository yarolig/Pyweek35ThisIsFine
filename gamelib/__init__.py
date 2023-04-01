#!/usr/bin/env python
import random

import pyglet
import pyglet.gl as gl
import pyglet.font
from pyglet.graphics.shader import Shader, ShaderProgram

pyglet.options['audio'] = ('openal', 'pulse', 'xaudio2', 'directsound')
import pyglet.media
player = None


all_sounds = {}
def get_sound(name):
    global  all_sounds
    if name in all_sounds:
        return all_sounds[name]
    all_sounds[name] = pyglet.media.load(name, streaming=False)
    return all_sounds[name]

def play_sound(fn):
    s = get_sound(fn)
    s.play()


class GameWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fps_display = pyglet.window.FPSDisplay(self)
        self.set_caption("Pyweek35 This is fine")
        #self.keys = pyglet.window.key.KeyStateHandler()
        #self.push_handlers(self.keys)
        self.started = False
        self.ticks = 0

        #pyglet.font.add_directory("data/fonts")
        #self.font = pyglet.font.load("Funtype", 8, False, False)
        #print (self.font)


        #self.label = pyglet.text.Label('Hello, world', x=10, y=10)
        #                                font_name="Constantine",
        #                                font_size=12,x=10, y=10)

    def on_key_press(self, symbol, modifiers):
        print('on_key_press', pyglet.window.key.symbol_string(symbol), modifiers)
        print((symbol, 'in', (pyglet.window.key.W, pyglet.window.key.UP)))
        if symbol in (pyglet.window.key.W, pyglet.window.key.UP):
            self.main.last_dir = 'W'

        if symbol in (pyglet.window.key.S, pyglet.window.key.DOWN):
            self.main.last_dir = 'S'
        if symbol in (pyglet.window.key.A, pyglet.window.key.LEFT):
            self.main.last_dir = 'A'
        if symbol in (pyglet.window.key.D, pyglet.window.key.RIGHT):
            self.main.last_dir = 'D'
        #print(f'{self.last_dir=}')
        if symbol in (pyglet.window.key.ESCAPE,):
            self.close()


    def on_maybe_start(self):
        if self.started:
            return
        self.started = True

        self.main = Main()
        self.level = Level()

        self.level.cell(3, 3).front_entity = SnakeHead()
        self.level.cell(3, 3).front_entity.connection = 'W'
        self.level.cell(3, 3).front_entity.direction = 'S'

        self.level.cell(3, 4).front_entity = SnakeBody()
        self.level.cell(3, 4).front_entity.connection = 'W'
        self.level.cell(3, 4).front_entity.direction = 'S'

        self.level.cell(3, 5).front_entity = SnakeTail()
        self.level.cell(3, 5).front_entity.direction = 'S'

        self.level.cell(6,7).front_entity = Apple()
        self.level.cell(1,0).front_entity = Apple()
        self.level.cell(5,2).front_entity = Lamp()


        self.level.cell(7, 2).front_entity = Bird()

        for a, b, c in self.level.enum_cells():
            c.back_entity = Grass()


    def on_draw(self, dt=0):
        self.on_maybe_start()
        self.ticks += 1

        self.main.micro_tick(self.level, {})
        if self.ticks % 20 == 0:
            self.main.macro_tick(self.level, {})


        gl.glClearColor(0.0, 0.0, 0.0, 1.0)
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
    blocks_light = True
    light_level = 0
    image_template = ''
    edible = False

    # points to moving direction or connected head-side body part
    direction = ''

    # points to tail-side connected body part
    connection = ''
    def get_image_name(self):
        return self.image_template.replace('X', self.direction)

    def on_tick(self, level):
        pass
    def on_tick_after_light(self, level):
        pass


class Grass(Entity):
    direction = 'W'
    image_template = 'data/pics/grass.png'


class SnakeHead(Entity):
    direction = 'W'
    image_template = 'data/pics/snake_headX.png'
    tail_x = 0
    tail_y = 0

    def on_tick(self, level):
        pass
        #print (self.x, self.y)
        #level.cell(self.x, self.y).light_level = 100

class SnakeBody(Entity):
    direction = 'W'
    image_template = 'data/pics/snake_bodyX.png'
    def get_image_name(self):
        x = self.direction
        dc = self.direction + self.connection
        if dc in ('WD', 'DW'):
            x = 'LW'
        elif dc in ('DS', 'SD'):
            x = 'LD'
        elif dc in ('SA', 'AS'):
            x = 'LS'
        elif dc in ('AW', 'WA'):
            x = 'LA'

        return self.image_template.replace('X', x)

class SnakeTail(Entity):
    direction = 'W'
    image_template = 'data/pics/snake_tailX.png'

class Apple(Entity):
    direction = 'W'
    image_template = 'data/pics/apple.png'
    edible = True


class Bird(Entity):
    direction = 'W'
    image_template = 'data/pics/birdX.png'
    fly_away = 0
    edible = True

    def on_tick_after_light(self, level):
        if self.fly_away > 10:
            level.cell(self.x, self.y).front_entity = None
            return
        if self.fly_away:
            return
        for a in range(-1, 2):
            for b in range(-1, 2):
                c = level.cell(self.x+a, self.y+b)
                if (c and c.front_entity
                    and isinstance(c.front_entity, SnakeHead)
                    and c.light_level>0
                ):
                    self.fly_away = max(self.fly_away, 1)
                    play_sound('data/sound/'+random.choice(['fly-away3.ogg', 'fly-away2.ogg']))
    def get_image_name(self):
        if self.fly_away > 10:
            self.fly_away += 1
            return self.image_template.replace('X', '2')

        if self.fly_away > 5:
            self.fly_away += 1
            return self.image_template.replace('X', '2')

        if self.fly_away > 0:
            self.fly_away += 1
            return self.image_template.replace('X', '1')
        return self.image_template.replace('X', '')

class Lamp(Entity):
    direction = 'W'
    image_template = 'data/pics/lamp.png'
    blocks_light = False
    LD = 100

    def light_a_line(self, ps, pd, level):
        x, y = ps
        tx, ty = pd
        dx = (tx - x) * (1.0 / self.LD)
        dy = (ty - y) * (1.0 / self.LD)
        #print(f"{x} {y} {dx} {dy}")
        for i in range(0, self.LD):
            c = level.cell(int(x + 0.5 + dx * i), int(y + 0.5 + dy * i))
            if c:
                #print ('lighting', c.x, c.y, i, (x + dx * i), (y + dy * i))
                c.light_level = int(max(c.light_level, 100 - self.LD * i / 5))
                if c.front_entity and c.front_entity.blocks_light:
                    break
            else:
                break

    def on_tick(self, level):
        #print ('lamp at ', self.x, self.y)
        level.cell(self.x, self.y).light_level = self.LD
        for i in range(-self.LD, self.LD+1):
            self.light_a_line((self.x, self.y), (self.x+i, self.y+self.LD), level)
            self.light_a_line((self.x, self.y), (self.x+i, self.y-self.LD), level)
            self.light_a_line((self.x, self.y), (self.x+self.LD, self.y+i), level)
            self.light_a_line((self.x, self.y), (self.x-self.LD, self.y+i), level)

class Cell:
    x = 0
    y = 0
    back_entity = None
    front_entity = None
    light_level = 0
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Level:
    def __init__(self):
        self.w = 12
        self.h = 8
        self.cells = [Cell(a,b)
            for b in range(self.h)
            for a in range(self.w)]
        self.player_head = None

    def cell(self, x ,y) -> Cell:
        if (0 <= x < self.w) and (0 <= y < self.h):
            return self.cells[x+y*self.w]
        return  None

    def enum_cells(self) -> (int, int , Cell):
        for b in range(self.h):
            for a in range(self.w):
                yield a, b, self.cell(a,b)

class Main:
    def __init__(self):
        self.foreground_batch = pyglet.graphics.Batch()
        self.foreground_batch_sprites = []
        self.background_batch = pyglet.graphics.Batch()
        self.background_batch_sprites = []
        self.dark_batch = pyglet.graphics.Batch()
        self.last_dir = 'S'
        self.darkness_sprite = pyglet.sprite.Sprite(get_image('data/pics/darkness.png'))
        self.darkness_sprite.opacity = 10

    def draw_level(self, level):
        self.foreground_batch_sprites = []
        self.dark_batch_sprites = []
        self.background_batch_sprites = []
        # diffuse lights
        '''
        for a, b, c in level.enum_cells():
            lsum = 0
            lcnt = 0
            for (da,db) in ((0,0), (1,0), (-1,0), (0,1), (0,-1)):
                    oc = level.cell(a+da, b+db)
                    if oc:
                        lsum += oc.light_level
                        lcnt += 1
            c.new_light_level = lsum // lcnt

        for a, b, c in level.enum_cells():
            c.light_level = c.new_light_level
        '''
        for a, b, c in level.enum_cells():
            assert isinstance(c, Cell)

            if c.back_entity:
                if c.light_level:
                    img_name_b = c.back_entity.get_image_name()
                    s_b = pyglet.sprite.Sprite(get_image(img_name_b), a * 64, b * 64, batch=self.background_batch)
                    self.background_batch_sprites.append(s_b)
                    #s_b.draw()

            if c.front_entity:
                assert isinstance(c.front_entity, Entity)
                if c.light_level or (c.front_entity and isinstance(c.front_entity, SnakeHead)):
                    img_name = c.front_entity.get_image_name()
                    s = pyglet.sprite.Sprite(get_image(img_name), a*64, b*64, batch=self.foreground_batch)
                    self.foreground_batch_sprites.append(s)
                    #s.draw()

            if c.light_level<100:
                ds = pyglet.sprite.Sprite(get_image('data/pics/darkness.png'), a*64, b*64, batch=self.dark_batch)
                ds.opacity = max(0, 200 - 3*c.light_level)
                self.dark_batch_sprites.append(ds)



        self.background_batch.draw()
        self.foreground_batch.draw()
        self.dark_batch.draw()

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
            if oc and oc.front_entity and (isinstance(oc.front_entity, SnakeBody)
                                           or isinstance(oc.front_entity, SnakeTail)):
                self.move_bodypart(oc, sc, level)

            if sc.front_entity:
                sc.front_entity.direction = old_dir
                sc.front_entity.connection = old_conn


    def move_snake(self, hx, hy, level):
        c = level.cell(hx, hy)
        dd = self.last_dir # c.front_entity.direction
        cc = c.front_entity.connection
        print(f'{dd=}')
        dx, dy = DIRECTIONS_XY[dd]
        newx, newy = hx + dx, hy + dy
        tgt_cell = level.cell(newx, newy)


        if tgt_cell and not tgt_cell.front_entity:
            self.move_bodypart(c, tgt_cell, level)
            tgt_cell.front_entity.connection = DIRECTIONS_XY_R[(-dx, -dy)]
            tgt_cell.front_entity.direction = dd

        if tgt_cell and tgt_cell.front_entity and tgt_cell.front_entity.edible:
            play_sound('data/sound/' + random.choice(['eat1.ogg', 'eat2.ogg']))
            #self.move_bodypart(c, tgt_cell, level)
            fe = c.front_entity
            c.front_entity = SnakeBody()
            c.front_entity.x = fe.x
            c.front_entity.y = fe.y

            tfe = tgt_cell.front_entity
            tgt_cell.front_entity = fe
            tgt_cell.front_entity.x = tfe.x
            tgt_cell.front_entity.y = tfe.y
            tgt_cell.front_entity.direction = dd

            for r in range(1000):
                x = random.randint(0, level.w-1)
                y = random.randint(0, level.h-1)
                if not level.cell(x, y).front_entity:
                    if random.randint(1,10) < 6:
                        e = Apple()
                    else:
                        e = Bird()
                    level.cell(x, y).front_entity = e
                    level.cell(x, y).front_entity.x = x
                    level.cell(x, y).front_entity.y = y
                    break


            tgt_cell.front_entity.connection = DIRECTIONS_XY_R[(-dx, -dy)]

        if c and c.front_entity:
            c.front_entity.direction = dd
            c.front_entity.connection = cc

    def micro_tick(self, level, keys):
        head_cell = None

        for a, b, c in level.enum_cells():
            c.light_level = 0

        for a, b, c in level.enum_cells():
            if c.front_entity:
                c.front_entity.x = a
                c.front_entity.y = b
                c.front_entity.on_tick(level)


        for a, b, c in level.enum_cells():
            if c.front_entity:
                c.front_entity.on_tick_after_light(level)

        for a, b, c in level.enum_cells():
            #            print (b,a,c.front_entity)
            if c.front_entity and isinstance(c.front_entity, SnakeHead):
                head_cell = c
                level.player_head = c
                #print('head is at', a, b)
                break
        '''
        if head_cell:
            if keys[pyglet.window.key.W]:
                self.last_dir = 'W'
                self.last_dir = 'W'
            if keys[pyglet.window.key.S]:
                self.last_dir = 'S'
            if keys[pyglet.window.key.A]:
                self.last_dir = 'A'
            if keys[pyglet.window.key.D]:
                self.last_dir = 'D'
        '''
    def macro_tick(self, level, keys):
        # find snake's head
        # try to move head in its direction
        # pull conected body parts :)
        # update body parts location
        #print('macro tick')
        head_cell = None

        for a, b, c in level.enum_cells():
    #            print (b,a,c.front_entity)
             if c.front_entity and isinstance(c.front_entity, SnakeHead):
                 head_cell = c
                 level.player_head = c
                 #print('head is at', a, b)
                 break
        '''
        if head_cell:
             if keys[pyglet.window.key.W]:
                 self.last_dir = 'W'
             if keys[pyglet.window.key.S]:
                 self.last_dir = 'S'
             if keys[pyglet.window.key.A]:
                 self.last_dir = 'A'
             if keys[pyglet.window.key.D]:
                 self.last_dir = 'D'
             dd = self.last_dir
        '''
        if head_cell:
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
        #else:
        #    print('no head')

def main():
    #print('qwe')
    pyglet.options['shadow_window'] = False
    config = gl.Config(double_buffer=True,
                       #vsync=False,
                       #major_version=2,
                       #minor_version=0,
                       #forward_compatible=True,
                       #opengl_api="gl",
                       #debug=True
                       )
    #print (config)

    gw = GameWindow(config=config, resizable=True)
    #print(gw.context)
    pyglet.app.run()
