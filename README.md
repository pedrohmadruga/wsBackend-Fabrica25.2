
# Fábrica de Software Desafio – Gerenciador de livros com API Google Books

Este projeto é um **gerenciador de livros online** chamado **Bookly**, que permite aos usuários buscar livros usando a **API do Google Books**, adicionar livros à sua lista pessoal, editar o status de leitura e remover livros da lista. A aplicação é construída com **Django** e oferece autenticação de usuários, gerenciamento de listas e visualização de detalhes de cada livro.

----------

## Funcionalidades

-   Cadastro e login de usuários (somente com username único).
    
-   Busca de livros usando a API do Google Books.
    
-   Visualização de resultados de busca com detalhes básicos (título, autores, editora, data de publicação e capa).
    
-   Adição de livros à lista pessoal do usuário.
    
-   Edição do status de leitura de cada livro (Planejo ler, Lendo, Completo, Abandonado).
    
-   Remoção de livros da lista do usuário.
    
-   Visualização detalhada de livros, incluindo descrição, páginas, categorias, idioma e link de preview.
    
-   Filtros por status na lista de livros do usuário.
    
-   Mensagens de confirmação ao adicionar, editar ou remover livros.
    
-   Layout responsivo com Bootstrap 4.
    

----------

## Tecnologias Usadas

-   Python 3.12.3
    
-   Django 4.x
    
-   PostgreSQL 16
    
-   Bootstrap 4
        
-   API Google Books (para busca de livros)
    

----------

## Instalação

1.  **Clone o repositório:**
    
    ```bash
    git clone https://github.com/pedrohmadruga/wsBackend-Fabrica25.2
    cd wsBackend-Fabrica25.2
    
    ```
    
2.  **Crie e ative um ambiente virtual:**
    
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows: venv\Scripts\activate
    
    ```
    
3.  **Instale os requisitos:**
    
    ```bash
    pip install -r requirements.txt
    
    ```
    
4.  **Configure o banco de dados:**
    
    No `settings.py`, configure a conexão com o PostgreSQL:
    
    ```python
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'bookly_db',
            'USER': 'bookly_user',
            'PASSWORD': 'bookly_password',
            'HOST': 'localhost',
            'PORT': 5432,
        }
    }
    
    ```
    
    Ou, para SQLite, para desenvolvimento simples:
    
    ```python
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / "db.sqlite3",
        }
    }
    
    ```
    
5.  **Execute as migrations:**
    
    ```bash
    python manage.py migrate
    
    ```
    
6.  **Crie um superusuário (opcional):**
    
    ```bash
    python manage.py createsuperuser
    
    ```
    
7.  **Execute a aplicação:**
    
    ```bash
    python manage.py runserver
    
    ```
    
    Acesse `http://127.0.0.1:8000` no navegador.
    

----------

## Uso da aplicação
- **Login:** Faça login pelo link da página inicial para desfrutar de todas as funcionalidades da aplicação

-   **Busca de livros:** Digite o nome de um livro no campo de busca e clique em "Buscar".
    
-   **Adicionar à lista:** Clique em "Adicionar à lista" no resultado da busca.
    
-   **Editar status:** Na página do perfil, use o dropdown de status para atualizar o progresso de leitura.
    
-   **Remover livro:** Clique no botão "Remover" na página do perfil.
    
-   **Visualizar detalhes:** Clique no botão "Ver detalhes" para acessar informações completas do livro, diretamente da API do Google Books.
    
-   **Filtrar por status:** Use o dropdown de filtro na página de perfil para mostrar apenas livros com um status específico.
----------

## Estrutura do projeto

```
bookly/
├── core/                   Pacote da aplicação principal
│   ├── models.py           Modelos de usuários e livros
│   ├── views.py            Views para busca, perfil, adicionar/remover livros
│   ├── urls.py             URLs da aplicação
│   └── templates/          Templates HTML (search, profile, detail, base, login, signup)
├── bookly/                 Pacote principal do projeto
│   ├── settings.py         Configurações do Django, banco e apps
│   ├── urls.py             URLs globais
├── manage.py               Comando para rodar o Django
├── requirements.txt        Lista de dependências
```

----------

## Autor

Este projeto foi feito unicamente por **Pedro Madruga** para fins acadêmicos, como desafio para ingressar no projeto **Fábrica de Software** da UNIPÊ.
