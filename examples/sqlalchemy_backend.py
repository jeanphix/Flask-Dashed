# -*- coding: utf-8 -*-
import odict
import wtforms

from flask import Flask

from flask_dashed.admin import Admin
from flask_dashed.ext.sqlalchemy import ModelAdminModule

from flaskext.sqlalchemy import SQLAlchemy

from sqlalchemy.orm import aliased, contains_eager

from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.ext.sqlalchemy.orm import model_form


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.debug = True

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.jinja_env.trim_blocks = True


db = SQLAlchemy(app)
db_session = db.session


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)

    def __unicode__(self):
        return unicode(self.name)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255))
    is_active = db.Column(db.Boolean())


class Profile(db.Model):
    id = db.Column(db.Integer, db.ForeignKey(User.id), primary_key=True)
    name = db.Column(db.String(255))
    location = db.Column(db.String(255))
    company_id = db.Column(db.Integer, db.ForeignKey(Company.id))

    user = db.relationship(User, backref=db.backref("profile",
        remote_side=id, uselist=False, cascade="all, delete-orphan"))

    company = db.relationship(Company, backref=db.backref("staff"))


user_group = db.Table(
    'user_group', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'))
)


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)

    users = db.relationship("User", secondary=user_group, backref="groups")

    def __unicode__(self):
        return unicode(self.name)


db.drop_all()
db.create_all()


admin = Admin(app, title="my business administration")


class ProfileForm(wtforms.Form):
    name = wtforms.TextField('Full name',
        [wtforms.validators.Length(min=4, max=255)])
    location = wtforms.TextField('Location',
        [wtforms.validators.Length(min=0, max=255)])
    company = QuerySelectField(
        query_factory=db_session.query(Company).all, allow_blank=True)


class UserForm(wtforms.Form):
    username = wtforms.TextField('Username',
        [wtforms.validators.Length(min=4, max=25)])
    groups = QuerySelectMultipleField(
        query_factory=db_session.query(Group).all)
    profile = wtforms.FormField(ProfileForm)


class UserModule(ModelAdminModule):
    model = User
    db_session = db_session
    profile_alias = aliased(Profile)

    list_fields = odict.odict((
        ('id', {'label': 'id', 'column': User.id}),
        ('username', {'label': 'username', 'column': User.username}),
        ('profile.name', {'label': 'name', 'column': profile_alias.name}),
        ('profile.location', {'label': 'location',
            'column': profile_alias.location}),
    ))

    list_title = 'user list'

    searchable_fields = ['username', 'profile.name', 'profile.location']

    order_by = ('id', 'desc')

    list_query_factory = model.query\
           .outerjoin(profile_alias, 'profile')\
           .options(contains_eager('profile', alias=profile_alias))\

    form_class = UserForm

    def create_object(self):
        user = self.model()
        user.profile = Profile()
        return user


class GroupModule(ModelAdminModule):
    model = Group
    db_session = db_session
    form_class = model_form(Group, exclude=('id',))


class CompanyModule(ModelAdminModule):
    model = Company
    db_session = db_session
    form_class = model_form(Company, exclude=('id',))


security = admin.register_node('/security', 'security', 'security management')

user_module = admin.register_module(UserModule, '/users', 'users',
    'users', parent=security)

group_module = admin.register_module(GroupModule, '/groups', 'groups',
    'groups', parent=security)

admin.register_module(CompanyModule, '/companies', 'companies', 'companies')


@app.route('/')
def hello_world():
    return 'Hello World!'

if __name__ == '__main__':
    app.run()
