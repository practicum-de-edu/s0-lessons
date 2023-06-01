#!/usr/bin/env python3

import os
import sys
import json

import requests

INVITE_TOKEN = os.getenv('INVITE_TOKEN')

TOKEN_PATH = ".check_service_token"
PUBLIC_CHECK_SERVICE_HOST = "https://de-sprint0-checks.sprint9.tgcloudenv.ru"
CHECK_SERVICE_HOST = os.getenv("CHECK_SERVICE_HOST", PUBLIC_CHECK_SERVICE_HOST)
API_PATH = "api/v1/checks"


class TokenRepository:
    def __init__(self, token_path):
        self.token_path = token_path

    def get_token(self):
        try:
            with open(self.token_path, "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            return None

    def save_token(self, token):
        with open(self.token_path, "w") as f:
            f.write(token)


token_repository = TokenRepository(TOKEN_PATH)


class TerminalColors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    def ok(self, message):
        print(f'\n{self.OKGREEN}{message}{self.ENDC}\n')

    def header(self, message):
        print(f'\n{self.HEADER}{message}{self.ENDC}\n')

    def fail(self, message):
        print(f'\n{self.FAIL}{message}{self.ENDC}\n')

    def okcyan(self, message):
        print(f'\n{self.OKCYAN}{message}{self.ENDC}\n')

    def warn(self, message):
        print(f'\n{self.WARNING}{message}{self.ENDC}\n')


def service_error(status_code, address):
    tk.fail('Что-то пошло не так, сервер вернул ошибку '
            f'{status_code}\n{address}')


tk = TerminalColors()


def auth_user():
    if token_repository.get_token():
        return

    address = "api/v1/auth/token/"

    try:
        r = requests.post(
            f"{CHECK_SERVICE_HOST}/{address}",
            data={"username": 'sp0user', "password": str(INVITE_TOKEN)},
        )

    except Exception as e:
        tk.fail('Не получилось создать пользователя из-за ошибки.')
        print(e)
        return

    if r.status_code == 200:
        token_repository.save_token(r.json()["access_token"])
    elif r.status_code == 400:
        tk.fail("Не получилось создать пользователя")
    else:
        service_error(r.status_code, address)


def headers():
    return {"Authorization": f"Bearer {token_repository.get_token()}"}


def create_playground():
    auth_user()

    address = "api/v1/playgrounds/"
    try:
        r = requests.post(
            f"{CHECK_SERVICE_HOST}/{address}",
            headers=headers(),
        )

    except Exception as e:
        print(e)
        return

    if r.status_code == 200:
        response = r.json()
        message = response.pop('message', None)
        response.pop('student_id', None)
        response.pop('secret_key', None)
        tk.header('Параметры подключения:')
        tk.ok(json.dumps(response, indent=1))
        tk.okcyan(message)

    elif r.status_code == 400:
        tk.warn(r.json()['message'])
    else:
        service_error(r.status_code, address)


def get_playground():
    address = "api/v1/playgrounds/"
    try:
        r = requests.get(
            f"{CHECK_SERVICE_HOST}/{address}",
            headers=headers(),
        )

    except Exception as e:
        print(e)
        return

    if r.status_code == 200:
        response = r.json()
        response.pop('message', None)
        response.pop('student_id', None)
        response.pop('secret_key', None)
        tk.header('\nПараметры подключения:')
        tk.ok(json.dumps(response['student_db_connection'], indent=1))

    elif r.status_code == 400:
        tk.fail(f'Что-то пошло не так, сервер вернул ошибку {r.status_code}')
    elif r.status_code == 504:
        tk.fail('Пользователь не найден, сперва запустите `1. Вперёд, к '
                'окружению/6. Как работает Docker-тренажёр/submit.py`')
    else:
        service_error(r.status_code, address)


def submit(task_path: str, checker: str, rlz_file: str = "realization.sql"):
    task_path = os.path.dirname(os.path.abspath(task_path))
    user_file = f"{task_path}/{rlz_file}"

    try:
        with open(user_file, "r", encoding="utf8") as u_file:
            user_code = u_file.read()
    except FileNotFoundError:
        tk.warn(f'Не найден файл `{user_file}')
        tk.warn(f'Сохраните решение в {task_path}/{rlz_file}')
        sys.exit()

    try:
        r = requests.post(
            f"{CHECK_SERVICE_HOST}/{API_PATH}/{checker}/",
            json={"student_id": 'st0', "student_solution": user_code},
            headers=headers(),
            timeout=300,
        )

    except Exception as e:
        tk.fail(e)
        return

    if r.status_code == 200:
        if r.json()["status"] == "success":
            tk.ok(r.json()["message"])
        else:
            tk.fail(r.json()["message"])
    elif r.status_code == 401:
        tk.fail('Не авторизованный доступ, выполните запуск `1. Вперёд, к '
                'окружению/6. Как работает Docker-тренажёр/submit.py')
    else:
        service_error(r.status_code, checker)


def healthcheck():
    checker = "api/v1/health/healthcheck"
    try:
        r = requests.get(f"{CHECK_SERVICE_HOST}/{checker}")

    except Exception as e:
        return e
    return r, r.content


if __name__ == "__main__":
    # print(f"{healthcheck() = }")
    # print(f"{auth_user() = }")
    # print(f"{create_playground() = }")
    print(f"{get_playground() = }")

    # # auth_user()
