import secrets
from collections import defaultdict
from threading import Lock

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from ..common.errors import ServiceError, ValidationError
from .pydmodels import (
    LogoutRequest, CredsRequest, FundsRequest,
    PortfolioRequest, TransactionRequest,
    StockData, PortfolioData, UserData
) 

frontend_api = None
router = APIRouter()

active_sessions : dict[str, int] = {}
user_sessions : defaultdict[int,set] = defaultdict(set)

active_users : dict[int, object] = {}

session_lock = Lock()


# INPUT:
#   -api(FrontendApi); functional interface
# OUTPUT: None
# PRECONDITION:
#   -api; fully constructed FrontendApi instance
# POSTCONDITION:
#   -frontend_api; passed api is assigned to global module memory
# RAISES: None
def connect(api) -> None:
    global frontend_api
    frontend_api = api


# INPUT: None
# OUTPUT:
#   -session_id(str); randomly generated hex string
# PRECONDITION: None
# POSTCONDITION:
#   -session_id; does not exist as a key in active_sessions
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
#   -user; fully populated
# POSTCONDITION:
#   -active_sessions; session_id mapped to user.id
#   -active_users; user.id mapped to user
# RAISES: None
def start_session(user) -> str:
    with session_lock:
        session_id = generate_session_id()
        active_sessions[session_id] = user.id
        user_sessions[user.id].add(session_id)
        active_users[user.id] = user

    return session_id


# INPUT:
#   -session_id(str); a session of some user
# OUTPUT:
#   -user(User); a user account
# PRECONDITION: None
# POSTCONDITION:
#   -user; User matching session_id returned if session exists, None otherwise
# RAISES: None
def find_sessions_user(session_id : str):
    u_id = active_sessions.get(session_id)
    user = active_users.get(u_id)

    return user


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
def register(req : CredsRequest) -> dict[str, str]:

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
#   -response(dict[str,str|UserData]); session id and user data sent to client
# PRECONDITION:
#   -router; exists as a valid router
#   -frontend_api; contains control flow pipeline methods
# POSTCONDITION:
#   -frontend_api; see FrontendApi.find_account() POSTCONDITION
#   -active_sessions; see start_session() POSTCONDITION
#   -response; contains session_id and UserData for authenticated user
# RAISES:
#   -HTTPException(400); a ValidationError is raised, malformed credentials
#   -HTTPException(401); a ServiceError is raised, account not found
@router.post("/login", status_code = 200)
def login(req : CredsRequest) -> dict[str, str | UserData]:

    creds = (req.login, req.password)

    try:
        u_id = frontend_api.resolve_uid(req.login)
        user = active_users.get(u_id)

        if user is None:
            user = frontend_api.find_account(creds)

    except ValidationError as e:
        raise HTTPException(status_code = 400, detail = str(e))

    except ServiceError as e:
        raise HTTPException(status_code = 401, detail = str(e))

    session_id = start_session(user)
    
    response = {"session_id" : session_id, "user" : UserData.convert(user)}

    return response


# INPUT:
#   -req(LogoutRequest); HTTP logout payload
# OUTPUT:
#   -response(dict[str,str]); success confirmation sent to client
# PRECONDITION:
#   -router; exists as a valid router
#   -active_sessions; contains all active sessions
# POSTCONDITION:
#   -active_sessions; matching session id from payload is removed
#   -active_users; user removed if no remaining sessions exist
# RAISES:
#   -HTTPException(404); session id is not found in active sessions
@router.post("/logout")
def logout(req : LogoutRequest) -> dict[str, str]:

    with session_lock:
        u_id = active_sessions.pop(req.session_id, None)
        
        if u_id is None:
            raise HTTPException(status_code = 404, detail = "session not found")

        user_sessions[u_id].discard(req.session_id)

        if not user_sessions[u_id]:
            active_users.pop(u_id, None)
            user_sessions.pop(u_id, None)

    response = {"message" : "logged out"}

    return response


