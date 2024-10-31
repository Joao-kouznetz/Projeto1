from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List
from typing import Optional
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import select
from sqlalchemy import Table
from sqlalchemy import Column


# https://docs.sqlalchemy.org/en/20/tutorial/engine.html
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url)
# A url indica, qual é a database que utilizaremos,
# echo indica para colocar todos os SQL it emits to a Python logger that will write to standard out.


class Base(DeclarativeBase):
    pass


association_table = Table(
    "association_table",
    Base.metadata,
    Column("address_id", ForeignKey("address_table.id"), primary_key=True),
    Column("propriedade_id", ForeignKey("propriedade_table.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "user_table"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    fullname: Mapped[Optional[str]]  # esse optional indica que pode ser nulo o valor
    addresses: Mapped[List["Address"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"


class Address(Base):
    __tablename__ = "address_table"
    id: Mapped[int] = mapped_column(primary_key=True)
    rua: Mapped[str] = mapped_column(String(50))
    Complemento: Mapped[Optional[str]]  # esse optional indica que pode ser nulo o valor
    user_id: Mapped[int] = mapped_column(ForeignKey("user_table.id"))
    user: Mapped["User"] = relationship(back_populates="addresses")
    propriedades: Mapped[List["Propriedade"]] = relationship(
        secondary=association_table, back_populates="enderecos"
    )

    def __repr__(self) -> str:
        return f"Address(id={self.id!r}, rua={self.rua!r}, complemento={self.Complemento!r})"


class Propriedade(Base):
    __tablename__ = "propriedade_table"
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(50))
    enderecos: Mapped[List["Address"]] = relationship(
        secondary=association_table, back_populates="propriedades"
    )


Base.metadata.create_all(
    engine
)  # isso cria todas as base de dados Emitting DDL to the database from an ORM mapping¶

# Criando sessão
session = Session(engine)

# Criando instâncias
UsuarioJ = User(name="UsuarioJ", fullname="Squidward Tentacles")
# criando endereco
AddressJ = Address(rua="Jeronimo da veiga", Complemento="11 B")
# criando propriedade
Propriedade1 = Propriedade(nome="Primeira")
Propriedade2 = Propriedade(nome="Segunda")
# adicionando o endereco no usuario
UsuarioJ.addresses.append(AddressJ)
# adicionando as propriedades no endereco
AddressJ.propriedades.append(Propriedade1)
AddressJ.propriedades.append(Propriedade2)


session.add(UsuarioJ)
# session.add(krabs)
session.commit()

# t = (
#     select(User.name, User.id, Address.rua, Address.id, Propriedade.nome)
#     .join_from(User, Address)
#     .join_from(Address, Propriedade)
#     .where(User.name == "UsuarioJ")
# )
t = (
    select(User.name, User.id, Address.rua, Address.id, Propriedade.nome)
    .join(User.addresses)  # Join entre User e Address usando o relacionamento
    .join(Address.propriedades)  # Join entre Address e Propriedade
    .where(User.name == "UsuarioJ")
)
with Session(engine) as session:
    for row in session.execute(t):
        print(row)
# # f = select(Address.user_id, Address.rua)
# # with Session(engine) as session:
# #     for row in session.execute(f):
# #         print(row)

# print()
