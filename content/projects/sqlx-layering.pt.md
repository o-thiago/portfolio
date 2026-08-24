+++
title = "sqlx-conditional-queries-layering: Metaprogramação de Queries SQL em Tempo de Compilação"
description = "Biblioteca em Rust para composição modular, herança de variáveis e fusão de templates de consultas SQL condicionais sobre o SQLx."
date = 2025-03-20
weight = 3

[extra]
category = "Rust / Metaprogramação"
author = "@o-thiago"
github = "https://github.com/o-thiago/sqlx-conditional-queries-layering"
stack = ["Rust", "SQLx", "Macros Declarativas", "Metaprogramação", "paste", "macro_metavar_expr"]
+++

## Visão Geral & O Problema

No desenvolvimento de aplicações de alta performance em **Rust** utilizando **SQLx**, construir queries SQL dinâmicas (como filtros de busca opcionais, inserts condicionais ou nomes de tabelas variáveis) frequentemente esbarra em um dilema: como manter segurança estrita de tipos sem recorrer a repetição excessiva de código ou abrir mão da ergonomia do compilador.

A biblioteca [`sqlx_conditional_queries`](https://docs.rs/sqlx_conditional_queries) introduziu o conceito de variáveis de template (`{#var}`) mapeadas para expressões `match` em Rust. No entanto, ela não possuía suporte a composição: todas as variáveis e regras condicionais precisavam ser declaradas de forma monolítica em cada chamada de query. Não havia como:
1. Criar templates de consultas reutilizáveis como blocos base.
2. Estender templates existentes com novas variáveis condicionais.
3. Mesclar (merge) dois ou mais templates independentes em uma única query combinada.

O **`sqlx_conditional_queries_layering`** (desenvolvido e publicado no GitHub por **`@o-thiago`**) resolve esse problema fornecendo um motor declarativo de camadas e composição de macros em Rust.

---

## Conceitos Arquiteturais Centrais

A biblioteca fornece três macros declarativas centrais que operam em tempo de compilação:

### 1. Definição de Templates (`create_conditional_query_as!`)

Cria um template parametrizado que gera dinamicamente uma nova macro capturando as variáveis condicionais definidas:

```rust
let keehee = [Keehee::OwO, Keehee::UmU, Keehee::UwU]
    .choose(&mut rand::thread_rng())
    .cloned()
    .unwrap_or_default();

// Gera uma nova macro `$keehee_query` capturando a variável condicional #keehee
create_conditional_query_as!(
    $keehee_query,
    #keehee = match keehee {
        Keehee::OwO => "owo",
        Keehee::UmU => "umu",
        Keehee::UwU => "uwu"
    }
);
```

### 2. Injeção e Extensão de Variáveis (`supply_sql_variables_to_query_as!`)

Recebe uma macro de template existente e injeta novas variáveis condicionais nela, criando um alias estendido sem alterar a macro original:

```rust
// Estende $keehee_query com a variável #name, criando $lewdy_query
supply_sql_variables_to_query_as!(
    $keehee_query as lewdy_query,
    #name = match Fall::Through {
        _ => "{keehee_name}",
    }
);
```

### 3. Fusão de Templates (`merge_sql_query_as!`)

Mescla dois ou mais templates de query independentes em uma única macro unificada, combinando todas as variáveis condicionais em uma execução atômica:

```rust
// Faz o merge de lewdy_query e return_id_query gerando lewdy_with_return_id_query
merge_sql_query_as!($(lewdy, return_id));

// Executa a query composta com todos os parâmetros mesclados
let result = lewdy_with_return_id_query!(
    BigID,
    "INSERT INTO {#keehee} (name) VALUES ({#name}) {#return_id}",
)
.fetch_one(&pool)
.await;
```

---

## Engenharia Interna de Metaprogramação em Rust

Para permitir que macros gerem, herdem e mesclem outras macros no sistema de regras de sintaxe do Rust (`macro_rules!`), a biblioteca emprega técnicas avançadas de compilador:

- **Escape de Metavariáveis (`$dollar:tt`):** Utilização do recurso `#![feature(macro_metavar_expr)]` para permitir que uma macro gere dinamicamente a definição de outra `macro_rules!` sem colisão de identificadores `$`.
- **Protocolo de Dispatch Interno com `paste!`:** Uso da biblioteca `paste::paste!` para criar identificadores internos (`[<_DO_NOT_USE_EXPLICITLY_ $name>]` e `[<_$name _DO_NOT_USE_EXPLICITLY>]`) que operam como canais privados de troca de árvores de sintaxe (TokenTrees) entre macros.
- **Fusão Variádica Recursiva:** Suporte a merge em cadeia (`merge_sql_query_as!(a, b, c)`) através de recursão por pares de templates até a expansão completa.

---

## Benefícios e Impacto

1. **Zero Overhead em Runtime:** Toda a resolução de templates, injeção de variáveis e merge de macros ocorre exclusivamente durante a compilação.
2. **Reutilização e Composição (DRY):** Elimina ramificações duplicadas em SQL para autenticação, multitenancy, filtros de busca e paginação.
3. **Segurança de Tipos com SQLx:** Mantém o mapeamento fortemente tipado de resultados do banco de dados.

- **Repositório:** [github.com/o-thiago/sqlx-conditional-queries-layering](https://github.com/o-thiago/sqlx-conditional-queries-layering)
- **Autor:** Thiago Macedo Mendes (`@o-thiago` / `@o-thiago`)
