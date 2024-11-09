import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort


def get_db_connection():
    conn = sqlite3.connect('database/database.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM tickets WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post

app = Flask(__name__)

app.config['SECRET_KEY'] = 'your secret key'


@app.route('/')
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM tickets').fetchall()
    conn.close()
    print(f"Number of posts fetched: {len(posts)}")
    if request.args.get('query'):
        query = request.args.get('query')
        posts = [post for post in posts if query.lower() in str(post).lower()]
    return render_template('index.html', posts=posts)


@app.route('/search', methods=['GET', 'POST'])
def search():
    query = ''
    results = []

    if request.method == 'POST':
        query = request.form['query']
        conn = get_db_connection()
        results = conn.execute('SELECT * FROM tickets WHERE title LIKE ? OR development_proposal LIKE ?', 
                               ('%' + query + '%', '%' + query + '%')).fetchall()
        conn.close()

    return render_template('index.html', posts=results, query=query)


@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    return render_template('post.html', post=post)

@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        content_clarification = request.form['content_clarification']
        
        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO tickets (title, development_proposal, development_clarification) VALUES (?, ?, ?)',
                         (title, content, content_clarification))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
    
    return render_template('create.html')

@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        status = request.form.get('status', 'untagged')
        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE tickets SET title = ?, development_proposal = ?, status = ? WHERE id = ?', 
                         (title, content, status, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('edit.html', post=post)



@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    post = get_post(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
