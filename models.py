import sqlite3
from typing import List
from flask_wtf import FlaskForm
from dataclasses import dataclass
from wtforms.validators import InputRequired
from wtforms.fields.simple import StringField

BOOK_DATA = [
    {'id': 0, 'title': 'A Byte of Python', 'author': 2},
    {'id': 1, 'title': 'Moby-Dick; or, The Whale', 'author': 1},
    {'id': 2, 'title': 'War and Peace', 'author': 3}
]

AUTHOR_DATA = [
    {'author_id': 0, 'first_name': 'Herman', 'last_name': 'Melville', 'middle_name': ''},
    {'author_id': 1, 'first_name': 'Swaroop', 'last_name': 'Chitlur', 'middle_name': ''},
    {'author_id': 2, 'first_name': 'Leo', 'last_name': 'Tolstoy', 'middle_name': 'Nikolayevich'}
]


class AddBookForm(FlaskForm):
    title_field = StringField(validators=[InputRequired()])
    author_first_field = StringField(validators=[InputRequired()])
    author_last_field = StringField(validators=[InputRequired()])
    author_middle_field = StringField()


@dataclass
class Book:
    id: int
    title: str
    author_id: int
    view_counter: int

    def __getitem__(self, item):
        return getattr(self, item)

    def get_author(self):
        with sqlite3.connect('table_books_3.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM table_authors WHERE author_id = ?', [self.author_id])
            author_name = cursor.fetchone()
            return f'{author_name[1]} {author_name[2]} {author_name[3]}'


@dataclass
class Author:
    author_id: int
    first_name: str
    last_name: int
    middle_name: int

    def __getitem__(self, item):
        return getattr(self, item)


def init_db(initial_records_books: List[dict], initial_records_authors: List[dict]) -> None:
    with sqlite3.connect('table_books_3.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master "
            "WHERE name = 'table_books';"
        )
        exists = cursor.fetchone()

        if not exists:
            cursor.executescript(
                "CREATE TABLE 'table_authors' "
                "(author_id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "first_name TEXT, "
                "last_name TEXT, "
                "middle_name TEXT)"
            )
            cursor.executemany(
                "INSERT INTO 'table_authors' "
                "(first_name, last_name, middle_name) VALUES (?, ?, ?)",
                [(item['first_name'], item['last_name'], item['middle_name']) for item in initial_records_authors]
            )
            cursor.executescript(
                "CREATE TABLE 'table_books' "
                "(id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "title TEXT, "
                "author_id INTEGER, "
                "view_counter INTEGER, "
                "FOREIGN KEY (author_id) REFERENCES table_authors(author_id)"
                "ON UPDATE CASCADE)"
            )
            cursor.executemany(
                "INSERT INTO 'table_books' "
                "(title, author_id, view_counter) VALUES (?, ?, 0)",
                [(item['title'], item['author']) for item in initial_records_books]
            )


def get_all_books() -> List[Book]:
    with sqlite3.connect('table_books_3.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM table_books')
        all_books = cursor.fetchall()
        return [Book(*row) for row in all_books]


def input_book(form) -> bool:
    try:
        with sqlite3.connect('table_books_3.db') as conn:
            first_name = form.author_first_field.data
            last_name = form.author_last_field.data
            middle_name = form.author_middle_field.data

            cursor = conn.cursor()
            cursor.execute('SELECT * FROM table_authors '
                           'WHERE first_name = ? '
                           'AND last_name = ? '
                           'AND middle_name = ?',
                           [first_name, last_name, middle_name])
            result = cursor.fetchone()

            if not result:
                cursor.execute(
                    "INSERT INTO 'table_authors' (first_name, last_name, middle_name) VALUES (?, ?, ?)",
                    [first_name, last_name, middle_name]
                )
                author_id = cursor.lastrowid
            else:
                author_id = result[0]

            cursor.execute(
                "INSERT INTO 'table_books' (title, author_id, view_counter) VALUES (?, ?, 0)",
                [form.title_field.data, author_id]
            )
        return True

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False


def get_book(book_id: int) -> Book:
    with sqlite3.connect('table_books_3.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM table_books WHERE id = ?', [book_id])
        book_data = cursor.fetchone()
        view_count = book_data[-1]
        cursor.execute(
            f'UPDATE table_books '
            f'SET "view_counter" = {view_count + 1} '
            f'WHERE "id" = {book_id};'
        )
        # book_data[-1] += 1
        return Book(*book_data)


if __name__ == '__main__':
    init_db(BOOK_DATA, AUTHOR_DATA)