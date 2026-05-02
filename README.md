# KOSAGO.RU

Веб-приложение для автоматизации работы брокеров и агентов по страхованию ОСАГО. Построено на Django с личным кабинетом, BI-дашбордом, управлением полисами и ролевой моделью пользователей.

## Возможности

- **Авторизация** — вход, регистрация, восстановление пароля по email (SMTP)
- **Личный кабинет** — профиль с ФИО, телефоном, ролью, аватаром и статистикой полисов
- **Роли** — Брокер и Агент с цветными бейджами
- **ОСАГО** — создание, редактирование и просмотр страховых полисов (страхователь, ТС, параметры полиса)
- **BI-дашборд** — сводная аналитика по сделкам и сотрудникам с графиками Chart.js
- **Форма обратной связи** — предложения по улучшению проекта в модальном окне с отправкой на email
- **Мультиязычное приветствие** — случайный язык при каждом входе в профиль
- **Аватар** — загрузка фото профиля с предпросмотром
- **Автовыход по бездействию** — через 10 минут без активности

## Что используется

- Django 6.0.3
- SQLite
- Pillow — обработка изображений (аватары)
- Chart.js 4.4.0 — графики дашборда
- SMTP — отправка писем (обратная связь, восстановление пароля)

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

## Автодеплой на VPS после `git push`

В репозиторий добавлен workflow [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml), который:

- запускается при `push` в ветку `main` и вручную через `workflow_dispatch`;
- сначала прогоняет `python manage.py test`;
- затем подключается к VPS по SSH и запускает [`scripts/deploy.sh`](scripts/deploy.sh).

Что делает deploy-скрипт на сервере:

- забирает свежие изменения из ветки `main`;
- обновляет зависимости из `requirements.txt`;
- применяет миграции;
- собирает статику;
- выполняет `python manage.py check --deploy`;
- перезапускает systemd-сервис приложения и при необходимости делает reload nginx.

### 1. Что нужно подготовить на VPS один раз

1. Установите проект на сервер, например в `/var/www/testSite`:

```bash
git clone https://github.com/chubits/testSite.git /var/www/testSite
cd /var/www/testSite
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py collectstatic --noinput
```

2. Заполните `.env` продакшен-значениями, минимум:

- `SECRET_KEY`
- `DEBUG=False`
- `ALLOWED_HOSTS=ваш-домен,IP`
- SMTP-переменные при использовании отправки почты

3. Убедитесь, что приложение запускается через `systemd` и вы знаете имя сервиса, например `testsite` или `gunicorn`.

Пример проверки:

```bash
sudo systemctl status testsite
sudo systemctl status nginx
```

4. Разрешите deploy-пользователю выполнять перезапуск сервиса через `sudo` без пароля. Пример для пользователя `deploy`:

```bash
sudo visudo -f /etc/sudoers.d/testsite-deploy
```

И добавьте строку:

```text
deploy ALL=NOPASSWD:/bin/systemctl restart testsite,/bin/systemctl reload nginx
```

Если имя сервиса другое, подставьте своё.

### 2. Какие GitHub Secrets добавить

В репозитории GitHub откройте `Settings -> Secrets and variables -> Actions` и создайте секреты:

- `DEPLOY_HOST` — IP-адрес или домен VPS
- `DEPLOY_PORT` — SSH-порт, обычно `22`
- `DEPLOY_USER` — пользователь для SSH, например `deploy`
- `DEPLOY_SSH_KEY` — приватный SSH-ключ этого пользователя
- `DEPLOY_PATH` — путь к проекту на сервере, например `/var/www/testSite`
- `DEPLOY_VENV_PATH` — путь к виртуальному окружению, например `/var/www/testSite/venv`
- `APP_SERVICE` — systemd-сервис приложения, например `testsite`
- `NGINX_SERVICE` — обычно `nginx`; можно оставить пустым, если reload не нужен
- `DEPLOY_KNOWN_HOSTS` — опционально, вывод `ssh-keyscan -H your-host`
- `DJANGO_COLLECTSTATIC` — опционально, `1` или `0`
- `DJANGO_RUN_DEPLOY_CHECK` — опционально, `1` или `0`

### 3. Как это работает после настройки

После обычного:

```bash
git push origin main
```

GitHub Actions автоматически:

1. прогонит тесты;
2. подключится к VPS;
3. выполнит deploy-скрипт;
4. перезапустит приложение.

Если нужен ручной запуск без нового коммита, используйте `Actions -> Deploy to VPS -> Run workflow`.

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

## Загрузка аватаров на VPS

Если при загрузке аватара сервер отвечает `413 Request Entity Too Large`, запрос отбрасывает nginx до того, как он попадет в Django. Для прод-сервера нужно увеличить лимит тела запроса в конфигурации сайта или `nginx.conf`:

```nginx
server {
	...
	client_max_body_size 10M;
	...
}
```

После изменения конфигурации примените проверку и перезапустите nginx:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

В приложении дополнительно действует ограничение на размер аватара `5 МБ`, чтобы пользователь получал понятную ошибку формы уже на уровне Django.

## Нагрузочный тест на 100 пользователей

Для проекта добавлен сценарий Locust в [load_tests/locustfile.py](load_tests/locustfile.py). Он имитирует реальный поток для авторизованного пользователя:

- вход в систему;
- открытие профиля;
- открытие списка полисов ОСАГО;
- редкое создание черновика полиса;
- выход из системы.

Для небольшого VPS с SQLite, 1 vCPU и 1 GB RAM это более реалистичный и безопасный профиль нагрузки, чем постоянные конкурентные записи в базу.

1. Установите зависимости для нагрузочного теста:

```bash
pip install -r requirements-loadtest.txt
```

2. Подготовьте 100 тестовых пользователей и стартовые полисы:

```bash
python manage.py seed_load_test_data --users 100 --policies-per-user 2
```

3. Запустите Django-приложение:

```bash
python manage.py runserver 0.0.0.0:8000
```

4. Запустите нагрузочный тест на 100 пользователей в headless-режиме:

```bash
locust -f load_tests/locustfile.py \
	--host http://127.0.0.1:8000 \
	--users 100 \
	--spawn-rate 5 \
	--run-time 5m \
	--headless \
	--csv loadtest_100u
```

Что значит эта конфигурация:

- `--users 100` — одновременно 100 виртуальных пользователей;
- `--spawn-rate 5` — плавный разгон, чтобы не уронить VPS мгновенным пиком;
- `wait_time = 2..5s` в сценарии — пауза между действиями, близкая к реальному пользователю;
- доля записи в БД ограничена, чтобы тест был ближе к обычной эксплуатации сайта.

При необходимости можно поменять пароль и префикс тестовых пользователей через переменные окружения:

```bash
export LOADTEST_PASSWORD='LoadTestPass123!'
export LOADTEST_USERNAME_PREFIX='loaduser'
export LOADTEST_USER_POOL='100'
```

Для первого прогона на таком VPS имеет смысл сделать короткий smoke-run на 1 минуту, а затем уже полный прогон на 5 минут и смотреть:

- `Requests/s`;
- `95% percentile` по времени ответа;
- долю ошибок;
- загрузку CPU, RAM и задержки SQLite.