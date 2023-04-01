#!/usr/bin/env python
import random

import pyglet
import pyglet.gl as gl
import pyglet.font

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

MODE_NORMAL = 0
MODE_OBJECTIVES = 1

class GameWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.fps_display = pyglet.window.FPSDisplay(self)
        self.set_caption("Pyweek35 The fine dinner")
        #self.keys = pyglet.window.key.KeyStateHandler()
        #self.push_handlers(self.keys)
        self.started = False
        self.ticks = 0
        self.mode = MODE_OBJECTIVES

        #pyglet.font.add_directory("data/fonts")        #self.font = pyglet.font.load("Funtype", 8, False, False)
        #self.font = pyglet.font.load('Constantine')
        #print (self.font)


    def objectives_onkey_instead(self, symbol, modifiers):
        self.mode = MODE_NORMAL

    def on_key_press(self, symbol, modifiers):
        #print('on_key_press', pyglet.window.key.symbol_string(symbol), modifiers)
        #print((symbol, 'in', (pyglet.window.key.W, pyglet.window.key.UP)))


        if self.mode == MODE_OBJECTIVES:
            return self.objectives_onkey_instead(symbol, modifiers)

        if symbol in (pyglet.window.key.O,pyglet.window.key.F1 ):
            self.mode = MODE_OBJECTIVES


        if symbol in (pyglet.window.key.R, ):
            self.reset_level()

        if symbol in (pyglet.window.key.W, pyglet.window.key.UP):
            self.main.last_dir = 'W'

        if symbol in (pyglet.window.key.S, pyglet.window.key.DOWN):
            self.main.last_dir = 'S'
        if symbol in (pyglet.window.key.A, pyglet.window.key.LEFT):
            self.main.last_dir = 'A'
        if symbol in (pyglet.window.key.D, pyglet.window.key.RIGHT):
            self.main.last_dir = 'D'

        if symbol == pyglet.window.key.N and modifiers:
            self.level.level_is_win = True
        #print(f'{self.last_dir=}')
        if symbol in (pyglet.window.key.ESCAPE,):
            self.close()




    def on_maybe_start(self):
        if self.started:
            return
        self.started = True

        self.main = Main()

        self.load_first_level()

    def load_first_level(self):
        self.level = LevelStart()

    def load_next_level(self):
        self.level = self.level.next_level()
        self.main.last_dir = 'S'


    def reset_level(self):
        self.level = self.level.__class__()

    def draw_objectives_instead(self):

        gl.glClearColor(0.0, 0.0, 0.0, 1.0)
        self.clear()

        self.label = pyglet.text.Label(self.level.title,
                                        font_size=24, x=int(self.width * 0.33), y=self.height - 50)
        self.olist = []
        n = 0
        for i in self.level.objectives:
            n += 1
            lbl = pyglet.text.Label(i, font_size=16,
                                                x=int(self.width * 0.03),
                                                y=self.height - 150 - n * 20)
            lbl.draw()
            self.olist.append(lbl)
        self.label.draw()


    def on_draw(self, dt=0):
        self.on_maybe_start()

        if self.mode == MODE_OBJECTIVES:
            return self.draw_objectives_instead()

        if self.level.level_is_win:
            self.load_next_level()
            self.mode = MODE_OBJECTIVES
            return
        self.ticks += 1

        self.main.micro_tick(self.level, {})
        if self.ticks % 20 == 0:
            self.main.macro_tick(self.level, {})


        gl.glClearColor(0.0, 0.0, 0.0, 1.0)
        self.clear()
        self.main.draw_level(self.level)
        #self.fps_display.draw()



    def on_resize(self, width, height):
        super().on_resize(width, height)
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
    can_pass = True
    blocks_light = True
    light_level = 0
    image_template = ''
    edible = False
    spreads_fire = False

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

class Basket(Entity):
    direction = 'W'
    image_template = 'data/pics/basket.png'

class Fence(Entity):
    direction = 'W'
    image_template = 'data/pics/fence.png'
    can_pass = False

class Furniture(Entity):
    direction = 'W'
    image_template = 'data/pics/furniture.png'
    can_pass = False

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
                    self.edible = False
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
    spreads_fire = True
    LDD = 100
    LD = 100
    DIM = 5

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
                c.light_level = int(max(c.light_level, self.LDD - self.LD * i / self.DIM))
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


class Mushroom(Lamp):
    LDD = 10
    LD = 4
    DIM = 0.7
    image_template = 'data/pics/mushroom.png'
    blocks_light = False
    edible = True
    spreads_fire = False

