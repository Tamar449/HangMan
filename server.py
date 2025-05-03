import json
import random
from functools import wraps

from User import User

from flask import Flask, jsonify, request, make_response

from flask_cors import CORS

app = Flask(__name__)

CORS(app, supports_credentials=True)

# global variables
users = []
counter = -1
words = []


def save_data():
    global users, counter, words
    data = {'users': users, 'counter': counter, 'words': words}
    with open('./data.json', 'w') as f:
        json.dump(data, f, default=save_default)


def save_default(obj):
    if isinstance(obj, set):
        return list(obj)
    return obj


def validate_cookie(f):
    @wraps(f)
    def validate_cookie_function(*args, **kwargs):
        user_index = request.cookies.get('userIndex')
        if not user_index:
            return jsonify({"error": "Cookie is invalid or expired."}), 401
        return f(*args, **kwargs)

    return validate_cookie_function


@app.route('/', methods=['GET'])
def init():
    with open('data.json') as f:
        data = json.load(f)
        global users, counter, words
        users = data['users']
        counter = data['counter']
        words = data['words']
    return make_response('Data has been initialized.'), 200


@app.route('/UserVerification', methods=['post'])
def user_verification_func():
    req = request.json
    global users
    user, index = {}, -1
    for i, u in enumerate(users):
        if u['id'] == req['id']:
            user = u
            index = i
            break
    if user == {}:
        return make_response('user does not exist'), 400
    if user['password'] != req['password']:
        return make_response('wrong password'), 400
    response = make_response(user)
    response.set_cookie('userIndex', str(index), max_age=600, httponly=True, secure=False)
    return response, 200


@app.route('/addUser', methods=['post'])
def add_user_func():
    req = request.json
    global users, counter
    counter = int(counter)
    counter += 1
    new_user = User(counter, req['name'], req['password']).__dict__
    users.append(new_user)
    index = len(users) - 1
    save_data()
    response = make_response(new_user)
    response.set_cookie('userIndex', str(index), max_age=600, httponly=True, secure=False)
    return response, 200


@app.route('/getWord', methods=['GET'])
@validate_cookie
def get_word_func():
    num = int(request.args.get('num'))
    random.shuffle(words)
    return make_response(words[num % len(words)]), 200


@app.route('/putCountGames', methods=['PUT'])
@validate_cookie
def put_count_games_func():
    global users
    current_user_index = int(request.cookies.get('userIndex'))
    users[current_user_index]['countGames'] += 1
    save_data()
    return jsonify({'message': 'count games has been updated.', 'currentUser': users[current_user_index]}), 200


@app.route('/putWord', methods=['PUT'])
@validate_cookie
def put_word_func():
    global users
    current_user_index = int(request.cookies.get('userIndex'))
    set_words = set(users[current_user_index]['words'])
    set_words.add(request.args.get('word'))
    users[current_user_index]['words'] = list(set_words)
    save_data()
    return jsonify({'message': 'words has been updated.', 'currentUser': users[current_user_index]}), 200


@app.route('/putCountWins', methods=['PUT'])
@validate_cookie
def put_count_wins_func():
    global users
    current_user_index = int(request.cookies.get('userIndex'))
    users[current_user_index]['countWins'] += 1
    save_data()
    return jsonify({'message': 'count wins has been updated.', 'currentUser': users[current_user_index]}), 200


if __name__ == "__main__":
    app.run(debug=True)
