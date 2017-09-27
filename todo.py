"""ToDo application for CLI."""
import datetime
import json
import sqlite3
import subprocess
import sys
import tempfile
import os

from pathlib import Path

DATABASE = '_todo.sqlite3'
TABLES = """
create table tasks (
    task_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    title       VARCHAR(100),
    description TEXT,
    create_at   TIMESTAMP,
    update_at   TIMESTAMP,
    done        INTEGER
)
"""


class Task:
    def __init__(self, title, description, create_at, update_at, done):
        self.title = title
        self.description = description
        self.create_at = create_at
        self.update_at = update_at
        self.done = done


class Command():
    def __init__(self):
        self.commands = dict()
        self.start_up = Command._start_up_stab
        self.clean_up = Command._clean_up_stub
        self.welcome_message = ''

    @staticmethod
    def _start_up_stab():
        pass

    @staticmethod
    def _clean_up_stub():
        pass

    def set_start_up(self):
        def decorator(func):
            self.start_up = func
            return func
        return decorator

    def set_clean_up(self):
        def decorator(func):
            self.clean_up = func
            return func
        return decorator

    def add_command(self, command, func, **options):
        self.commands[command] = (func, options)

    def command(self, command, **options):
        """Decorator for implement ToDo commands.
        USAGE:
        app = Command()
        
        @app.command('list')
        def list():
            return todo_list
        app.run()
        """
        def decorator(func):
            self.add_command(command, func, **options)
            return func
        return decorator

    def help(self):
        return 'help!'
    
    def run(self):
        self.start_up()
        if self.welcome_message:
            print(self.welcome_message)

        while True:
            command, *args = input('> ').split(' ')
            try:
                func, options = self.commands[command]
                if options:
                    # @app.command('command', args=[]) のargsで決めた引数だけ取り込む
                    # もう少し作り込めそうだけどとりあえずこれだけ
                    result = func(*args[:len(options)])
                else:
                    result = func()
                print(result)
            except KeyError:
                if command == 'quit':
                    break
                print(self.help()) # include command:'help'

        self.clean_up()
        print('Bye!')


con = sqlite3.connect(DATABASE)
cur = con.cursor()
app = Command()
app.welcome_message = 'Welcome to Japari Park!'
tempfiles = dict()


@app.command('list')
def list():
    tasks = cur.execute('SELECT title FROM tasks WHERE done = 0;').fetchall()
    return '\n'.join(['%d\t%s' % (idx+1, task[0]) for idx, task in enumerate(tasks)])

@app.command('show')
def show():
    tasks = cur.execute('''SELECT title, create_at, update_at, description
                        FROM tasks
                        WHERE done = 0;''').fetchall()
    template = '''================================================================================
Title: %s
Create: %s\tLast Update: %s
--------------------------------------------------------------------------------
%s
================================================================================
'''
    return ''.join(template % (task[0], task[1], task[2], task[3].rstrip())
                   for task in tasks)

@app.command('add', args=['title'])
def add(title):
    now = datetime.datetime.now()
    with tempfile.NamedTemporaryFile(suffix='.md', delete=False) as tf:
        tf.write(('# %s\n' % title).encode())
        tf_path = tf.name
    cp = subprocess.run(['editor', tf_path])
    if cp.returncode == 0:
        with open(tf_path) as f:
            description = f.read()
    else:
        description = ''
    cur.execute('INSERT INTO tasks(title, description, create_at, update_at, done) VALUES (?, ?, ?, ?, ?);',
                (title, description, now, now, False))
    row_id = cur.execute('select last_insert_rowid();').fetchone()[0]
    tempfiles[row_id] = tf_path # tempfileをキャッシュ
    return 'add: %s' % title

@app.command('edit', args=['task_id'])
def edit(task_id):
    try:
        task_id = int(task_id)
    except ValueError:
        return '%s is not found.' % task_id
    cur.execute('SELECT task_id, title, description FROM tasks WHERE task_id = (?);', (task_id,))
    task = cur.fetchone()
    if not task:
        return '%s is not found.'

    if task[0] not in tempfiles: # task_id not in tempfiles
        with tempfile.NamedTemporaryFile(suffix='.md', delete=False) as tf:
            if task[2]: # description
                tf.write(task[2].encode())
            else:
                tf.write(('# %s\n' % task[1]).encode()) # title
            tempfile_path = tf.name
    cp = subprocess.run(['editor', tempfile_path])
    if cp.returncode == 0:
        with open(tempfile_path) as tf:
            description = tf.read()
            title = description.split('\n')[0].split(' ')[1]
        cur.execute('UPDATE tasks SET title=?, description=?, update_at=? WHERE task_id=?;',
                    (title, description, datetime.datetime.now(), task[0]))
        tempfiles[task[0]] = tempfile_path
        return 'update: %s' % title
    return 'update failed'

@app.command('done')
def done():
    return 'not implement'

@app.set_clean_up()
def clean_up():
    con.commit()
    con.close()

    for path in tempfiles.values():
        os.unlink(path)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'table':
        con = sqlite3.connect(DATABASE)
        cur = con.cursor()
        cur.execute(TABLES)
        con.commit()
        con.close()
    else:
        app.run()

