import secrets

from fastapi import APIRouter, HTTPException

from common.errors import ServiceError, ValidationError
from .frontendapi import FrontendApi
from .pydmodels import LogoutRequest, CredsRequest, FundsRequest, PortfolioRequest, TransactionRequest, StockData, PortfolioData, UserData 

router = APIRouter()

frontend_api : FrontendApi

active_sessions : dict = {}


# INPUT:
#   -api(FrontendApi); functional interface
# OUTPUT: None
# PRECONDITION:
#   -api; is populated with a service and validator
# POSTCONDITION:
#   -frontend_api; passed api is assigned to global module memory
# RAISES: None
def connect(api : FrontendApi) -> None:
    global frontend_api
    frontend_api = api


# INPUT: None
# OUTPUT:
#   -session_id(str); randomly generated hex string
# PRECONDITION: None
# POSTCONDITION:
#   -session_id; unique among all keys in active sessions
# RAISES: None
def generate_session_id() -> str:
    session_id = secrets.token_hex(32)

    while session_id in active_sessions:
        session_id = secrets.token_hex(32)

    return session_id


# INPUT:
#   -user(User); a user account
# OUTPUT:
#   -session_id(str); randomly generated hex string
# PRECONDITION:
#   -user; is fully populated
# POSTCONDITION:
#   -active_sessions; new entry maps session id to user
# RAISES: None
def start_session(user) -> str:
    session_id = generate_session_id()
    active_sessions[session_id] = user
    return session_id


# INPUT:
#   -req(CredsRequest); HTTP credential payload
# OUTPUT:
#   -response(dict[str,str]); success confirmation sent to client
# PRECONDITION:
#   -router; exists as a valid router
#   -frontend_api; contains control flow pipeline methods
# POSTCONDITION:
#   -frontend_api; see FrontendApi.create_account() POSTCONDITION
#   -response; contains key "message" with value "account created"
# RAISES:
#   -HTTPException(400); a ValidationError is raised, malformed credentials
#   -HTTPException(500); a ServiceError is raised, server side error
@router.post("/register", status_code = 201)
def register(req : CredsRequest) -> dict[str,str]:

    creds = (req.login, req.password)

    try:

        frontend_api.create_account(creds)
        
    except ValidationError as e:
        raise HTTPException(status_code = 400, detail = str(e))

    except ServiceError as e:
        raise HTTPException(status_code = 500, detail = str(e))

    response = {"message" : "account created"}

    return response


# INPUT:
#   -req(CredsRequest); HTTP credential payload
# OUTPUT:
#   -response(dict[str,int|UserData]); session id and user data sent to client
# PRECONDITION:
#   -router; exists as a valid router
#   -frontend_api; contains control flow pipeline methods
# POSTCONDITION:
#   -frontend_api; see FrontendApi.find_account() POSTCONDITION
#   -active_sessions; see start_session() POSTCONDITION
#   -response; session id for user and user data is sent to client  
# RAISES:
#   -HTTPException(400); a ValidationError is raised, malformed credentials
#   -HTTPException(404); a ServiceError is raised, account not found
@router.post("/login", status_code = 200)
def login(req : CredsRequest) -> dict[str, int | UserData]:

    creds = (req.login, req.password)

    try:

        user = frontend_api.find_account(creds)

    except ValidationError as e:
        raise HTTPException(status_code = 400, detail = str(e))

    except ServiceError as e:
        raise HTTPException(status_code = 404, detail = str(e))


    session_id = start_session(user)
    
    response = {"session_id" : session_id, "user" : UserData.convert(user)}

    return response


# INPUT:
#   -req(LogoutRequest): HTTP logout payload
# OUTPUT:
#   -response(dict[str,str]); success confirmation sent to client
# PRECONDITION:
#   -router; exists as a valid router
#   -active_sessions; contains all active sessions
# POSTCONDITION:
#   -active_sessions; matching session id from payload is removed
# RAISES:
#   -HTTPException(404); session id is not found in active sessions
@router.post("/logout")
def logout(req : LogoutRequest) -> dict[str,str]:
    user = active_sessions.pop(req.session_id, None)

    if user is None:
        raise HTTPException(status_code = 404, detail = "session not found")

    response = {"message" : "logged out"}

    return response


# INPUT:
# OUTPUT:
# PRECONDITION:
# POSTCONDITION:
# RAISES:
@router.post("/fund")
def fund(req : FundsRequest) -> dict[str, UserData]:
    user = active_sessions.get(req.session_id)

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid session")

    try:

        frontend_api.fund_account(user, req.funds_requested)
       
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except ServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))

    response = {"user" : UserData.convert(user)}

    return response
    

# INPUT:
# OUTPUT:
# PRECONDITION:
# POSTCONDITION:
# RAISES:
@router.post("/portfolio/create", status_code=201)
def create_portfolio(req : PortfolioRequest) -> dict[str, UserData]:
    user = active_sessions.get(req.session_id)

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid session")

    try:

        frontend_api.create_portfolio(user, req.name)
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except ServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))

    response = {"user" : UserData.convert(user)}

    return response


# INPUT:
# OUTPUT:
# PRECONDITION:
# POSTCONDITION:
# RAISES:
@router.post("/portfolio/remove")
def remove_portfolio(req : PortfolioRequest) -> dict[str, UserData]:
    user = active_sessions.get(req.session_id)

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid session")

    try:

        frontend_api.remove_portfolio(user, req.name)
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except ServiceError as e:
        raise HTTPException(status_code=404, detail=str(e))

    response = {"user" : UserData.convert(user)}    

    return response 


# INPUT:
# OUTPUT:
# PRECONDITION:
# POSTCONDITION:
# RAISES:
@router.post("/buy")
def buy(req : TransactionRequest) -> dict[str, PortfolioData]:
    user = active_sessions.get(req.session_id)
    shares_requested = (req.ticker, req.quantity)

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid session")

    portfolio = user.portfolios.get(req.portfolio_name)

    if portfolio is None:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    try:

        frontend_api.execute_buy(user, portfolio, shares_requested)
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except ServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))

    response = {"portfolio" : PortfolioData.convert(portfolio)}

    return response


# INPUT:
# OUTPUT:
# PRECONDITION:
# POSTCONDITION:
# RAISES:
@router.post("/sell")
def sell(req : TransactionRequest) -> dict[str, PortfolioData]:
    user = active_sessions.get(req.session_id)
    shares_requested = (req.ticker, req.quantity)

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid session")

    portfolio = user.portfolios.get(req.portfolio_name)

    if portfolio is None:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    try:

        frontend_api.execute_sell(user, portfolio, shares_requested)
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except ServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))

    response = {"portfolio" : PortfolioData.convert(portfolio)}

    return response 


# INPUT:
# OUTPUT:
# PRECONDITION:
# POSTCONDITION:
# RAISES:
@router.get("/user")
def get_user(session_id : str) -> dict[str, UserData]:
    user = active_sessions.get(session_id)

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid session")

    response = {"user": UserData.convert(user)}

    return response