"""
Flask-Dashed
-----------

Adds a way to easily build backends.

"""
from setuptools import setup


setup(
    name='Flask-Dashed',
    version='0.1',
    url='https://github.com/jean-philippe/Flask-Dashed',
    license='MIT',
    author='Jean-Philippe Serafin',
    author_email='serafinjp@gmail.com',
    description='Adds a way to easily build backends',
    long_description=__doc__,
    namespace_packages=['flaskext'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask',
        'Flask-SQLAlchemy',
        'Flask-WTF',
        'odict'
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    packages=[
        'flaskext',
        'flaskext.dashed',
        'flaskext.dashed.ext',
    ])
