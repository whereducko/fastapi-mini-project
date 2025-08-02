import uvicorn
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from crud.router import router as crud_router
from database import FAKE_DB
from utils import (
    create_access_token,
    get_user_from_db_wo_pass,
    get_user_from_db,
    insert_new_user_in_db,
    token_authenticate_user,
)

app = FastAPI(
    summary="Мини-проект от @whereducko",
    description="[github](https://github.com/whereducko)",
    version="0.1")
app.include_router(crud_router)
templates = Jinja2Templates(directory="pages/templates")


@app.get("/")
def home(request: Request, is_auth: dict | bool = Depends(token_authenticate_user)):
    if is_auth:
        username = is_auth["username"]
        return templates.TemplateResponse("home.html", {"request": request, "nickname": username})
    return RedirectResponse(url="/login", status_code=302)


@app.get("/register")
def register_user(request: Request, is_auth: dict | bool = Depends(token_authenticate_user)):
    if is_auth:
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
def register_page(
        login_input: str = Form(...),
        pass_input: str = Form(...),
):
    user = get_user_from_db_wo_pass(FAKE_DB, login_input)
    if user is None and (len(login_input) > 0 and len(pass_input) > 0):
        new_user = insert_new_user_in_db(FAKE_DB, login_input, pass_input)
        return RedirectResponse(url="/login", status_code=302)
    return RedirectResponse(url="/register", status_code=302)


@app.get("/login")
def login_user(request: Request, is_auth: dict | bool = Depends(token_authenticate_user)):
    if is_auth:
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def login_page(
        login_input: str = Form(...),
        pass_input: str = Form(...),
):
    user = get_user_from_db(FAKE_DB, login_input, pass_input)
    if user:
        access_token = create_access_token(user)
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie("access_token", access_token, expires=900, httponly=True)
        return response
    return RedirectResponse(url="/login", status_code=302)


@app.post("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("access_token")
    return response


if __name__ == "__main__":
    uvicorn.run(app)
