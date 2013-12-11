#!/usr/bin/env python
# - coding: utf-8 -

# Copyright 2013 Bryce W. Harrington <bryce@bryceharrington.org>
# Dual licensed under the MIT or GPL Version 2 licenses.
# See http://github.com/tbaugis/hamster_experiments/blob/master/README.textile

from lib import graphics

class GridElement(object):
    def __init__(self, i,j, height,width, **args):
        self.__graphic = None
        self.i = i
        self.j = j
        self.height = height
        self.width = width
        self.stroke_width = args.get('stroke_width', 2)
        self.color_foreground = args.get('color_foreground', "#fff")
        self.color_stroke = args.get('color_stroke', "#000")
        self.args = args

    def set_origin(self, x, y):
        self.graphic.x = x
        self.graphic.y = y

    def create_sprite(self):
        t = GridElementSprite(self.i, self.j, self.width, self.height, **self.args)
        t.interactive = True
        t.connect('on-render', self.on_render)
        t.connect('on-mouse-over', self.on_over)
        t.connect('on-mouse-out', self.on_out)
        if 'on_click' in self.args.keys():
            t.connect('on-click', self.args['on_click'])
        return t

    def on_over(self, sprite):
        if not sprite: return # ignore blank clicks
        tmp = self.color_foreground
        self.color_foreground = self.color_stroke
        self.color_stroke = tmp
        print sprite.i, sprite.j, type(sprite)

    def on_out(self, sprite):
        if not sprite: return # ignore blank clicks
        tmp = self.color_foreground
        self.color_foreground = self.color_stroke
        self.color_stroke = tmp

    def on_render(self, sprite):
        '''Draw the shape for this element

        Override this with your own drawing code
        '''
        # TODO: Make this a required function to override
        pass

    @property
    def graphic(self):
        if self.__graphic is None:
            self.__graphic = self.create_sprite()
        assert(self.__graphic is not None)
        return self.__graphic


class GridElementSprite(graphics.Sprite):
    def __init__(self, i, j, width=100, height=100, color_foreground="#333", color_stroke="#000", stroke_width=2, on_click=None):
        graphics.Sprite.__init__(self)
        self.i = i
        self.j = j
        self.width = width
        self.height = height
        self.stroke_width = stroke_width
        self.color_foreground = color_foreground
        self.color_stroke = color_stroke


class Grid(graphics.Sprite):
    '''Infinite 2D array of grid elements'''
    def __init__(self, x=0, y=0, x_spacing=50, y_spacing=50):
        '''
        The x,y coordinates is the canvas location for the top left
        origin of the grid.  The x_spacing and y_spacing are the offsets
        of each subsequent grid element's location.  The spacings should
        be equal to the grid element dimensions to make a regular packed grid.
        '''
        graphics.Sprite.__init__(self, x=x, y=y)
        self.x_spacing = x_spacing
        self.y_spacing = y_spacing
        self.__elements = {}
        self.connect("on-render", self.on_render)

    def add(self, e):
        '''Adds an element to the grid at the element's i,j coordinate'''
        if e.i not in self.__elements.keys():
            self.__elements[e.i] = {}
        self.__elements[e.i][e.j] = e

    def get(self, i, j):
        '''Returns the element at the given i,j coordinate'''
        if (i not in self.__elements.keys() or
            j not in self.__elements[i].keys()):
            return None
        return self.__elements[i][j]

    def set(self, i, j, e):
        self.__elements[i][j] = e

    def on_render(self, widget):
        x = 0
        y = 0
        self.graphics.clear()
        self.sprites = []
        for column in self.__elements.values():
            for e in column.values():
                e.set_origin(x, y)
                e.on_render(e.graphic)
                self.add_child(e.graphic)
                y += self.y_spacing
            y = 0
            x += self.x_spacing

    # TODO: Maybe change this to an __iter__ and yield?
    def elements(self):
        for row in self.__elements.values():
            for col in row.values():
                yield col


