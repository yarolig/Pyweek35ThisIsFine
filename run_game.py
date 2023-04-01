#!/usr/bin/env python

import pyglet

if pyglet.version.startswith('1.'):
    print("Please install pyglet>=2.0\n Current version: ", pyglet.version)


import gamelib
gamelib.main()
