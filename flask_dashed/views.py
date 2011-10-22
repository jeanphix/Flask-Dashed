# -*- coding: utf-8 -*-
from __future__ import absolute_import

from functools import wraps
from math import ceil
from flask import render_template, request, flash, redirect, url_for
from flask import abort
from flask.views import MethodView


def get_next_or(url):
    """Returns next request args or url.
    """
    return request.args['next'] if 'next' in request.args else url


def secure(endpoint, function, http_code):
    """Secures view function.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(self, *args, **kwargs):
            if not function(self, *args, **kwargs):
                return abort(http_code)
            return view_func(self, *args, **kwargs)
        return _wrapped_view
    return decorator


class AdminModuleMixin(object):
    """Provides admin node.

    :param admin_module: the admin module
    """
    def __init__(self, admin_module):
        self.admin_module = admin_module


class DashboardView(MethodView, AdminModuleMixin):
    """Displays user dashboard.

    :param admin_module: the admin module
    """
    def get(self):
        return  render_template('flask_dashed/dashboard.html',
            admin=self.admin_module.admin, module=self.admin_module)


def compute_args(request, update={}):
    """Merges all view_args and request args then update with
    user args.

    :param update: the user args
    """
    args = request.view_args.copy()
    args = dict(dict(request.args.to_dict(flat=True)), **args)
    args = dict(args, **update)
    return args


class ObjectListView(MethodView, AdminModuleMixin):
    """Lists objects.

    :param admin_module: the admin module
    """
    def get(self, page=1):
        """Displays object list.

        :param page: the current page index
        """
        page = int(page)
        search = request.args.get('search', None)
        order_by = request.args.get('orderby', None)
        order_direction = request.args.get('orderdir', None)
        count = self.admin_module.count_list(search=search)
        return  render_template(
            self.admin_module.list_template,
            admin=self.admin_module.admin,
            module=self.admin_module,
            objects=self.admin_module.get_object_list(
                search=search,
                offset=self.admin_module.list_per_page * (page - 1),
                limit=self.admin_module.list_per_page,
                order_by_name=order_by,
                order_by_direction=order_direction,
            ),
            count=count,
            current_page=page,
            pages=self.iter_pages(count, page),
            compute_args=compute_args
        )

    def iter_pages(self, count, current_page, left_edge=2,
                   left_current=2, right_current=5, right_edge=2):
        per_page = self.admin_module.list_per_page
        pages = int(ceil(count / float(per_page)))
        last = 0
        for num in xrange(1, pages + 1):
            if num <= left_edge or \
               (num > current_page - left_current - 1 and \
                num < current_page + right_current) or \
               num > pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num


class ObjectFormView(MethodView, AdminModuleMixin):
    """Creates or updates object.

    :param admin_module: the admin module
    """
    def get(self, pk=None):
        """Displays form.

        :param pk: the object primary key
        """
        obj = self.object
        if pk and obj is None:
            abort(404)
        is_new = pk is None
        form = self.admin_module.get_form(obj)
        return  render_template(
            self.admin_module.edit_template,
            admin=self.admin_module.admin,
            module=self.admin_module,
            object=obj,
            form=form,
            is_new=is_new
        )

    def post(self, pk=None):
        """Process form.

        :param pk: the object primary key
        """
        obj = self.object
        if pk and obj is None:
            abort(404)
        is_new = pk is None
        form = self.admin_module.get_form(obj)
        form.process(request.form)
        if form.validate():
            form.populate_obj(obj)
            self.admin_module.save_object(obj)
            if is_new:
                flash("Object successfully created", "success")
            else:
                flash("Object successfully updated", "success")
            return redirect(get_next_or(url_for(".%s_%s" %
                (self.admin_module.endpoint, 'list'))))
        else:
            flash("Can't save object due to errors", "error")
        return  render_template(
            self.admin_module.edit_template,
            admin=self.admin_module.admin,
            module=self.admin_module,
            object=obj,
            form=form,
            is_new=is_new
        )

    @property
    def object(self):
        """Gets object required by the form.

        :param pk: the object primary key
        """
        if not hasattr(self, '_object'):
            if 'pk' in request.view_args:
                self._object = self.admin_module.get_object(
                    request.view_args['pk'])
            else:
                self._object = self.admin_module.create_object()
        return self._object


class ObjectDeleteView(MethodView, AdminModuleMixin):
    """Deletes object.

    :param admin_module: the admin module
    """
    def get(self, pk):
        """Deletes object at given pk.

        :param pk: the primary key
        """
        obj = self.admin_module.get_object(pk)
        self.admin_module.delete_object(obj)
        flash("Object successfully deleted", "success")
        return redirect(get_next_or(url_for(".%s_%s" %
            (self.admin_module.endpoint, 'list'))))
