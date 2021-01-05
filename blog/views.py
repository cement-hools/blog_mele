from django.core.mail import send_mail
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView

from .forms import EmailPostForm
from .models import Post


def post_list(request):
    object_list = Post.published.all()
    paginator = Paginator(object_list, 2)  # По 2 статьи на каждой странице.
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # Если страница не является целым числом, возвращаем первую страницу.
        posts = paginator.page(1)
    except EmptyPage:
        # Если номер страницы больше, чем общее количество страниц, возвращаем последнюю.
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html',
                  {'page': page, 'posts': posts})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, status='published',
                             publish__year=year,
                             publish__month=month, publish__day=day)
    return render(request, 'blog/post/detail.html', {'post': post})


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'  # использовать posts в качестве переменной контекста HTML-шаблона, в которой будет храниться список объектов. Если не указать атрибут context_object_name, по умолчанию используется переменная object_list;
    paginate_by = 2
    template_name = 'blog/post/list.html'


def post_share(request, post_id):
    # Получение статьи по идентификатору.
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method == 'POST':
        # Форма была отправлена на сохранение.
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Все поля формы прошли валидацию.
            cd = form.cleaned_data
            # Отправка электронной почты.
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = ('{} ({}) recommends you reading "'
                       '{}"').format(cd['name'], cd['email'], post.title)
            message = ('Read "{}" at {}\n\n{}\'s comments: '
                       '{}').format(post.title, post_url, cd['name'],
                                    cd['comments'])
            send_mail(subject, message, 'admin@myblog.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request,
                  'blog/post/share.html',
                  {'post': post, 'form': form, 'sent': sent}
                  )
