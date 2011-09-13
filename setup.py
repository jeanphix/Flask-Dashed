"""
Flask-Dashed
-----------

Adds a way to easily build backends.

"""
from setuptools import setup


setup(
    name='Flask-Dashed',
    version='0.1-dev',
    url='toto',
    license='MIT',
    author='Jean-Philippe Serafin',
    author_email='serafinjp@gmail.com',
    description='Adds a way to easily build backends',
    long_description=__doc__,
    packages=['flaskext'],
    namespace_packages=['flaskext'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask',
        'Flask-SQLAlchemy',
        'Flask-WTF',
        'odict'
    ],
    classifiers=[
        'Development Status :: 5 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
