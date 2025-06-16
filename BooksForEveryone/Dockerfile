# Используем официальный образ Python
FROM python:3.11-slim

# Рабочая директория внутри контейнера
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект внутрь контейнера
COPY . .

# Указываем, что будем запускать через gunicorn
CMD ["gunicorn", "BooksForEveryone.wsgi:application", "--bind", "0.0.0.0:8000"]