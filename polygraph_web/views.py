from django.shortcuts import render, redirect
from django.core.validators import URLValidator, ValidationError
from engine.models import DocumentModel

from engine import Engine
from engine import Searcher

# Create your views here.


def search(request):
    results = []

    if not request.method == "POST":
        return redirect('/')

    query = request.POST.get('query')
    if query is None or query == "":
        return redirect('/')

    result_dict = Searcher.search_result(query.split()).items()
    result_dict.sort(key=lambda x: x[1], reverse=True)
    for item in result_dict:
        results.append(DocumentModel.get(DocumentModel.id == item[0]))

    return render(request, 'polygraph/searchResult.html', {
        'documents': results[:10],
        'query': query,
    })


def home(request):
    return render(request, "polygraph/home.html", {})


def indexURL(request):
    if request.method == "POST":
        urls_for_indexing = []
        uv = URLValidator(schemes=['http', 'https'])
        engine = Engine.Engine()

        urls_from_form = request.POST.get('urls')
        if urls_from_form:
            list_urls = [url.strip() for url in urls_from_form.split("\n")]
            for url in list_urls:
                try:
                    uv(url)
                except ValidationError:
                    continue

                urls_for_indexing.append(url)

        file_with_urls = request.FILES.get('urlfile')
        if file_with_urls:
            list_urls = [url.strip() for url in file_with_urls]
            for url in list_urls:
                try:
                    uv(url)
                except ValidationError:
                    continue

                urls_for_indexing.append(url)

        if len(urls_for_indexing):
            engine.load_queue(urls_for_indexing)
            engine.start_crawler(max_depth=2, max_width=10, isAsync=False)
            engine.start_ranker(isAsync=False, isRepeat=False)
            msg = 'OK'
        else:
            msg = 'No valid URLs'

    else:
        msg = None

    return render(request, 'polygraph/indexURL.html', {'msg': msg})

