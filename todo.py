"""ToDo application for CLI."""
import configparser
import datetime
import os
import platform
import sqlite3
import subprocess
import sys
import tempfile

from pathlib import Path
from command import Command
from model import ToDo, DATABASE, TABLES

EDITOR_APP = ''
if (Path().home()/'.config'/'todo'/'config').exists():
    config = configparser.ConfigParser()
    config.read('config')
    EDITOR_APP = config['default']['editor']
else:
    if 'EDITOR' in os.environ:
        EDITOR_APP = os.environ['EDITOR']
    elif platform.system() == 'Linux':
        EDITOR_APP = 'vim'
    elif platform.system() == 'Mac':
        EDITOR_APP = 'open'
    elif platform.system() == 'Windows':
        EDITOR_APP = 'notepad.exe'


class Task:
    def __init__(self, task_id, title, description, create_at, update_at, done):
        self.task_id = task_id
        self.title = title
        self.description = description
        self.create_at = create_at
        self.update_at = update_at
        self.done = done


con = sqlite3.connect(str(DATABASE))
cur = con.cursor()
todo = ToDo(cur)
app = Command()
app.welcome_message = 'Welcome to Japari Park!'
tempfiles = dict()


@app.command('list', help='show tasks (title only)')
def list():
    tasks = todo.getall()
    return 'task id\ttitle\n' + \
           '\n'.join(['%d\t%s' % (task.task_id, task.title) for task in tasks])

@app.command('show', help='show tasks (all info)')
def show():
    tasks = todo.getall()
    template = '''================================================================================
Title: %s [Task ID:%d]
Create: %s\tLast Update: %s
--------------------------------------------------------------------------------
%s
================================================================================
'''
    return ''.join(
        template % (
            task.title, task.task_id, task.create_at, task.update_at, task.description
        ) for task in tasks
    )

@app.command('add', args=['title'], help='add task')
def add(title):
    with tempfile.NamedTemporaryFile(suffix='.md', delete=False) as tf:
        tf.write(('# %s\n' % title).encode())
        tf_path = tf.name
    cp = subprocess.run([EDITOR_APP, tf_path])
    if cp.returncode == 0:
        with open(tf_path) as f:
            description = f.read()
            title = description.split('\n')[0].split(' ')[1]
    else:
        description = ''
    row_id = todo.add(title, description)
    tempfiles[row_id] = tf_path # tempfileをキャッシュ
    return 'add: %s' % title

@app.command('edit', args=['task_id'], help='edit task')
def edit(task_id):
    task = todo.get(task_id)
    if not task:
        return '%s is not found.'

    if task.task_id in tempfiles:
        tempfile_path = tempfiles[task.task_id]
    else:
        with tempfile.NamedTemporaryFile(suffix='.md', delete=False) as tf:
            if task.description:
                tf.write(task.description.encode())
            else:
                tf.write(('# %s\n' % task.title).encode())
            tempfile_path = tf.name
    cp = subprocess.run([EDITOR_APP, tempfile_path])
    if cp.returncode == 0:
        with open(tempfile_path) as tf:
            description = tf.read()
            title = description.split('\n')[0].split(' ')[1]
        todo.update(task.task_id, title, description)
        tempfiles[task.task_id] = tempfile_path
        return 'update: %s' % title
    return 'update failed'

@app.command('done', args=['task_id'])
def done(task_id):
    task = todo.get(task_id)
    if not task:
        return '%s is not found.'

    todo.done(task_id)
    return 'done: %s' % task.title

@app.set_clean_up()
def clean_up():
    con.commit()
    con.close()

    for path in tempfiles.values():
        os.unlink(path)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'table':
        con = sqlite3.connect(str(DATABASE))
        cur = con.cursor()
        cur.execute(TABLES)
        con.commit()
        con.close()
    else:
        app.run()

