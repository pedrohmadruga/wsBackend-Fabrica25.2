from django.views.generic import TemplateView
import requests

class HomeView(TemplateView):
    template_name = 'home.html'

class BookSearchView(TemplateView):
    template_name = "search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q", "")
        results = []

        if query:
            url = "https://www.googleapis.com/books/v1/volumes"
            params = {
                "q": query,
                "maxResults": 20,
            }
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                for item in data.get("items", []):
                    info = item.get("volumeInfo", {})
                    results.append({
                        "title": info.get("title", "Sem título"),
                        "authors": ", ".join(info.get("authors") or ["Desconhecido"]),
                        "publisher": info.get("publisher", "Desconhecido"),
                        "published_date": info.get("publishedDate", "Desconhecido"),
                        "thumbnail": (info.get("imageLinks") or {}).get("thumbnail"),
                    })
        context["results"] = results
        context["query"] = query
        return context