#!/usr/bin/env python
import pyglet
import pyglet.gl as gl
import pyglet.font
from pyglet.graphics.shader import Shader, ShaderProgram


default_vs = """#version 150 core
    in vec3 position;
    in vec4 colors;
    out vec4 vertex_colors;

    uniform mat4 projection;

    void main()
    {
        gl_Position = projection * vec4(position, 1.0);
        vertex_colors = colors;
    }
"""

default_fs = """#version 150 core
    in vec4 vertex_colors;
    out vec4 final_color;

    void main()
    {
        final_color = vertex_colors*0 + vec4(1,0,0,0);
    }
"""
class GameWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fps_display = pyglet.window.FPSDisplay(self)
        self.set_caption("Pyweek35 This is fine")
        self.default_shader = ShaderProgram(Shader(default_vs, 'vertex'),
                                            Shader(default_fs, 'fragment'))

        print(self.default_shader.attributes)
        self.vbo1 = self.default_shader.vertex_list(3, gl.GL_TRIANGLES)
        print(self.vbo1.position[:])
        self.vbo1.position[:] = (0, 0, 0, 100, 100, 100)

        #pyglet.font.add_directory("data/fonts")
        #self.font = pyglet.font.load("Funtype", 8, False, False)
        #print (self.font)


        #self.label = pyglet.text.Label('Hello, world', x=10, y=10)
        #                                font_name="Constantine",
        #                                font_size=12,x=10, y=10)

    def on_draw(self, dt=0):
        gl.glClearColor(0.2, 0.3, 0.4, 1.0)
        self.clear()

        self.fps_display.draw()

    def on_resize(self, width, height):
        gl.glViewport(0, 0, width, height)



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
