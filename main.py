from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.request import Request

import secrets
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="templates")
security = HTTPBasic()

# Mock user data (in a real-world scenario, you'd use a database)
users = {"admin": "password",
    "johnDoe": "johnd123",
    "aliceSmith": "aliceS456",
    "bobBrown": "bobB789",
    "charlieGreen": "charlieG101",
    "eveWhite": "eveW202"}

# Keeping track of logged in users (using tokens for simplicity, but you'd want a more secure approach in production)
logged_in_users = []




def get_optional_token(request: Request):
    token = request.cookies.get("token")
    if token in logged_in_users:
        return token
    return None

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    # 사용자가 존재하는지 확인
    user_password = users.get(credentials.username)
    
    # 사용자가 존재하면 비밀번호 확인, 그렇지 않으면 인증 실패
    if user_password and secrets.compare_digest(credentials.password, user_password):
        return credentials.username
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    
@app.get("/login-failed")
def login_failed():
    return {"message": "Login failed! Please check your credentials and try again."}

@app.get("/")
def login_page(request: Request, token: str = Depends(get_optional_token)):
    if token:
        # 토큰이 유효한 경우 메인 페이지로 리다이렉트
        return RedirectResponse(url="/main")
    # 그렇지 않은 경우 로그인 페이지를 보여줍니다.
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def login(username: str = Depends(get_current_username)):
    token = secrets.token_urlsafe(16)
    logged_in_users.append(token)
    # 로그인에 성공하면 메인 페이지로 리다이렉트하고, 이동한 메인 페이지에서는 토큰을 사용하여 인증을 처리할 수 있습니다.
    response = RedirectResponse(url="/main")
    response.set_cookie(key="token", value=token)  # 선택사항: 메인 페이지에서 토큰을 사용하려면 쿠키에 토큰을 설정할 수 있습니다.
    return response

@app.get("/logout")
def logout(token: str):
    if token in logged_in_users:
        logged_in_users.remove(token)
        return {"message": "You have been logged out!"}
    return {"error": "Invalid token or user already logged out"}

@app.get("/main")
def main_page(request: Request, token: str = Depends(get_optional_token)):
    if not token:
        return RedirectResponse(url="/")
    return templates.TemplateResponse("main.html", {"request": request})

@app.get("/page1")
def page_1(request: Request, token: str = Depends(get_optional_token)):
    if not token:
        return RedirectResponse(url="/")
    return templates.TemplateResponse("page1.html", {"request": request})

@app.get("/page2")
def page_2(request: Request, token: str = Depends(get_optional_token)):
    if not token:
        return RedirectResponse(url="/")
    return templates.TemplateResponse("page2.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, ssl_keyfile="key.pem", ssl_certfile="cert.pem")