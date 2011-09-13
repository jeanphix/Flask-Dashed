# -*- coding: utf-8 -*-

class Dashboard():
    """A dashboard is a Widget holder usually used as admin entry point.
    """
    def __init__(self, widgets=[]):
        self.widgets = widgets


class DashboardWidget():
    """Dashboard widget builder.
    """
    def __init__(self, title):
        """Initialize a new widget instance.

        :param title: the widget title
        """
        self.title = title

    def render(self):
        """Returns html content to display.
        """
        raise NotImplementedError()


class HelloWorldWidget(DashboardWidget):
    def render(self):
        return '<p>Hello world!</p>'


# Lets make a default dashboard
default_dashboard = Dashboard(widgets=[HelloWorldWidget('my first dashboard widget')])
