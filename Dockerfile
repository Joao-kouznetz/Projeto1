FROM python:3.10-slim 

# Definindo o diretório de trabalho
WORKDIR /usr/local/app

# Copiando o conteúdo da pasta local 'app' para dentro do container
COPY app ./

ENV salt="18274393"
ENV sqlite_file_name="database.db"
ENV SECRET_KEY="2e6e8cc741f246604c750dcc672fed67c877b2fe9f77eafaa41245ce91b5a0d3"

# Instalando as dependências
# Caso você tenha um requirements.txt, utilize:
# COPY requirements.txt ./  # Copia o arquivo requirements.txt para dentro do container
RUN pip install "fastapi[standard]"
RUN pip install SQLAlchemy
RUN pip install pydantic
RUN pip install uuid
RUN pip install PyJWT
RUN pip install passlib

# Garantir que a pasta do app tenha permissões corretas para o SQLite
RUN chmod -R 777 /usr/local/app

# Expondo a porta para acesso externo
EXPOSE 8000


# Comando padrão para rodar a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]