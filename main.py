import uvicorn
from fastapi import FastAPI, WebSocket, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.models import Server as tcp_data, Database


# MySQL数据库连接配置
db_config = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "123456",
    "database": "seismic"
}
host = "192.168.1.109"  # 服务器主机地址
port = 8888  # 服务器端口

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
server = tcp_data(host, port, db_config)
database = Database(db_config)

@app.get("/")
def get_index(request: Request):
    # username = request.cookies.get("username")  # 从Cookie中获取用户名
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/node-control")
def get_node_control(request: Request):
    node_data = database.get_node_data()
    print(node_data[0][0])
    return templates.TemplateResponse("NodeContrl.html", {"request": request, "node_data": node_data})


@app.get("/connect_node")
def connect_node(request: Request):
    server.start_server()
    return {"message": "连接成功"}


@app.get("/map")
def get_map(request: Request):
    return templates.TemplateResponse("map.html", {"request": request})


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
