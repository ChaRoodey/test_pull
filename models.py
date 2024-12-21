import sqlite3
from dataclasses import dataclass
from typing import List, Optional

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


@dataclass
class Book:
    title: str
    author_id: int
    id: Optional[int] = None
    view_counter: Optional[int] = 0

    def __getitem__(self, item):
        return getattr(self, item)


@dataclass
class Author:
    first_name: str
    last_name: str
    author_id: Optional[int] = None
    middle_name: Optional[str] = None


@dataclass
class AuthorWithBooks:
    author: Author
    books: list[Book]


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


def _get_book_obj_from_row(row) -> Book:
    return Book(id=row[0], title=row[1], author_id=row[2], view_counter=row[3])


def _get_author_obj_from_row(row) -> Author:
    return Author(author_id=row[0], first_name=row[1], last_name=row[2], middle_name=row[3])


def get_all_books() -> List[Book]:
    with sqlite3.connect('table_books_3.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM table_books')
        all_books = cursor.fetchall()
        return [_get_book_obj_from_row(row) for row in all_books]


def add_book(book: Book) -> Book:
    try:
        with sqlite3.connect('table_books_3.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO 'table_books' (title, author_id, view_counter) VALUES (?, ?, 0)",
                (book.title, book.author_id)
            )
            book.id = cursor.lastrowid
            book.view_counter = 0
            return book

    except sqlite3.Error as e:
        print(f"Database error: {e}")


def get_book_by_id(book_id: int) -> Optional[Book]:
    with sqlite3.connect('table_books_3.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM table_books WHERE id = ?', (book_id, ))
        book = cursor.fetchone()
        if book:
            view_count = book[-1]
            cursor.executescript(
                f'UPDATE table_books '
                f'SET "view_counter" = {view_count + 1} '
                f'WHERE "id" = {book_id};'
            )
            return _get_book_obj_from_row(book)


def update_book_by_id(book: Book) -> None:
    with sqlite3.connect('table_books_3.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"""
            UPDATE table_books 
            SET title = ?, 
                author_id = ? 
            WHERE id = ?;
            """, (book.title, book.author_id, book.id)
        )
        conn.commit()


def delete_book_by_id(book_id: int) -> None:
    with sqlite3.connect('table_books_3.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"""
                    DELETE FROM table_books 
                    WHERE id = ?;
                """, (book_id, )
        )
        conn.commit()


def get_books_by_author_id(author_id: int) -> Optional[List[Book]]:
    with sqlite3.connect('table_books_3.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM table_books WHERE author_id = ?', (author_id, ))
        books = cursor.fetchall()
        if books:
            return [_get_book_obj_from_row(book) for book in books]

        return None


def add_author(author: Author) -> Author:
    try:
        with sqlite3.connect('table_books_3.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO 'table_authors' (first_name, last_name, middle_name) VALUES (?, ?, ?)",
                (author.first_name, author.last_name, author.middle_name)
            )
            author.author_id = cursor.lastrowid
            return author

    except sqlite3.Error as e:
        print(f"Database error: {e}")


def get_author_by_id(author_id: int) -> Optional[Author]:
    with sqlite3.connect('table_books_3.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM table_authors WHERE author_id = ?', (author_id, ))
        author = cursor.fetchone()
        if author:
            return _get_author_obj_from_row(author)

        return None


def delete_author_and_books_by_author_id(author_id: int) -> None:
    with sqlite3.connect('table_books_3.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"""
                    DELETE FROM table_books 
                    WHERE author_id = ?;
                """, (author_id, )
        )
        conn.commit()
        cursor.execute(
            f"""
                    DELETE FROM table_authors 
                    WHERE author_id = ?;
                """, (author_id,)
        )
        conn.commit()
