import uvicorn
from fastapi import FastAPI, WebSocket, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.models import Server as tcp_data, Database
import json
from fastapi import Response
import datetime


# MySQL数据库连接配置
db_config = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "123456",
    "database": "seismic"
}
host = "0.0.0.0"  # 服务器主机地址
port = 8888  # 服务器端口

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
server = tcp_data(host, port, db_config)
database = Database(db_config)


@app.get("/")
async def get_index(request: Request):
    node_number = database.get_node_number()
    node_classification = database.get_classification_node_number()
    chart_data = json.dumps([{"value": count, "name": classification} for classification, count in node_classification])
    node_status = database.get_node_status()
    values = list(node_status[0])
    status = json.dumps([{"value": value} for value in values])
    node_allinfo = database.get_allnode_info()
    # print(node_allinfo)
    return templates.TemplateResponse("index.html", {"request": request, "node_number": node_number,
                                                     "chart_data": chart_data, "status": status,
                                                     "node_allinfo": node_allinfo})


@app.get("/node-control")
async def get_node_control(request: Request):
    node_data = database.get_node_data()
    return templates.TemplateResponse("NodeContrl.html", {"request": request, "node_data": node_data})


@app.get("/get_node_data/{node_id}")
async def get_node_data(node_id: str):
    # Implement your logic here to fetch the updated node data
    node_data = database.get_node_data(node_id)  # Modify this to fetch data for the given node_id
    if not node_data:
        return {"error": f"Node with ID {node_id} not found"}

    # Format the node_data as needed, e.g., converting datetime to string, etc.
    formatted_node_data = {
        "id": node_data[0],
        "status": node_data[1],
        "longitude": node_data[2],
        "latitude": node_data[3],
        "electricity": node_data[4],
        "space": node_data[5],
        "gps": node_data[6],
        "detector": node_data[7],
        "angle": node_data[8]
    }
    # print(formatted_node_data)
    # Return the formatted node data as a JSON response
    return formatted_node_data


@app.get("/connect_node")
def connect_node(request: Request):
    server.start_server()
    return {"message": "连接成功"}


@app.get("/map")
async def get_map(request: Request):
    node_allinfo = database.get_allnode_info()
    return templates.TemplateResponse("map.html", {"request": request, "node_allinfo": node_allinfo})


@app.get("/get_table_data")
async def get_table_data():
    node_allinfo = database.get_allnode_info()
    sorted_data = sorted(node_allinfo, key=lambda x: x[4], reverse=True)
    return [sorted_data]


# def json_encoder(obj):
#     if isinstance(obj, datetime.datetime):
#         return obj.strftime("%Y-%m-%d %H:%M:%S")
#     raise TypeError(f"Object of type '{obj.__class__.__name__}' is not JSON serializable")
#
#
# @app.get("/get_table_data")
# async def get_table_data():
#     node_allinfo = database.get_allnode_info()
#     encoded_data = json.dumps(node_allinfo, default=json_encoder)
#     # print(encoded_data)
#     # print(json.dumps(encoded_data))
#     return Response(content=json.dumps(encoded_data), media_type="application/json")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
