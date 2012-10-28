from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Gio
import sys

class MyWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        Gtk.Window.__init__(self, title="Toolbar Example", application=app)
        self.set_default_size(400, 200)

        # a grid to attach the toolbar
        grid = Gtk.Grid()

        # a toolbar created in the method create_toolbar (see below)
        toolbar = self.create_toolbar()
        # with extra horizontal space
        toolbar.set_hexpand(True)
        # show the toolbar
        toolbar.show()

        # attach the toolbar to the grid
        grid.attach(toolbar, 0, 0, 1, 1)

        # add the grid to the window
        self.add(grid)

        # create the actions that control the window and connect their signal to a
        # callback method (see below):

        # undo
        undo_action = Gio.SimpleAction.new("undo", None)
        undo_action.connect("activate", self.undo_callback)
        self.add_action(undo_action)

        # fullscreen
        fullscreen_action = Gio.SimpleAction.new("fullscreen", None)
        fullscreen_action.connect("activate", self.fullscreen_callback)
        self.add_action(fullscreen_action)

    # a method to create the toolbar
    def create_toolbar(self):
        # a toolbar
        toolbar = Gtk.Toolbar()

        # which is the primary toolbar of the application
        toolbar.get_style_context().add_class(Gtk.STYLE_CLASS_PRIMARY_TOOLBAR);

        # create a button for the "new" action, with a stock image
        new_button = Gtk.ToolButton.new_from_stock(Gtk.STOCK_NEW)
        # label is shown
        new_button.set_is_important(True)
        # insert the button at position in the toolbar
        toolbar.insert(new_button, 0)
        # show the button
        new_button.show()
        # set the name of the action associated with the button.
        # The action controls the application (app)
        new_button.set_action_name("app.new")

        # button for the "open" action
        open_button = Gtk.ToolButton.new_from_stock(Gtk.STOCK_OPEN)
        open_button.set_is_important(True)
        toolbar.insert(open_button, 1)
        open_button.show()
        open_button.set_action_name("app.open")

        # button for the "undo" action
        undo_button = Gtk.ToolButton.new_from_stock(Gtk.STOCK_UNDO)
        undo_button.set_is_important(True)
        toolbar.insert(undo_button, 2)
        undo_button.show()
        undo_button.set_action_name("win.undo")

        # button for the "fullscreen/leave fullscreen" action
        self.fullscreen_button = Gtk.ToolButton.new_from_stock(Gtk.STOCK_FULLSCREEN)
        self.fullscreen_button.set_is_important(True)
        toolbar.insert(self.fullscreen_button, 3)
        self.fullscreen_button.set_action_name("win.fullscreen")

        # return the complete toolbar
        return toolbar

    # callback method for undo
    def undo_callback(self, action, parameter):
        print "You clicked \"Undo\"."

    # callback method for fullscreen / leave fullscreen
    def fullscreen_callback(self, action, parameter):
        # check if the state is the same as Gdk.WindowState.FULLSCREEN, which is a bit flag
        is_fullscreen = self.get_window().get_state() & Gdk.WindowState.FULLSCREEN != 0
        if not is_fullscreen:
            self.fullscreen_button.set_stock_id(Gtk.STOCK_LEAVE_FULLSCREEN)
            self.fullscreen()
        else:
            self.fullscreen_button.set_stock_id(Gtk.STOCK_FULLSCREEN)
            self.unfullscreen()

class MyApplication(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self)

    def do_activate(self):
        win = MyWindow(self)
        win.show_all()

    def do_startup(self):
        Gtk.Application.do_startup(self)

        # create the actions that control the window and connect their signal to a
        # callback method (see below):

        # new
        new_action = Gio.SimpleAction.new("new", None)
        new_action.connect("activate", self.new_callback)
        app.add_action(new_action)

        # open
        open_action = Gio.SimpleAction.new("open", None)
        open_action.connect("activate", self.open_callback)
        app.add_action(open_action)

    # callback method for new
    def new_callback(self, action, parameter):
        print "You clicked \"New\"."

    # callback method for open
    def open_callback(self, action, parameter):
        print "You clicked \"Open\"."

app = MyApplication()
exit_status = app.run(sys.argv)
sys.exit(exit_status)
