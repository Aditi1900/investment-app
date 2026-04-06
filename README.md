# System Architecture
```mermaid
flowchart TD
    A([App.run])

    A --> B[Cli]
    A --> C[Frontend]
    B -.-> VIZ([Visualizer])
    VIZ ~~~ ERR[/Errors/]
    ERR ~~~ G

    B --> D([Client])
    C --> D

    D --> E[Sanitizer]

    E -->|CLI| G[Validator]
    E -->|Frontend| F[FrontendApi]
    F --> G

    G --> H[Service]
    G --> EXT[External API]
    EXT ~~~ H
    H --> DOM[Domain Models]
    H --> I[(Database)]
    H --> EXT

    style A fill:#F1EFE8,stroke:#888780,color:#444441
    style D fill:#F1EFE8,stroke:#888780,color:#444441
    style VIZ fill:#F1EFE8,stroke:#888780,color:#444441
    style B fill:#EEEDFE,stroke:#534AB7,color:#3C3489
    style C fill:#EEEDFE,stroke:#534AB7,color:#3C3489
    style E fill:#E1F5EE,stroke:#0F6E56,color:#085041
    style F fill:#F1EFE8,stroke:#888780,color:#444441
    style G fill:#EAF2FB,stroke:#185FA5,color:#0C447C
    style H fill:#EAF2FB,stroke:#185FA5,color:#0C447C
    style I fill:#FAECE7,stroke:#993C1D,color:#712B13
    style EXT fill:#FAEEDA,stroke:#854F0B,color:#633806
    style DOM fill:#F1EFE8,stroke:#888780,color:#444441
    style ERR fill:#FCEBEB,stroke:#A32D2D,color:#791F1F
```

# Feature Pipelines

Core feature pipelines with traversal through layers and main method calls excluding helper functions.

---

## Create Account
```mermaid
flowchart TD
    A([client])
    A --> B[Sanitizer.sanitize_credentials]
    B -->|CLI| D[Validator.account_validator]
    B -->|Frontend| C[FrontendApi.create_account]
    C --> D
    D --> E[Service.create_account]
    E --> F[(Database.insert_user)]

    style A fill:#F1EFE8,stroke:#888780,color:#444441
    style B fill:#E1F5EE,stroke:#0F6E56,color:#085041
    style C fill:#F1EFE8,stroke:#888780,color:#444441
    style D fill:#EAF2FB,stroke:#185FA5,color:#0C447C
    style E fill:#EAF2FB,stroke:#185FA5,color:#0C447C
    style F fill:#FAECE7,stroke:#993C1D,color:#712B13
```

## Find Account
```mermaid
flowchart TD
    A([client])
    A --> B[Sanitizer.sanitize_credentials]
    B -->|CLI| D[Validator.account_validator]
    B -->|Frontend| C[FrontendApi.find_account]
    C --> D
    D --> E[Service.find_account]
    E --> F[(Database.pull_user + pull_portfolios + pull_stocks)]

    style A fill:#F1EFE8,stroke:#888780,color:#444441
    style B fill:#E1F5EE,stroke:#0F6E56,color:#085041
    style C fill:#F1EFE8,stroke:#888780,color:#444441
    style D fill:#EAF2FB,stroke:#185FA5,color:#0C447C
    style E fill:#EAF2FB,stroke:#185FA5,color:#0C447C
    style F fill:#FAECE7,stroke:#993C1D,color:#712B13
```

## Fund Account
```mermaid
flowchart TD
    A([client])
    A --> B[Sanitizer.sanitize_funds_request]
    B -->|CLI| D[Validator.fund_validator]
    B -->|Frontend| C[FrontendApi.fund_account]
    C --> D
    D --> E[Service.fund_account]
    E --> F[(Database.update_funds)]

    style A fill:#F1EFE8,stroke:#888780,color:#444441
    style B fill:#E1F5EE,stroke:#0F6E56,color:#085041
    style C fill:#F1EFE8,stroke:#888780,color:#444441
    style D fill:#EAF2FB,stroke:#185FA5,color:#0C447C
    style E fill:#EAF2FB,stroke:#185FA5,color:#0C447C
    style F fill:#FAECE7,stroke:#993C1D,color:#712B13
```

