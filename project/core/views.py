from django.views.generic import TemplateView, CreateView, ListView
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
import requests, math
from django.urls import reverse_lazy
from .models import CustomUser, UserBook, Book

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
                        "google_book_id": item.get("id"),
                        "title": info.get("title", "Sem título"),
                        "authors": ", ".join(info.get("authors") or ["Desconhecido"]),
                        "publisher": info.get("publisher", "Desconhecido"),
                        "published_date": info.get("publishedDate", "Desconhecido"),
                        "thumbnail": (info.get("imageLinks") or {}).get("thumbnail"),
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
    
class ProfileView(LoginRequiredMixin, ListView):
    model = UserBook
    template_name = 'profile.html'
    context_object_name = 'books'
    paginate_by = 10

    def get_queryset(self):
        return UserBook.objects.filter(user=self.request.user).order_by("-added_at")
    
from django.shortcuts import redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from core.models import UserBook

class AddBookToListView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        # Dados do livro vindos do formulário
        google_book_id = request.POST.get("google_book_id")
        title = request.POST.get("title")
        authors = request.POST.get("authors", "")
        publisher = request.POST.get("publisher", "")
        published_date = request.POST.get("published_date", "")
        thumbnail = request.POST.get("thumbnail", "")

        # cria ou pega o objeto Book
        book_obj, created = Book.objects.get_or_create(
            google_book_id=google_book_id,
            defaults={
                "title": title,
                "authors": authors,
                "publisher": publisher,
                "published_date": published_date,
                "thumbnail": thumbnail,
            }
        )

        # cria UserBook
        UserBook.objects.get_or_create(
            user=request.user,
            book=book_obj,
            defaults={"status": "plan"}
        )

        return redirect(request.META.get("HTTP_REFERER", "home"))