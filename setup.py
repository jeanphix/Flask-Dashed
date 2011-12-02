"""
Flask-Dashed
-----------

Adds a way to easily build admin apps.

"""
from setuptools import setup, find_packages


setup(
    name='Flask-Dashed',
    version='0.1b',
    url='https://github.com/jeanphix/Flask-Dashed',
    license='mit',
    author='Jean-Philippe Serafin',
    author_email='serafinjp@gmail.com',
    description='Adds a way to easily build admin apps',
    long_description=__doc__,
    data_files=[('', ['README'])],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask',
        'Flask-WTF',
        'WTAlchemy',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
