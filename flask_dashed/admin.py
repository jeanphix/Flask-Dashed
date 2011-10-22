# -*- coding: utf-8 -*-
from werkzeug import OrderedMultiDict

from flask import Blueprint, url_for, request, abort
from views import ObjectListView, ObjectFormView
from views import ObjectDeleteView, secure


def recursive_getattr(obj, attr):
    """Returns object related attributes, as it's a template filter None
    is return when attribute doesn't exists.

    eg::

        a = object()
        a.b = object()
        a.b.c = 1
        recursive_getattr(a, 'b.c') => 1
        recursive_getattr(a, 'b.d') => None
    """
    try:
        if "." not in attr:
                return getattr(obj, attr)
        else:
            l = attr.split('.')
            return recursive_getattr(getattr(obj, l[0]), '.'.join(l[1:]))
    except AttributeError:
        return None


class AdminNode(object):
    """An AdminNode just act as navigation container, it doesn't provide any
    rules.

    :param admin: the parent admin object
    :param url_prefix: the url prefix
    :param enpoint: the endpoint
    :param short_title: the short module title use on navigation
        & breadcrumbs
    :param title: the long title
    :param parent: the parent node
    """
    def __init__(self, admin, url_prefix, endpoint, short_title, title=None,
            parent=None):
        self.admin = admin
        self.parent = parent
        self.url_prefix = url_prefix
        self.endpoint = endpoint
        self.short_title = short_title
        self.title = title
        self.children = []

    @property
    def url_path(self):
        """Returns the url path relative to admin one.
        """
        if self.parent:
            return self.parent.url_path + self.url_prefix
        else:
            return self.url_prefix

    @property
    def parents(self):
        """Returns all parent hierarchy as list. Usefull for breadcrumbs.
        """
        if self.parent:
            parents = list(self.parent.parents)
            parents.append(self.parent)
            return parents
        else:
            return []

    def secure(self, http_code=403):
        """Gives a way to secure specific url path.

        :param http_code: the response http code when False
        """
        def decorator(f):
            self.admin.add_path_security(self.url_path, f, http_code)
            return f
        return decorator


class Admin(object):
    """Class that provides a way to add admin interface to Flask applications.

    :param app: the Flask application
    :param url_prefix: the url prefix
    :param main_dashboard: the main dashboard object
    :param endpoint: the endpoint
    """
    def __init__(self, app, url_prefix="/admin", title="flask-dashed",
            main_dashboard=None, endpoint='admin'):

        if not main_dashboard:
            from dashboard import DefaultDashboard
            main_dashboard = DefaultDashboard

        self.blueprint = Blueprint(endpoint, __name__,
            static_folder='static', template_folder='templates')
        self.app = app
        self.url_prefix = url_prefix
        self.endpoint = endpoint
        self.title = title
        self.secure_functions = OrderedMultiDict()
        # Checks security for current path
        self.blueprint.before_request(
            lambda: self.check_path_security(request.path))

        self.app.register_blueprint(self.blueprint, url_prefix=url_prefix)
        self.root_nodes = []

        self._add_node(main_dashboard, '/', 'main-dashboard', 'dashboard')
        # Registers recursive_getattr filter
        self.app.jinja_env.filters['recursive_getattr'] = recursive_getattr

    def register_node(self, url_prefix, endpoint, short_title, title=None,
            parent=None, node_class=AdminNode):
        """Registers admin node.

        :param url_prefix: the url prefix
        :param endpoint: the endpoint
        :param short_title: the short title
        :param title: the long title
        :param parent: the parent node path
        :param node_class: the class for node objects
        """
        return self._add_node(node_class, url_prefix, endpoint, short_title,
            title=title, parent=parent)

    def register_module(self, module_class, url_prefix, endpoint, short_title,
            title=None, parent=None):
        """Registers new module to current admin.
        """
        return self._add_node(module_class, url_prefix, endpoint, short_title,
            title=title, parent=parent)

    def _add_node(self, node_class, url_prefix, endpoint, short_title,
        title=None, parent=None):
        """Registers new node object to current admin object.

        """
        title = short_title if not title else title
        if parent and not issubclass(parent.__class__, AdminNode):
            raise Exception('`parent` class must be AdminNode subclass')
        new_node = node_class(self, url_prefix, endpoint, short_title,
            title=title, parent=parent)
        if parent:
            parent.children.append(new_node)
        else:
            self.root_nodes.append(new_node)
        return new_node

    @property
    def main_dashboard(self):
        return self.root_nodes[0]

    def add_path_security(self, path, function, http_code=403):
        """Registers security function for given path.

        :param path: the endpoint to secure
        :param function: the security function
        :param http_code: the response http code
        """
        self.secure_functions.add(path, (function, http_code))

    def check_path_security(self, path):
        """Checks security for specific and path.

        :param path: the path to check
        """
        for key in self.secure_functions.iterkeys():
            if path.startswith("%s%s" % (self.url_prefix, key)):
                for function, http_code in self.secure_functions.getlist(key):
                    if not function():
                        return abort(http_code)