class TriangularGridElement(GridElement):
    x_spacing_factor = 0.5
    y_spacing_factor = 1
    def __init__(self, i,j, height,width, **args):
        GridElement.__init__(self, i,j, height,width, **args)

    def set_origin(self, x,y):
        if self.i % 2 == 0:
            GridElement.set_origin(self, x, y)
        else:
            GridElement.set_origin(self, x, y+self.height)

    def on_render(self, sprite):
        sprite.graphics.clear()
        if self.i % 2 == 1:
            sprite.graphics.triangle(0,0, self.width,-1 * self.height)
        else:
            sprite.graphics.triangle(0,0, self.width,self.height)
        sprite.graphics.set_line_style(self.stroke_width)
        sprite.graphics.fill_preserve(self.color_foreground)
        sprite.graphics.stroke(self.color_stroke)

    def create_sprite(self):
        t = GridElement.create_sprite(self)
        if self.i % 2 == 1:
            t.height = -1 * t.height
        return t


class RectangularGridElement(GridElement):
    x_spacing_factor = 1
    y_spacing_factor = 1
    def __init__(self, i,j, height,width, **args):
        GridElement.__init__(self, i,j, height,width, **args)

    def set_origin(self, x,y):
        GridElement.set_origin(self, x, y)

    def on_render(self, sprite):
        sprite.graphics.clear()
        sprite.graphics.rectangle(0, 0, self.width, self.height)
        sprite.graphics.set_line_style(self.stroke_width)
        sprite.graphics.fill_preserve(self.color_foreground)
        sprite.graphics.stroke(self.color_stroke)


class HexagonalGridElement(GridElement):
    x_spacing_factor = 0.75
    y_spacing_factor = 0.866
    def __init__(self, i,j, height,width, **args):
        GridElement.__init__(self, i,j, height,width, **args)

    def set_origin(self, x,y):
        if self.i % 2 == 1:
            GridElement.set_origin(self, x, y + self.height/2 * 0.866)
        else:
            GridElement.set_origin(self, x, y)

    def on_render(self, sprite):
        sprite.graphics.clear()
        sprite.graphics.hexagon(0,0, self.height)
        sprite.graphics.set_line_style(self.stroke_width)
        sprite.graphics.fill_preserve(self.color_foreground)
        sprite.graphics.stroke(self.color_stroke)


