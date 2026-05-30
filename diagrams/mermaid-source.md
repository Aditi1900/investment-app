
# System Architecture
```mermaid
flowchart TB
    A(["App.run"]) --> B["Cli"] & C["Frontend"]
    B -.-> VIZ(["Visualizer"])
    VIZ ~~~ ERR[/"Errors"/]
    ERR ~~~ G["Validator"]
    B --> D(["Client"])
    C --> D
    D --> E["Sanitizer"]
    E -- CLI --> G
    E -- Frontend --> F["FrontendApi"]
    F --> G
    G --> H["Service"] & LC["LiveCache"]
    H --> DOM["Domain Models"] & I[("Database")] & LC
    LC --> EXT["External API"]

    style A fill:#F1EFE8,stroke:#888780,color:#444441
    style B fill:#EEEDFE,stroke:#534AB7,color:#3C3489
    style C fill:#EEEDFE,stroke:#534AB7,color:#3C3489
    style VIZ fill:#F1EFE8,stroke:#888780,color:#444441
    style ERR fill:#FCEBEB,stroke:#A32D2D,color:#791F1F
    style G fill:#EAF2FB,stroke:#185FA5,color:#0C447C
    style D fill:#F1EFE8,stroke:#888780,color:#444441
    style E fill:#E1F5EE,stroke:#0F6E56,color:#085041
    style F fill:#F1EFE8,stroke:#888780,color:#444441
    style H fill:#EAF2FB,stroke:#185FA5,color:#0C447C
    style LC fill:#EAF3DE,stroke:#3B6D11,color:#27500A
    style DOM fill:#F1EFE8,stroke:#888780,color:#444441
    style I fill:#FAECE7,stroke:#993C1D,color:#712B13
    style EXT fill:#FAEEDA,stroke:#854F0B,color:#633806
    linkStyle 0 stroke:#FF6D00,fill:none
    linkStyle 1 stroke:#FF6D00,fill:none
    linkStyle 2 stroke:#FF6D00,fill:none
    linkStyle 3 stroke:#FF6D00,fill:none
    linkStyle 4 stroke:#FF6D00,fill:none
    linkStyle 5 stroke:#FF6D00,fill:none
    linkStyle 6 stroke:#FF6D00,fill:none
    linkStyle 7 stroke:#FF6D00,fill:none
    linkStyle 8 stroke:#FF6D00,fill:none
    linkStyle 9 stroke:#FF6D00,fill:none
    linkStyle 10 stroke:#FF6D00,fill:none
    linkStyle 11 stroke:#FF6D00,fill:none
    linkStyle 12 stroke:#FF6D00,fill:none
    linkStyle 13 stroke:#FF6D00,fill:none
    linkStyle 14 stroke:#FF6D00,fill:none
    linkStyle 15 stroke:#FF6D00,fill:none
    linkStyle 16 stroke:#FF6D00
```
## Database Architecture
```mermaid
erDiagram
	direction LR
	USERS {
		INTEGER id PK ""  
		TEXT login UK ""  
		TEXT password  ""  
		REAL balance  ""  
	}

	PORTFOLIOS {
		INTEGER id PK ""  
		INTEGER user_id FK ""  
		TEXT name  ""  
	}

	STOCKS {
		INTEGER id PK ""  
		INTEGER portfolio_id FK ""  
		TEXT ticker  ""  
		INTEGER quantity  ""  
	}

	USERS||--o{PORTFOLIOS:"has"
	PORTFOLIOS||--o{STOCKS:"contains"

	style USERS fill:#E1BEE7,stroke:#AA00FF
	style PORTFOLIOS stroke:#FF6D00,fill:#FFE0B2
	style STOCKS stroke:#00C853,fill:#C8E6C9
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
    style F fill:#FAECE7,stroke:#993C1D,color:#712B13\
    linkStyle 0 stroke:#FF6D00,fill:none
    linkStyle 1 stroke:#FF6D00,fill:none
    linkStyle 2 stroke:#FF6D00,fill:none
    linkStyle 3 stroke:#FF6D00,fill:none
    linkStyle 4 stroke:#FF6D00,fill:none
    linkStyle 5 stroke:#FF6D00
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
    linkStyle 0 stroke:#FF6D00,fill:none
    linkStyle 1 stroke:#FF6D00,fill:none
    linkStyle 2 stroke:#FF6D00,fill:none
    linkStyle 3 stroke:#FF6D00,fill:none
    linkStyle 4 stroke:#FF6D00,fill:none
    linkStyle 5 stroke:#FF6D00
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
    linkStyle 0 stroke:#FF6D00,fill:none
    linkStyle 1 stroke:#FF6D00,fill:none
    linkStyle 2 stroke:#FF6D00,fill:none
    linkStyle 3 stroke:#FF6D00,fill:none
    linkStyle 4 stroke:#FF6D00,fill:none
    linkStyle 5 stroke:#FF6D00
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
    linkStyle 0 stroke:#FF6D00,fill:none
    linkStyle 1 stroke:#FF6D00,fill:none
    linkStyle 2 stroke:#FF6D00,fill:none
    linkStyle 3 stroke:#FF6D00,fill:none
    linkStyle 4 stroke:#FF6D00,fill:none
    linkStyle 5 stroke:#FF6D00
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
    linkStyle 0 stroke:#FF6D00,fill:none
    linkStyle 1 stroke:#FF6D00,fill:none
    linkStyle 2 stroke:#FF6D00,fill:none
    linkStyle 3 stroke:#FF6D00,fill:none
    linkStyle 4 stroke:#FF6D00,fill:none
    linkStyle 5 stroke:#FF6D00
```

