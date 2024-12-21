from flask import Flask, render_template, request
from models import init_db, get_all_books, input_book, AddBookForm, get_book


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['WTF_CSRF_ENABLED'] = False
init_db([], [])


@app.route('/books')
def index():
    return render_template('index.html', books=get_all_books())


@app.route('/books/form', methods=['GET', 'POST'])
def get_books_form():
    if request.method == 'POST':
        form = AddBookForm()

        if form.validate_on_submit():
            if input_book(form):
                return render_template('success.html')
        else:
            return f'Validation form error', 500

    return render_template('add_book.html')


@app.route('/books/<int:book_id>')
def get_book_by_id(book_id: int):
    book_data = get_book(book_id)
    return render_template('single_book_by_id.html', book=book_data)


if __name__ == '__main__':
    app.run(debug=True)