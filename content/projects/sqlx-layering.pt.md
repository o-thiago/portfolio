+++
title = "Padrão de Camadas para Consultas SQL Dinâmicas em Rust com SQLx"
description = "Arquitetura tipada e modular em Rust para composição dinâmica de consultas SQL via SQLx QueryBuilder mantendo garantias de tipo em tempo de compilação."
date = 2025-03-20
weight = 4

[extra]
category = "Rust / Sistemas"
author = "@o-thiago"
github = "https://github.com/o-thiago/sqlx-conditional-queries-layering"
stack = ["Rust", "SQLx", "PostgreSQL", "Rust Assíncrono", "Tipagem Estática"]
+++

## Motivação & Contexto

No desenvolvimento de motores de busca, paginação e filtros complexos em sistemas backend, desenvolvedores enfrentam com frequência dois extremos:
1. **ORMs Pesados:** Alto custo de overhead em tempo de execução e perda de controle fino sobre a execução das queries SQL.
2. **Concatenação de Strings:** Elevado risco de injeção de SQL (SQL injection) e fragilidade no bind de parâmetros.

Este projeto de código aberto (publicado sob o handle **`@o-thiago`**) propõe um **Padrão de Camadas para Consultas** em **Rust** utilizando a biblioteca **SQLx**, garantindo segurança de tipos em tempo de compilação e composição modular de predicados SQL.

---

## Padrão Arquitetural

Ao encapsular predicados de filtragem em métodos puros que operam sobre instâncias de `sqlx::QueryBuilder`, regras isoladas de negócio (filtros de status, intervalos temporais, busca textual multicoluna e ordenação dinâmica) podem ser encadeadas em uma única execução atômica:

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

---

## Benefícios

- Zero overhead de alocação além do vetor de parâmetros do banco.
- Proteção nativa e estrita contra SQL injection via queries parametrizadas.
- Fragmentos de consulta modulares e fáceis de testar em microsserviços.
- Repositório mantido no GitHub: [github.com/o-thiago/sqlx-conditional-queries-layering](https://github.com/o-thiago/sqlx-conditional-queries-layering).
