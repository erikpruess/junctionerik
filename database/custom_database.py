import sqlite3
from os.path import isfile
from typing import Literal

from custom_exceptions import (
    InvalidTicketError,
    UserExistsError,
    UserNotExistError,
    TicketExistsError
)





class DatabaseConnector:
    def __init__(self, db_path: str):
        if not isfile(db_path):
            raise FileNotFoundError(f'Database file not found at {db_path!r}')
        
        self._db_path = db_path
        
        self.connect()
        
    
    def connect(self) -> None:
        """Connects to the database"""
        self._conn = sqlite3.connect(self._db_path)
        self._conn.row_factory = sqlite3.Row
        self._cursor = self._conn.cursor()
        print(f'Connected to {self._db_path!r}')
        
        
    def close(self) -> None:
        """Closes the database connection"""
        self._conn.close()
        print('Connection closed')
        
        
    def _query(self, query: str, *args) -> sqlite3.Cursor:
        """Quoeies the database and returns the cursor
        
        Parameters
        ----------
        query : str
            The query to be executed
        *args : tuple
            The arguments to be passed to the query
            
        Returns
        -------
        sqlite3.Cursor
            The cursor object
        """
        return self._cursor.execute(query, *args)
    
    
    def _fetch_one(self, query: str, *args) -> sqlite3.Row:
        """Fetches one row from the database
        
        Parameters
        ----------
        query : str
            The query to be executed
        *args : tuple
            The arguments to be passed to the query
        
        Returns
        -------
        sqlite3.Row
            The row object
        """
        return self._query(query, *args).fetchone()
    
    
    def fetch_all(self, query: str, *args) -> list[sqlite3.Row]:
        """Fetches all the rows from the database
        
        Parameters
        ----------
        query : str
            The query to be executed
        *args : tuple
            The arguments to be passed to the query
        
        Returns
        -------
        list[sqlite3.Row]
            A list of sqlite3.Row objects
        """
        return self._query(query, *args).fetchall()
    
    
    def _commit(self, query: str, *args) -> None:
        """Commits the query to the database
        
        Parameters
        ----------
        query : str
            The query to be executed
        *args : tuple
            The arguments to be passed to the query
        """
        self._query(query, *args)
        self._conn.commit()
        
    
    def get_all_tickets(self) -> list[sqlite3.Row]:
        """Returns all the tickets in the database
        
        Returns
        -------
        list[sqlite3.Row]
            A list of sqlite3.Row objects
        """
        return self._query('SELECT * FROM tickets').fetchall()
    
    
    def create_a_user(self, email: str, password: str, role: Literal['user', 'admin'] = 'user') -> int:
        """Creates a new user in the database
        
        Parameters
        ----------
        email : str
            The email of the user
        password : str
            The password of the user
        role : Literal['user', 'admin'], optional
            The role of the user, by default 'user'
        
        Raises
        ------
        UserExistsError
            If the user already exists
        ValueError
            If the email is not valid
        """
        if self._fetch_one('SELECT * FROM users WHERE email = ?', (email,)):
            raise UserExistsError(f'User with email: {email!r} already exists')
        
        # Raise an error if the email does not contain '@'
        if '@' not in email:
            raise ValueError('Email is not valid')
        
        # Add user to database
        self._commit('INSERT INTO users (email, password, role) VALUES (?, ?, ?)', (email, password, role))
        print(f'User created: {email!r}')
        
        # Return the user id
        return self._fetch_one('SELECT id FROM users WHERE email = ?', (email,))['id']
    
    
    def create_a_ticket(self, user_id: int, **kwargs) -> None:
        """Create a new ticket in the database
        
        Parameters
        ----------
        user_id : int
            The id of the user
        **kwargs
            The ticket details
        
        Raises
        ------
        UserNotExistError
            If the user does not exist
        TicketExistsError
            If the ticket already exists
        InvalidTicketError
            If the title is not provided
        """
        _title = kwargs.get('title')
        
        # Raise an error if the title is not provided
        if not _title:
            raise InvalidTicketError('Title is required')
        
        # Raise an error if the user does not exist
        elif not self._fetch_one('SELECT * FROM users WHERE id = ?', (user_id,)):
            raise UserNotExistError(f'User not found for id: {user_id}')
        
        # Raise an error if the ticket already exists
        elif self._fetch_one('SELECT * FROM tickets WHERE title = ?', (_title,)):
            raise TicketExistsError(f'Ticket with title: {_title!r} already exists')
        
        # Save the ticket to the database
        self._commit(
            'INSERT INTO tickets (user_id, title, status, development_proposal, development_clarifiacation, release_date, functional_area, ball_park_estimate, impact_on_market, product_improvement, priority, comment, next_steps) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', # noqa
            (
                user_id,
                _title,
                kwargs.get('status', 'open'),
                kwargs.get('development_proposal'),
                kwargs.get('development_clarification'),
                kwargs.get('release_date'),
                kwargs.get('functional_area'),
                kwargs.get('ball_park_estimate'),
                kwargs.get('impact_on_market'),
                kwargs.get('product_improvement'),
                kwargs.get('priority', 'low'),
                kwargs.get('comment'),
                kwargs.get('next_steps')
            )
        )
        print(f'Ticket {_title!r} created for user_id: {user_id}')
        
        
    def get_user_tickets(self, user_id: int) -> list[sqlite3.Row]:
        """Returns all the tickets for a user
        
        Parameters
        ----------
        user_id : int
            The id of the user
        
        Returns
        -------
        list[sqlite3.Row]
            A list of sqlite3.Row objects
        """
        return self.fetch_all('SELECT * FROM tickets WHERE user_id = ?', (user_id,))
    
    
    def get_ticket(self, ticket_id: int) -> sqlite3.Row:
        """Returns a ticket by id
        
        Parameters
        ----------
        ticket_id : int
            The id of the ticket
        
        Returns
        -------
        sqlite3.Row
            The ticket object
        """
        return self._fetch_one('SELECT * FROM tickets WHERE id = ?', (ticket_id,))
    
    
    def update_ticket(self, ticket_id: int, **kwargs) -> None:
        """Updates a ticket in the database
        
        Parameters
        ----------
        ticket_id : int
            The id of the ticket
        **kwargs
            The ticket details to be updated
        
        Raises
        ------
        InvalidTicketError
            If the title is not provided
        """
        _title = kwargs.get('title')
        
        # Raise an error if the title is not provided
        if not _title:
            raise InvalidTicketError('Title is required')
        
        # Update the ticket in the database
        self._commit(
            'UPDATE tickets SET title = ?, status = ?, development_proposal = ?, development_clarification = ?, release_date = ?, functional_area = ?, ball_park_estimate = ?, impact_on_market = ?, product_improvement = ?, priority = ?, comment = ?, next_steps = ? WHERE id = ?', # noqa
            (
                _title,
                kwargs.get('status', 'open'),
                kwargs.get('development_proposal'),
                kwargs.get('development_clarification'),
                kwargs.get('release_date'),
                kwargs.get('functional_area'),
                kwargs.get('ball_park_estimate'),
                kwargs.get('impact_on_market'),
                kwargs.get('product_improvement'),
                kwargs.get('priority', 'low'),
                kwargs.get('comment'),
                kwargs.get('next_steps'),
                ticket_id
            )
        )
        print(f'Ticket {_title!r} updated')
        
        
    def delete_ticket(self, ticket_id: int) -> None:
        """Deletes a ticket from the database
        
        Parameters
        ----------
        ticket_id : int
            The id of the ticket
        """
        self._commit('DELETE FROM tickets WHERE id = ?', (ticket_id,))
        print(f'Ticket with id: {ticket_id} deleted')
        
        
    def delete_user(self, user_id: int) -> None:
        """Deletes a user from the database
        
        Parameters
        ----------
        user_id : int
            The id of the user
        """
        self._commit('DELETE FROM users WHERE id = ?', (user_id,))
        print(f'User with id: {user_id} deleted')

    
    
    
    
if __name__ == '__main__':
    db = DatabaseConnector('database/database.db')
    
    db.create_a_user('test@mail.com', 'password')
    
    db.close()
