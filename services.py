import psycopg2
import random
from psycopg2 import Error
from psycopg2.extensions import (
    connection as Connection,
    cursor as Cursor
)
from config import (
    USER,
    PASSWORD,
    HOST,
    PORT,
)


class Connection:
    """Class for working to DataBase"""

    def __init__(self) -> None:
        try:
            self.connection: Connection = psycopg2.connect(
                user=USER,
                password=PASSWORD,
                host=HOST,
                port=PORT,
                database="flask_db"
            )
            print("[INFO] Connection is successful")
        except (Exception, Error) as e:
            print("{0} [ERROR] Connection to database is bad:".format(
                e
            ))

    def __new__(cls: type[any]) -> any:
        if not hasattr(cls, 'instance'):
            cls.instance = super(Connection, cls).__new__(cls)
        return cls.instance

    # func of creating tables (game, genre, game_genre(third table with game.id, genre.id))
    def create_tables(self) -> None:
        with self.connection.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS customer (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(10) NOT NULL UNIQUE,
                    balance FLOAT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS game (
                   id SERIAL PRIMARY KEY,
                   title TEXT NOT NULL,
                   year_production VARCHAR NOT NULL,
                   price FLOAT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS genre(
                    id SERIAL PRIMARY KEY,
                    genre TEXT NOT NULL,
                    description TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS game_code(
                    id SERIAL PRIMARY KEY,
                    is_active BOOLEAN DEFAULT TRUE,
                    code TEXT NOT NULL,
                    id_code INTEGER REFERENCES game(id)
                );
                CREATE TABLE IF NOT EXISTS game_genre
                (
                    game_id INTEGER REFERENCES game(id),
                    genre_id INTEGER REFERENCES genre(id),
                    CONSTRAINT game_genre_pk PRIMARY KEY (game_id, genre_id)
                );
                """)
        self.connection.commit()
        print("[INFO] Tables is created")

    # function which returning all elements from genre table
    def get_all_genres(self) -> list[tuple]:
        with self.connection.cursor() as cur:
            cur.execute('SELECT * FROM genre;')
            select_genre: list[tuple] = cur.fetchall()
        self.connection.commit()
        return select_genre

    # function which returning data from three tables (game, genre, game_genre)
    def all_connected_tables(self) -> list[tuple]:
        with self.connection.cursor() as cur:
            cur.execute("""SELECT game.id, game.price, game.title, game.year_production, genre.genre, 
            genre.description, game_code.code, game_code.is_active FROM game 
            LEFT JOIN game_genre ON game_genre.game_id=game.id 
            LEFT JOIN genre ON game_genre.genre_id = genre.id
            LEFT JOIN game_code ON game_code.id = game.id;""")
            data: list[tuple] = cur.fetchall()
        self.connection.commit()
        return data

    # function which returning all elements from game table
    def get_all_games(self) -> list[tuple]:
        with self.connection.cursor() as cur:
            cur.execute('SELECT * FROM game;')
            select_game: list[tuple] = cur.fetchall()
        self.connection.commit()
        return select_game

    # selecting only genre with id from genre table
    def select_genre_items(self) -> list[tuple]:
        with self.connection.cursor() as cur:
            cur.execute('SELECT genre.genre, genre.id FROM genre;')
            genre_items: list[tuple] = cur.fetchall()
        self.connection.commit()
        return genre_items

    # inserting into table game values (new_game, year of production of a new game), returns last id
    def insert_game_to_db(self, game_title, year_production, price) -> tuple:
        with self.connection.cursor() as cur:
            cur.execute(f"""
                INSERT INTO game (title, year_production, price) 
                VALUES ('{game_title}','{year_production}', '{price}') RETURNING ID;
            """)
            game_id = cur.fetchone()
            return game_id

    # generating code to game and adding to database
    def generate_code(self, game_id):
        generated_code = 'JDF' + str(random.randint(1000, 9999)) + 'DFSDF' + str(random.randint(100, 999))
        with self.connection.cursor() as cur:
            cur.execute(f"""
                INSERT INTO game_code (is_active, code, id_code) VALUES (TRUE,'{generated_code}', '{game_id}');
            """)
            self.connection.commit()

    # function inserting into table (game_genre) new elements (new game id, title)
    def insert_game_genre(self, new_game_id, title) -> None:
        with self.connection.cursor() as cur:
            cur.execute(f"""
               INSERT INTO game_genre VALUES ('{new_game_id}','{title}'); 
            """)
            self.connection.commit()

    # function inserting into table genre new elements (genre, description)
    def insert_items_to_genre(self, genre, description) -> None:
        with self.connection.cursor() as cur:
            cur.execute(f"""
                INSERT INTO genre (genre, description) VALUES ('{genre}', '{description}');
            """)
            self.connection.commit()

    # function showing all users with balance in database
    def select_user_from_database(self) -> list[tuple]:
        with self.connection.cursor() as cur:
            cur.execute('SELECT customer.id, customer.username, customer.balance FROM customer;')
            user_items: list[tuple] = cur.fetchall()
        self.connection.commit()
        return user_items

    # function add user with balance to database (username, balance)
    def add_user_to_database(self, username, balance) -> None:
        with self.connection.cursor() as cur:
            cur.execute(f"""
                INSERT INTO customer (username, balance) VALUES ('{username}', '{balance}');
            """)
            self.connection.commit()

    # function checking username in database
    def username_check(self, username) -> list[tuple]:
        with self.connection.cursor() as cur:
            cur.execute(f"""SELECT username FROM customer WHERE username='{username}';""")
            user_check: list[tuple] = cur.fetchone()
        self.connection.commit()
        return user_check

    # function showing user's money
    def username_money(self, username) -> list[tuple]:
        with self.connection.cursor() as cur:
            cur.execute(f"""SELECT balance FROM customer WHERE username='{username}';""")
            user_check: list[tuple] = cur.fetchone()
        self.connection.commit()
        return user_check

    # funtion showing all games to current user
    def showing_games(self) -> list[tuple]:
        with self.connection.cursor() as cur:
            cur.execute("""
            SELECT game.title, genre, genre.description, game.price FROM game 
            LEFT JOIN game_genre ON game_genre.game_id = game.id
            LEFT JOIN genre ON game_genre.genre_id = genre.id;
            """)
            all_games: list[tuple] = cur.fetchall()
        self.connection.commit()
        return all_games

    # transaction with user money
    def buying_game(self, user, game_price) -> None:
        with self.connection.cursor() as cur:
            cur.execute(f"""
            BEGIN;
            UPDATE customer SET balance = balance - {game_price}
                WHERE username = '{user}';
            SAVEPOINT my_savepoint;
            COMMIT;
            """)
        self.connection.commit()

    # showing user game key
    def showing_key(self, game) -> list[tuple]:
        with self.connection.cursor() as cur:
            cur.execute(f"""
            SELECT game.id, game.title, game_code.code FROM game LEFT JOIN game_code ON game_code.id_code = game.id 
            WHERE game.title = '{game}'
            """)
            show_key: list[tuple] = cur.fetchall()
        self.connection.commit()
        return show_key

    # function changing game key to false, if user bought game
    def changing_game_key_status(self, game_id) -> None:
        with self.connection.cursor() as cur:
            cur.execute(f"""
            BEGIN;
            UPDATE game_code SET is_active = FALSE
                WHERE id_code = '{game_id}';
            SAVEPOINT game_key_savepoint;
            COMMIT;
            """)
        self.connection.commit()

    # function writing game key to txt file
    def writing_game_key(self, game, game_key):
        with open(r"game_key.txt", "w") as file:
            file.writelines('Your key from store v.1.0 ' + '\n'
                            + '---------------' + '\n' + 'Game Title: ' + '\n'
                            + game + '\n' + 'Game Key: ' + '\n' + game_key + '\n' + '---------------')