class Scene(graphics.Scene):
    ELEMENT_CLASSES = [
        RectangularGridElement,
        HexagonalGridElement,
        TriangularGridElement,
        ]

    def __init__(self, width, height):
        graphics.Scene.__init__(self)
        self.background_color = "#000"
        self.element_number = 0
        self.size = 60
        self.cols = 0
        self.rows = 0
        self.old_width = width
        self.old_height = height

        self.connect('on-mouse-over', self.on_mouse_over)
        self.connect('on-mouse-out', self.on_mouse_out)
        self.connect('on-resize', self.on_resize)
        self.create_grid(50, 50, width-50, height-50)

    def create_element(self, cls, i, j):
        if j % 2 == i % 2:
            color = "#060"
        else:
            color = "#666"
        e = cls(i, j, height=self.size, width=self.size,
                color_foreground=color,
                color_stroke="#000",
                stroke_width=2)
        self.grid.add(e)

    def set_action(self, i, j, on_click):
        e = self.grid.get(i, j)
        if not e: return
        e.color_foreground = "#0a0"
        e.args['color_foreground'] = "#0a0"
        e.args['on_click'] = self.prev_grid_type

    def create_grid(self, x, y, width, height):
        self.grid = Grid(x=x, y=y)
        cls = self.ELEMENT_CLASSES[0]
        self.grid.x_spacing = self.size * cls.x_spacing_factor
        self.grid.y_spacing = self.size * cls.y_spacing_factor
        self.add_child(self.grid)

        self.cols = int(width / self.grid.x_spacing)
        self.rows = int(height / self.grid.y_spacing)
        #print("Grid: %d x %d" %(self.cols, self.rows))
        for i in range(0, self.cols):
            for j in range(0, self.rows):
                self.create_element(cls, i, j)

        # Add next and forward links
        self.set_action(0, 0, self.prev_grid_type)
        self.set_action(self.cols-1, 0, self.next_grid_type)

    def _set_grid_type(self, element_number):
        self.element_number = element_number
        cls = self.ELEMENT_CLASSES[self.element_number]
        for e in self.grid.elements():
            new_e = cls(e.i, e.j, self.size, self.size, **e.args)
            self.grid.set(e.i, e.j, new_e)
        self.grid.x_spacing = self.size * new_e.x_spacing_factor
        self.grid.y_spacing = self.size * new_e.y_spacing_factor
        self.grid.on_render(new_e)

    def prev_grid_type(self, widget, event):
        self._set_grid_type( (self.element_number - 1) % len(self.ELEMENT_CLASSES))

    def next_grid_type(self, widget, event):
        self._set_grid_type( (self.element_number + 1) % len(self.ELEMENT_CLASSES))

    def on_resize(self, scene, event):
        cls = self.ELEMENT_CLASSES[self.element_number]

        # Resize X
        offset_x = (event.width - self.old_width)
        size_x = self.size * cls.x_spacing_factor
        if offset_x > size_x:
            # Add more columns to the grid
            num_new_columns = int(offset_x / size_x)
            for i in range(self.cols, self.cols+num_new_columns):
                for j in range(0, self.rows):
                    self.create_element(cls, i,j)
            self.cols += num_new_columns
            offset_x -= num_new_columns * size_x
        elif offset_x < -size_x:
            num_removed_columns = int(offset_x / size_x)
            for i in range(self.cols-num_removed_columns, self.cols):
                self.grid.remove_column(i)
            self.cols -= num_removed_columns
            offset_x += num_removed_columns * size_x
        self.grid.x += offset_x/2.0
        self.old_width = event.width

        # Resize Y
        offset_y = event.height - self.old_height
        print("offset_y: %d" %(offset_y))
        size_y = self.size * cls.y_spacing_factor
        if offset_y > size_y:
            # Add more rows to the grid
            num_new_rows = int(offset_y / size_y)
            print "New rows: ", num_new_rows
            for j in range(self.rows, self.rows+num_new_rows):
                for i in range(0, self.cols):
                    self.create_element(cls, i, j)
            self.rows += num_new_rows
            offset_y -= num_new_rows * size_y
        elif offset_y < -size_y:
            num_removed_rows = int(offset_y / size_y)
            for j in range(self.rows-num_removed_rows, self.rows):
                self.grid.remove_row(j)
            self.rows -= num_removed_rows
            offset_y += num_removed_rows * size_y
        self.grid.y += offset_y/2.0
        self.old_height = event.height

        self.grid.on_render(scene)

    def on_mouse_over(self, scene, sprite):
        if not sprite: return # ignore blank clicks
        if self.tweener.get_tweens(sprite): return
        tmp = sprite.color_foreground
        sprite.color_foreground = sprite.color_stroke
        sprite.color_stroke = tmp
        print sprite.i, sprite.j, type(sprite)

    def on_mouse_out(self, scene, sprite):
        if not sprite: return # ignore blank clicks
        tmp = sprite.color_foreground
        sprite.color_foreground = sprite.color_stroke
        sprite.color_stroke = tmp


if __name__ == '__main__':
    import gtk

    class BasicWindow:
        def __init__(self):
            window = gtk.Window(gtk.WINDOW_TOPLEVEL)
            window.set_default_size(800, 800)
            window.connect("delete_event", lambda *args: gtk.main_quit())
            window.add(Scene(800, 800))
            window.show_all()

    window = BasicWindow()
    gtk.main()
