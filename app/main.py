from fastapi import FastAPI, Query, APIRouter, HTTPException, status
from sqlalchemy import select  # para conseguir manipular a base de dados
from models import User as UserModel
from models import UserIn as UserModelIn
from schema import User as UserSchema

# from schema import UserIn as UserSchemaIn
from database import SessionDB, create_db_and_tables
from typing import List, Annotated
from contextlib import asynccontextmanager


# faz codigo abaixo para criar os banco de dados quando a aplicação é inciada
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello World"}


router_user = APIRouter()


@router_user.get(
    "/usuarios/",
    response_model=List[UserSchema],  # Usa o schema para a resposta
    tags=["Usuarios"],
    summary="Obter todos os usuarios",
    description="Retorna a lista de todos os usuarios disponíveis (cadastrados).",
)
def read_usuarios(
    session: SessionDB,
    offset: int = 0,  # coloca quanto de offset ent se for 10 nao retorna os 10 primeiros
    limit: Annotated[
        int, Query(le=100)
    ] = 100,  # limite de quantidade para ser retornado
):
    stmt = select(UserModel).offset(offset).limit(limit)
    usuarios = session.execute(stmt)
    # Converte os objetos ORM para Pydantic (UserSchema) usando model_validate
    locais_resposta = [UserSchema.model_validate(user) for user, in usuarios]
    return locais_resposta


@router_user.post(
    "/usuario/",
    response_model=UserSchema,  # Usa o schema para a resposta
    tags=["Usuarios"],
    summary="Criar novo usuario",
    description="Adiciona um novo usuario com as informações fornecidas.",
)
def create_usuario(usuario: UserSchema, session: SessionDB):
    email_existe = session.query(UserModelIn).filter_by(email=usuario.email).first()
    if email_existe:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email já cadastrado.",
        )

    novo_usuario = UserModelIn(
        **usuario.model_dump(exclude_unset=True)
    )  # coloca todas as infirmacoes de usuario na configuração de UserModel
    session.add(novo_usuario)
    session.commit()
    session.refresh(novo_usuario)
    return novo_usuario


app.include_router(router_user, prefix="/usuarios", tags=["Usuarios"])