class Fire(Lamp):
    LDD = 100
    LD = 4
    DIM = 0.1
    image_template = 'data/pics/fireX.png'
    blocks_light = False
    spreads_fire = False

    def __init__(self):
        self.time = 100
    def get_image_name(self):
        return self.image_template.replace('X', random.choice('12'))

    def on_tick_after_light(self, level):
        self.time += 1
        if self.time < 25:
            return

        if random.randint(0, 20) != 1:
            return

        spread_fire(self, level, 'regular')
        self.time = 0

def spread_fire(s, level, comment=''):
    #print('spread fire from', s.x, s.y, s)
    for a in range(-1, 2):
        for b in range(-1, 2):
            c = level.cell(s.x + a, s.y + b)
            if (c and not c.front_entity
                    and isinstance(c.back_entity, Grass)
            ):
                c.front_entity = Fire()
                c.front_entity.time = 0


class Cell:
    x = 0
    y = 0
    back_entity = None
    front_entity = None
    light_level = 10
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Level:
    def __init__(self):
        self.w = 14
        self.h = 8
        self.level_is_win = False
        self.cells = [Cell(a,b)
            for b in range(self.h)
            for a in range(self.w)]
        self.player_head = None
        self.food_tgt = 10
        self.title = "Level 1"
        self.objectives = ['Use arrow-keys or WSAD to change direction.',
                           'Press O to review your goals.',
                           '',
                           'Eat at least 10 things and return to your basket.',
                           '','','',
                           'Press any key to continue']
        self.init()

    def init(self):
        for a, b, c in self.enum_cells():
            c.back_entity = Grass()
        '''
        self.cell(3, 3).front_entity = SnakeHead()
        self.cell(3, 3).front_entity.connection = 'W'
        self.cell(3, 3).front_entity.direction = 'S'
        self.cell(3, 4).front_entity = SnakeBody()
        self.cell(3, 4).front_entity.connection = 'W'
        self.cell(3, 4).front_entity.direction = 'S'
        
        self.cell(3, 5).back_entity = Basket()
        self.cell(3, 5).front_entity = SnakeTail()
        self.cell(3, 5).front_entity.direction = 'S'
        
        '''

        '''
        self.cell(6, 7).front_entity = Apple()
        self.cell(1, 0).front_entity = Apple()
        self.cell(5, 2).front_entity = Lamp()
        self.cell(5, 2).back_entity = Furniture()

        self.cell(1, 1).front_entity = Fire()
        self.cell(7, 2).front_entity = Bird()

        self.cell(10, 6).front_entity = Mushroom()
        self.cell(9, 3).front_entity = Mushroom()
        self.cell(9, 1).front_entity = Mushroom()
        self.cell(1, 7).front_entity = Mushroom()
        self.cell(4, 7).front_entity = Mushroom()
        self.cell(8, 7).front_entity = Mushroom()
        '''

        level_text = '''
.m...........m#
..............#
..S.......m...#
..............#
.....L.B.....m#
..............#
.A.........m..#
..............#
'''
        self.text_to_level(level_text)

    def text_to_level(self, level_text):
        lineno = 0
        for line in level_text.split('\n'):
            if not line:
                continue
            lineno += 1
            chno = -1
            for ch in line:
                chno += 1
                x = chno
                y = self.h - lineno
                if not self.cell(chno, y):
                    pass
                elif ch == '#':
                    self.cell(chno, y).back_entity = Furniture()
                elif ch == 'L':
                    self.cell(chno, y).front_entity = Lamp()
                    self.cell(chno, y).back_entity = Furniture()
                elif ch == 'l':
                    self.cell(chno, y).front_entity = Lamp()
                elif ch == 'm':
                    self.cell(chno, y).front_entity = Mushroom()
                elif ch == 'B':
                    self.cell(chno, y).front_entity = Bird()
                elif ch == 'A':
                    self.cell(chno, y).front_entity = Apple()
                elif ch == 'f':
                    self.cell(chno, y).front_entity = Fire()
                elif ch == 'S':
                    self.spawn_snake(chno, y)

    def get_stats(self):
        stats = {}
        for a, b, c in self.enum_cells():
            assert isinstance(c, Cell)
            cl = c.front_entity.__class__

            if cl in stats:
                stats[cl] += 1
            else:
                stats[cl] =1
        return stats



    def on_update(self):
        snake_len = 2
        head_at_basket = False
        stats = self.get_stats()
        #print(stats)
        for a, b, c in self.enum_cells():
            assert isinstance(c, Cell)
            if isinstance(c.front_entity, SnakeBody):
                snake_len += 1
            if isinstance(c.front_entity, SnakeHead) and isinstance(c.back_entity, Basket):
                head_at_basket = True

        if stats.get(SnakeBody, 0) - 1 >= self.food_tgt and head_at_basket:
            self.level_is_win = True

        self.spawn_apples(stats, 3)

    def next_level(self):
        return Level2()

    def spawn_snake(self, sx, sy):
        self.cell(sx, sy).front_entity = SnakeHead()
        self.cell(sx, sy).front_entity.connection = 'W'
        self.cell(sx, sy).front_entity.direction = 'S'
        self.cell(sx, sy + 1).front_entity = SnakeBody()
        self.cell(sx, sy + 1).front_entity.connection = 'W'
        self.cell(sx, sy + 1).front_entity.direction = 'S'
        self.cell(sx, sy + 2).back_entity = Basket()
        self.cell(sx, sy + 2).front_entity = SnakeTail()
        self.cell(sx, sy + 2).front_entity.direction = 'S'

    def spawn_apples(self, stats, count, prob=5):
        if stats.get(Apple, 0) < count:
            if random.randint(0, 100) < prob:
                self.spawn_random_apple()

    def spawn_birds(self, stats, count, prob=5):
        if stats.get(Bird, 0) < count:
            if random.randint(0, 100) < prob:
                self.spawn_random_bird()

    def spawn_mushrooms(self, stats, count, prob=5):
        if stats.get(Mushroom, 0) < count:
            if random.randint(0, 10) < prob:
                self.spawn_random_mushroom()

    def spawn_lamps(self, stats, count, prob=5):
        if stats.get(Lamp, 0) < count:
            if random.randint(0, 10) < prob:
                self.spawn_random_lamp()

    def spawn_fires(self, stats, count, prob=5):
        if stats.get(Fire, 0) < count:
            if random.randint(0, 10) < prob:
                self.spawn_random_fire()


    def spawn_random_apple(self):
        for r in range(1000):
            x = random.randint(0, self.w - 1)
            y = random.randint(0, self.h - 1)
            if not self.cell(x, y).front_entity:
                e = Apple()
                self.cell(x, y).front_entity = e
                self.cell(x, y).front_entity.x = x
                self.cell(x, y).front_entity.y = y
                play_sound('data/sound/drop.ogg')
                break

    def spawn_random_bird(self):
        for r in range(1000):
            x = random.randint(0, self.w - 1)
            y = random.randint(0, self.h - 1)
            c = self.cell(x, y)
            if not c:
                continue
            if c.front_entity:
                continue
            if c.light_level <=10 :
                continue
            e = Bird()
            self.cell(x, y).front_entity = e
            self.cell(x, y).front_entity.x = x
            self.cell(x, y).front_entity.y = y
            #play_sound('data/sound/drop.ogg')
            break

    def spawn_random_mushroom(self):
        for r in range(1000):
            x = random.randint(0, self.w - 1)
            y = random.randint(0, self.h - 1)
            c = self.cell(x, y)
            if not c:
                continue
            if c.front_entity:
                continue
            if not isinstance(c.back_entity, Grass):
                continue
            if c.light_level >= 10:
                continue
            e = Mushroom()
            self.cell(x, y).front_entity = e
            self.cell(x, y).front_entity.x = x
            self.cell(x, y).front_entity.y = y
            #play_sound('data/sound/drop.ogg')
            break

    def spawn_random_lamp(self):
        for r in range(1000):
            x = random.randint(0, self.w - 1)
            y = random.randint(0, self.h - 1)
            c = self.cell(x, y)
            if not c:
                continue
            if c.front_entity:
                continue
            if not isinstance(c.back_entity, Grass):
                continue
            if c.light_level >= 10:
                continue
            e = Lamp()
            self.cell(x, y).front_entity = e
            self.cell(x, y).front_entity.x = x
            self.cell(x, y).front_entity.y = y
            #play_sound('data/sound/drop.ogg')
            break

    def spawn_random_fire(self):
        for r in range(1000):
            x = random.randint(0, self.w - 1)
            y = random.randint(0, self.h - 1)
            c = self.cell(x, y)
            if not c:
                continue
            if c.front_entity:
                continue
            if not isinstance(c.back_entity, Grass):
                continue
            #if c.light_level >= 10:
            #    continue
            e = Fire()
            self.cell(x, y).front_entity = e
            self.cell(x, y).front_entity.x = x
            self.cell(x, y).front_entity.y = y
            #play_sound('data/sound/drop.ogg')
            break

    def cell(self, x ,y) -> Cell:
        if (0 <= x < self.w) and (0 <= y < self.h):
            return self.cells[x+y*self.w]
        return  None

    def enum_cells(self) -> (int, int , Cell):
        for b in range(self.h):
            for a in range(self.w):
                yield a, b, self.cell(a,b)

