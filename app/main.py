from fastapi import FastAPI, Query, APIRouter, HTTPException, status, Depends, Request
from sqlalchemy import select  # para conseguir manipular a base de dados
from models import User as UserModel
from models import UserIn as UserModelIn
from schema import User as UserSchema
from schema import UserValidate as UserSchemaValidate
from database import SessionDB, create_db_and_tables
from typing import List, Annotated
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os

from pydantic import BaseModel, ValidationError


# usado para authenticacao
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext  # usado para hash
from typing import Union, Any


SALT = os.getenv("SALT")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# modelo pydantic que vai ser usado para a token endpoint response
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str
    exp: str


from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


# faz codigo abaixo para criar os banco de dados quando a aplicação é inciada
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


# modulo usado para verificar, fazer hash  etc..
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# funcao para verificar se esta certo o hash
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password + str(SALT), hashed_password)


# retorna o password como hash
def get_password_hash(password):
    return pwd_context.hash(password + str(SALT))


# Utility function to generate a new access token.
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


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
    "/registrar/",
    response_model=Token,  # Usa o schema para a resposta
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
    # Cria o hash da senha antes de salvar no banco
    hashed_password = get_password_hash(usuario.senha)
    novo_usuario = UserModelIn(
        **usuario.model_dump(exclude_unset=True)
    )  # coloca todas as infirmacoes de usuario na configuração de UserModel
    novo_usuario.senha = hashed_password
    session.add(novo_usuario)
    session.commit()
    session.refresh(novo_usuario)
    # Gera o token JWT com o ID ou email do usuário
    access_token = create_access_token(data={"email": novo_usuario.email})
    return Token(access_token=access_token, token_type="bearer")


@router_user.post(
    "/login",
    response_model=Token,
    tags=["Usuarios"],
    summary="Login de usuario",
    description="Autentica um usuario e retorna o token JWT se as credenciais estiverem corretas.",
)
def login(session: SessionDB, usuario: UserSchemaValidate):
    usuario_banco = session.query(UserModel).filter_by(email=usuario.email).first()
    if not usuario_banco:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email Não foi encontrado cadastrado.",
        )
    if not verify_password(usuario.senha, usuario_banco.senha):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="senha incorreta",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": usuario_banco.email})
    return Token(access_token=access_token, token_type="bearer")


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403, detail="Invalid authentication scheme."
                )
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(
                    status_code=403, detail="Invalid token or expired token."
                )
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str) -> bool:
        isTokenValid: bool = False

        try:
            payload = jwt.decode(jwtoken, SECRET_KEY, algorithms=ALGORITHM)
        except:
            payload = None
        if payload:
            isTokenValid = True

        return isTokenValid


async def get_current_user(
    session: SessionDB, token: str = Depends(JWTBearer())
) -> UserSchema:
    try:
        # Decodifica o token JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # verificando se esta expirado
        if datetime.fromtimestamp(payload["exp"]) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (jwt.PyJWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Obtém o usuário pelo email do token
    user = session.query(UserModelIn).filter_by(email=payload["email"]).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find user",
        )

    return UserSchema.model_validate(user)


@app.get("/me", tags=["Usuarios"], summary="Get details of currently logged in user")
async def get_me(user: UserSchema = Depends(get_current_user)):
    return user


# @router_user.get(
#     "/consultar",
#     tags=["Usuarios"],
#     summary="Retorna dados de uma Api",
#     description="Verifica se o usuário esta cadastrado com o token JWT e se estiver retorna o dado de uma API",
# )
# def consulta(session: SessionDB, token: str = Depends(oauth2_scheme)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#         token_data = TokenData(username=username)
#     except InvalidTokenError:
#         raise credentials_exception
#     return {"msg": "Deu certo! Voce é bravo!"}


app.include_router(router_user, prefix="/usuarios", tags=["Usuarios"])
