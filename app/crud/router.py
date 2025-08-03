from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.utils import full_auth_check
from app.database import (
    get_db_func,
    insert_db_func,
    update_db_func,
    delete_user_from_db_func,
    get_count_rows_db,
    insert_more_data_db,
    delete_all_data_from_db,
)

router = APIRouter(prefix="/db", tags=["БД. CRUD"])
templates = Jinja2Templates(directory="pages/templates/crud")


@router.get("")
def get_db(
        request: Request,
        page: int = 1,
        is_auth: dict | bool = Depends(full_auth_check)
):
    if is_auth:
        return templates.TemplateResponse(
            "db-users.html",
            {
                "request": request,
                "number_page": page,
                "count_pages": int((get_count_rows_db() / 100 + 0.99) // 1),
                "database": get_db_func(100, (page - 1) * 100),
            }
        )
    return RedirectResponse(url="/login", status_code=302)


@router.get("/add")
def add_user_page(request: Request, is_auth: dict | bool = Depends(full_auth_check)):
    if is_auth:
        return templates.TemplateResponse("add-user.html", {"request": request})
    return RedirectResponse(url="/login", status_code=302)


@router.post("/add")
def add_user_in_db(
        id_input: str = Form(...),
        username_input: str = Form(...),
        password_input: str = Form(...),
        email_input: str = Form(...),
):
    insert_db_func(int(id_input), username_input, password_input, email_input)
    return RedirectResponse("/db", status_code=302)


@router.get("/update")
def add_user_page(request: Request, is_auth: dict | bool = Depends(full_auth_check)):
    if is_auth:
        return templates.TemplateResponse("update-user.html", {"request": request})
    return RedirectResponse(url="/login", status_code=302)


@router.post("/update")
def update_user_in_db(
        id_input: str = Form(...),
        username_input: str = Form(...),
        password_input: str = Form(...),
        email_input: str = Form(...),
):
    update_db_func(int(id_input), username_input, password_input, email_input)
    return RedirectResponse("/db", status_code=302)


@router.get("/delete")
def add_user_page(request: Request, is_auth: dict | bool = Depends(full_auth_check)):
    if is_auth:
        return templates.TemplateResponse("delete-user.html", {"request": request})
    return RedirectResponse(url="/login", status_code=302)


@router.post("/delete")
def delete_user_from_db(
        id_input: str = Form(...),
):
    delete_user_from_db_func(int(id_input))
    return RedirectResponse("/db", status_code=302)


@router.get("/experiments")
def experiments_page(request: Request, is_auth: dict | bool = Depends(full_auth_check)):
    if is_auth:
        return templates.TemplateResponse("experimental.html", {"request": request})
    return RedirectResponse(url="/login", status_code=302)

@router.post("/experiments/add-more-users")
def experiments_things(
        count_users: str = Form(...),
):
    insert_more_data_db(int(count_users))
    return RedirectResponse("/db", status_code=302)


@router.post("/experiments/delete-all-users")
def experiments_things():
    delete_all_data_from_db()
    return RedirectResponse("/db", status_code=302)