class LevelStart(Level):
    def __init__(self):
        self.w = 14
        self.h = 8
        self.level_is_win = False
        self.cells = [Cell(a, b)
                      for b in range(self.h)
                      for a in range(self.w)]
        self.player_head = None
        self.title = "The fine dinner"
        self.objectives = ['',
                           'Pyweek 35 entry by yarolig',
                           '',
                           '',
                           '', '', '',
                           'Press any key to continue']
        self.level_is_win = True
    def next_level(self):
        return Level()

class Level2(Level):
    def __init__(self):
        self.w = 14
        self.h = 8
        self.level_is_win = False
        self.cells = [Cell(a,b)
            for b in range(self.h)
            for a in range(self.w)]
        self.player_head = None
        self.food_tgt = 10
        self.title = "Level 2"
        self.objectives = ['Eat at least 10 things',
                           '',
                           '(optional) Do not eat any apples.',
                           '',
                           'When ready return to your basket.',
                           '','',
                           'Press R to restart the level.',
                           'Press any key to continue']
        self.init()

    def init(self):
        for a, b, c in self.enum_cells():
            c.back_entity = Grass()
            c.light_level = 10

        self.spawn_snake(3, 3)

        #self.cell(6, 7).front_entity = Apple()
        #self.cell(1, 0).front_entity = Apple()
        for i in range(5):
            for t in range(1000):
                x = random.randint(0, self.w-1)
                y = random.randint(0, self.h-1)
                if not self.cell(x, y).front_entity:
                    self.cell(x, y).front_entity = Lamp()
                    break

        #self.cell(1, 1).front_entity = Fire()
        #self.cell(7, 2).front_entity = Bird()
        for i in range(5):
            for t in range(1000):
                x = random.randint(0, self.w-1)
                y = random.randint(0, self.h-1)
                if not self.cell(x, y).front_entity:
                    self.cell(x, y).front_entity = Bird()
                    break

    def on_update(self):
        snake_len = 2
        head_at_basket = False
        stats = self.get_stats()
        for a, b, c in self.enum_cells():
            assert isinstance(c, Cell)
            if isinstance(c.front_entity, SnakeBody):
                snake_len += 1
            if isinstance(c.front_entity, SnakeHead) and isinstance(c.back_entity, Basket):
                head_at_basket = True

        if stats.get(SnakeBody, 0) - 1 >= self.food_tgt and head_at_basket:
            self.level_is_win = True
        #if snake_len >= 2 and head_at_basket:
        #    self.level_is_win = True


        self.spawn_birds(stats, 3, 100)
        self.spawn_apples(stats, 1, 30)

    def next_level(self):
        return Level3()




