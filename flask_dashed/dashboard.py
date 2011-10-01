# -*- coding: utf-8 -*-
from admin import AdminModule
from views import DashboardView


class Dashboard(AdminModule):
    """A dashboard is a Widget holder usually used as admin entry point.
    """
    widgets = []

    def register_rules(self):
        self.add_url_rule('/', 'show', DashboardView.as_view(
            'dashboard', self))


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


class DefaultDashboard(Dashboard):
    """Default dashboard."""
    widgets = [HelloWorldWidget('my first dashboard widget')]
