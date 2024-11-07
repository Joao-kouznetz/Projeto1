from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import Session
from models import User, Base
from sqlalchemy import select
from typing import Annotated  # para ter validaçÕes
from fastapi import Depends  #

# criando database

# https://docs.sqlalchemy.org/en/20/tutorial/engine.html
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url)
# A url indica, qual é a database que utilizaremos,
# echo indica para colocar todos os SQL it emits to a Python logger that will write to standard out.


def create_db_and_tables():
    Base.metadata.create_all(
        engine
    )  # isso cria todas as base de dados Emitting DDL to the database from an ORM mapping¶


# Criando sessão


# Uma Session é o que armazena o objeto na memória e mantêm validando e vendo a as alterações
#  necessárias com os dados depois é utilizado a engine para comunicar com a base de dados
def get_session():
    with Session(engine) as session:
        yield session


# vai se criado uma dependencia com o fastAPI com yiel para fazer uma a sessão para cada
# requisição isso garante que so tem uma sessão por requisição
SessionDB = Annotated[Session, Depends(get_session)]


# # Criando instâncias
# UsuarioJ = User(nome="UsuarioJ", email="usuario@gmail.com", senha="1234")

# # adicionando na base de dados
# session.add(UsuarioJ)
# session.commit()

# usuarios = select(User.nome, User.id, User.email, User.senha)
# with Session(engine) as session:
#     for row in session.execute(usuarios):
#         print(row)