## Create/Remove Portfolio
```mermaid
flowchart TD
    A([client])
    A --> B[Sanitizer.sanitize_portfolio_name]
    B -->|CLI| D[Validator.portfolio_validator]
    B -->|Frontend| C[FrontendApi.create/remove_portfolio]
    C --> D
    D --> E[Service.create/remove_portfolio]
    E --> F[(Database.insert/delete_portfolio)]

    style A fill:#F1EFE8,stroke:#888780,color:#444441
    style B fill:#E1F5EE,stroke:#0F6E56,color:#085041
    style C fill:#F1EFE8,stroke:#888780,color:#444441
    style D fill:#EAF2FB,stroke:#185FA5,color:#0C447C
    style E fill:#EAF2FB,stroke:#185FA5,color:#0C447C
    style F fill:#FAECE7,stroke:#993C1D,color:#712B13
```

## Execute Buy/Sell
```mermaid
flowchart TD
    A([client])
    A --> B[Sanitizer.sanitize_shares_request]
    B -->|CLI| D[Validator.shares_request_validator]
    B -->|Frontend| C[FrontendApi.execute_buy/sell]
    C --> D
    D --> E[Service.execute_buy/sell]
    E --> F[(Database.update/insert/delete_stock)]

    style A fill:#F1EFE8,stroke:#888780,color:#444441
    style B fill:#E1F5EE,stroke:#0F6E56,color:#085041
    style C fill:#F1EFE8,stroke:#888780,color:#444441
    style D fill:#EAF2FB,stroke:#185FA5,color:#0C447C
    style E fill:#EAF2FB,stroke:#185FA5,color:#0C447C
    style F fill:#FAECE7,stroke:#993C1D,color:#712B13
```

# Program Documentation Guidelines

Fields marked **"if N/A – None"** must still appear with the literal value `None` so readers know the field was considered.

---

## Classes
```python
# PURPOSE:
#    - <ClassName> provides <X> abstraction
#    - <why the abstraction exists>
```

## Functions
```python
# INPUT: if N/A - None
#    - <param_name>(type); <what it represents>
# OUTPUT: if N/A - None
#    - <var_name>(type); <what it represents>
# PRECONDITION: if N/A - None
#    - <param_name or state>; <value constraint>
# POSTCONDITION: if N/A - None
#    - <param or state>; <observable guarantee after return>
# RAISES: if N/A - None
#    - <ExceptionType>; <condition that triggers it>
def function_name(param_name: type) -> type:
    return var_name
```

---

## Style Rules

| Rule | Description |
|---|---|
| **Semicolons** | Separate name/type from description with `"; "` |
| **Indentation** | Labels flush-left; entries indented with TAB |
| **Types** | Use Python builtins or `typing` module. Project-defined types listed in [Types](#types) below. Persistent types carry `id` (database primary key). Nested collections may be abbreviated in higher layers when element types are defined in a referenced `POSTCONDITION`. |
| **Constraints** | State value constraints, not types — `n > 0` not `"must be int"` |
| **Guarantees** | Describe observable state, not implementation details |
| **Be brief** | Short phrase per entry, not full sentences |

---

# Program Models

## Types

| Type | Description |
|---|---|
| `User` | Represents a user account; holds login, balance, and a collection of portfolios |
| `Portfolio` | Represents a named collection of stocks |
| `Stock` | Represents a stock holding; ticker and quantity |

---

## Request Models

JSON request bodies sent to the Frontend API.

**LogoutRequest**
```json
{
    "session_id": "string"
}
```

**CredsRequest**
```json
{
    "login": "string",
    "password": "string"
}
```

**FundsRequest**
```json
{
    "session_id": "string",
    "funds_requested": 0.00
}
```

**PortfolioRequest**
```json
{
    "session_id": "string",
    "name": "string"
}
```

**TransactionRequest**
```json
{
    "session_id": "string",
    "portfolio_name": "string",
    "ticker": "string",
    "quantity": 0
}
```

---

## Response Models

JSON response bodies returned by the Frontend API.

**StockData**
```json
{
    "ticker": "AAPL",
    "quantity": 4
}
```

**PortfolioData**
```json
{
    "name": "tech",
    "stocks": {
        "AAPL": { }
    }
}
```
> `stocks` values follow the `StockData` schema above.

**UserData**
```json
{
    "login": "john_doe",
    "balance": 1000.00,
    "portfolios": {
        "tech": { }
    }
}
```
> `portfolios` values follow the `PortfolioData` schema above.