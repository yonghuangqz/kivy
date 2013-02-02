'''
Drawer
======

.. versionadded:: 1.6.0

.. image:: images/drawer.jpg
    :align: right

.. warning::

    This widget is still experimental, and its API is subject to change in
    a future version.

The :class:`Drawer` is a widget that imitates a sliding drawer. This widget
like :class:`~kivy.uix.scrollview.Scrollview` allows only one child widget.

Usage::

    drawer = Drawer(open_to = 'right')
    drawer.add_widget(layout_or_widget_instance)

    drawer.collapse_size = 100
    drawer.expand_size = 250

Change size of the strip/border used to resize::

    splitter.handle_size = '10pt'

Change appearance::

    splitter.handle_cls = your_custom_class

You could also change the appearance of the `handle_cls` which defaults to
:class:`DrawerHandle` by overriding the `kv` rule for like so in your app::

    <DrawerHandle>:
        horizontal: True if self.parent and self.parent.open_to[0] \
in ('t', 'b') else False
        background_normal: 'path to normal horizontal image' \
if self.horizontal else 'path to vertical normal image'
        background_down: 'path to pressed horizontal image' \
if self.horizontal else 'path to vertical pressed image'

'''


__all__ = ('Drawer', )

from kivy.uix.splitter import Splitter, SplitterStrip
from kivy.properties import AliasProperty, StringProperty, ListProperty, \
                            ObjectProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.animation import Animation


class DrawerHandle(Button):
    '''class used for graphical representation of \
    :class:`kivy.uix.drawer.DrawerHandle
    '''
    pass


class Drawer(Splitter):
    '''see module documentation.
    '''

    collapsed = BooleanProperty(True)
    '''Indicates the current state of the drawer

    :data:`collapsed` is a :class:`~kivy.properties.BoleanProperty`, \
    default to True
    '''

    border = ListProperty([4, 4, 4, 4])
    '''Border used for :class:`~kivy.graphics.vertex_instructions.BorderImage`
    graphics instruction.

    It must be a list of four values: (top, right, bottom, left). Read the
    BorderImage instruction for more information about how to use it.

    :data:`border` is a :class:`~kivy.properties.ListProperty`, \
    default to (4, 4, 4, 4)
    '''

    def _get_handle_cls(self):
        return self.strip_cls

    def _set_handle_cls(self, value):
        self.strip_cls = value

    handle_cls = AliasProperty(
                                _get_handle_cls,
                                _set_handle_cls,
                                bind=('strip_cls',))
    '''Specifies the class used for the Drawer Handle

    :data:`handle_cls` is a :class:`kivy.properties.ObjectProperty`
    defaults to :class:`~kivy.uix.drawer.DrawerHandle` which is of type\
    :class:`~kivy.uix.Drawer.DrawerHandle`
    '''

    def _get_open_to(self):
        return self.sizable_from

    def _set_open_to(self, value):
        self.sizable_from = value

    open_to = AliasProperty(
                            _get_open_to,
                            _set_open_to,
                            bind=('sizable_from', ))
    '''Specifies wether the widget is expandable from ::
        `left`, `right`, `top` or `bottom`

    :data:`open_to` is a :class:`~kivy.properties.AliasProperty`
    defaults to `left`
    '''

    def _get_handle_size(self):
        return self.strip_size

    def _set_handle_size(self, value):
        self.strip_size = value

    handle_size = AliasProperty(
                                _get_handle_size,
                                _set_handle_size,
                                bind=('strip_size', ))
    '''Specifies the size of the Handle

    :data:`handle_size` is a :class:`~kivy.properties.AliasProperty`
    defaults to `10pt`
    '''

    def _get_collapse_size(self):
        return self.min_size

    def _set_collapse_size(self, value):
        self.min_size = value

    collapse_size = AliasProperty(
                                    _get_collapse_size,
                                    _set_collapse_size,
                                    bind=('min_size', ))
    '''Specifies the minimum size beyond which the widget does not collapse

    :data:`collapse_size` is a :class:`~kivy.properties.AliasProperty`
    defaults to :data:`handle_size`
    '''

    def _get_expand_size(self):
        return self.max_size

    def _set_expand_size(self, value):
        self.max_size = value

    expand_size = AliasProperty(
                                _get_expand_size,
                                _set_expand_size,
                                bind=('max_size', ))
    '''Specifies the maximum size beyond which the drawer is not expandable

    :data:`expand_size` is a :class:`~kivy.properties.AliasProperty`
    defaults to `500pt`
    '''

    expand_animation = StringProperty('out_quad')
    '''Specifies the animation used for expanding the drawer

    :data:`expand_animation` is a :class:`~kivy.properties.StringProperty`
    defaults to `out_quad`
    '''

    collapse_animation = StringProperty('in_quad')
    '''Specifies the animation used for collapsing the drawer

    :data:`collapse_animation` is a :class:`~kivy.properties.StringProperty`
    defaults to `in_quad`
    '''

    def __init__(self, **kwargs):
        self.collapse_size = self.handle_size
        self.handle_cls = DrawerHandle
        self.width = 0
        super(Drawer, self).__init__(**kwargs)

    def on_release(self):
        '''This event is fired when the handle of the Drawer is released
        '''
        Animation.cancel_all(self, 'width')
        if self.collapsed:
            Animation(
                        width=self.expand_size,
                        d=.5,
                        t=self.expand_animation).start(self)
        else:
            Animation(
                        width=self.collapse_size,
                        d=.5,
                        t=self.collapse_animation).start(self)
        self.collapsed = not self.collapsed

if __name__ == '__main__':
    from kivy.app import App
    from kivy.uix.button import Button
    from kivy.uix.floatlayout import FloatLayout
    from kivy.lang import Builder

    class DrawerApp(App):

        def build(self):
            root = FloatLayout()
            spl = Drawer(
                size_hint=(None, .25),
                height=250,
                open_to='right')
            bl = BoxLayout()
            bl.add_widget(Button(text='Hello'))
            bl.add_widget(Button())
            bl.add_widget(Button())
            bl.add_widget(Button())
            spl.add_widget(bl)
            root.add_widget(spl)
            return root

    DrawerApp().run()