class Level3(Level):
    def __init__(self):
        self.w = 14
        self.h = 8
        self.level_is_win = False
        self.cells = [Cell(a,b)
            for b in range(self.h)
            for a in range(self.w)]
        self.player_head = None
        self.food_tgt = 20
        self.title = "Level 3"
        self.objectives = ['Eat at least 20 mushrooms',
                           '',
                           'When ready return to your basket.',
                           '','','',
                           'Press any key to continue']
        self.init()

    def init(self):
        for a, b, c in self.enum_cells():
            c.back_entity = Grass()

        level_text = '''
L.....#......m
......#.......
..S...#.......
..............
......#.......
......#.......
......#.......
L.....#......m
'''
        self.text_to_level(level_text)

    def on_update(self):
        snake_len = 2
        head_at_basket = False

        stats = self.get_stats()
        for a, b, c in self.enum_cells():
            assert isinstance(c, Cell)
            if isinstance(c.front_entity, SnakeBody):
                snake_len += 1
            if isinstance(c.front_entity, SnakeHead) and isinstance(c.back_entity, Basket):
                head_at_basket = True
        #if snake_len >= 2 and head_at_basket:
        #    self.level_is_win = True

        self.spawn_mushrooms(stats, 5, 20)
        if stats.get(SnakeBody, 0) - 1 >= self.food_tgt and head_at_basket:
            self.level_is_win = True

    def next_level(self):
        return Level4()



