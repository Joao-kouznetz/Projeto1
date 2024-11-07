from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
import hashlib
from dotenv import load_dotenv
import os
import uuid
from uuid import UUID


# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Obter o salt da variável de ambiente
SALT = os.getenv("SALT")


# Função para calcular o SHA-256
def calculate_sha256(input_string: str) -> str:
    # Cria um objeto hash SHA-256
    sha256_hash = hashlib.sha256()
    # Atualiza o hash com a string convertida para bytes
    input_with_salt = input_string + str(SALT)
    sha256_hash.update(input_with_salt.encode("utf-8"))
    # Retorna o hash em formato hexadecimal
    return sha256_hash.hexdigest()


def generate_uuid():
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user_table"
    id: Mapped[UUID] = mapped_column(
        # default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
        default=uuid.uuid4,
    )
    nome: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100))
    senha: Mapped[str] = mapped_column(String(100))

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.nome!r}, email={self.email!r}, senha={self.senha!r})"


class UserIn(User):
    def __init__(self, **kw):
        super().__init__(**kw)
        # self.id = generate_uuid()
        self.senha = calculate_sha256(self.senha)
