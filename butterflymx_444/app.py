import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from typing import Annotated, Any

from butterflymx import ButterflyMX, EmailAndPassword, OauthCredentials, Tenant
from fastapi import Cookie, Depends, FastAPI, Form, HTTPException
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from starlette.responses import FileResponse, RedirectResponse, Response

import butterflymx_444.settings as settings
from butterflymx_444 import credential_cache
from butterflymx_444.security import (
    compare_passwords,
    create_jwt_token,
    get_user,
    hash_password,
    validate_jwt_token,
)

global bmx_tenants
# noinspection PyRedeclaration
bmx_tenants: list[Tenant] | None = None

global access_token, refresh_token
# noinspection PyRedeclaration
access_token, refresh_token = credential_cache.load()

app = FastAPI(title="ButterflyMX", debug=settings.DEBUG)
templates = Jinja2Templates(directory="butterflymx_444/templates")


class HttpResponseException(Exception):
    def __init__(self, response: Response):
        super().__init__("This is an Exception for returning a response from a dependency")
        self.response = response


async def get_bmx_initializer() -> ButterflyMX:
    global access_token, refresh_token

    bmx = ButterflyMX(
        oauth_credentials=OauthCredentials(
            client_id=settings.OAUTH_CLIENT_ID,
            client_secret=settings.OAUTH_CLIENT_SECRET,
        ),
        email_and_password=EmailAndPassword(
            email=settings.BUTTERFLYMX_EMAIL,
            password=settings.BUTTERFLYMX_PASSWORD,
        ),
        access_token=access_token,
        refresh_token=refresh_token,
    )

    async with bmx:
        await bmx.client.ensure_access_token()

    # Save token data to cache if necessary
    if access_token != bmx.client.access_token or refresh_token != bmx.client.refresh_token:
        with ThreadPoolExecutor() as tpe:
            await asyncio.get_event_loop().run_in_executor(
                tpe,
                (lambda: credential_cache.save(
                    access_token=bmx.client.access_token,
                    refresh_token=bmx.client.refresh_token,
                )),
            )

            access_token = bmx.client.access_token
            refresh_token = bmx.client.refresh_token

    return bmx


async def bmx_get_tenants() -> list[Tenant]:
    global bmx_tenants

    if bmx_tenants is None:
        async with await get_bmx_initializer() as bmx:
            bmx_tenants = await bmx.get_tenants()

    return bmx_tenants


@app.middleware('http')
async def app_handle_http_response_exception(request: Request, call_next: Any):
    try:
        return await call_next(request)
    except HttpResponseException as e:
        return e.response


async def authorized_user(token: Annotated[str | None, Cookie()] = None) -> None:
    authorized = token is not None and validate_jwt_token(token)

    if not authorized:
        response = RedirectResponse(url="/login/")

        raise HttpResponseException(response=response)


@app.get('/favicon.ico')
async def app_favicon_ico():
    return FileResponse('static/favicon.ico')

@app.get('/login')
async def app_login(request: Request):
    return templates.TemplateResponse('login.html.jinja', {
        'request': request,
        'login_action': app.url_path_for(app_login.__name__),
    })


@app.post('/login')
async def app_login_submit(
    request: Request,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
):
    user = get_user(username)

    if user is None:
        raise HTTPException(status_code=401)

    hashed_password, _ = hash_password(password, user.salt)

    if not compare_passwords(hashed_password, user.password):
        raise HTTPException(status_code=401)

    token, _ = create_jwt_token(user.username)

    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        "token",
        token,
        max_age=int(timedelta(days=settings.JWT_EXPIRATION_DAYS).total_seconds()),
    )

    return response


@app.post('/access_point/open', dependencies=[Depends(authorized_user)])
async def app_access_point_open_submit(access_point_id: Annotated[str, Form()]):
    for tenant in await bmx_get_tenants():
        for access_point in tenant.access_points:
            if access_point.id != access_point_id:
                continue

            async with await get_bmx_initializer() as bmx:
                await bmx.open_access_point(tenant, access_point)

            return RedirectResponse(url=app.url_path_for(app_index.__name__), status_code=303)


@app.get('/', dependencies=[Depends(authorized_user)])
async def app_index(request: Request):
    return templates.TemplateResponse('index.html.jinja', {
        'request': request,
        'bmx_tenants': await bmx_get_tenants(),
        'open_access_point_action': app.url_path_for(app_access_point_open_submit.__name__),
    })
