from dataclasses import asdict
from flask import Flask, request
from marshmallow import ValidationError
from schemas import BookSchema, AuthorSchema
from flask_restx import Api, Resource, abort
from models_2 import (
    Book,
    Author,
    AuthorWithBooks,
    add_book,
    add_author,
    get_all_books,
    get_author_by_id,
    update_book_by_id,
    delete_book_by_id,
    get_books_by_author_id,
    delete_author_and_books_by_author_id
)


app = Flask(__name__)
api = Api(app)


@api.route('/api/books')
class BookList(Resource):
    def get(self):
        return {'data': [asdict(book) for book in get_all_books()]}, 200

    def post(self):
        data = request.json
        schema = BookSchema()

        try:
            book = schema.load(data)
        except ValidationError as exc:
            return exc.messages, 400

        book = add_book(Book(**data))
        return schema.dump(book), 201


@api.route('/api/books/<int:book_id>')
class BookList(Resource):
    def put(self, book_id):
        data = request.json

        update_book_by_id(Book(id=book_id, **data))
        return {'status': 'updated'}, 201

    def patch(self, book_id):
        data = request.json

        book = add_book(Book(id=book_id, **data))
        return asdict(book), 201

    def delete(self, book_id):
        delete_book_by_id(book_id)
        return {'status': 'deleted'}, 201


@api.route('/api/authors/<int:author_id>')
class AuthorsList(Resource):
    def get(self, author_id):
        author = get_author_by_id(author_id)
        if not author:
            abort(404, message=f"Author with ID {author_id} not found.")

        books = get_books_by_author_id(author_id)

        author_with_books = AuthorWithBooks(author=author, books=books)

        return asdict(author_with_books), 200

    def post(self, author_id):
        data = request.json
        schema = AuthorSchema()

        try:
            author = schema.load(data)
        except ValidationError as exc:
            return exc.messages, 400

        author = add_author(Author(**data))
        return schema.dump(author), 201

    def delete(self, author_id):
        delete_author_and_books_by_author_id(author_id)
        return {'status': 'deleted'}, 201


if __name__ == '__main__':
    app.run(debug=True)
