# Como rodar o código

## 1. Criar o Ambiente Virtual

Navegue até a raiz do seu projeto e execute o seguinte comando:

```bash
python -m venv venv
```

## 2. Ativando virtual Enviroment

No Windows:

```bash
.\venv\Scripts\activate
```

No MAC/Linux:

```bash
source venv/bin/activate
```

Após ativar o ambiente virtual, você verá o nome do ambiente (venv) prefixado no seu terminal

## 3. Instalando Dependencias

As dependências do projeto estão listadas no arquivo requirements.txt. Para instalar as dependências, execute o seguinte comando:

```bash
pip install -r requirements.txt
```

## Colocar api para rodar

```bash
fastapi dev main.py
```

Com docker ficou bem mais facil: agora é so fazer o seguinte qunado for rodar a primeira vez

```
docker-compose up --build
```

e quando ja river rodado isso fazer o seguinte:

```
docker-compose up
```

e para descer o app fazer

```
docker-compose down
```

precisa dar build se você mudar algo na configuração do docker

# Informações sobre como o projeto é desenvolvido no arquivo DEVELOPER.md
