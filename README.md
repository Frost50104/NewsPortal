# Новостной портал (Django)

Полнофункциональный учебный проект новостного портала на Django с системой аутентификации, подписками на категории, email-уведомлениями и фоновой обработкой задач.

## Основные возможности
- **CRUD для новостей и статей** с пагинацией и поиском
- **Аутентификация** через django-allauth (локальная + OAuth Яндекс)
- **Система ролей и прав** (группы `common` и `authors`)
- **Email-уведомления** (мгновенные при публикации + еженедельный дайджест)
- **Подписки на категории** новостей
- **Фоновые задачи** через Celery и Redis
- **Логирование** с разделением по уровням и файлам
- **Фильтр цензуры** нежелательных слов

## Что реализовано
1) Список новостей: `/news/`
   - Выводятся только объекты `Post` с типом `NEWS`.
   - Порядок: от более свежих к более старым.
   - Пагинация: по 10 новостей на страницу. Показаны ближайшие номера страниц, а также ссылки на первую и последнюю страницы.
   - Для каждой новости: заголовок, дата публикации (`дд.мм.гггг`) и первые 20 символов текста.

2) Полная новость: `/news/<id>/`
   - Отображаются заголовок, полный текст (с сохранением переносов) и дата публикации в формате `дд.мм.гггг`.

3) Поиск новостей: `/news/search/`
   - Критерии:
   - по названию (`title` — содержит, нечувствительно к регистру),
   - по имени пользователя автора (`author` — содержит),
   - по дате публикации позже/равно (`date_after`, формат `YYYY-MM-DD`).
   - Можно комбинировать несколько критериев одновременно.
   - Результаты постранично; параметры фильтрации сохраняются при навигации по страницам.

4) CRUD для новостей и статей
   - Новости (тип `NEWS`):
   - Создание: `/news/create/`
   - Редактирование: `/news/<id>/edit/`
   - Удаление: `/news/<id>/delete/`
   - Статьи (тип `ARTICLE`) — по требуемым путям в корне:
   - Создание: `/articles/create/`
   - Просмотр: `/articles/<id>/`
   - Редактирование: `/articles/<id>/edit/`
   - Удаление: `/articles/<id>/delete/`
   - Примечание: для создания требуется существующий `Author`. В учебных целях в формах автоматически выбирается первый доступный автор. Если авторов нет — форма сообщит об этом.

5) Фильтр шаблонов `censor`
   - Находит нежелательные слова и заменяет их буквы на `*` (регистронезависимо, по границам слов).
   - Подключение: `{% load censor_filters %}`. Пример: `{{ post.title|censor }}`.

6) Подписки на категории и рассылки
   - Подписка на категорию: страница категории `/news/categories/<id>/` содержит кнопку подписки/отписки (после входа).
   - Мгновенное оповещение email при добавлении НОВОЙ СТАТЬИ (тип `ARTICLE`) в подписанную категорию: приходит превью + ссылка на статью.
   - Еженедельный дайджест: список новых статей за 7 дней одним письмом с кликабельными ссылками.
   - Приветственное письмо отправляется при регистрации пользователя.

## Быстрый старт
1) Python 3.10+ (рекомендуется) и виртуальное окружение.
2) Установите зависимости:
   ```bash
   pip install django django-allauth celery redis
   ```
   Основные пакеты:
   - `django>=4.2` — веб-фреймворк
   - `django-allauth` — аутентификация и OAuth
   - `celery>=5.3` — фоновые задачи
   - `redis>=5.0` — брокер сообщений для Celery
3) Примените миграции:
   - `python manage.py makemigrations`
   - `python manage.py migrate`
4) (Опционально) создайте суперпользователя: `python manage.py createsuperuser`.
5) Настройте вход/регистрацию и домен сайта:
   - В админке (`/admin/`) откройте "Sites" и убедитесь, что домен соответствует вашему (например, 127.0.0.1:8000).
   - Создайте SocialApp для провайдера Yandex в разделе Social applications:
     - Provider: Yandex
     - Name: произвольное, например "Yandex OAuth"
     - Client id и Secret: из кабинета Яндекс.OAuth
     - Свяжите приложение с текущим сайтом (Sites).
   - Альтернатива: создайте SocialApp через shell — см. `docs/django_shell_commands.txt`.
