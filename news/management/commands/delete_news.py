from django.core.management.base import BaseCommand, CommandError
from news.models import Post, Category


class Command(BaseCommand):
    help = 'Удаляет все новости из указанной категории'

    def add_arguments(self, parser):
        parser.add_argument('category_name', type=str, help='Название категории')

    def handle(self, *args, **options):
        category_name = options['category_name']
        
        try:
            category = Category.objects.get(name=category_name)
        except Category.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Категория "{category_name}" не найдена'))
            return

        self.stdout.write(f'Вы действительно хотите удалить все статьи в категории {category.name}? yes/no')
        answer = input()

        if answer.lower() == 'yes':
            posts = Post.objects.filter(categories=category)
            count = posts.count()
            posts.delete()
            self.stdout.write(self.style.SUCCESS(f'Успешно удалено {count} постов из категории {category.name}'))
        else:
            self.stdout.write(self.style.ERROR('Отменено'))
