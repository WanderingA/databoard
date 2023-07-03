import binascii
import datetime
import mysql.connector
import socket
import struct
import threading
from concurrent.futures import ThreadPoolExecutor


def analyze_data(data):
    arr = bytearray.fromhex(data[44:48])
    Id = (arr[1] << 8) | arr[0]

    flags = int(data[18:20], 16)
    seismic_state = "正常" if flags & 0x80 else "异常"
    gps_state = "正常" if flags & 0x40 else "异常"
    detector_state = "正常" if flags & 0x20 else "异常"
    angle = "正常" if flags & 0x10 else "倾斜"
    if gps_state == "异常" or detector_state == "异常" or angle == "倾斜":
        seismic_state = "异常"
    arr1 = bytearray.fromhex(data[22:30])
    converted_int1 = (0xff000000 & (arr1[3] << 24)) | (0x00ff0000 & (arr1[2] << 16)) | (
        0x0000ff00 & (arr1[1] << 8)) | (0x000000ff & arr1[0])
    longitude = struct.unpack('!f', struct.pack('!I', converted_int1))[0]

    arr2 = bytearray.fromhex(data[30:38])
    converted_int2 = (0xff000000 & (arr2[3] << 24)) | (0x00ff0000 & (arr2[2] << 16)) | (
        0x0000ff00 & (arr2[1] << 8)) | (0x000000ff & arr2[0])
    latitude = struct.unpack('!f', struct.pack('!I', converted_int2))[0]

    energy = ((0x38 & int(data[40:42], 16)) >> 3) * 100 / 8
    space = (0x07 & int(data[40:42], 16)) * 100 / 8

    return Id, seismic_state, longitude, latitude, energy, space, gps_state, detector_state, angle


class Server:
    def __init__(self, host, port, db_config):
        self.host = host
        self.port = port
        self.server_socket = None
        self.db_config = db_config
        self.db_connection_pool = None
        self.class_labels = ["Human", "Tracked", "Wheeled", "Aircraft", "Noise"]
        self.node_id_mapping = {}  # 用于保存连接和节点之间的映射关系的字典
        self.lock = threading.Lock()

    def analyze_data_frame(self, data):
        message = binascii.hexlify(data).decode('utf-8')
        if (int(message[0:2], 16) != 0x19) or (int(message[2:4], 16) != 0x24):
            return None
        try:
            node_data = analyze_data(message)
            return node_data
        except Exception as e:
            print("解析数据帧时出错:", e)
            return None

    def connect_to_database(self):
        self.db_connection_pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="my_pool",
                                                                             pool_size=10,
                                                                             **self.db_config)

    def insert_node_data(self, node_data):
        try:
            query = """
                INSERT INTO nodes (Id, seismic_state, longitude, latitude, energy, space, gps_state,
                detector_state, angle, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                ON DUPLICATE KEY UPDATE seismic_state = VALUES(seismic_state),
                longitude = VALUES(longitude),
                latitude = VALUES(latitude),
                energy = VALUES(energy),
                space = VALUES(space),
                gps_state = VALUES(gps_state),
                detector_state = VALUES(detector_state),
                angle = VALUES(angle),
                timestamp = VALUES(timestamp)
            """

            with self.db_connection_pool.get_connection() as db_connection:
                with db_connection.cursor() as db_cursor:
                    db_cursor.execute(query, node_data)
                    db_connection.commit()
        except mysql.connector.errors.IntegrityError as e:
            if e.errno == 1062:
                pass

    def insert_classifications_data(self, node_id, timestamp, classification):
        try:
            query = "INSERT INTO node_classifications (node_id, timestamp, classification) VALUES (%s, %s, %s)"
            values = (node_id, timestamp, classification)

            with self.db_connection_pool.get_connection() as db_connection:
                with db_connection.cursor() as db_cursor:
                    db_cursor.execute(query, values)
                    db_connection.commit()
        except mysql.connector.Error as e:
            print("插入数据异常:", str(e))

    def handle_classifications_data(self, data, address):
        try:
            timestamp_data = datetime.datetime.now()
            #print("接收到的字节串:", data)  # 调试输出
            # prediction = int.from_bytes(data, byteorder='big')
            prediction = int.from_bytes(data, byteorder='little', signed=False)  # 修改此行
            #print("转换后的预测结果:", prediction)  # 调试输出
            prediction_label = self.class_labels[prediction]
            node_id = self.get_node_id_from_address(address)
            self.insert_classifications_data(node_id, timestamp_data, prediction_label)
        except IndexError:
            # print("接收到的数据越界：", data)
            pass
        except Exception as e:
            print(f"解析接收到的数据时出错: {e}")

    def receive_data_frame(self, client_socket, address):
        print(f"来自{address[0]}:{address[1]}的数据帧连接")
        while True:
            data = client_socket.recv(1024)
            if not data:
                print(f"{address[0]}:{address[1]}断开连接")
                break
            node_data = self.analyze_data_frame(data)
            if node_data:
                with self.lock:
                    node_id = node_data[0]
                    self.node_id_mapping[address] = node_id
                    self.insert_node_data(node_data)
                    print("节点数据插入成功：", node_data)

        client_socket.close()
        print("数据帧连接已断开。")

    def receive_classifications_data(self, client_socket, address):
        print(f"来自{address[0]}:{address[1]}的地震数据连接")
        while True:
            data = client_socket.recv(1024)
            if not data:
                print(f"{address[0]}:{address[1]}断开连接")
                break
            self.handle_classifications_data(data, address)

        client_socket.close()
        print("地震数据连接已断开。")

    def handle_client(self, client_socket, address):
        data_frame_thread = threading.Thread(target=self.receive_data_frame,
                                             args=(client_socket, address))
        classifications_data_thread = threading.Thread(target=self.receive_classifications_data,
                                                       args=(client_socket, address))

        data_frame_thread.start()
        classifications_data_thread.start()

        data_frame_thread.join()
        classifications_data_thread.join()

        print("客户端已断开连接。")

    def get_node_id_from_address(self, address):
        return self.node_id_mapping.get(address)

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server is listening at {self.host}:{self.port}")
        self.connect_to_database()

        with ThreadPoolExecutor() as executor:
            while True:
                client_socket, address = self.server_socket.accept()
                executor.submit(self.handle_client, client_socket, address)

class Database:
    def __init__(self, db_config):
        self.db_config = db_config
        self.lock = threading.Lock()

    def get_node_data(self):
        try:
            query = "SELECT * FROM nodes"
            with mysql.connector.connect(**self.db_config) as db_connection:
                with db_connection.cursor() as db_cursor:
                    db_cursor.execute(query)
                    result = db_cursor.fetchall()
                    return result
        except mysql.connector.Error as e:
            print("数据库查询错误:", str(e))
            return []

    def get_node_number(self):
        try:
            query = """
            SELECT
                COUNT(*) AS total_nodes,
                COUNT(CASE WHEN `seismic_state` = '正常' THEN 1 END) AS normal_nodes
            FROM
                `nodes`
            """
            with mysql.connector.connect(**self.db_config) as db_connection:
                with db_connection.cursor() as db_cursor:
                    db_cursor.execute(query)
                    result = db_cursor.fetchall()
                    return result
        except mysql.connector.Error as e:
            print("数据库查询错误:", str(e))
            return []


# 创建服务器对象并启动服务器
if __name__ == "__main__":
    host = "192.168.1.109"  # 服务器主机地址
    port = 8888  # 服务器端口
    # MySQL数据库连接配置
    db_config = {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "123456",
        "database": "seismic"
    }
    server = Server(host, port, db_config)
    server.start_server()
