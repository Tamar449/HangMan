import requests

from ApiError import ApiError

url = 'http://127.0.0.1:5000'
session = requests.session()

cookie = None
with open('hang_man.txt', 'r') as f:
    text = f.read()
    hang_man_list = text.split('.')


def start():
    response = session.get(f'{url}/')
    if response.status_code != 200:
        raise ApiError(response.status_code, 'Data has not been initialized.')
    x = int(input('hi!\nto login enter 1, to register enter 2\n'))
    while x != 1 and x != 2:
        print('invalid input')
        x = int(input('to login enter 1, to register enter 2\n'))
    if x == 1:
        login()
    if x == 2:
        register()


def login():
    user_id = int(input('enter your id \n'))
    password = input('enter your password \n')
    obj = {'id': user_id, 'password': password}
    response = session.post(f'{url}/UserVerification', json=obj)
    if response.status_code == 400:
        response_text = response.text
        if response_text == 'user does not exist':
            print(f'{response_text}\nplease register: ')
            register()
        if response_text == 'wrong password':
            while response.status_code == 400 and response_text == 'wrong password':
                print(response_text)
                password = input('enter your password \n')
                obj['password'] = password
                response = session.post(f'{url}/UserVerification', json=obj)
                response_text = response.text
    if response.status_code != 200:
        raise ApiError(response.status_code, 'User verification has been failed.')
    global cookie
    cookie = response.cookies
    print(f"hello {response.json()['name']}!")
    play()


def register():
    print('register')
    name = input('enter your name \n')
    password = input('enter your password \n')
    obj = {'name': name, 'password': password}
    response = session.post(f'{url}/addUser', json=obj)
    if response.status_code != 200:
        raise ApiError(response.status_code, 'Register has been failed.')
    global cookie
    cookie = response.cookies
    print(f'your id is: {response.json()["id"]}\nSave the number for identification on future logins.')
    play()


def get_word():
    while True:
        try:
            num = int(input('enter a number \n'))
            break
        except ValueError as e:
            print('Value error.')
    params = {'num': num}
    response = session.get(f'{url}/getWord', params=params, cookies=cookie)
    if response.status_code == 401 and response.json()['error'] == 'Cookie is invalid or expired.':
        print(f"{response.json()['error']} you have to login again.")
        login()
    if response.status_code != 200:
        raise ApiError(response.status_code, 'Get a word failed.')
    return response.text


def play():
    global cookie
    response = session.put(f'{url}/putCountGames', cookies=cookie)
    if response.status_code == 401 and response.json()['error'] == 'Cookie is invalid or expired.':
        print(f"{response.json()['error']} you have to login again.")
        login()
    if response.status_code != 200:
        print(response.json())
        raise ApiError(response.status_code, 'Put count games failed.')
    current_user = response.json()['currentUser']
    word = get_word()
    response = session.put(f'{url}/putWord', params={'word': word}, cookies=cookie)
    if response.status_code == 401 and response.json()['error'] == 'Cookie is invalid or expired.':
        print(f"{response.json()['error']} you have to login again.")
        login()
    if response.status_code != 200:
        raise ApiError(response.status_code, 'put word has failed.')
    current_user = response.json()['currentUser']
    s = ''
    for i in range(0, len(word)):
        s += '_' if word[i] != ' ' else ' '
    count_errors = 0
    print("let's start play! ")
    global hang_man_list
    print(f'{s}\nerrors:{count_errors}/7\n{hang_man_list[count_errors].strip()}')
    while count_errors < 7 and s.count('_') > 0:
        c = input('enter a char \n')
        if word.__contains__(c):
            s1 = ''
            for i in range(0, len(word)):
                s1 += s[i] if word[i] != c else c
            s = s1
        else:
            count_errors += 1
        print(f'{s}\nerrors:{count_errors}/7\n{hang_man_list[count_errors].strip()}')
    if count_errors == 7:
        print('oops...\ntry play again!')
    else:
        print('you are amazing!!!')
        response = session.put(f'{url}/putCountWins', cookies=cookie)
        if response.status_code == 401 and response.json()['error'] == 'Cookie is invalid or expired.':
            print(f"{response.json()['error']} you have to login again.")
            login()
        if response.status_code != 200:
            raise ApiError(response.status_code, 'Put count wins failed.')
        current_user = response.json()['currentUser']
    x = input(
        "To play again type 1, To see information about your previous games type 2, To logout type any character. \n")
    if x == '1':
        play()
    if x == '2':
        show_details(current_user)


def show_details(current_user):
    print(f"{current_user['name']} games' details:")
    print(f"you played {current_user['countGames']} times.")
    print(f"you won {current_user['countWins']} times.")


start()
