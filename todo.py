"""ToDo application for CLI."""
import datetime
import json
import sqlite3
import subprocess
import sys
import tempfile

from pathlib import Path

DATABASE = '_todo.sqlite3'
TABLES = """
create table tasks (
    task_id     INT PRIMARY KEY,
    title       VARCHAR(100),
    description TEXT,
    create_at   TIMESTAMP,
    update_at   TIMESTAMP,
    done        BOOL
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

    def add_command(self, command, func, options=[]):
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
                    result = func(**options)
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


@app.command('list')
def list():
    cur.execute('SELECT * FROM `tasks`;')
    tasks = cur.fetchall()
    # return '\n'.join([task for task in tasks])
    return tasks

@app.command('show')
def show():
    return 'not implement'

@app.command('add')
def add():
    return 'not implement'

@app.command('edit')
def edit():
    return 'not implement'

@app.command('done')
def done():
    return 'not implement'

@app.set_clean_up()
def clean_up():
    con.commit()
    con.close()

def main():
    todo_file = Path('./todo.json').absolute()
    if todo_file.exists():
        with todo_file.open('r') as json_f:
            todo = [dict2task(t) for t in json.load(json_f)]
    else:
        todo = []

    while True:
        command, *args = input('> ').split(' ')
        if command == 'list':
            for idx, task in enumerate(todo):
                print(idx+1, task.title)
        elif command == 'show':
            for idx, task in enumerate(todo):
                print(idx+1, task.title)
                print(task.description)
                print()
        elif command == 'add':
            title = ' '.join(args)
            with tempfile.NamedTemporaryFile(suffix='.md', delete=False) as tf:
                tf.write(('# %s\n' % title).encode())
                tf_path = tf.name
            cp = subprocess.run(['editor', tf_path])
            if cp.returncode == 0:
                with open(tf_path) as f:
                    description = f.read()
            else:
                description = ''
            todo.append(Task(title, description, temp_file=tf_path))
        elif command == 'edit':
            idx = int(args[0]) - 1
            if len(todo) < idx + 1:
                print('not found: %d' % (idx + 1))
                continue
            if not todo[idx].temp_file:
                with tempfile.NamedTemporaryFile(suffix='.md', delete=False) as tf:
                    if todo[idx].description:
                        tf.write(todo[idx].description.encode())
                    else:
                        tf.write(('# %s\n' % todo[idx].title).encode())
                    todo[idx].temp_file = tf.name
            cp = subprocess.run(['editor', todo[idx].temp_file])
            if cp.returncode == 0:
                with open(todo[idx].temp_file) as f:
                    description = todo[idx].description = f.read()
                    todo[idx].title = description.split('\n')[0].split(' ')[1]
            else:
                pass
        elif command == 'done':
            idx = int(args[0]) - 1
            try:
                del todo[idx]
            except IndexError:
                print('not found: %d' % (idx + 1))
        elif command == 'quit':
            break
        elif command == 'help':
            print(_help())
        else:
            print(_help())

    with todo_file.open('w') as json_f:
        json.dump([task2dict(task) for task in todo], json_f)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'table':
        con = sqlite3.connect(DATABASE)
        cur = con.cursor()
        cur.execute(TABLES)
        con.commit()
        con.close()
    else:
        app.run()

