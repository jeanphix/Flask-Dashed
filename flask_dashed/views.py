# -*- coding: utf-8 -*-
from __future__ import absolute_import

from math import ceil
from flask import render_template, request, flash, redirect, url_for
from flask.views import MethodView


def get_next_or(url):
    """Returns next request args or url.
    """
    return request.args['next'] if 'next' in request.args else url


class DashboardView(MethodView):
    """Displays user dashboard.
    """
    def __init__(self, dashboard):
        self.dashboard = dashboard

    def get(self):
        return  render_template('dashboard.html', admin=self.dashboard.admin,
            dashboard=self.dashboard)


def compute_args(request, update={}):
    """Merges all view_args and request args then update with
    user args.
    """
    args = request.view_args.copy()
    args = dict(dict(request.args.to_dict(flat=True)), **args)
    args = dict(args, **update)
    return args


class ObjectListView(MethodView):
    """Lists objects.
    """
    def __init__(self, admin_module):
        self.admin_module = admin_module

    def get(self, page=1):
        """Displays object list."""
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


class ObjectFormView(MethodView):
    """Creates or updates object.
    """
    def __init__(self, admin_module):
        self.admin_module = admin_module

    def get(self, pk=None):
        """Displays form.
        """
        obj, is_new = self._get_object(pk)
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
        """
        obj, is_new = self._get_object(pk)
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
            form=form
        )

    def _get_object(self, pk=None):
        """Gets object required by the form.
        """
        if pk:
            obj = self.admin_module.get_object(pk)
            is_new = False
        else:
            obj = self.admin_module.create_object()
            is_new = True
        return obj, is_new


class ObjectDeleteView(MethodView):
    """Deletes object."""
    def __init__(self, admin_module):
        self.admin_module = admin_module

    def get(self, pk):
        obj = self.admin_module.get_object(pk)
        self.admin_module.delete_object(obj)
        flash("Object successfully deleted", "success")
        return redirect(get_next_or(url_for(".%s_%s" %
            (self.admin_module.endpoint, 'list'))))
