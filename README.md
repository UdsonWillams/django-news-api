# News API

Um sistema completo para gerenciamento de notícias, planos e assinaturas usando Django REST Framework.

## 🛠️ Tecnologias e Frameworks

### Backend

- **Django 4.2+**: Framework web para desenvolvimento rápido e limpo
- **Django REST Framework**: API RESTful poderosa e flexível
- **PostgreSQL**: Sistema de banco de dados relacional (produção)
- **SQLite**: Banco de dados leve para desenvolvimento

### Autenticação e Segurança

- **JWT (JSON Web Tokens)**: Autenticação segura via Simple JWT
- **Django Permission System**: Sistema de permissões granular

### Documentação e Testes

- **DRF Spectacular**: Documentação automática de API com Swagger/OpenAPI
- **Pytest**: Framework de testes moderno e poderoso
- **Coverage**: Métricas de cobertura de testes

### Ferramentas de Desenvolvimento

- **Docker & Docker Compose**: Contêinerização para ambientes consistentes
- **Makefile**: Comandos simplificados para operações comuns
- **Ruff**: Formatação de código e linting em uma única ferramenta

## 📋 Requisitos

- Python 3.12 ou superior
- Docker e Docker Compose (opcional, para contêineres)
- PostgreSQL (para produção)
- **libpq-dev** e **python3-dev** (para desenvolvimento local)

## 🔧 Configuração do Ambiente

### 1. Clone o repositório

```bash
git clone https://github.com/udsonwillams/django-news-api
cd django-news-api
```

### 2. Instalar dependências do sistema (para desenvolvimento local)

Certifique-se de instalar as dependências necessárias para o ambiente local:

```bash
sudo apt update
sudo apt install libpq-dev python3-dev
```

### 3. Ambiente Virtual (para desenvolvimento local)

```bash
# Criar ambiente virtual
python3.12 -m venv venv

# Ativar ambiente virtual
# No Linux/Mac:
source venv/bin/activate
# No Windows:
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### 4. Configuração do arquivo .env

**⚠️ IMPORTANTE**: O sistema depende de variáveis de ambiente para funcionar corretamente.

1. Crie um arquivo `.env` na raiz do projeto
2. Use o exemplo abaixo como base para criar seu arquivo:

```bash
# Configurações básicas
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Configuração do banco de dados
DB_DEBUG=True  # Use True para SQLite em desenvolvimento
DB_NAME=jota-news
DB_USER=postgres
DB_PASS=your_password
DB_HOST=localhost
DB_PORT=5432
```

## ▶️ Executando o Projeto

### Usando Makefile (mais fácil)

```bash
# Executar servidor local com SQLite
make localserver

# Executar com Docker
make up

# Executar testes com cobertura
make coverage
```

### Usando Docker

```bash
# Construir e iniciar todos os serviços
docker-compose up

# Construir antes de iniciar (quando houver mudanças)
docker-compose up --build

# Executar em modo detached (background)
docker-compose up -d
```

### Executando Localmente

1. Certifique-se de que a variável `DB_DEBUG=1` está definida no arquivo `.env`
2. Execute as migrações do banco:
   ```bash
   python manage.py migrate
   ```
3. Crie um superusuário (admin):
   ```bash
   python manage.py createsuperuser
   ```
4. Inicie o servidor de desenvolvimento:
   ```bash
   python manage.py runserver
   ```

## 📚 Documentação da API

A documentação interativa da API está disponível nos seguintes endpoints quando o servidor está em execução:

- **Swagger UI**: `/api/swagger/` - Interface gráfica interativa
- **ReDoc**: `/api/redoc/` - Documentação mais limpa e legível
- **Exportar OpenAPI Schema**: `/api/schema/` - Baixar schema em formato JSON

## 🔍 Testes

Execute os testes com:

```bash
# Testes básicos
python manage.py test

# Testes com pytest (recomendado)
pytest

# Testes com relatório de cobertura
make coverage
```
