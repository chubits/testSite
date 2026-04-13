# testSite

Небольшой Django-проект с авторизацией пользователей, личным профилем и формой обратной связи с отправкой письма на почту.

## Что используется

- Django 6.0.3
- SQLite
- SMTP для отправки писем из формы обратной связи и восстановления пароля

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
- `EMAIL_HOST` — SMTP-сервер, для Jino это `mail.jino.ru`
- `EMAIL_PORT` — SMTP-порт, для SSL это `465`, для TLS это `587`
- `EMAIL_USE_SSL` — `True` при порте `465`
- `EMAIL_USE_TLS` — `True` при порте `587`
- `EMAIL_HOST_USER` — полный почтовый ящик, например `recovery@kasago.ru`
- `EMAIL_HOST_PASSWORD` — пароль почтового ящика или SMTP-пароль провайдера
- `DEFAULT_FROM_EMAIL` — адрес отправителя
- `PASSWORD_RESET_FROM_EMAIL` — адрес отправителя писем восстановления пароля
- `SITE_DOMAIN` — домен для ссылок в письмах, например `kasago.ru`
- `SITE_PROTOCOL` — протокол для ссылок, обычно `https`
- `FEEDBACK_RECIPIENT_EMAIL` — адрес, куда будут приходить сообщения из формы, например `feedback@kasago.ru`

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

## Настройка SMTP

Для доменной почты на Jino используйте такие параметры:

- `EMAIL_HOST=mail.jino.ru`
- `EMAIL_PORT=465`
- `EMAIL_USE_SSL=True`
- `EMAIL_USE_TLS=False`

Альтернативно можно использовать STARTTLS:

- `EMAIL_HOST=mail.jino.ru`
- `EMAIL_PORT=587`
- `EMAIL_USE_SSL=False`
- `EMAIL_USE_TLS=True`

Если хотите только проверить работу формы локально без реальной отправки писем, можно временно указать в `.env`:

```dotenv
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

Тогда письма будут выводиться в консоль вместо отправки через SMTP.