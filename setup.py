import sqlite3

from setuptools import setup
from model import DATABASE, TABLES


if not DATABASE.exists():
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
    entry_points='''
        [console_scripts]
        todo=todo:app.run
    '''
)

