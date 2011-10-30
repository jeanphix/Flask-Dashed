# -*- coding: utf-8 -*-
from __future__ import absolute_import

from flask import url_for
from flask_dashed.admin import ObjectAdminModule
from flask_dashed.views import ObjectFormView
from sqlalchemy.sql.expression import or_
from wtalchemy.orm import model_form as mf
from flaskext.wtf import Form


def model_form(*args, **kwargs):
    if not 'base_class' in kwargs:
        kwargs['base_class'] = Form
    return mf(*args, **kwargs)


class ModelAdminModule(ObjectAdminModule):
    """SQLAlchemy model admin module builder.
    """
    model = None
    form_view = ObjectFormView
    form_class = None
    db_session = None

    def __new__(cls, *args, **kwargs):
        if not cls.model:
            raise Exception('ModelAdminModule must provide `model` attribute')
        if not cls.list_fields:
            cls.list_fields = {}
            for column in cls.model.__table__._columns:
                cls.list_fields[column.name] = {'label': column.name,
                    'column': getattr(cls.model, column.name)}
        if not cls.form_class:
            cls.form_class = model_form(cls.model, cls.db_session)
        return super(ModelAdminModule, cls).__new__(cls, *args, **kwargs)

    def get_object_list(self, search=None, order_by_name=None,
            order_by_direction=None, offset=None, limit=None):
        """Returns ordered, filtered and limited query.

        :param search: the string for search filter
        :param order_by_name: the field name to order by
        :param order_by_direction: the field direction
        :param offset: the offset position
        :param limit: the limit
        """
        limit = limit if limit else self.list_per_page
        query = self._get_filtered_query(self.list_query_factory, search)
        if not (order_by_name and order_by_direction)\
                and self.order_by is not None:
            order_by_name = self.order_by[0]
            order_by_direction = self.order_by[1]
        if order_by_name and order_by_direction:
            try:
                query = query.order_by(
                    getattr(self.list_fields[order_by_name]['column'],
                        order_by_direction)()
                )
            except KeyError:
                raise Exception('Order by field must be provided in ' +
                    'list_fields with a column key')
        return query.limit(limit).offset(offset).all()

    def count_list(self, search=None):
        """Counts filtered list.

        :param search: the string for quick search
        """
        query = self._get_filtered_query(self.list_query_factory, search)
        return query.count()

    @property
    def list_query_factory(self):
        """Returns non filtered list query.
        """
        return self.db_session.query(self.model)

    @property
    def edit_query_factory(self):
        """Returns query for object edition.
        """
        return self.db_session.query(self.model).get

    def get_actions_for_object(self, object):
        """"Returns actions for object as and tuple list.

        :param object: the object
        """
        return [
            ('edit', 'edit', 'Edit object', url_for(
                "%s.%s_edit" % (self.admin.blueprint.name, self.endpoint),
                pk=object.id)),
            ('delete', 'delete', 'Delete object', url_for(
                "%s.%s_delete" % (self.admin.blueprint.name, self.endpoint),
                pk=object.id)),
        ]

    def get_object(self, pk):
        """Gets back object by primary key.

        :param pk: the object primary key
        """
        obj = self.edit_query_factory(pk)
        return obj

    def create_object(self):
        """New object instance new object."""
        return self.model()

    def save_object(self, obj):
        """Saves object.

        :param object: the object to save
        """
        self.db_session.add(obj)
        self.db_session.commit()

    def delete_object(self, object):
        """Deletes object.

        :param object: the object to delete
        """
        self.db_session.delete(object)
        self.db_session.commit()

    def _get_filtered_query(self, query, search=None):
        """Filters query.

        :param query: the non filtered query
        :param search: the string for quick search
        """
        if search and self.searchable_fields:
            condition = None
            for field in self.searchable_fields:
                if field in self.list_fields\
                        and 'column' in self.list_fields[field]:
                    if condition is None:
                        condition = self.list_fields[field]['column'].\
                            contains(search)
                    else:
                        condition = or_(condition, self.\
                            list_fields[field]['column'].contains(search))
                else:
                    raise Exception('Searchables fields must be in ' +
                        'list_fields with specified column.')
            query = query.filter(condition)
        return query
