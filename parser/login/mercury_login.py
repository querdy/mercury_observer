from bs4 import BeautifulSoup
from parser.login import users
# from parser.login.users import users
from parser.login.base_session import BaseSession


def check_cookies(file):
    """Проверка имеющихся куки и попытка логина, если они не действительны"""

    URL = 'https://mercury.vetrf.ru/gve/operatorui'
    sess = BaseSession(file)
    page = sess.fetch(URL)
    if 'Добро пожаловать,' in page.text:
        return sess
    else:
        _login()
        sess = BaseSession(file)
        page = sess.fetch(URL)
        if 'Добро пожаловать,' in page.text:
            return sess
        else:
            return False 


def _login():

    """логин в системе Меркурий и сохранение куки"""

    URL = 'http://mercury.vetrf.ru/gve'
    my_sess = BaseSession()

    page = my_sess.fetch(URL)
    soup = BeautifulSoup(page.content, 'html5lib')

    # находим скрытую форму
    form = soup.find('form')
    fields = form.findAll('input')

    # тут получим первый SAMLRequest из странницы
    form_data = dict((field.get('name'), field.get('value')) for field in fields if field.get('name') is not None)

    # запрос к системе авторизации
    page = my_sess.fetch(form['action'], data=form_data)

    # добавляем данные для авторизации
    form_data['j_username'] = users.USER.login
    form_data['j_password'] = users.USER.password
    form_data['_eventId_proceed'] = ''
    form_data['ksid'] = 'lolkek'
    # из текущей странницы нам нужна ссылка по которой отправить авторизационные данные
    soup = BeautifulSoup(page.content, 'html5lib')
    form = soup.find('form')

    # запрос к системе авторизации по специальной ссылке с данными для авторизации
    page = my_sess.fetch(f"https://idp.vetrf.ru{form['action']}", data=form_data)

    # теперь у нас должен появиться SAMLResponse (который мы поставим вместо SAMLRequest)
    soup = BeautifulSoup(page.content, 'html5lib')
    form = soup.find('form')
    fields = form.findAll('input')
    temp_data = dict((field.get('name'), field.get('value')) for field in fields if field.get('name') is not None)

    # SAMLResponse мы поставим вместо SAMLRequest
    try:
        form_data['SAMLResponse'] = temp_data['SAMLResponse']
        del form_data['SAMLRequest']
    except KeyError:
        print('неудачная авторизация, проверить верность логина и пароля')
        return 'неудачная авторизация, проверить верность логина и пароля'
        # sys.exit(0)

    # и отправляем по ссылке (где ее спарсить!?!?! блэд) для подтверждения данных
    page = my_sess.fetch('https://mercury.vetrf.ru/gve/saml/SSO/alias/gve', data=form_data)

    my_sess.save_cookies('cookies.json')
    print('LogIn -> Success')

    return my_sess
