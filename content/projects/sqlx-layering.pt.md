+++
title = "Padrão de Camadas para Consultas SQL Dinâmicas em Rust com SQLx"
description = "Arquitetura tipada e modular em Rust para composição dinâmica de consultas SQL via SQLx QueryBuilder mantendo garantias de tipo em tempo de compilação."
date = 2025-03-20
weight = 4

[extra]
category = "Rust / Sistemas"
github = "https://github.com/o-thiago/sqlx-conditional-queries-layering"
stack = ["Rust", "SQLx", "PostgreSQL", "Rust Assíncrono", "Tipagem Estática"]
+++

## Motivação do Projeto

Ao construir filtros de busca e paginação complexos no backend, desenvolvedores frequentemente enfrentam um dilema:
1. **ORMs Pesados:** Alto custo de abstração em tempo de execução e perda de controle sobre a consulta gerada.
2. **Concatenação de Strings:** Risco de injeção de SQL e fragilidade no bind de parâmetros.

Este projeto implementa um padrão de **Camadas de Consulta (Query Layering)** em **Rust** utilizando o **SQLx**, garantindo segurança e clareza na montagem atômica de queries parametrizadas.

```rust
pub struct UserFilter {
    pub search: Option<String>,
    pub is_active: Option<bool>,
    pub role: Option<UserRole>,
}

impl UserFilter {
    pub fn apply_to<'a, DB: sqlx::Database>(
        &'a self,
        builder: &mut sqlx::QueryBuilder<'a, DB>,
    ) {
        if let Some(ref search) = self.search {
            builder.push(" AND (username ILIKE ");
            builder.push_bind(format!("%{}%", search));
            builder.push(" OR email ILIKE ");
            builder.push_bind(format!("%{}%", search));
            builder.push(")");
        }
        
        if let Some(active) = self.is_active {
            builder.push(" AND is_active = ");
            builder.push_bind(active);
        }
    }
}
```