6) Запустите сервер: `python manage.py runserver`.
7) Проверьте в браузере:
   - Список: `http://127.0.0.1:8000/news/`
   - Вход: `http://127.0.0.1:8000/accounts/login/` (кнопка "Yandex" отображается только если настроен SocialApp для текущего сайта)
   - Поиск: `http://127.0.0.1:8000/news/search/`
   - Создать новость: `http://127.0.0.1:8000/news/create/`
   - Создать статью: `http://127.0.0.1:8000/articles/create/`
   - Страница категории (для подписки): `http://127.0.0.1:8000/news/categories/<id>/`

### Redis и Celery (фоновая обработка)
Celery используется для асинхронной отправки email-уведомлений и запуска периодических задач (еженедельный дайджест).

**Установка Redis:**
- macOS (Homebrew): `brew install redis && brew services start redis`
- Linux (Debian/Ubuntu): `sudo apt-get install redis-server && sudo systemctl start redis`
- Windows: используйте Docker: `docker run -d -p 6379:6379 redis:7`

**Настройка подключения (опционально):**
Если Redis не на localhost, установите переменные окружения:
```bash
export CELERY_BROKER_URL=redis://<host>:6379/0
export CELERY_RESULT_BACKEND=redis://<host>:6379/1
```

**Запуск Celery** (требуется 2 отдельных терминала):

1. **Воркер** (обработка задач):
   ```bash
   celery -A newsportal worker -l info
   ```

2. **Beat** (планировщик для еженедельной рассылки):
   ```bash
   celery -A newsportal beat -l info
   ```

**Расписание задач:**
- Еженедельный дайджест: понедельник 08:00 (локальное время `Europe/Moscow`)
- Конфигурация: `newsportal/settings.py`, секция `CELERY_BEAT_SCHEDULE`

**Примечание:** Без запущенного воркера мгновенные уведомления и дайджесты отправляться не будут.

## Почта: настройка и проверка
- По умолчанию используется консольный backend: письма выводятся в консоль сервера (см. `settings.py`, `EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'`).
- Для боевого SMTP укажите переменные в `settings.py` (пример):
  ```python
  EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
  EMAIL_HOST = 'smtp.yourprovider.com'
  EMAIL_PORT = 587
  EMAIL_USE_TLS = True
  EMAIL_HOST_USER = 'user@domain.tld'
  EMAIL_HOST_PASSWORD = '***'
  DEFAULT_FROM_EMAIL = 'no-reply@domain.tld'
  ```
- В админке проверьте домен в разделе Sites — он будет использован для формирования ссылок в письмах.

## Команды управления

### Еженедельный дайджест
- **Команда**: `python manage.py send_weekly_digest`
  - Собирает все новые статьи (тип `ARTICLE`) за последние 7 дней для каждого пользователя по его подпискам.
  - Отправляет одно письмо пользователю со списком ссылок.
- **Автоматическое расписание** через Celery Beat: понедельник 08:00 (см. `CELERY_BEAT_SCHEDULE` в `settings.py`). При запущенных процессах worker+beat письма отправятся автоматически.
- **Альтернатива без Celery**: можно использовать системный cron, пример:
  ```cron
  0 9 * * SUN /path/to/venv/bin/python /path/to/project/manage.py send_weekly_digest >> /var/log/newsportal_digest.log 2>&1
  ```

### Удаление новостей по категории
- **Команда**: `python manage.py delete_news <название_категории>`
  - Удаляет все посты (новости и статьи) из указанной категории.
  - Перед удалением запрашивает подтверждение (yes/no).
  - Пример: `python manage.py delete_news Спорт`

## Мгновенные уведомления и приветственное письмо
- Мгновенные уведомления отсылаются при добавлении статьи к категории (при сохранении формы добавления/редактирования статьи) — теперь асинхронно через Celery.
- Превью берётся из метода `Post.preview()`; в письме всегда есть гиперссылка на статью.
- Приветственное письмо отправляется при создании пользователя (сигнал `post_save`).

## Структура шаблонов
- Базовый шаблон: `templates/default.html`
- Список новостей: `templates/news/news_list.html`
- Полная новость: `templates/news/news_detail.html`
- Поиск: `templates/news/news_search.html`
- Формы и удаление: `templates/news/news_form.html`, `templates/news/news_confirm_delete.html`, `templates/news/article_form.html`, `templates/news/article_confirm_delete.html`

## Аутентификация и роли
- Используется django-allauth (локальная форма входа + вход через Яндекс).
- Маршруты:
  - Вход: `/accounts/login/`
  - Регистрация: `/accounts/signup/`
  - Профиль (редактирование): `/news/profile/` (требуется вход)
  - Стать автором: `/news/become-author/` (требуется вход)
