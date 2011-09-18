Installation
------------

    pip install Flask-Dashed


Code::

    from flask import Flask
    from flask_dashed.admin import Admin

    app = Flask(__name__)
    admin = Admin(app)

    if __name__ == '__main__':
        app.run()
