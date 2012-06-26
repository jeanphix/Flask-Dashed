# -*- coding: utf-8 -*-
import unittest
import wtforms
from werkzeug import OrderedMultiDict
from flask import Flask, url_for
from flask.ext.testing import TestCase
from flask.ext.sqlalchemy import SQLAlchemy
from flask_dashed.admin import Admin, ObjectAdminModule
from flask_dashed.ext.sqlalchemy import ModelAdminModule
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from sqlalchemy.orm import aliased, contains_eager


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SECRET_KEY'] = 'secret'
db = SQLAlchemy(app)
admin = Admin(app)


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

    def __unicode__(self):
        return "Autor: %s" % self.name


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    year = db.Column(db.Integer)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))
    author = db.relationship(Author, primaryjoin=author_id == Author.id,
        backref="books")


class BaseTest(TestCase):
    def setUp(self):
        db.create_all()
        alain_fournier = Author(name=u"Alain Fournier")
        db.session.add(Book(title=u"Le grand Meaulnes",
            author=alain_fournier, year=1913))
        db.session.add(Book(title=u"Miracles",
            author=alain_fournier, year=1924))
        db.session.add(Book(title=u"Lettres à sa famille",
            author=alain_fournier, year=1929))
        db.session.add(Book(title=u"Lettres au petit B.",
            author=alain_fournier, year=1930))

        charles_baudelaire = Author(name=u"Charles Baudelaire")
        db.session.add(Book(title=u"La Fanfarlo",
            author=charles_baudelaire, year=1847))
        db.session.add(Book(title=u"Du vin et du haschisch",
            author=charles_baudelaire, year=1851))
        db.session.add(Book(title=u"Fusées",
            author=charles_baudelaire, year=1851))
        db.session.add(Book(title=u"L'Art romantique",
            author=charles_baudelaire, year=1852))
        db.session.add(Book(title=u"Morale du joujou",
            author=charles_baudelaire, year=1853))
        db.session.add(Book(title=u"Exposition universelle",
            author=charles_baudelaire, year=1855))
        db.session.add(Book(title=u"Les Fleurs du mal",
            author=charles_baudelaire, year=1857))
        db.session.add(Book(title=u"Le Poème du haschisch",
            author=charles_baudelaire, year=1858))
        db.session.add(Book(title=u"Les Paradis artificiels",
            author=charles_baudelaire, year=1860))
        db.session.add(Book(title=u"La Chevelure",
            author=charles_baudelaire, year=1861))
        db.session.add(Book(title=u"Réflexions sur quelques-uns de "
            + "mes contemporains", author=charles_baudelaire, year=1861))

        albert_camus = Author(name=u"Albert Camus")
        db.session.add(Book(title=u"Révolte dans les Asturies",
            author=albert_camus, year=1936))
        db.session.add(Book(title=u"L'Envers et l'Endroit",
            author=albert_camus, year=1937))
        db.session.add(Book(title=u"Caligula", author=albert_camus, year=1938))
        db.session.add(Book(title=u"Noces", author=albert_camus, year=1939))
        db.session.add(Book(title=u"Le Mythe de Sisyphe",
            author=albert_camus, year=1942))
        db.session.add(Book(title=u"L'Étranger",
            author=albert_camus, year=1942))
        db.session.add(Book(title=u"Le Malentendu",
            author=albert_camus, year=1944))
        db.session.add(Book(title=u"La Peste", author=albert_camus, year=1947))
        db.session.add(Book(title=u"L'État de siège",
            author=albert_camus, year=1948))
        db.session.add(Book(title=u"Les Justes",
            author=albert_camus, year=1949))
        db.session.add(Book(title=u"L'Homme révolté",
            author=albert_camus, year=1951))
        db.session.add(Book(title=u"L'Été", author=albert_camus, year=1954))
        db.session.add(Book(title=u"La Chute", author=albert_camus, year=1956))
        db.session.add(Book(title=u"L'Exil et le Royaume",
            author=albert_camus, year=1957))

        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class AutoModelAdminModuleTest(BaseTest):

    class AutoBookModule(ModelAdminModule):
        db_session = db.session
        model = Book

    class AutoAuthorModule(ModelAdminModule):
        db_session = db.session
        model = Author

    def create_app(self):
        self.book_module = admin.register_module(self.AutoBookModule,
            '/book', 'book', 'auto generated book module')
        return app

    def test_created_rules(self):
        for endpoint in ('.book_list', '.book_edit', '.book_delete',):
            self.assertIn(endpoint, str(self.app.url_map))

    def test_get_objects(self):
        objects = self.book_module.get_object_list()
        self.assertEqual(len(objects), ObjectAdminModule.list_per_page)

    def test_count_list(self):
        self.assertEqual(self.book_module.count_list(), Book.query.count())

    def test_list_view(self):
        r = self.client.get(url_for('admin.book_list'))
        self.assertEqual(r.status_code, 200)

    def test_edit_view(self):
        r = self.client.get(url_for('admin.book_edit',
            pk=Book.query.first().id))
        self.assertEqual(r.status_code, 200)

    def test_secure_node(self):

        @self.book_module.secure(403)
        def secure():
            return False

        self.assertIn(self.book_module.url_path,
            admin.secure_functions.keys())
        r = self.client.get(url_for('admin.book_list'))
        self.assertEqual(r.status_code, 403)
        r = self.client.get(url_for('admin.book_new'))
        self.assertEqual(r.status_code, 403)

    def test_secure_parent_node(self):

        @self.book_module.secure(403)
        def secure():
            return True

        admin.register_module(self.AutoAuthorModule, '/author', 'author',
            'auto generated author module', parent=self.book_module)
        self.assertIn(self.book_module.url_path,
            admin.secure_functions.keys())
        r = self.client.get(url_for('admin.author_list'))
        self.assertEqual(r.status_code, 403)
        r = self.client.get(url_for('admin.author_new'))
        self.assertEqual(r.status_code, 403)

    def test_secure_module_endpoint(self):

        author_module = admin.register_module(self.AutoAuthorModule,
            '/author-again', 'author_again', 'auto generated author module')

        @author_module.secure_endpoint('list', 403)
        def secure(view):
            return False

        r = self.client.get(url_for('admin.author_again_list'))
        self.assertEqual(r.status_code, 403)
        r = self.client.get(url_for('admin.author_again_new'))
        self.assertEqual(r.status_code, 200)


