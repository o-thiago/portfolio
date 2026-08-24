+++
title = "sqlx-conditional-queries-layering: Macros para Queries SQL no Rust"
description = "Biblioteca de macros declarativas em Rust para compor, estender e mesclar templates de consultas SQL condicionais no SQLx."
date = 2025-03-20
weight = 3

[extra]
category = "Rust / Metaprogramação"
author = "@o-thiago"
github = "https://github.com/o-thiago/sqlx-conditional-queries-layering"
stack = ["Rust", "SQLx", "Macros Declarativas", "paste", "macro_metavar_expr"]
+++

## Motivação

Ao usar o **SQLx** no Rust, a biblioteca [`sqlx_conditional_queries`](https://docs.rs/sqlx_conditional_queries) permite definir variáveis condicionais (`{#var}`) com `match` dentro da string da query.

Porém, ela não oferecia uma forma direta de reutilizar ou combinar esses templates. Cada query precisava declarar todas as variáveis e condições do zero. O **`sqlx_conditional_queries_layering`** foi criado para permitir:
1. Criar templates de queries que geram novas macros reutilizáveis.
2. Injetar novas variáveis em templates existentes.
3. Mesclar (merge) duas ou mais queries em uma só em tempo de compilação.

---

## Como funciona

A biblioteca exporta três macros principais:

### 1. Criar template (`create_conditional_query_as!`)

Gera uma macro que encapsula as variáveis condicionais definidas:

```rust
let keehee = [Keehee::OwO, Keehee::UmU, Keehee::UwU]
    .choose(&mut rand::thread_rng())
    .cloned()
    .unwrap_or_default();

// Cria a macro $keehee_query com a variável condicional #keehee
create_conditional_query_as!(
    $keehee_query,
    #keehee = match keehee {
        Keehee::OwO => "owo",
        Keehee::UmU => "umu",
        Keehee::UwU => "uwu"
    }
);
```

### 2. Adicionar variáveis a um template (`supply_sql_variables_to_query_as!`)

Permite estender um template existente com novas variáveis sem alterar a macro original:

```rust
// Adiciona a variável #name ao $keehee_query e gera $lewdy_query
supply_sql_variables_to_query_as!(
    $keehee_query as lewdy_query,
    #name = match Fall::Through {
        _ => "{keehee_name}",
    }
);
```

### 3. Mesclar templates (`merge_sql_query_as!`)

Combina as variáveis de templates diferentes em uma única macro final:

```rust
// Mescla lewdy_query e return_id_query gerando lewdy_with_return_id_query
merge_sql_query_as!($(lewdy, return_id));

// Executa a query resultante
let result = lewdy_with_return_id_query!(
    BigID,
    "INSERT INTO {#keehee} (name) VALUES ({#name}) {#return_id}",
)
.fetch_one(&pool)
.await;
```

---

## Detalhes de Implementação

- **`macro_metavar_expr` (`$dollar:tt`):** Permite que uma macro do Rust gere o código de outra `macro_rules!` internamente sem conflito de identificadores `$`.
- **`paste!`:** Utilizado para gerar macros auxiliares internas (`[<_DO_NOT_USE_EXPLICITLY_ $name>]`) que transportam os tokens de uma macro para a outra.
- **Custo zero em runtime:** Todas as expansões e junções acontecem durante a compilação.

---

## Repositório

- **GitHub:** [github.com/o-thiago/sqlx-conditional-queries-layering](https://github.com/o-thiago/sqlx-conditional-queries-layering)
- **Autor:** Thiago Macedo Mendes (`@o-thiago`)
