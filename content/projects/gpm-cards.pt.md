+++
title = "GPMecatrônica Cards: Plataforma Web de Membros"
description = "Aplicação web desenvolvida com Next.js e PostgreSQL para cadastro e geração de cartões de membros do GPMecatrônica (IFRO)."
date = 2025-04-10
weight = 2

[extra]
category = "Web / Full-Stack"
author = "@o-thiago"
github = "https://github.com/o-thiago/gpm-cards"
stack = ["Next.js", "TypeScript", "PostgreSQL", "Tailwind CSS", "Nix", "Docker"]
+++

## O que é o projeto

Aplicação web desenvolvida para o grupo de pesquisa **GPMecatrônica** do IFRO (Campus Porto Velho Calama). O sistema serve para cadastrar membros do laboratório, exibir seus perfis e gerar cartões digitais de identificação para eventos e apresentações científicas.

---

## Como foi feito

- **Frontend & Backend:** Feito com **Next.js** (App Router) e **TypeScript**, com rotas de API tipadas e estilização em Tailwind CSS.
- **Ambiente Local com Nix:** Utilizei o `process-compose` no Nix Flakes para subir o banco de dados PostgreSQL localmente de forma automática. Com isso, novos membros do laboratório conseguem rodar o projeto local com um único comando, sem precisar instalar e configurar o PostgreSQL manualmente no sistema operacional.
- **Docker:** Criação de contêineres Docker para facilitar o deploy e padronizar as dependências em produção.

```nix
/* Exemplo da configuração do PostgreSQL local com process-compose */
services.postgres."gpm-cards-db" = {
  enable = true;
  initialDatabases = [ { name = "gpm-cards"; } ];
  initialScript.after = ''
    CREATE ROLE postgres WITH SUPERUSER LOGIN PASSWORD 'postgres';
  '';
};
```

---

## Repositório

- **GitHub:** [github.com/o-thiago/gpm-cards](https://github.com/o-thiago/gpm-cards)
- **Autor:** Thiago Macedo Mendes (`@o-thiago`)