class BookForm(wtforms.Form):
    title = wtforms.TextField('Title', [wtforms.validators.required()])
    author = QuerySelectField(query_factory=Author.query.all,
        allow_blank=True)


class ExplicitModelAdminModuleTest(BaseTest):

    class BookModule(ModelAdminModule):
        """Sample module with explicit eager loaded query.
        """
        model = Book
        db_session = db.session
        author_alias = aliased(Author)

        list_fields = OrderedMultiDict((
            ('id', {'label': 'id', 'column': Book.id}),
            ('title', {'label': 'book title', 'column': Book.title}),
            ('year', {'label': 'year', 'column': Book.year}),
            ('author.name', {'label': 'author name',
                'column': author_alias.name}),
        ))
        list_title = 'books list'

        searchable_fields = ['title', 'author.name']

        order_by = ('id', 'asc')

        list_query_factory = model.query\
               .outerjoin(author_alias, 'author')\
               .options(contains_eager('author', alias=author_alias))\

        form_class = BookForm

    def create_app(self):
        self.book_module = admin.register_module(self.BookModule,
            '/book', 'book', 'auto generated book module')
        return app

    def test_filtered_get_objects(self):
        objects = self.book_module.get_object_list(search='lettres')
        self.assertEqual(len(objects), 2)


if __name__ == '__main__':
    unittest.main()
