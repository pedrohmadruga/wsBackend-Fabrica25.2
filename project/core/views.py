from django.views.generic import TemplateView, CreateView
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
import requests, math
from django.urls import reverse_lazy
from .models import CustomUser

class HomeView(TemplateView):
    template_name = 'home.html'

class BookSearchView(TemplateView):
    template_name = "search.html"
    RESULTS_PER_PAGE = 21
    MAX_VISIBLE_PAGES = 5
    MAX_RESULTS_API = RESULTS_PER_PAGE * 5 # máximo de 5 páginas

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q", "")
        page_str = self.request.GET.get("page", "1")  # pega a página como string
        try:
            page = int(page_str)
            if page < 1:
                page = 1
        except ValueError:
            page = 1
        total_items = 0
        results = []

        if query:
            start_index = (page - 1) * self.RESULTS_PER_PAGE # pula os livros já exibidos para não haver repetição na página seguinte
            url = "https://www.googleapis.com/books/v1/volumes"
            params = {
                "q": f"intitle:{query}", # Buscar apenas os livros com a query de busca em seu título
                "maxResults": self.RESULTS_PER_PAGE,
                "startIndex": start_index,
                "printType": "books" # Mostra apenas livros, excluindo revistas, artigos, jornais, etc
            }
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                total_items = data.get("totalItems", 0)
                for item in data.get("items", []):
                    info = item.get("volumeInfo", {}) # dicionário com os dados do livro retornado pela API
                    results.append({
                        "title": info.get("title", "Sem título"),
                        "authors": ", ".join(info.get("authors") or ["Desconhecido"]),
                        "publisher": info.get("publisher", "Desconhecido"),
                        "published_date": info.get("publishedDate", "Desconhecido"),
                        "thumbnail": (info.get("imageLinks") or {}).get("thumbnail"), # Tenta pegar a imagem do livro, se existir
                    })

                total_items = min(data.get("totalItems", 0), self.MAX_RESULTS_API)
        total_pages = math.ceil(total_items / self.RESULTS_PER_PAGE)

        context["results"] = results
        context["query"] = query
        context["pages"] = list(range(1, total_pages + 1))
        context["page"] = page
        context["total_pages"] = total_pages
        return context
    
class CustomLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True
    next_page = reverse_lazy('home')

class SignUpView(CreateView):
    model = CustomUser
    template_name = 'signup.html'
    fields = ["username", "email", "password"]
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data["password"])
        user.save()
        login(self.request, user)
        return super().form_valid(form)