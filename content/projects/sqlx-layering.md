+++
title = "sqlx-conditional-queries-layering: Compile-Time SQL Macros in Rust"
description = "A Rust declarative macro library for composing, extending, and merging conditional SQL query templates on top of SQLx."
date = 2025-03-20
weight = 3

[extra]
category = "Rust / Metaprogramming"
author = "@o-thiago"
github = "https://github.com/o-thiago/sqlx-conditional-queries-layering"
stack = ["Rust", "SQLx", "Declarative Macros", "paste", "macro_metavar_expr"]
+++

## Motivation

When working with **SQLx** in Rust, the [`sqlx_conditional_queries`](https://docs.rs/sqlx_conditional_queries) crate allows defining conditional template variables (`{#var}`) using `match` expressions within a query string.

However, it lacked a way to reuse or compose these templates. Every query had to declare all its variables and matching logic in a single monolithic call. I built **`sqlx_conditional_queries_layering`** to allow:
1. Creating base query templates that generate reusable macros.
2. Injecting additional variables into existing templates.
3. Merging two or more independent query templates into a single final macro at compile time.

---

## How it works

The crate provides three main declarative macros:

### 1. Defining a template (`create_conditional_query_as!`)

Generates a macro capturing the defined conditional variables:

```rust
let keehee = [Keehee::OwO, Keehee::UmU, Keehee::UwU]
    .choose(&mut rand::thread_rng())
    .cloned()
    .unwrap_or_default();

// Generates the $keehee_query macro with the #keehee variable
create_conditional_query_as!(
    $keehee_query,
    #keehee = match keehee {
        Keehee::OwO => "owo",
        Keehee::UmU => "umu",
        Keehee::UwU => "uwu"
    }
);
```

### 2. Extending a template (`supply_sql_variables_to_query_as!`)

Adds new variables to an existing template without modifying the original:

```rust
// Adds the #name variable to $keehee_query and generates $lewdy_query
supply_sql_variables_to_query_as!(
    $keehee_query as lewdy_query,
    #name = match Fall::Through {
        _ => "{keehee_name}",
    }
);
```

### 3. Merging templates (`merge_sql_query_as!`)

Combines variables from multiple templates into a single compound macro:

```rust
// Merges lewdy_query and return_id_query into lewdy_with_return_id_query
merge_sql_query_as!($(lewdy, return_id));

// Executes the resulting query
let result = lewdy_with_return_id_query!(
    BigID,
    "INSERT INTO {#keehee} (name) VALUES ({#name}) {#return_id}",
)
.fetch_one(&pool)
.await;
```

---

## Implementation Details

- **`macro_metavar_expr` (`$dollar:tt`):** Allows a declarative macro in Rust to generate another nested `macro_rules!` definition without `$` identifier collisions.
- **`paste!`:** Used to generate internal helper macros (`[<_DO_NOT_USE_EXPLICITLY_ $name>]`) that carry token trees between macros.
- **Zero runtime cost:** All template resolution and merges resolve strictly during compilation.

---

## Repository

- **GitHub:** [github.com/o-thiago/sqlx-conditional-queries-layering](https://github.com/o-thiago/sqlx-conditional-queries-layering)
- **Author:** Thiago Macedo Mendes (`@o-thiago`)
