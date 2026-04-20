# PetLife Loyalty Platform

## Sobre o repositório

Este repositório concentra a base do produto de fidelização comercializado para a **PetLife**, estruturado para apoiar a operação de relacionamento recorrente com clientes por meio de campanhas de fidelidade, acompanhamento de compras e gestão de resgates.

Mais do que uma aplicação administrativa, o projeto foi concebido como um ativo digital de negócio: uma solução pronta para ser operada como produto, com identidade visual personalizada, painel interno de gestão e experiência pública para consulta de progresso do cliente final.

Seu propósito é oferecer à PetLife uma plataforma simples de operar no dia a dia, mas suficientemente sólida para sustentar uma estratégia de retenção, recompra e valorização do relacionamento com a base de clientes.

## Contexto do produto

A proposta do produto nasce da necessidade de transformar a fidelização em um processo estruturado, visível e mensurável. Em vez de depender de controles manuais, cartões físicos ou registros dispersos, a plataforma centraliza a jornada de campanha em um único ambiente.

No contexto da PetLife, isso significa permitir que a empresa:

- registre compras vinculadas a clientes cadastrados;
- acompanhe a evolução individual de cada participante na campanha ativa;
- configure recompensas e critérios de elegibilidade;
- mantenha uma presença visual alinhada à marca;
- disponibilize uma consulta pública para que o próprio cliente acompanhe seu progresso.

O sistema, portanto, cumpre uma função operacional e estratégica ao mesmo tempo: organiza a execução interna do programa de fidelidade e fortalece a percepção de valor da marca perante o cliente.

## Objetivo de negócio

O produto foi desenhado para apoiar três frentes centrais:

- **retenção de clientes**, incentivando recorrência por meio de recompensas claras;
- **padronização operacional**, reduzindo falhas em registros de compras e resgates;
- **fortalecimento da marca**, ao oferecer uma experiência própria, personalizada e coerente com a identidade visual da empresa.

Em termos práticos, a solução ajuda a PetLife a transformar compras recorrentes em relacionamento contínuo, com visibilidade tanto para a equipe interna quanto para o cliente atendido.

## Escopo funcional

Atualmente, o sistema contempla os principais componentes de operação do programa:

- **Painel administrativo** para autenticação e gestão interna;
- **Configuração institucional da empresa**, incluindo nome, cores, logo, banner e informações de contato;
- **Gestão de campanha ativa**, com definição de meta de compras e recompensa;
- **Cadastro e manutenção de clientes**;
- **Registro de compras** e acompanhamento do ciclo de fidelidade;
- **Controle de resgates**;
- **Tela pública de consulta de progresso**, voltada ao cliente final.

## Arquitetura da solução

O projeto foi desenvolvido em **Django**, com estrutura orientada a aplicações internas e separação clara de responsabilidades. A base atual está organizada em módulos que representam os domínios principais do produto:

- `core`: dashboard, estrutura base e visão geral da operação;
- `accounts`: autenticação e fluxo de acesso ao painel;
- `company`: identidade visual e dados institucionais da empresa;
- `loyalty`: campanha ativa, regras de fidelidade e resgates;
- `customers`: cadastro de clientes, compras e consulta pública.

## Modelo de operação

Esta implementação segue uma abordagem **single-tenant**, isto é, cada cliente comercial opera em sua própria instância da aplicação, com banco de dados, identidade visual e campanha independentes.

No cenário da PetLife, isso garante:

- isolamento de dados;
- autonomia de branding;
- simplicidade de implantação;
- menor complexidade operacional no MVP comercial.

As premissas atuais do modelo são:

- existe apenas uma configuração institucional por instância;
- existe apenas uma campanha principal ativa por vez;
- cada operação possui sua própria base de dados.

## Stack tecnológica

- Python
- Django
- Django Templates
- PostgreSQL em produção
- Docker
- Gunicorn
- Railway

## Execução local

### Com Docker

1. Copie `.env.example` para `.env`.
2. Suba os serviços:

```bash
docker compose up --build
```

3. Em outro terminal, crie o superusuário:

```bash
docker compose exec web python manage.py createsuperuser
```

4. Acesse:

- Painel administrativo: `http://localhost:8000/accounts/login/`
- Consulta pública: `http://localhost:8000/customers/progress/`

### Sem Docker

1. Crie e ative um ambiente virtual.
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Execute as migrations:

```bash
python manage.py migrate
```

4. Crie o superusuário:

```bash
python manage.py createsuperuser
```

5. Inicie o servidor:

```bash
python manage.py runserver
```

## Fluxo inicial de configuração

Após o primeiro acesso administrativo:

1. Configure a empresa em `/company/settings/`;
2. Cadastre a campanha ativa em `/loyalty/campaign/`;
3. Registre os clientes em `/customers/`;
4. Associe compras e acompanhe o progresso de cada cliente;
5. Disponibilize a consulta pública em `/customers/progress/`.

## Deploy

O projeto está preparado para implantação via Docker, com uso recomendado de PostgreSQL em produção.

### Referência de publicação no Railway

1. Crie o projeto a partir deste repositório.
2. Adicione um banco PostgreSQL.
3. Configure as variáveis de ambiente:

- `SECRET_KEY`
- `DEBUG=False`
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`
- `DATABASE_URL`
- `STATIC_URL`
- `STATIC_ROOT`
- `MEDIA_URL`
- `MEDIA_ROOT`
- `TIME_ZONE`

4. Garanta persistência para arquivos enviados em `MEDIA_ROOT`.
5. Finalize o deploy.
6. Execute a criação do superusuário no ambiente publicado:

```bash
python manage.py createsuperuser
```

## Considerações finais

Este repositório representa a base de um produto com vocação comercial, desenhado para entregar valor operacional imediato e, ao mesmo tempo, consolidar uma frente de fidelização digital para a PetLife.

Sua relevância não está apenas na tecnologia empregada, mas no papel que exerce dentro da estratégia de relacionamento da empresa: transformar recompra em vínculo, rotina operacional em processo e atendimento recorrente em experiência de marca.
