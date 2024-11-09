from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort

from database.custom_database import DatabaseConnector


# def get_db_connection():
#     conn = sqlite3.connect('database.db')
#     conn.row_factory = sqlite3.Row
#     return conn

# def get_ticket(ticket_id):
#     conn = get_db_connection()
#     ticket = conn.execute('SELECT * FROM tickets WHERE id = ?',
#                         (ticket_id,)).fetchone()
#     conn.close()
#     if ticket is None:
#         abort(404)
#     return ticket

db = DatabaseConnector('database/database.db')

app = Flask(__name__)

app.config['SECRET_KEY'] = 'your secret key'


@app.route('/')
def index():
    db.connect()
    ret = render_template('index.html', tickets=db.get_all_tickets())
    db.close()
    
    return ret




@app.route('/ticket/create', methods=('GET', 'POST'))
def create():
    db.connect()
    
    print(request)
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        status = request.form.get('status', 'untagged')  # Default to 'untagged' if not provided
        
        if not title:
            flash('Title is required!')
        else:
            db.create_a_ticket(2, title=title, status=status, comment=content)
            return redirect(url_for('index'))
    
    db.close()
    
    return render_template('create.html')


@app.route('/ticket/<int:ticket_id>')
def ticket(ticket_id):
    db.connect()
    ret = render_template('ticket.html', ticket=db.get_ticket(ticket_id))
    db.close()
    return ret



@app.route('/ticket/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    db.connect()
    
    ticket = db.get_ticket(id)
    
    match request.method:
        case 'POST':
            title = request.form['title']
            comment = request.form['comment']
            status = request.form['status']
            
            if not title:
                flash('Title is required!')
            else:
                db.update_ticket(id, title=title, comment=comment, status=status)
                return redirect(url_for('index'))
            
        case 'GET':
            print('Nothing to GET from here')
            pass
        
        
    db.close()

    return render_template('edit.html', ticket=ticket)



@app.route('/ticket/<int:id>/delete', methods=('POST',))
def delete(id):
    db.connect()
    db.delete_ticket(id)
    flash(f'Ticket with id: {id} deleted')
    db.close()
    return redirect(url_for('index'))




if __name__ == '__main__':
    app.run(debug=True)
