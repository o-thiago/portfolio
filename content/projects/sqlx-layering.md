+++
title = "sqlx-conditional-queries-layering: Compile-Time SQL Query Metaprogramming"
description = "A powerful Rust macro library for composable, layered, and mergeable conditional SQL query templates on top of SQLx."
date = 2025-03-20
weight = 3

[extra]
category = "Rust / Metaprogramming"
author = "@o-thiago"
github = "https://github.com/o-thiago/sqlx-conditional-queries-layering"
stack = ["Rust", "SQLx", "Declarative Macros", "Metaprogramming", "paste", "macro_metavar_expr"]
+++

## Overview & The Problem

When developing database-intensive applications in **Rust** using **SQLx**, developers often encounter a challenge: how to build dynamic, conditional SQL queries (such as dynamic search filters, conditional inserts, or environment-dependent table names) without losing type safety or having to rewrite repetitive conditional matching boilerplate.

While the crate [`sqlx_conditional_queries`](https://docs.rs/sqlx_conditional_queries) introduced conditional template variables (`{#var}`) mapped to Rust `match` expressions, it lacked composability. In standard `sqlx_conditional_queries`, all query variables and conditionals had to be declared monolithically within each individual query call. There was no way to:
1. Create reusable base query templates.
2. Extend existing query templates with new conditional variables.
3. Merge multiple independent query templates into a single compound query.

**`sqlx_conditional_queries_layering`** (published on GitHub by **`@o-thiago`**) solves this by introducing a declarative macro layering and composition engine in Rust.

---

## Core Architectural Concepts

The library provides three core declarative macros that generate and compose code during compilation:

### 1. Template Definition (`create_conditional_query_as!`)

Defines a parameterized query template that generates a new reusable macro capturing the defined conditional variables:

```rust
let keehee = [Keehee::OwO, Keehee::UmU, Keehee::UwU]
    .choose(&mut rand::thread_rng())
    .cloned()
    .unwrap_or_default();

// Generates a reusable `$keehee_query` macro with #keehee variable
create_conditional_query_as!(
    $keehee_query,
    #keehee = match keehee {
        Keehee::OwO => "owo",
        Keehee::UmU => "umu",
        Keehee::UwU => "uwu"
    }
);
```

### 2. Variable Injection & Extension (`supply_sql_variables_to_query_as!`)

Takes an existing query template macro and injects additional conditional variables into it, creating an extended alias without modifying the original:

```rust
// Extends $keehee_query with the #name variable, creating $lewdy_query
supply_sql_variables_to_query_as!(
    $keehee_query as lewdy_query,
    #name = match Fall::Through {
        _ => "{keehee_name}",
    }
);
```

### 3. Query Merging (`merge_sql_query_as!`)

Merges two or more independent query templates into a single compound macro, combining all conditional variables into a unified query pipeline:

```rust
// Merges lewdy_query and return_id_query into lewdy_with_return_id_query
merge_sql_query_as!($(lewdy, return_id));

// Execute the merged query atomically
let result = lewdy_with_return_id_query!(
    BigID,
    "INSERT INTO {#keehee} (name) VALUES ({#name}) {#return_id}",
)
.fetch_one(&pool)
.await;
```

---

## Advanced Macro Metaprogramming Under the Hood

To make macros mergeable and extensible in Rust's declarative macro system (`macro_rules!`), the library implements advanced compiler-level techniques:

- **Dollar-Escaping (`$dollar:tt`):** Uses metavar expression escaping (`#![feature(macro_metavar_expr)]`) to generate nested `macro_rules!` definitions dynamically from within parent macros.
- **Internal Dispatch Protocols (`paste!`):** Employs `paste::paste!` identifier concatenation to generate hidden helper macros (`[<_DO_NOT_USE_EXPLICITLY_ $name>]` and `[<_$name _DO_NOT_USE_EXPLICITLY>]`) that serve as private communication channels for passing AST token trees between independent macro definitions.
- **Variadic Template Folding:** Supports cascading merges (`merge_sql_query_as!(a, b, c)`) by recursively expanding pairwise merges into a single merged token stream.

---

## Key Benefits

1. **Zero Runtime Overhead:** All template expansions, variable injections, and macro merges resolve entirely during compilation.
2. **DRY & Composable:** Eliminates duplicate SQL branching across services by modularizing common predicates (tenancy, auditing, filtering, pagination).
3. **Type-Safe Dynamic SQL:** Retains compile-time guarantees and typed deserialization with SQLx.

- **Repository:** [github.com/o-thiago/sqlx-conditional-queries-layering](https://github.com/o-thiago/sqlx-conditional-queries-layering)
- **Author:** Thiago Macedo Mendes (`@o-thiago` / `@o-thiago`)
