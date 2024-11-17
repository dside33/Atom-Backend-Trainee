# Atom-Backend-Trainee

## Описание
API атом чата, в котором пользователи могут общаться друг с другом в приватных каналах.
ТЗ: https://github.com/notafavor/test-cases/blob/main/case_2.md

## Требования
- Docker и Docker Compose
- Python 3.9+

## Установка и запуск

### 1. Клонирование репозитория
```bash
git clone https://github.com/your-username/your-repository.git
cd your-repository
```
### 2. Настройка переменных окружения
Создайте файл .env в корневой папке проекта и заполните следующие переменные:
```bash
DB_HOST=db
DB_PORT=5432
DB_USER=root
DB_PASS=root
DB_NAME=atomdb

SECRET=SECRET
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=2
ACCESS_COOKIE_EXPIRE_HOURS=2
ISSUER=atom_api
```
### 3. Билд проекта и запуск
```bash
docker-compose build
docker-compose up -d
```
### 4. Доступ к API
Документация API доступна по адресу:
```bash
http://127.0.0.1:8000/docs
```
