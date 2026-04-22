from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

# Carpeta donde se guardarán imágenes
UPLOAD_FOLDER = 'static/img'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ------------------ DB ------------------

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            image TEXT
        )
    ''')
    conn.commit()
    conn.close()

create_table()

# ------------------ READ ------------------

@app.route('/')
def index():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template('index.html', products=products)

# ------------------ CREATE ------------------

@app.route('/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        stock = request.form['stock']

        file = request.files['image']
        filename = None

        if file and file.filename != '':
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO products (name, price, stock, image) VALUES (?, ?, ?, ?)',
            (name, price, stock, filename)
        )
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    return render_template('add_product.html')

# ------------------ UPDATE ------------------

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    conn = get_db_connection()

    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        stock = request.form['stock']

        file = request.files['image']
        filename = None

        if file and file.filename != '':
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            conn.execute(
                'UPDATE products SET name=?, price=?, stock=?, image=? WHERE id=?',
                (name, price, stock, filename, id)
            )
        else:
            conn.execute(
                'UPDATE products SET name=?, price=?, stock=? WHERE id=?',
                (name, price, stock, id)
            )

        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    product = conn.execute('SELECT * FROM products WHERE id=?', (id,)).fetchone()
    conn.close()

    return render_template('edit_product.html', product=product)

# ------------------ DELETE ------------------

@app.route('/delete/<int:id>')
def delete_product(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM products WHERE id=?', (id,))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

# ------------------ RUN ------------------

if __name__ == '__main__':
    app.run(debug=True)