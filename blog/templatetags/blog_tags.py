from django import template
from django.db.models import Count

from ..models import Post

register = template.Library()  # регистрации пользовательских тегов и фильтров в системе


# Однако можно указать явно, как обращаться к тегу из шаблонов.
# Для этого достаточно передать в декоратор аргумент name – @register.simple_tag(name='my_tag').
@register.simple_tag  # для регистрации нового тега
def total_posts():
    return Post.published.count()


@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
    # Чтобы задать любое другое количество статей, используйте такую запись: {% show_latest_posts 3 %}.
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}


@register.simple_tag
def get_most_commented_posts(count=5):
    return Post.published.annotate(total_comments=Count('comments')
                                   ).order_by('-total_comments')[:count]