class AdminModule(AdminNode):
    """Class that provides a way to create simple admin module.

    :param admin: the parent admin object
    :param url_prefix: the url prefix
    :param enpoint: the endpoint
    :param short_title: the short module title use on navigation
        & breadcrumbs
    :param title: the long title
    :param parent: the parent node
    """
    def __init__(self, *args, **kwargs):
        super(AdminModule, self).__init__(*args, **kwargs)
        self.rules = OrderedMultiDict()
        self._register_rules()

    def add_url_rule(self, rule, endpoint, view_func, **options):
        """Adds a routing rule to the application from relative endpoint.
        `view_class` is copied as we need to dynamically apply decorators.

        :param rule: the rule
        :param endpoint: the endpoint
        :param view_func: the view
        """
        class ViewClass(view_func.view_class):
            pass

        ViewClass.__name__ = "%s_%s" % (self.endpoint, endpoint)
        ViewClass.__module__ = view_func.__module__
        view_func.view_class = ViewClass
        full_endpoint = "%s.%s_%s" % (self.admin.endpoint,
            self.endpoint, endpoint)
        self.admin.app.add_url_rule("%s%s%s" % (self.admin.url_prefix,
            self.url_path, rule), full_endpoint, view_func, **options)
        self.rules.setlist(endpoint, [(rule, endpoint, view_func)])

    def _register_rules(self):
        """Registers all module rules after initialization.
        """
        if not hasattr(self, 'default_rules'):
            raise NotImplementedError('Admin module class must provide'
                + ' default_rules')
        for rule, endpoint, view_func in self.default_rules:
            self.add_url_rule(rule, endpoint, view_func)

    @property
    def url(self):
        """Returns first registered (main) rule as url.
        """
        try:
            return url_for("%s.%s_%s" % (self.admin.endpoint,
                self.endpoint, self.rules.lists()[0][0]))
                # Cause OrderedMultiDict.keys() doesn't preserve order...
        except IndexError:
            raise Exception('`AdminModule` must provide at list one rule.')

    def secure_endpoint(self, endpoint,  http_code=403):
        """Gives a way to secure specific url path.

        :param endpoint: the endpoint to protect
        :param http_code: the response http code when False
        """
        def decorator(f):
            self._secure_enpoint(endpoint, f, http_code)
            return f
        return decorator

    def _secure_enpoint(self, endpoint, secure_function, http_code):
        """Secure enpoint view function via `secure` decorator.

        :param enpoint: the endpoint to secure
        :param secure_function: the function to check
        :param http_code: the response http code when False.
        """
        rule, endpoint, view_func = self.rules.get(endpoint)
        view_func.view_class.dispatch_request =\
            secure(endpoint, secure_function, http_code)(
                view_func.view_class.dispatch_request)


class ObjectAdminModule(AdminModule):
    """Base class for object admin modules backends.
    Provides all required methods to retrieve, create, update and delete
    objects.
    """
    # List relateds
    list_view = ObjectListView
    list_template = 'flask_dashed/list.html'
    list_fields = None
    list_title = 'list'
    list_per_page = 10
    searchable_fields = None
    order_by = None
    # Edit relateds
    edit_template = 'flask_dashed/edit.html'
    form_view = ObjectFormView
    form_class = None
    edit_title = 'edit object'
    # New relateds
    new_title = 'new object'
    # Delete relateds
    delete_view = ObjectDeleteView

    def __new__(cls, *args, **kwargs):
        if not cls.list_fields:
            raise NotImplementedError()
        return super(ObjectAdminModule, cls).__new__(cls, *args, **kwargs)

    @property
    def default_rules(self):
        """Adds object list rule to current app.
        """
        return [
            ('/', 'list', self.list_view.as_view('short_title', self)),
            ('/page/<page>', 'list', self.list_view.as_view('short_title',
                self)),
            ('/new', 'new', self.form_view.as_view('short_title', self)),
            ('/<pk>/edit', 'edit', self.form_view.as_view('short_title',
                self)),
            ('/<pk>/delete', 'delete', self.delete_view.as_view('short_title',
                self)),
        ]

    def get_object_list(self, search=None, order_by_field=None,
            order_by_direction=None, offset=None, limit=None):
        """Returns objects list ordered and filtered.

        :param search: the search string for quick filtering
        :param order_by_field: the ordering field
        :param order_by_direction: the ordering direction
        :param offset: the pagintation offset
        :param limit: the pagination limit
        """
        raise NotImplementedError()

    def count_list(self, search=None):
        """Counts filtered object list.

        :param search: the search string for quick filtering.
        """
        raise NotImplementedError()

    def get_actions_for_object(self, object):
        """Returns action available for each object.

        :param object: the raw object
        """
        raise NotImplementedError()

    def get_form(self, obj):
        """Returns form initialy populate from object instance.

        :param obj: the object
        """
        return self.form_class(obj=obj)

    def get_object(self, pk=None):
        """Returns object retrieve by primary key.

        :param pk: the object primary key
        """
        raise NotImplementedError()

    def create_object(self):
        """Returns new object instance."""
        raise NotImplementedError()

    def save_object(self, object):
        """Persits object.

        :param object: the object to persist
        """
        raise NotImplementedError()

    def delete_object(self, object):
        """Deletes object.

        :param object: the object to delete
        """
        raise NotImplementedError()
