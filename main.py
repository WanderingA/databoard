import uvicorn
from fastapi import FastAPI, WebSocket, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles


app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def get_index(request: Request):
    username = request.cookies.get("username")  # 从Cookie中获取用户名
    return templates.TemplateResponse("index.html", {"request": request, "username": username})


@app.get("/node-control")
def get_node_control(request: Request):
    return templates.TemplateResponse("NodeContrl.html", {"request": request})


@app.get("/map")
def get_map(request: Request):
    return templates.TemplateResponse("map.html", {"request": request})


@app.get("/statistics")
def get_statistics(request: Request):
    return templates.TemplateResponse("static.html", {"request": request})


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
