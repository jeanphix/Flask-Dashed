# -*- coding: utf-8 -*-
import odict

from flask import Blueprint, url_for, request, abort
from views import DashboardView, ObjectListView, ObjectFormView
from views import ObjectDeleteView
from dashboard import default_dashboard


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
    """
    def __init__(self, admin, endpoint, short_title, title=None, parent=None):
        """Construct new AdminNode instance.

        :param admin: the parent admin object
        :param short_title: the short module title use on navigation
            & breadcrumbs
        :param title: the long title
        """
        self.admin = admin
        self.endpoint = endpoint
        self.short_title = short_title
        self.title = title
        self.parent = parent


class Admin(object):
    """Class that provides a way to add admin interface to Flask applications.

    @TODO: need to write something better for endpoint factories
    """
    def __init__(self, app, url_prefix="/admin",
            main_dashboard=default_dashboard, endpoint='admin'):
        self.blueprint = Blueprint(endpoint, __name__,
            static_folder='static', template_folder='templates')
        self.register_main_dashboard(main_dashboard)
        self.app = app
        self.url_prefix = url_prefix
        self.endpoint = endpoint
        self.secure_functions = {}

        @self.blueprint.before_request
        def before_request():
            """Checks security for current endpoint."""
            endpoint = request.url_rule.endpoint\
                .lstrip("%s" % self.endpoint)
            self.check_endpoint_security(endpoint)

        self.blueprint.add_url_rule('/', view_func=DashboardView.as_view(
            'dashboard', dashboard=self.main_dashboard))
        self.app.register_blueprint(self.blueprint, url_prefix=url_prefix)
        self.registered_nodes = odict.odict()
        # Registers recursive_getattr filter
        self.app.jinja_env.filters['recursive_getattr'] = recursive_getattr

    def register_node(self, endpoint,  short_title, title=None, parent=None,
            node_class=AdminNode):
        title = short_title if not title else title
        new_node = node_class(self, endpoint, short_title, title=None)
        self._add_node(new_node, endpoint, parent=parent)
        return new_node

    def register_module(self, module_class, rule, endpoint, short_title,
            title=None, parent=None):
        """Registers new module to current admin.
        """
        title = short_title if not title else title
        new_module = module_class(self, rule, endpoint, short_title, title,
            parent=parent)
        self._add_node(new_module, endpoint, parent=parent)
        return new_module

    def _add_node(self, node_object, endpoint, parent=None):
        if parent and not parent in self.registered_nodes:
            raise Exception('parent admin node doesn\'t exist')
        path = "%s.%s" % (parent, endpoint) if parent else endpoint
        self.registered_nodes[path] = node_object

    def register_main_dashboard(self, main_dashboard):
        self.main_dashboard = main_dashboard
        self.main_dashboard.admin = self

    @property
    def navigation(self):
        """Returns main navigation elements as nested dict.
        """
        depth = {}
        depth[0] = {
            'class': 'main-dashboard',
            'short_title': 'dashboard',
            'title': 'Go to main dashboard',
            'url': url_for('%s.dashboard' % self.blueprint.name),
            'children': [],
        }
        navigation = [depth[0]]
        for path in self.registered_nodes:
            module = self.registered_nodes[path]
            level = path.count('.')
            if hasattr(module, 'rules') and len(module.rules) > 0:
                url = url_for(module.rules[0])
            else:
                url = None
            depth[level] = {
                'class': path,
                'short_title': module.short_title,
                'title': 'Go to %s' % module.short_title,
                'url': url,
                'children': [],
            }
            if level == 0:
                navigation.append(depth[level])
            else:
                parent = depth[level - 1]
                parent['children'].append(depth[level])
        return navigation

    def secure_path(self, path, http_code=403):
        """Gives a way to secure specific path.

        :param path: the path to protect
        :param http_code: the response http code
        """
        def decorator(f):
            self.add_security_at_path(path, f, http_code)
            return f
        return decorator

    def add_security_at_path(self, path, function, http_code=403):
        """Registers security function for given path.

        :param path: the path to secure
        :function: the security function
        :param http_code: the response http code
        """
        if path in self.secure_functions:
            self.secure_functions[path].append((function, http_code,))
        else:
            self.secure_functions[path] = [(function, http_code,)]

    def check_endpoint_security(self, endpoint):
        """Checks security for specific and point.

        :param endpoint: the endpoint to check
        """
        for path in self.secure_functions:
            if endpoint.startswith(path):
                for function, http_code in self.secure_functions[path]:
                    if not function():
                        return abort(http_code)


class AdminModule(AdminNode):
    """Class that provides a way to create simple admin module.
    """
    def __init__(self, admin, url_prefix, endpoint, short_title, title,
            parent=None):
        """Constructs new module instance.

        :param admin: the parent admin object
        :param url_prefix: the url prefix
        :param short_title: the short module title use un navigation
            & breadcrumbs
        :param title: the long title
        """
        self.admin = admin
        self.endpoint = endpoint
        self.short_title = short_title
        self.title = title
        self.url_prefix = url_prefix
        self.rules = []
        self.parent = parent
        self.register_rules()

    def add_url_rule(self, rule, endpoint, view_func=None, **options):
        """Adds a routing rule to the application from relative endpoint.

        :param rule: the rule
        :param endpoint: the endpoint
        :param view_func: the view
        """
        full_endpoint = "%s.%s_%s" % (self.admin.endpoint,
            self.endpoint, endpoint)
        self.admin.app.add_url_rule("%s%s%s" % (self.admin.url_prefix,
            self.url_prefix, rule), full_endpoint, view_func, **options)
        self.rules.append(full_endpoint)

    def register_rules(self):
        """Registers all module rules after initialization.
        """
        raise NotImplementedError('Admin module class must provide'
            + ' register_rules()')

    def secure_path(self, path, http_code=403):
        """Gives a way to secure endpoints.

        :param endpoint: the endpoint to protect
        """
        def decorator(f):
            self.admin.add_security_at_path(".%s_%s" % (self.endpoint,
                path.lstrip('.')), f, http_code)
            return f
        return decorator


class ObjectAdminModule(AdminModule):
    """Base class for object admin modules backends.
    Provides all required methods to retrieve, create, update and delete
    objects.
    """
    # List relateds
    list_view = ObjectListView
    list_template = 'list.html'
    list_fields = None
    list_title = 'list'
    list_per_page = 10
    searchable_fields = None
    order_by = None
    # Edit relateds
    edit_template = 'edit.html'
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

    def register_rules(self):
        """Adds object list rule to current app.
        """
        self.add_url_rule('/', 'list',
            view_func=self.list_view.as_view('short_title', self))
        self.add_url_rule('/page/<page>', 'list',
            view_func=self.list_view.as_view('short_title', self))
        self.add_url_rule('/new', 'new',
            view_func=self.form_view.as_view('short_title', self))
        self.add_url_rule('/<pk>/edit', 'edit',
            view_func=self.form_view.as_view('short_title', self))
        self.add_url_rule('/<pk>/delete', 'delete',
            view_func=self.delete_view.as_view('short_title', self))

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

    def get_form(self, object):
        """Returns form initialy populate from object instance.

        :param object: the edited object
        """
        return self.form_class(obj=object)

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