# INPUT:
#   -req(FundsRequest); HTTP funds to add payload
# OUTPUT:
#   -response(dict[str,UserData]); user data JSON payload
# PRECONDITION:
#   -router; exists as a valid router
#   -frontend_api; contains control flow pipeline methods
# POSTCONDITION:
#   -frontend_api; see FrontendApi.fund_account() POSTCONDITION
#   -response; contains updated UserData
# RAISES:
#   -HTTPException(400); a ValidationError is raised, invalid funds request
#   -HTTPException(401); unauthorized, user session does not exist
#   -HTTPException(500); a ServiceError is raised, server side error
@router.post("/fund")
def fund(req : FundsRequest) -> dict[str, UserData]:
    user = find_sessions_user(req.session_id)

    if user is None:
        raise HTTPException(status_code = 401, detail = "Invalid session")

    try:

        with user.lock:
            frontend_api.fund_account(user, req.funds_requested)
       
    except ValidationError as e:
        raise HTTPException(status_code = 400, detail = str(e))

    except ServiceError as e:
        raise HTTPException(status_code = 500, detail = str(e))

    response = {"user" : UserData.convert(user)}

    return response


# INPUT:
#   -req(PortfolioRequest); HTTP portfolio creation payload
# OUTPUT:
#   -response(dict[str,UserData]); user data JSON payload 
# PRECONDITION:
#   -router; exists as a valid router
#   -frontend_api; contains control flow pipeline methods 
# POSTCONDITION:
#   -frontend_api; see FrontendApi.create_portfolio() POSTCONDITION
#   -response; contains updated UserData
# RAISES:
#   -HTTPException(400); a ValidationError is raised, invalid portfolio name
#   -HTTPException(401); unauthorized, user session does not exist
#   -HTTPException(500); a ServiceError is raised, server side error
@router.post("/portfolio/create", status_code = 201)
def create_portfolio(req : PortfolioRequest) -> dict[str, UserData]:
    user = find_sessions_user(req.session_id)

    if user is None:
        raise HTTPException(status_code = 401, detail = "Invalid session")

    try:
        
        with user.lock:
            frontend_api.create_portfolio(user, req.name)
        
    except ValidationError as e:
        raise HTTPException(status_code = 400, detail = str(e))

    except ServiceError as e:
        raise HTTPException(status_code = 500, detail = str(e))

    response = {"user" : UserData.convert(user)}

    return response


# INPUT:
#   -req(PortfolioRequest); HTTP portfolio removal payload
# OUTPUT:
#   -response(dict[str,UserData]); user data JSON payload 
# PRECONDITION:
#   -router; exists as a valid router
#   -frontend_api; contains control flow pipeline methods 
# POSTCONDITION:
#   -frontend_api; see FrontendApi.remove_portfolio() POSTCONDITION
#   -response; contains updated UserData
# RAISES:
#   -HTTPException(400); a ValidationError is raised, invalid portfolio name
#   -HTTPException(401); unauthorized, user session does not exist
#   -HTTPException(500); a ServiceError is raised, server side error
@router.post("/portfolio/remove")
def remove_portfolio(req : PortfolioRequest) -> dict[str, UserData]:
    user = find_sessions_user(req.session_id)

    if user is None:
        raise HTTPException(status_code = 401, detail = "Invalid session")

    try:

        with user.lock:
            frontend_api.remove_portfolio(user, req.name)
        
    except ValidationError as e:
        raise HTTPException(status_code = 400, detail = str(e))

    except ServiceError as e:
        raise HTTPException(status_code = 500, detail = str(e))

    response = {"user" : UserData.convert(user)}    

    return response 


