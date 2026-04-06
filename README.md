```mermaid
flowchart TD
    A([bootstrap.py → App.run])

    A --> B[Cli.execute]
    A --> C[Frontend.execute]
    B -.->|renders| VIZ([Visualizer / pie chart])

    B --> D([client])
    C --> D

    D --> E[Sanitizer\nsanitize_credentials · sanitize_funds_request\nsanitize_portfolio_name · sanitize_shares_request]

    E -->|CLI direct| G
    E -->|Frontend only| F[FrontendApi\ncreate_account · find_account · fund_account\ncreate_portfolio · remove_portfolio\nexecute_buy · execute_sell]
    F --> G

    EXT([ExternalApi\nyfinance]) --> G
    DOM([Domain models\nUser · Portfolio · Stock]) --> H

    G[Validator\naccount_validator · fund_validator\nportfolio_validator · shares_request_validator]
    G --> H[Service\ncreate_account · find_account · fund_account\ncreate_portfolio · remove_portfolio\nexecute_buy · execute_sell]

    H --> I[(Database\ninsert_user · pull_user · pull_portfolios · pull_stocks\nupdate_funds · insert_portfolio · delete_portfolio\nupdate_stock · insert_stock · delete_stock)]

    ERR[/errors.py\nDatabaseError · ValidationError · ServiceError\npropagates through all layers/]

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

# Program Documentation Guidelines

Fields marked **"if N/A – None"** must still appear with the literal value `None` so readers know the field was considered.

---

## Classes
```python
# PURPOSE:
#    - <ClassName> provides <X> abstraction
#    - <why the abstraction exists>
```

---

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
    "ticker": "string",
    "quantity": 0
}
```

**PortfolioData**
```json
{
    "name": "tech",
    "stocks": {
        "AAPL": {
            "ticker": "AAPL",
            "quantity": 10
        }
    }
}
```

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