class Level4(Level):
    def __init__(self):
        self.w = 14
        self.h = 8
        self.level_is_win = False
        self.cells = [Cell(a,b)
            for b in range(self.h)
            for a in range(self.w)]
        self.player_head = None
        self.title = "Level 4"
        self.food_tgt = 10
        self.objectives = ['Try to eat as much as you can!',
                           '',
                           '',
                           'When ready return to your basket.',
                           '','','',
                           'Press any key to continue']
        self.init()

    def init(self):
        for a, b, c in self.enum_cells():
            c.back_entity = Grass()
            c.light_level = 10
        level_text = '''
.....#######.A
.m...#L#.m.#..
..S..###mmm#..
.........mm#..
.....###m.m#..
...m.#L#mmm#..
.m...#######..
..............
'''
        self.text_to_level(level_text)


    def on_update(self):
        snake_len = 2
        head_at_basket = False

        stats = self.get_stats()
        for a, b, c in self.enum_cells():
            assert isinstance(c, Cell)
            if isinstance(c.front_entity, SnakeBody):
                snake_len += 1
            if isinstance(c.front_entity, SnakeHead) and isinstance(c.back_entity, Basket):
                head_at_basket = True
        #if snake_len >= 2 and head_at_basket:
        #    self.level_is_win = True
        if stats.get(SnakeBody, 0) - 1 >= self.food_tgt and head_at_basket:
            self.level_is_win = True


    def next_level(self):
        return Level5()



class Level5(Level):
    def __init__(self):
        self.w = 14
        self.h = 8
        self.level_is_win = False
        self.cells = [Cell(a,b)
            for b in range(self.h)
            for a in range(self.w)]
        self.player_head = None
        self.title = "Level 5"
        self.food_tgt = 10
        self.objectives = ['Eat at least 30 things',
                           '',
                           '',
                           'When ready return to your basket.',
                           '','','',
                           'Press any key to continue']
        self.init()

    def init(self):
        for a, b, c in self.enum_cells():
            c.back_entity = Grass()
        level_text = '''
.............A
...m..##m.....
.......#...S..
..............
...#.....m..#.
...##.......#.
m........####.
.............m
'''
        self.text_to_level(level_text)


    def on_update(self):
        snake_len = 2
        head_at_basket = False
        stats = self.get_stats()

        for a, b, c in self.enum_cells():
            assert isinstance(c, Cell)
            if isinstance(c.front_entity, SnakeBody):
                snake_len += 1
            if isinstance(c.front_entity, SnakeHead) and isinstance(c.back_entity, Basket):
                head_at_basket = True

        self.spawn_mushrooms(stats, 5, 20)
        self.spawn_apples(stats, 1, 20)
        self.spawn_fires(stats, 1, 1)
        if stats.get(SnakeBody, 0) - 1 >= self.food_tgt and head_at_basket:
            self.level_is_win = True

    def next_level(self):
        return Level6()

class Level6(Level):
    def __init__(self):
        self.w = 14
        self.h = 8
        self.level_is_win = False
        self.cells = [Cell(a,b)
            for b in range(self.h)
            for a in range(self.w)]
        self.player_head = None
        self.title = "Level 5"
        self.food_tgt = 2
        self.objectives = ['Stop fire!',
                           '',
                           '',
                           'When ready return to your basket.',
                           '','','',
                           'Press any key to continue']
        self.init()

    def init(self):
        for a, b, c in self.enum_cells():
            c.back_entity = Grass()
        level_text = '''
.m....#.......
...#.A..A.....
S......#.....#
...A.....#.A..
.....fffffff..
...#ff...A....
.A.ff.....#...
..ff..#.......
'''
        self.text_to_level(level_text)

    def on_update(self):
        snake_len = 2
        head_at_basket = False
        stats = self.get_stats()

        for a, b, c in self.enum_cells():
            assert isinstance(c, Cell)
            if isinstance(c.front_entity, SnakeBody):
                snake_len += 1
            if isinstance(c.front_entity, SnakeHead) and isinstance(c.back_entity, Basket):
                head_at_basket = True

        self.spawn_mushrooms(stats, 5, 20)
        self.spawn_apples(stats, 1, 20)
        #self.spawn_fires(stats, 1, 1)
        if stats.get(Fire, 0) == 0 and head_at_basket:
            self.level_is_win = True

    def next_level(self):
        return LevelWin()



