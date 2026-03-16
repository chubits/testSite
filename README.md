# testSite

Небольшой Django-проект с авторизацией пользователей, личным профилем и формой обратной связи с отправкой письма на почту.

## Что используется

- Django 6.0.3
- SQLite
- SMTP Mail.ru для отправки писем из формы обратной связи

## Запуск проекта

1. Клонируйте репозиторий и перейдите в папку проекта:

```bash
git clone https://github.com/chubits/testSite.git
cd testSite
```

2. Создайте виртуальное окружение и активируйте его:

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Установите зависимости:

```bash
pip install -r requirements.txt
```

4. Создайте локальный файл окружения на основе примера:

```bash
cp .env.example .env
```

5. Заполните `.env`.

Минимально нужно проверить эти поля:

- `SECRET_KEY` — секретный ключ Django
- `DEBUG` — режим отладки
- `ALLOWED_HOSTS` — список разрешенных хостов через запятую
- `EMAIL_HOST_USER` — почтовый ящик Mail.ru
- `EMAIL_HOST_PASSWORD` — пароль приложения Mail.ru
- `DEFAULT_FROM_EMAIL` — адрес отправителя
- `FEEDBACK_RECIPIENT_EMAIL` — адрес, куда будут приходить сообщения из формы

6. Примените миграции:

```bash
python manage.py migrate
```

7. При необходимости создайте администратора:

```bash
python manage.py createsuperuser
```

8. Запустите сервер разработки:

```bash
python manage.py runserver
```

После запуска проект будет доступен по адресу:

```text
http://127.0.0.1:8000/
```

## Основные маршруты

- `/` — вход и регистрация
- `/profile/` — профиль пользователя и форма обратной связи
- `/admin/` — административная панель Django

## Настройка почты Mail.ru

Для отправки писем через Mail.ru нужен не обычный пароль почтового ящика, а пароль приложения.

Параметры по умолчанию:

- `EMAIL_HOST=smtp.mail.ru`
- `EMAIL_PORT=465`
- `EMAIL_USE_SSL=True`
- `EMAIL_USE_TLS=False`

Если хотите только проверить работу формы локально без реальной отправки писем, можно временно указать в `.env`:

```dotenv
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

Тогда письма будут выводиться в консоль вместо отправки через SMTP.