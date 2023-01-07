from flask import Flask, render_template, request, flash, redirect, url_for, abort
from services import Connection


app = Flask(__name__)
conn: Connection = Connection()
conn.create_tables()
app.config['SECRET_KEY'] = 'your secret key'


@app.route('/', methods=['POST', 'GET'])
def login():
    select_all = conn.all_connected_tables()
    return render_template('login.html', title='Homework', select_all=select_all)

@app.route('/game_create', methods=['POST', 'GET'])
def add_game():
    select_game = conn.get_all_games()
    genre_data = conn.select_genre_items()
    row = [item[0] for item in genre_data]
    if request.method == 'POST':
        game_title = request.form["title"]
        year_production = request.form["year"]
        game_price = float(request.form["price"])
        game_genre = request.form.get('name')
        if game_title and year_production.isnumeric() and game_genre and type(game_price) == float:
            title_id = ''
            for i in genre_data:
                if game_genre in i:
                    title_id += str(i[1])
            flash(f'Game {game_title} with {float(game_price)}$ price added to database', 'info')
            new_game_id = conn.insert_game_to_db(game_title, year_production, float(game_price))
            conn.insert_game_genre(new_game_id[0], title_id)
            # generating code for added game
            conn.generate_code(new_game_id[0])
        else:
            flash('Please fill in all fields and select a genre!', 'info')
        return render_template('game_create.html', select_from_data=select_game, select_genre=row)
    return render_template('game_create.html', select_from_data=select_game, select_genre=row)

@app.route('/genre_create', methods=['POST', 'GET'])
def add_genre():
    all_genre = conn.get_all_genres()
    game_genre = [
        ('action',
         'challenges by physical means such as precise aim and quick response times.'),
        ('horror',
         'painful feeling caused by something frightfully shocking, terrifying and shuddering fear'),
        ('MMORPG',
         'combines aspects of a role-playing video game and a massively multiplayer online game.'),
        ('fighting', 'is a genre of video game that involves combat between two or more players.'),
        ('sports', 'is a video game that simulates the practice of sports.'),
        (
        'stealth', 'type of video game in which the player uses stealth to avoid or overcome opponents'),
        ('puzzle', 'make up a broad genre of video games that emphasize puzzle solving.')
    ]
    game_title = [i[0] for i in game_genre]
    text = ''
    if request.method == 'POST':
        genre = request.form.get('name')
        if genre:
            for i in game_genre:
                if genre in i:
                    text += i[1]
            conn.insert_items_to_genre(genre, text)
            flash(f'Genre added to database', 'info')
        else:
            flash('Please select genre to add!', 'info')
    return render_template('genre_create.html', select_from_data=all_genre, new_genre=game_title)

@app.route('/user_create', methods=['POST', 'GET'])
def add_user():
    all_users = conn.select_user_from_database()
    if request.method == 'POST':
        username = request.form.get('username')
        balance = float(request.form.get('balance'))
        if username and type(balance) == float:
            if balance <= 0:
                flash(f'This entered value - {balance} is incorrect!', 'info')
            else:
                conn.add_user_to_database(username, balance)
                flash(f'User {username} with {balance}$ on account is added to database', 'info')
        else:
            flash('Please enter username with balance', 'info')
        return render_template('user_create.html', select_from_data=all_users)
    return render_template('user_create.html', select_from_data=all_users)

@app.route('/user_login', methods=['POST', 'GET'])
def user_login():
    if request.method == 'POST':
        username = request.form.get('username')
        global user_check
        user_check = conn.username_check(username)
        if user_check:
            return redirect(url_for('store'))
        else:
            abort(401)
    return render_template('user_login.html')

@app.route('/store', methods=['POST', 'GET'])
def store():
    current_user = user_check[0]
    user_balance = conn.username_money(current_user)
    showing_all_games = conn.showing_games()
    list_games = conn.get_all_games()
    if request.method == 'POST':
        choose_game = request.form.get('game')
        #from tuple with game info. we choosing and writing price for selected game
        game_price = ''
        for i in showing_all_games:
            if choose_game in i:
                game_price += str(i[3])
        if choose_game:
            if user_balance[0] < float(game_price):
                flash(f"You haven't got enought money!", 'info')
            else:
                conn.buying_game(current_user, game_price)
                show_key = conn.showing_key(choose_game)
                flash(
                    f'User {current_user} with {user_balance[0]}$ on account, bought game {choose_game} | {game_price}$',
                    'info')
                flash(f'Your game key is - {show_key[0][2]} . Game key saved on your PC.', 'info')
                conn.writing_game_key(choose_game, show_key[0][2])
                conn.changing_game_key_status(show_key[0][0])
    return render_template('store.html', user=current_user, balance=user_balance[0],
                           all_games=showing_all_games, games=[i[1] for i in list_games])


if __name__ == '__main__':
    app.run(port=8080, debug=True)
