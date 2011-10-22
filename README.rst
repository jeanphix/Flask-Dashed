Introduction
------------

Flask-Dashed provides tools for build simple and extensible admin interfaces.

Online demonstration: http://flask-dashed.jeanphi.fr/ (Github account required).

List view:

.. image:: https://github.com/jean-philippe/Flask-Dashed/raw/master/docs/_static/screen.png

Form view:

.. image:: https://github.com/jean-philippe/Flask-Dashed/raw/master/docs/_static/screen-edit.png



Installation
------------

    pip install -e git+git://github.com/jean-philippe/Flask-Dashed.git#egg=Flask-Dashed


Minimal usage
-------------

Code::

    from flask import Flask
    from flask_dashed.admin import Admin

    app = Flask(__name__)
    admin = Admin(app)

    if __name__ == '__main__':
        app.run()


Deal with security
------------------

Securing all module endpoints::

    from flask import session

    book_module = admin.register_module(BookModule, '/books', 'books',
        'book management')

    @book_module.secure(http_code=401)
    def login_required():
        return "user" in session

Securing specific module endpoint::

    @book_module.secure_endpoint('edit', http_code=403)
    def check_edit_credential(view):
        # I'm now signed in, may I modify the ressource?
        return session.user.can_edit_book(view.object)


Organize modules
----------------

As admin nodes are registered into a "tree" it's quite easy to organize them.::

    library = admin.register_node('/library', 'library', my library)
    book_module = admin.register_module(BookModule, '/books', 'books',
        'book management', parent=library)

Navigation and breadcrumbs are automatically builds to feet your needs. Child module security will be inherited from parent one.


SQLALchemy extension
--------------------

Code::

    from flask_dashed.ext.sqlalchemy import ModelAdminModule


    class BookModule(ModelAdminModule):
        model = Book
        db_session = db.session

    book_module = admin.register_module(BookModule, '/books', 'books',
        'book management')
