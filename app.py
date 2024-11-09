from functools import wraps
import re
from typing import Literal
from flask import Flask, render_template, request, url_for, flash, redirect
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash

from database.custom_database import DatabaseConnector
from database.FlaskUser import User
from database.custom_exceptions import InvalidTicketError, TicketExistsError

# Create a database connection
db = DatabaseConnector('database/database.db')

db.connect()

# Create a Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Create a login manager for flask-login
login_manager = LoginManager(app=app)


def fprint(*args, **kwargs):
    print(*args, **kwargs)
    flash(*args, **kwargs)


def db_auto_connect(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        db.connect()
        try:
            ret_val = func(*args, **kwargs)
        finally:
            db.close()
        return ret_val
    return wrapper


@login_manager.user_loader
@db_auto_connect
def load_user(user_id: int) -> User | None:
    """Loads the user into the browser session
    
    Parameters
    ----------
    user_id: str
        User id of the user in the database
    
    
    Returns
    -------
    User | None
        User object if the user exists, None otherwise
    """
    return User.get(db, user_id)


@app.route('/')
@db_auto_connect
def index():
    sort_by = request.args.get('sort_by', 'created')
    order = request.args.get('order', 'asc')

    ticket_lst = list(map(dict, db.get_all_tickets(sort_by, order)))
    
    for ticket in ticket_lst:
        ticket['owner_email'] = db.get_user_by_id(ticket['user_id'])['email']

    return render_template('index.html', tickets=ticket_lst, sort_by=sort_by, order=order)



@app.route('/ticket/create', methods=('GET', 'POST'))
@login_required
@db_auto_connect
def create_ticket():
    if request.method == 'GET':
        return render_template('create_ticket.html')
    
    # POST request
    try:
        db.create_a_ticket(current_user.id, **request.form)
        
    except TicketExistsError:
        fprint('Ticket with the same title already exists!')
        return render_template('create_ticket.html')
        
    except InvalidTicketError:
        fprint('Title is required!')
        return render_template('create_ticket.html')
    
    return redirect(url_for('index'))


@app.route('/ticket/<int:ticket_id>')
@db_auto_connect
def ticket(ticket_id):
    ticket = db.get_ticket(ticket_id)
    
    # Add the owner email to the ticket
    ticket = dict(ticket)
    ticket['owner_email'] = db.get_user_by_id(ticket['user_id'])['email']
        
    return render_template('ticket.html', ticket=ticket)



@app.route('/ticket/<int:id>/edit', methods=('GET', 'POST'))
@login_required
@db_auto_connect
def edit(id):
    ticket = db.get_ticket(id)
    
    if request.method == 'GET':
        # Check that the user is the owner of the ticket
        if ticket['user_id'] != current_user.id:
            fprint('You are not the owner of this ticket!')
            return redirect(url_for('index'))
        
        return render_template('edit.html', ticket=ticket)
        
    db.update_ticket(id, **request.form)
    return redirect(url_for('index'))
        



@app.route('/ticket/<int:id>/delete', methods=('POST',))
@login_required
@db_auto_connect
def delete(id):
    ticket = db.get_ticket(id)
    
    # Check that the user is the owner of the ticket
    if ticket['user_id'] != current_user.id:
        fprint('You are not the owner of this ticket!')
    
    else:
        db.delete_ticket(id)
        fprint(f'Ticket with title {ticket["title"]!r} deleted successfully!')
        
    return redirect(url_for('index'))


@app.route('/register', methods=('GET', 'POST'))
@db_auto_connect
def register():
    match request.method:
        case 'POST':
            email = request.form['email']
            password = request.form['password']
            role: Literal['user', 'admin'] = request.form.get('role', 'user')  # type: ignore

            if not email or not password:
                fprint('Email and password are required!')
            else:
                user_id = db.create_a_user(email, password, role)
                fprint('User created successfully!')
                
                login_user(User(user_id, email, role))
                return redirect(url_for('index'))
            
        case 'GET':
            print('Nothing to GET from here')
            pass

    return render_template('register.html')


@app.route('/login', methods=('GET', 'POST'))
@db_auto_connect
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user_row = db.get_user_by_email(email)

        if user_row and check_password_hash(user_row['password'], password):
            user = User(user_row['id'], user_row['email'], user_row['role'])
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password!')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))




if __name__ == '__main__':
    app.run(debug=True)
