from django.views.generic import TemplateView, CreateView, ListView
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from .models import CustomUser, UserBook, Book
from django.shortcuts import redirect, get_object_or_404
from django.http import Http404
from django.views import View
import requests, math

class HomeView(TemplateView):
    template_name = 'home.html'


# Busca livros na API do google
class BookSearchView(TemplateView):
    template_name = "search.html"
    RESULTS_PER_PAGE = 21
    MAX_VISIBLE_PAGES = 5
    MAX_RESULTS_API = RESULTS_PER_PAGE * 5 # máximo de 5 páginas

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q", "") # string de pesquisa enviada pelo usuário
        page_str = self.request.GET.get("page", "1")  

        # pega a página como string
        try:
            page = int(page_str)
            if page < 1:
                page = 1
        except ValueError:
            page = 1
        total_items = 0 # contador de livros na página para paginação
        results = [] # lista de dicionários contendo as informações dos livros

        if query:
            start_index = (page - 1) * self.RESULTS_PER_PAGE # pula os livros já exibidos para não haver repetição na página seguinte
            url = "https://www.googleapis.com/books/v1/volumes"
            params = {
                "q": f"intitle:{query}", # Buscar apenas os livros com a query de busca em seu título
                "maxResults": self.RESULTS_PER_PAGE,
                "startIndex": start_index,
                "printType": "books" # Mostra apenas livros, excluindo revistas, artigos, jornais, etc
            }
            response = requests.get(url, params=params) # faz a chamada para a API do Google Books
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
    

# Página de login
class CustomLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True
    next_page = reverse_lazy('home')


# Página para cadastrar novo usuário
class SignUpView(CreateView):
    model = CustomUser
    template_name = 'signup.html'
    fields = ["username", "email", "password"]
    success_url = reverse_lazy("home") # redireciona para home após o cadastro

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data["password"]) # salva a senha como hash
        user.save()
        login(self.request, user) # loga automaticamente após o cadastro
        return super().form_valid(form)
    

# Exibe a lista de livros na lista do usuário
class ProfileView(LoginRequiredMixin, ListView): #LoginRequiredMixin: apenas usuários logados podem acessar
    model = UserBook
    template_name = 'profile.html'
    context_object_name = 'books'
    paginate_by = 12

    # retorna os livros com filtro de status, caso selecionado
    def get_queryset(self):
        queryset = UserBook.objects.filter(user=self.request.user).order_by("-added_at")
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_selected"] = self.request.GET.get("status", "")
        return context


# Adiciona livro à lista do usuário
class AddBookToListView(LoginRequiredMixin, View):
    # Recebe dados do formulário (preenchido automaticamente com os dados do livro)
    def post(self, request, *args, **kwargs):
        # Dados do livro vindos do formulário
        google_book_id = request.POST.get("google_book_id")
        title = request.POST.get("title")
        authors = request.POST.get("authors", "")
        publisher = request.POST.get("publisher", "")
        published_date = request.POST.get("published_date", "")
        thumbnail = request.POST.get("thumbnail", "")

        # cria ou pega o objeto Book no banco de dados
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

        # cria ou pega o objeto UserBook no banco de dados
        UserBook.objects.get_or_create(
            user=request.user,
            book=book_obj,
            defaults={"status": "plan"}
        )
        
        if created:
            messages.success(request, f'Livro "{book_obj.title}" adiconado à sua lista!')
        else:
            messages.info(request, f'Livro "{book_obj.title}" já estava na sua lista.')
        return redirect('search')

    
# Remove livro da lista do usuário
class RemoveBookFromListView(LoginRequiredMixin, View):
    # Recebe o ID do livro por formulário preenchido automaticamente
    def post(self, request, userbook_id, *args, **kwargs):
        userbook = get_object_or_404(UserBook, id=userbook_id, user=request.user)
        title = userbook.book.title
        userbook.delete()
        messages.success(request, f'Livro "{title}" removido de sua lista')
        return redirect('profile')
    

# Atualiza o status de um livro na lista do usuário (lendo, planejo ler...)
class UpdateBookStatusView(LoginRequiredMixin, View):
    def post(self, request, userbook_id, *args, **kwargs):
        userbook = get_object_or_404(UserBook, id=userbook_id, user=request.user)
        title = userbook.book.title
        new_status = request.POST.get("status")
        if new_status in dict(UserBook.STATUS_CHOICES):
            userbook.status = new_status
            userbook.save()
        new_status_display = userbook.get_status_display() # get_status_display pega o valor "amigável" do status ("Planejo ler" ao invés de "plan")
        messages.success(request, f'Alterado status de "{title}" para "{new_status_display}"')
        return redirect("profile")
    

# Exibe informações completas do livro com base nos dados da API
class BookDetailView(TemplateView):
    template_name = 'book_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        google_book_id = kwargs.get("google_book_id") # Pega o id do livro pela URL
        url = f"https://www.googleapis.com/books/v1/volumes/{google_book_id}"
        response = requests.get(url) # Pega os dados completos na API do google

        if response.status_code != 200:
            raise Http404("Livro não encontrado")

        data = response.json()
        info = data.get("volumeInfo", {})

        context.update({
            "google_book_id": google_book_id,
            "title": info.get("title", "Sem título"),
            "subtitle": info.get("subtitle", ""),
            "authors": ", ".join(info.get("authors") or ["Desconhecido"]),
            "publisher": info.get("publisher", "Desconhecido"),
            "published_date": info.get("publishedDate", "Desconhecido"),
            "description": info.get("description", "Sem descrição"),
            "page_count": info.get("pageCount", "Desconhecido"),
            "categories": ", ".join(info.get("categories") or ["Sem categoria"]),
            "thumbnail": (info.get("imageLinks") or {}).get("thumbnail"),
            "language": info.get("language", "Desconhecido"),
            "preview_link": info.get("previewLink"),
        })
        return context