- Группы и права:
  - При миграции автоматически создаются группы `common` и `authors`.
  - Новые пользователи автоматически добавляются в группу `common`.
  - Кнопка "Стать автором" добавляет пользователя в группу `authors`.
  - Группа `authors` имеет права `add_post` и `change_post`, что даёт доступ к созданию и редактированию новостей/статей.
- Конфигурация allauth (актуальные ключи):
  - `ACCOUNT_LOGIN_METHODS = {'email', 'username'}` — вход по имени пользователя или email.
  - `ACCOUNT_SIGNUP_FIELDS = ['username*', 'password1*', 'password2*']` — email опционален.

## Логирование
Проект использует встроенную систему логирования Django с разделением по уровням и назначению:

### В режиме DEBUG (DEBUG=True)
Логи выводятся в консоль с разными форматерами:
- **DEBUG** — общая отладочная информация: `%(asctime)s %(levelname)s %(message)s`
- **WARNING** — предупреждения с указанием пути к файлу: `%(asctime)s %(levelname)s %(message)s %(pathname)s`
- **ERROR** — ошибки с полной информацией об исключениях: `%(asctime)s %(levelname)s %(message)s %(pathname)s %(exc_info)s`

### В продакшене (DEBUG=False)
Логи записываются в файлы в корне проекта:
- **`general.log`** — общие логи уровня INFO и выше (django.*)
  - Формат: `%(asctime)s %(levelname)s %(module)s %(message)s`
- **`errors.log`** — ошибки из запросов (django.request, django.server, django.template, django.db.backends)
  - Формат: `%(asctime)s %(levelname)s %(message)s %(pathname)s %(exc_info)s`
- **`security.log`** — события безопасности (django.security)
  - Формат: `%(asctime)s %(levelname)s %(module)s %(message)s`
- **Email админам** — критические ошибки также отправляются по email (требуется настройка SMTP)

### Настройка
Все настройки логирования находятся в `newsportal/settings.py` (секция `LOGGING`). Вы можете изменить уровни логирования, форматеры и обработчики под свои требования.

## Структура проекта

```
NewsPortal/
├── newsportal/              # Основной модуль Django
│   ├── settings.py          # Настройки проекта (БД, Celery, логирование, allauth)
│   ├── urls.py              # Корневой URL-конфиг
│   ├── celery.py            # Конфигурация Celery
│   ├── wsgi.py              # WSGI entry point
│   └── asgi.py              # ASGI entry point
├── news/                    # Приложение новостного портала
│   ├── models.py            # Модели: Author, Category, Post, PostCategory, Comment, CategorySubscription
│   ├── views.py             # Представления (новости, статьи, подписки, профиль)
│   ├── urls.py              # URL-маршруты приложения
│   ├── signals.py           # Сигналы (группы, права, приветственное письмо)
│   ├── tasks.py             # Celery-задачи (email-уведомления, дайджест)
│   ├── admin.py             # Админка Django
│   ├── templatetags/        # Пользовательские теги и фильтры
│   │   ├── censor_filters.py   # Фильтр цензуры
│   │   └── social_helpers.py   # Хелперы для социальных кнопок
│   └── management/commands/ # Команды управления
│       ├── delete_news.py   # Удаление новостей по категории
│       └── send_weekly_digest.py  # Еженедельная рассылка
├── templates/               # HTML-шаблоны
│   ├── default.html         # Базовый шаблон
│   ├── news/                # Шаблоны новостей и статей
│   └── account/             # Шаблоны django-allauth (вход, регистрация)
├── docs/                    # Документация
│   └── django_shell_commands.txt  # Полезные команды для Django shell
├── db.sqlite3               # База данных SQLite (development)
├── manage.py                # CLI Django
└── README.md                # Этот файл
```

## Технологический стек
- **Backend**: Django 4.2+
- **База данных**: SQLite (development) / PostgreSQL (production рекомендуется)
- **Аутентификация**: django-allauth (локальная + OAuth через Яндекс)
- **Фоновые задачи**: Celery 5.3+
- **Брокер сообщений**: Redis 5.0+
- **Email**: Django Email (консоль в dev, SMTP в production)
- **Логирование**: встроенная система Django

## Полезное
- Команды для Django shell: `docs/django_shell_commands.txt` (примеры создания тестовых данных, работы с рейтингами и выборками, настройка OAuth).
- URL-маршруты: `newsportal/urls.py` + `news/urls.py`.
- Конфигурация Celery: `newsportal/celery.py` + `newsportal/settings.py` (CELERY_*)
- Система прав: группы `common` и `authors` создаются автоматически при миграции.

---

**Лицензия:** Учебный проект
**Обновлено:** 22.01.2026 (актуализация документации)
