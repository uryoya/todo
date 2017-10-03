"""ToDo Model."""
import sqlite3
import datetime

from pathlib import Path


DATABASE = Path().home()/'.config'/'todo'/'_todo.sqlite3'
TABLES = """
create table tasks (
    task_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT,
    description TEXT,
    create_at   TIMESTAMP,
    update_at   TIMESTAMP,
    done        INTEGER
)
"""


class Task:
    def __init__(self, task_id, title, description, create_at, update_at, done):
        self.task_id = task_id
        self.title = title
        self.description = description
        self.create_at = create_at
        self.update_at = update_at
        self.done = done

class ToDo:
    def __init__(self, cursor):
        """ToDo Constractor.
        cursor: sqlite cursor
        """
        self.cur = cursor

    def add(self, title, description):
        """Add new task to DB."""
        title = str(title)
        description = str(description)
        now = datetime.datetime.now()
        query = 'INSERT INTO tasks(title, description, create_at, update_at, done) VALUES (?, ?, ?, ?, ?);'
        self.cur.execute(query, (title, description, now, now, False))
        row_id = self.cur.execute('select last_insert_rowid();').fetchone()[0]
        return row_id

    def get(self, task_id):
        """Get task from task_id."""
        query = 'SELECT * FROM tasks WHERE task_id=?;'
        try:
            # task_id = int(task_id)
            task = self.cur.execute(query, (task_id,)).fetchone()
        except ValueError as err:
            # raise ValueError('`task_id` must be int')
            raise err
        except sqlite3.DatabaseError as err:
            raise err
        return Task(*task) if task else None

    def getall(self, done=False):
        """Get all tasks."""
        query = 'SELECT * FROM tasks WHERE done=?;'
        tasks = self.cur.execute(query, (done,)).fetchall()
        return [Task(*task) for task in tasks]

    def update(self, task_id, title, description):
        query = 'UPDATE tasks SET title=?, description=?, update_at=? WHERE task_id=?;'
        self.cur.execute(query, (title, description, datetime.datetime.now(), task_id))

    def done(self, task_id):
        """Task as done."""
        query = 'UPDATE tasks SET done=? WHERE task_id=?;'
        try:
            task_id = int(task_id)
            self.cur.execute(query, (True, task_id))
        except ValueError:
            raise ValueError('`task_id` must be int')
        except sqlite3.DatabaseError as err:
            raise err

        # 型がほしいよぉ...
