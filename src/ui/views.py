from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required

from .forms import QueryForm
from nlp import extractor
from engine.CrawlerEngine import CrawlerEngine


def login(request):
    return render(request, 'ui/login.html')


@login_required(login_url='/')
def home(request):
    if request.method == 'POST':
        form = QueryForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']
            crawler = CrawlerEngine()
            crawler.add_query(request.user.id, query)
            messages.add_message(request, messages.SUCCESS,
                                 'Query successfully added.')
            return render(request, 'ui/home.html', {'form': QueryForm()})
        else:
            messages.add_message(request, messages.ERROR, 'Invalid query.')
    form = QueryForm()
    return render(request, 'ui/home.html', {'form': form})


@login_required(login_url='/')
def query(request):
    crawler = CrawlerEngine()
    keywords = request.GET.get('keywords').split(',')
    keywords = filter(lambda keyword: len(keyword) > 0, keywords)
    urls = crawler.get_urls(keywords)
    return render(request, 'ui/query.html', {'urls': urls})


@login_required(login_url='/')
def queries(request):
    crawler = CrawlerEngine()
    queries = map(lambda query: (query, ','.join(extractor.keywords(query))),
                  crawler.get_queries(request.user.id))
    return render(request, 'ui/queries.html', {'queries': queries})


def logout(request):
    auth_logout(request)
    return redirect('/')