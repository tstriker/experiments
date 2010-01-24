#!/usr/bin/env python
# - coding: utf-8 -
# Copyright (C) 2010 Toms Bauģis <toms.baugis at gmail.com>
"""
    this was the first attempt to achieve motion blur
    hoping that fading out will do the job.
    this is not quite motion blur - to see what i mean, try moving the mouse
    around for a longer while - instead of motion blur what you get is motion
    tail, which is unwanted.
    still this example teaches something too.
"""

import colorsys

import gtk
from lib import graphics
from lib.pytweener import Easing



class Canvas(graphics.Area):
    def __init__(self):
        graphics.Area.__init__(self)

        self.connect("mouse-move", self.on_mouse_move)
        self.mouse_moving = False

        self.coords = []
        self.x, self.y = 0, 0
        self.radius = 30


    def on_mouse_move(self, area, coords, state):
        # oh i know this should not be performed using tweeners, but hey - a demo!
        x, y = coords
        self.coords.insert(0, (x, y))
        self.coords = self.coords[:10]  # limit trail length

    def on_expose(self):
        for i, coords in enumerate(reversed(self.coords)):
            x, y = coords

            if i == len(self.coords) - 1:
                alpha = 1
            else:
                alpha = float(i+1) / len(self.coords) / 2

            self.set_color("#666", alpha)
            self.draw_rect(x - self.radius, y - self.radius,
                           self.radius * 2, self.radius * 2, self.radius / 5)
            self.context.fill()

        if len(self.coords) > 1:
            self.coords.pop(-1)

        self.redraw_canvas() # constant redraw (maintaining the requested frame rate)


class BasicWindow:
    def __init__(self):
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_size_request(300, 300)
        window.connect("delete_event", lambda *args: gtk.main_quit())

        canvas = Canvas()

        box = gtk.VBox()
        box.pack_start(canvas)


        window.add(box)
        window.show_all()


if __name__ == "__main__":
    example = BasicWindow()
    gtk.main()
