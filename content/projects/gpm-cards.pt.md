+++
title = "GPMecatrônica Cards & Plataforma Web"
description = "Aplicação web full-stack e sistema gerador de cartões para os membros do Grupo de Pesquisa em Mecatrônica do IFRO."
date = 2025-04-10
weight = 2

[extra]
category = "Web / Full-Stack"
author = "@o-thiago"
github = "https://github.com/o-thiago/gpm-cards"
stack = ["Next.js 14", "TypeScript", "PostgreSQL", "Tailwind CSS", "Nix / process-compose", "Docker"]
+++

## Visão Geral

Desenvolvida para o grupo de pesquisa **GPMecatrônica** no Instituto Federal de Rondônia (IFRO), esta aplicação atua como vitrine interativa, gerenciador de credenciais de membros e gerador dinâmico de cartões de identificação para eventos científicos e perfis acadêmicos.

---

## Decisões Técnicas & Arquitetura

- **Arquitetura Full-Stack:** Desenvolvida sobre o **Next.js** App Router com **TypeScript**, utilizando server actions, renderização de imagem dinâmica e tipagem rigorosa de esquemas de banco de dados.
- **Ambiente de Desenvolvimento Reproduzível com Nix:** Criação de pipeline de orquestração local de serviços via `flake.nix` e `process-compose-flake`, automatizando a inicialização de bancos PostgreSQL locais e padronizando os runtimes para toda a equipe do laboratório sem passos manuais.
- **Conteinerização Determinística:** Builds de imagens Docker em camadas geradas diretamente pelo Nix (`dockerTools.buildLayeredImage`), garantindo imagens de produção compactas e seguras.

```nix
/* Composição declarativa de processos locais via process-compose */
services.postgres."gpm-cards-db" = {
  enable = true;
  initialDatabases = [ { name = "gpm-cards"; } ];
  initialScript.after = ''
    CREATE ROLE postgres WITH SUPERUSER LOGIN PASSWORD 'postgres';
  '';
};
```

---

## Impacto

Padronizou a geração de identidades visuais de membros, credenciamento para congressos científicos e acelerou o onboarding de novos bolsistas e pesquisadores no grupo.
