
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

# Feature Piplines

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

