import secrets

from fastapi import APIRouter, HTTPException

from common.errors import ServiceError, ValidationError
from .frontendapi import FrontendApi
from .pydmodels import LogoutRequest, CredsRequest, FundsRequest, PortfolioRequest, TransactionRequest, StockData, PortfolioData, UserData 

router = APIRouter()

frontend_api : FrontendApi

active_sessions : dict = {}

def init(api : FrontendApi) -> None:
    global frontend_api
    frontend_api = api

def generate_session_id() -> str:
    return secrets.token_hex(32)



@router.post("/register", status_code = 201)
def register(req : CredsRequest):

    creds = (req.login, req.password)

    try:

        frontend_api.create_account(creds)
        return {"message" : "account created"}

    except ValidationError as e:
        raise HTTPException(status_code = 400, detail = str(e))

    except ServiceError as e:
        raise HTTPException(status_code = 500, detail = str(e))


@router.post("/login", status_code = 200)
def login(req : CredsRequest):

    creds = (req.login, req.password)

    try:

        user = frontend_api.find_account(creds)
        session_id = generate_session_id()
        active_sessions[session_id] = user
        return {"session_id" : session_id, "user" : UserData.convert(user)}

    except ValidationError as e:
        raise HTTPException(status_code = 400, detail = str(e))

    except ServiceError as e:
        raise HTTPException(status_code = 404, detail = str(e))


@router.post("/logout")
def logout(req : LogoutRequest):
    active_sessions.pop(req.session_id, None)
    return {"message" : "logged out"}


@router.post("/fund")
def fund(req : FundsRequest):
    user = active_sessions.get(req.session_id)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid session")

    try:

        frontend_api.fund_account(user, req.funds_requested)
        return {"user" : UserData.convert(user)}

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except ServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/portfolio/create", status_code=201)
def create_portfolio(req : PortfolioRequest):
    user = active_sessions.get(req.session_id)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid session")

    try:
        frontend_api.create_portfolio(user, req.name)
        return {"user" : UserData.convert(user)}

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except ServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/portfolio/remove")
def remove_portfolio(req : PortfolioRequest):
    user = active_sessions.get(req.session_id)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid session")

    try:

        frontend_api.remove_portfolio(user, req.name)
        return {"user" : UserData.convert(user)}

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except ServiceError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/buy")
def buy(req : TransactionRequest):
    user = active_sessions.get(req.session_id)
    shares_requested = (req.ticker, req.quantity)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid session")

    portfolio = user.portfolios.get(req.portfolio_name)

    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    try:
        frontend_api.execute_buy(user, portfolio, shares_requested)
        return {"portfolio" : PortfolioData.convert(portfolio)}

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except ServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sell")
def sell(req : TransactionRequest):
    user = active_sessions.get(req.session_id)
    shares_requested = (req.ticker, req.quantity)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid session")

    portfolio = user.portfolios.get(req.portfolio_name)

    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    try:

        frontend_api.execute_sell(user, portfolio, shares_requested)
        return {"portfolio" : PortfolioData.convert(portfolio)}

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except ServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user")
def get_user(session_id : str):
    user = active_sessions.get(session_id)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid session")

    return {"user": UserData.convert(user)}