# INPUT:
#   -req(TransactionRequest); HTTP transaction payload
# OUTPUT:
#   -response(dict[str,PortfolioData]); portfolio data JSON payload 
# PRECONDITION:
#   -router; exists as a valid router
#   -frontend_api; contains control flow pipeline methods 
# POSTCONDITION:
#   -frontend_api; see FrontendApi.execute_buy() POSTCONDITION
#   -response; contains updated PortfolioData
# RAISES:
#   -HTTPException(400); a ValidationError is raised, invalid ticker, quantity or insufficient balance
#   -HTTPException(401); unauthorized, user session does not exist
#   -HTTPException(404); portfolio is not found
#   -HTTPException(500); a ServiceError is raised, server side error
@router.post("/buy")
def buy(req : TransactionRequest) -> dict[str, PortfolioData]:
    user = find_sessions_user(req.session_id)

    shares_requested = (req.ticker, req.quantity)

    if user is None:
        raise HTTPException(status_code = 401, detail = "Invalid session")


    try:

        with user.lock:
            portfolio = user.portfolios.get(req.portfolio_name)

            if portfolio is None:
                raise HTTPException(status_code = 404, detail = "Portfolio not found")

            frontend_api.execute_buy(user, portfolio, shares_requested)
        
    except ValidationError as e:
        raise HTTPException(status_code = 400, detail = str(e))

    except ServiceError as e:
        raise HTTPException(status_code = 500, detail = str(e))

    response = {"portfolio" : PortfolioData.convert(portfolio)}

    return response


# INPUT:
#   -req(TransactionRequest); HTTP transaction payload
# OUTPUT:
#   -response(dict[str,PortfolioData]); portfolio data JSON payload 
# PRECONDITION:
#   -router; exists as a valid router
#   -frontend_api; contains control flow pipeline methods 
# POSTCONDITION:
#   -frontend_api; see FrontendApi.execute_sell() POSTCONDITION
#   -response; contains updated PortfolioData
# RAISES:
#   -HTTPException(400); a ValidationError is raised, invalid ticker or quantity
#   -HTTPException(401); unauthorized, user session does not exist
#   -HTTPException(404); portfolio is not found
#   -HTTPException(500); a ServiceError is raised, server side error
@router.post("/sell")
def sell(req : TransactionRequest) -> dict[str, PortfolioData]:
    user = find_sessions_user(req.session_id)

    shares_requested = (req.ticker, req.quantity)

    if user is None:
        raise HTTPException(status_code = 401, detail = "Invalid session")
    try:

        with user.lock:
            portfolio = user.portfolios.get(req.portfolio_name)

            if portfolio is None:
                raise HTTPException(status_code = 404, detail = "Portfolio not found")

            frontend_api.execute_sell(user, portfolio, shares_requested)
        
    except ValidationError as e:
        raise HTTPException(status_code = 400, detail = str(e))

    except ServiceError as e:
        raise HTTPException(status_code = 500, detail = str(e))

    response = {"portfolio" : PortfolioData.convert(portfolio)}

    return response 


# INPUT:
#   -session_id(str); a session id
# OUTPUT:
#   -response(dict[str,UserData]); user data JSON payload 
# PRECONDITION:
#   -router; exists as a valid router
#   -frontend_api; contains control flow pipeline methods 
# POSTCONDITION:
#   -response; contains UserData for the requesting session
# RAISES:
#   -HTTPException(401); unauthorized, user session does not exist
@router.get("/user")
def get_user(session_id : str) -> dict[str, UserData]:
    user = find_sessions_user(session_id)

    if user is None:
        raise HTTPException(status_code = 401, detail = "Invalid session")

    response = {"user": UserData.convert(user)}

    return response


# INPUT:
#   -session_id(str); a session id
#   -portfolio_name(str); current portfolio name
# OUTPUT:
#   -return(StreamingResponse); a streaming response object
# PRECONDITION: None
# POSTCONDITION:
#   -StreamingResponse; streams each yielded chunk of the async generator directly to client
# RAISES:
#   -HTTPException(401); unauthorized, user session does not exist
#   -HTTPException(404); portfolio is not found   
@router.get("/live_data")
async def get_live_portfolio_data(session_id : str, portfolio_name : str):
    user = find_sessions_user(session_id)

    if user is None:
        raise HTTPException(status_code = 401, detail = "Invalid session")

    portfolio = user.portfolios.get(portfolio_name)

    if portfolio is None:
        raise HTTPException(status_code = 404, detail = "Portfolio not found")

    live_data = frontend_api.make_data_stream(portfolio)

    return StreamingResponse(live_data, media_type = "application/x-ndjson")
