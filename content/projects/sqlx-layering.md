+++
title = "SQLx Conditional Queries Layering Pattern"
description = "A modular, type-safe architecture in Rust for composing dynamic SQL queries using SQLx QueryBuilder without compromising compile-time safety."
date = 2025-03-20
weight = 4

[extra]
category = "Rust / Systems"
github = "https://github.com/o-thiago/sqlx-conditional-queries-layering"
stack = ["Rust", "SQLx", "PostgreSQL", "Async Rust", "Type Safety"]
+++

## Motivation & Problem Statement

When building complex search filters and pagination engines in backend systems, developers often struggle between two extremes:
1. **Bulky ORMs:** Heavy runtime overhead and loss of control over raw SQL execution.
2. **String Concatenation:** High risk of SQL injection and fragile parameter bindings.

This repository implements a composable **Query Layering Pattern** in **Rust** using **SQLx**, providing compile-time type guarantees alongside modular query predicate composition.

---

## Architectural Pattern

By encapsulating filter predicates into pure functions that operate on `sqlx::QueryBuilder`, individual filtering rules (e.g., status filters, date range filters, multi-column search, dynamic sorting) can be chained cleanly into a single atomic query execution:

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

## Benefits

- Zero runtime allocation overhead beyond parameter vectors.
- Complete protection against SQL injection via parameterized bindings.
- Highly testable and reusable query fragments across different microservices.
