# Porque o projeto foi desenvolvido?

Esse projeto tem como objetivo elaborar uma API RESTfull capaz de cadastrar e autenticar usuários. E dockernizar esse projeto para ser facilmente acessível.

# Tecnologias utilizadas

- FASTAPI (framework em python para desenvolvimento de APIs)
- SWAGGERUI (incluso no fastapi para desenvolvimento automático de documentação)
- PYDANTIC (método de tipagem para o python)
- JWT (método seguro para transmitir dados de maneira segura)
- SQLalchemy (ORM para conectar a base de dados)
- MYSQL (base de dados)
- Docker (método de conteinerização do aplicativo)
- MKDocs (maneira de fazer documentação utilizando markdown)

# Como rodar a aplicação?

Consegue acessar a aplicação acessada no seguinte link: [link codigo rodando na aws](http://a56a2d01abb4e409fb50de31aa7a7f2a-868540365.sa-east-1.elb.amazonaws.com/docs#/)

Para rodar a aplicação em a sua máquina local é apenas necessário utilizar o comando abaixo .

``` zsh
docker compose up
```

e para descer o app fazer

``` zsh
docker compose down
```

Caso deseje criar na maquina local é necessario mudar o `compose.yaml` para que ele de build e não rode com o arquivo

1. Clonar o repositório
2. Na pasta raiz do repositório copiar o docker-composeDEVELOPMENT para o arquivo docker-compose.yml
3. Com o docker baixado rodar o seguinte comando; `docker compose up --build`
4. Com isso você vai ter criado a sua própria imagem do app, voce pode utilizar agora os comandos `docker compose up` e `docker compose down` para colocar no ar e retirar do ar sua aplicação.

# Como abrir a documentação

Esse projeto tem dois tipos de documentação, uma feita com SWAGGERUI que é a documentação das apis e uma feita com Mkdocs. Para acessar a primeira  quando o projeto estiver rodando acessar a seguite url : `http://localhost:8000/docs`

A segunda você pode acessar pelos srquivos markdown na pasta `AppDocumentation/docs` ou de maneira mais estruturada voce roda o seguinte comando no terminal dentro da aba `appDocumeentation`

```bash
mkdocs serve
```

Com isso abrira uma url em que voce pode ler a documentação de forma mais organizada
