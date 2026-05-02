#!/usr/bin/env bash

set -euo pipefail

APP_DIR="${APP_DIR:-$(pwd)}"
VENV_PATH="${VENV_PATH:-$APP_DIR/venv}"
BRANCH="${BRANCH:-main}"
APP_SERVICE="${APP_SERVICE:-}"
NGINX_SERVICE="${NGINX_SERVICE:-}"
DJANGO_COLLECTSTATIC="${DJANGO_COLLECTSTATIC:-1}"
DJANGO_RUN_DEPLOY_CHECK="${DJANGO_RUN_DEPLOY_CHECK:-1}"

if [[ -z "$APP_SERVICE" ]]; then
  echo "APP_SERVICE is required" >&2
  exit 1
fi

if [[ ! -d "$APP_DIR/.git" ]]; then
  echo "Git repository not found: $APP_DIR" >&2
  exit 1
fi

if [[ ! -x "$VENV_PATH/bin/python" ]]; then
  echo "Python executable not found: $VENV_PATH/bin/python" >&2
  exit 1
fi

cd "$APP_DIR"

git fetch origin "$BRANCH"
git checkout "$BRANCH"
git pull --ff-only origin "$BRANCH"

"$VENV_PATH/bin/pip" install -r requirements.txt
"$VENV_PATH/bin/python" manage.py migrate --noinput

if [[ "$DJANGO_COLLECTSTATIC" == "1" ]]; then
  "$VENV_PATH/bin/python" manage.py collectstatic --noinput
fi

if [[ "$DJANGO_RUN_DEPLOY_CHECK" == "1" ]]; then
  "$VENV_PATH/bin/python" manage.py check --deploy
fi

sudo systemctl restart "$APP_SERVICE"

if [[ -n "$NGINX_SERVICE" ]]; then
  sudo systemctl reload "$NGINX_SERVICE"
fi

echo "Deployment completed for branch $BRANCH"