class LevelWin(Level):
    def __init__(self):
        self.w = 14
        self.h = 8
        self.level_is_win = False
        self.cells = [Cell(a,b)
            for b in range(self.h)
            for a in range(self.w)]
        self.player_head = None
        self.title = "You win :)"
        self.objectives = ['Thank you for playing the game.',
                           '',
                           '',
                           'PyWeek 35 entry by Alexander Izmailov',
                           '','','',
                           'Press any key to continue']
        self.init()

    def init(self):
        for a, b, c in self.enum_cells():
            c.back_entity = Grass()

        level_text = '''
.m............
..............
S.............
..............
..............
..............
..............
.............m
'''
        self.text_to_level(level_text)
        for i in range(2):
            for t in range(1000):
                x = random.randint(0, self.w-1)
                y = random.randint(0, self.h-1)
                if not self.cell(x, y).front_entity:
                    self.cell(x, y).front_entity = Lamp()
                    break

        for i in range(5):
            for t in range(1000):
                x = random.randint(0, self.w-1)
                y = random.randint(0, self.h-1)
                if not self.cell(x, y).front_entity:
                    self.cell(x, y).front_entity = Bird()
                    break

    def on_update(self):
        snake_len = 2
        head_at_basket = False

        stats = self.get_stats()
        for a, b, c in self.enum_cells():
            assert isinstance(c, Cell)
            if isinstance(c.front_entity, SnakeBody):
                snake_len += 1
            if isinstance(c.front_entity, SnakeHead) and isinstance(c.back_entity, Basket):
                head_at_basket = True
        if snake_len >= 2 and head_at_basket:
            self.level_is_win = True

        self.spawn_birds(stats, 2, 5)
        self.spawn_mushrooms(stats, 2, 5)
        self.spawn_apples(stats, 2, 5)
        self.spawn_lamps(stats, 1, 2)

    def next_level(self):
        return LevelWin()

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
                elif c.front_entity:
                    c.front_entity.get_image_name()

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
        #print(f'{dd=}')
        dx, dy = DIRECTIONS_XY[dd]
        newx, newy = hx + dx, hy + dy
        tgt_cell = level.cell(newx, newy)

        if not tgt_cell:
            pass
        elif tgt_cell.back_entity and not tgt_cell.back_entity.can_pass:
            pass
        elif not tgt_cell.front_entity:
            self.move_bodypart(c, tgt_cell, level)
            tgt_cell.front_entity.connection = DIRECTIONS_XY_R[(-dx, -dy)]
            tgt_cell.front_entity.direction = dd

        elif (isinstance(tgt_cell.front_entity, Fire)
              or isinstance(tgt_cell.front_entity, Lamp))\
                and not isinstance(tgt_cell.front_entity, Mushroom):
            if tgt_cell.front_entity.spreads_fire:
                spread_fire(tgt_cell.front_entity, level)

            tgt_cell.front_entity = None
            self.move_bodypart(c, tgt_cell, level)
            tgt_cell.front_entity.connection = DIRECTIONS_XY_R[(-dx, -dy)]
            tgt_cell.front_entity.direction = dd

        elif tgt_cell.front_entity.edible:
            ed = tgt_cell.front_entity.edible
            if tgt_cell.front_entity.edible:
                play_sound('data/sound/' + random.choice(['eat1.ogg', 'eat2.ogg']))

            if tgt_cell.front_entity.spreads_fire:
                spread_fire(tgt_cell.front_entity, level)
                pass
                # spread fire

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
            #self.spawn_food(level)

            tgt_cell.front_entity.connection = DIRECTIONS_XY_R[(-dx, -dy)]
            if not ed:
                self.move_bodypart(c, tgt_cell, level)

        if c and c.front_entity:
            c.front_entity.direction = dd
            c.front_entity.connection = cc

    def spawn_food(self, level):
        for r in range(1000):
            x = random.randint(0, level.w - 1)
            y = random.randint(0, level.h - 1)
            if not level.cell(x, y).front_entity:
                if random.randint(1, 10) < 6:
                    e = Apple()
                else:
                    e = Bird()
                level.cell(x, y).front_entity = e
                level.cell(x, y).front_entity.x = x
                level.cell(x, y).front_entity.y = y
                break

    def micro_tick(self, level, keys):
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
            c.light_level = 0

        for a, b, c in level.enum_cells():
            if c.front_entity:
                c.front_entity.x = a
                c.front_entity.y = b
                c.front_entity.on_tick(level)

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

        for a, b, c in level.enum_cells():
            if c.front_entity:
                c.front_entity.on_tick_after_light(level)
        level.on_update()

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
