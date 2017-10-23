import sqlite3

from setuptools import setup
from todo.model import DATABASE, TABLES


if not DATABASE.exists():
    if not DATABASE.parent.exists():
        DATABASE.parent.mkdir()
    con = sqlite3.connect(str(DATABASE))
    cur = con.cursor()
    cur.execute(TABLES)
    con.commit()
    con.close()

setup(
    name='ToDo',
    version='0.2',
    license='BSD',
    author='URANO Ryoya',
    author_email='urano.works.mail@gmail.com',
    description='ToDo application for CLI.',
    install_requirs=[
        'calcium',
    ],
    packages=['todo'],
    entry_points='''
        [console_scripts]
        todo=todo.todo:main
    '''
)

