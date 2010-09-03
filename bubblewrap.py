#!/usr/bin/env python
# - coding: utf-8 -
# Copyright (C) 2010 Toms Bauģis <toms.baugis at gmail.com>

"""Punishing cairo for expensive non-pixel-aligned stroking"""


import gtk
from lib import graphics
from lib.pytweener import Easing
import random

class Wonky(graphics.Sprite):
    def __init__(self, x, y, radius, cache_as_bitmap):
        graphics.Sprite.__init__(self, x=x, y=y, interactive=True, cache_as_bitmap = cache_as_bitmap)
        self.radius = radius
        self.fill = "#aaa"
        self.connect("on-render", self.on_render)

    def on_render(self, sprite):
        self.graphics.circle(0, 0, self.radius)
        self.graphics.fill_stroke(self.fill, "#222")



class Scene(graphics.Scene):
    def __init__(self):
        graphics.Scene.__init__(self, framerate=30)

        self.connect("on-mouse-over", self.on_mouse_over)
        self.connect("on-mouse-out", self.on_mouse_out)
        self.connect("on-mouse-move", self.on_mouse_move)
        self.connect("on-enter-frame", self.on_enter_frame)
        self.cache_as_bitmap = True

    def on_mouse_move(self, scene, event):
        sprite = self.get_sprite_at_position(event.x, event.y)

        if gtk.gdk.BUTTON1_MASK & event.state:
            if sprite.fill == "#f00":
                self.animate(sprite, fill="#aaa")
            else:
                self.animate(sprite, fill="#f00")


    def on_mouse_over(self, scene, sprite):
        sprite.original_radius = sprite.radius
        self.animate(sprite, radius = sprite.radius * 1.3, easing = Easing.Elastic.ease_out)


    def on_mouse_out(self, scene, sprite):
        self.animate(sprite, radius = sprite.original_radius, easing = Easing.Elastic.ease_out)

    def on_enter_frame(self, scene, context):
        print self.fps
        if not self.sprites:
            for x in range(30, self.width, 50):
                for y in range(30, self.height, 50):
                    wonky = Wonky(x, y, 20, self.cache_as_bitmap)
                    self.add_child(wonky)
                    self.animate(wonky,
                                 radius = wonky.radius * 1.3,
                                 easing = Easing.Elastic.ease_out,
                                 duration=2)




class BasicWindow:
    def __init__(self):
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_size_request(800, 500)
        window.connect("delete_event", lambda *args: gtk.main_quit())

        vbox = gtk.VBox()

        self.scene = Scene()
        vbox.pack_start(self.scene, True)

        self.button = gtk.Button("Cache as bitmap = True")

        def on_click(event):
            self.scene.cache_as_bitmap = not self.scene.cache_as_bitmap
            self.scene.clear()
            self.button.set_label("Cache as bitmap = %s" % str(self.scene.cache_as_bitmap))
            self.scene.redraw()


        self.button.connect("clicked", on_click)
        vbox.pack_start(self.button, False)

        window.add(vbox)
        window.show_all()

example = BasicWindow()
gtk.main()
