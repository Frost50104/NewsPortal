Новостной портал (Django)

В этом репозитории находится минимальный проект Django, реализующий модели, требуемые для задания «Новостной портал».

Приложение: news
Модели: Author, Category, Post, PostCategory, Comment.

Как запустить локально:
1) Создайте виртуальное окружение и установите Django: pip install django
2) Примените миграции: python manage.py makemigrations && python manage.py migrate
3) (Необязательно) Создайте суперпользователя для доступа к админке: python manage.py createsuperuser
4) Запустите сервер: python manage.py runserver

Команды для Django shell:
Смотрите docs/django_shell_commands.txt — в файле приведена точная последовательность команд для создания данных, настройки рейтингов и вывода результатов для шагов 1–11.
