# 🏥 Medical Information System

Медицинская информационная система для частных клиник.

## 🚀 Быстрый старт

### Установка
```bash
# 1. Создать виртуальное окружение
python3.12 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# 2. Установить зависимости
pip install --upgrade pip
pip install -r requirements.txt

# 3. Настроить окружение
cp .env.example .env
# Отредактируйте .env с вашими настройками

# 4. Инициализировать базу данных
python manage.py migrate

# 5. Создать суперпользователя
python manage.py createsuperuser

# 6. Запустить сервер
python manage.py runserver
```

### Swagger документация
http://localhost:8000/docs

## 📁 Структура проекта
```
medical_system/
├── app/
│   ├── modules/          # Модули приложения
│   │   ├── auth/        # Аутентификация
│   │   ├── patients/    # Пациенты
│   │   ├── appointments/# Записи
│   │   ├── visits/      # Визиты
│   │   └── ...
│   ├── core/            # Общий функционал
│   └── db/              # База данных
├── tests/               # Тесты
└── alembic/             # Миграции
```

## 🧪 Тестирование
```bash
# Запустить тесты
pytest

# С покрытием
pytest --cov=app --cov-report=html
```

## 📝 Лицензия

MIT
