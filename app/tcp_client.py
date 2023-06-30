import mysql.connector
import socket
import threading
import binascii
import struct
import datetime


def analyze_data(data):
    arr = bytearray.fromhex(data[44:48])
    Id = (arr[1] << 8) | arr[0]

    flags = int(data[18:20], 16)
    seismic_state = bool(flags & 0x80)
    gps_state = bool(flags & 0x40)
    detector_state = bool(flags & 0x20)
    angle = bool(flags & 0x10)

    arr1 = bytearray.fromhex(data[22:30])
    converted_int1 = (0xff000000 & (arr1[3] << 24)) | (0x00ff0000 & (arr1[2] << 16)) | (
        0x0000ff00 & (arr1[1] << 8)) | (0x000000ff & arr1[0])
    longitude = struct.unpack('!f', struct.pack('!I', converted_int1))[0]

    arr2 = bytearray.fromhex(data[30:38])
    converted_int2 = (0xff000000 & (arr2[3] << 24)) | (0x00ff0000 & (arr2[2] << 16)) | (
        0x0000ff00 & (arr2[1] << 8)) | (0x000000ff & arr2[0])
    latitude = struct.unpack('!f', struct.pack('!I', converted_int2))[0]

    energy = (0x38 & int(data[40:42], 16) >> 3) * 100 / 8
    space = (0x07 & int(data[40:42], 16)) * 100 / 8

    return Id, seismic_state, longitude, latitude, energy, space, gps_state, detector_state, angle


class Server:
    def __init__(self, host, port, db_config):
        self.host = host
        self.port = port
        self.connected_nodes = set()  # 用于存储已连接的节点
        self.server_socket = None
        self.db_config = db_config
        self.db_connection_pool = None
        self.node_id = 0

    def analyze_data_frame(self, data):
        message = binascii.hexlify(data).decode('utf-8')
        if (int(message[0:2], 16) != 0x19) or (int(message[2:4], 16) != 0x24):
            return None
        node_id, seismic_state, longitude, latitude, energy, space, gps_state, detector_state, angle = analyze_data(
            message)
        self.node_id = node_id
        return node_id, seismic_state, longitude, latitude, energy, space, gps_state, detector_state, angle

    def connect_to_database(self):
        self.db_connection_pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="my_pool",
                                                                             pool_size=5,
                                                                             **self.db_config)

    def disconnect_from_database(self):
        if self.db_connection_pool:
            self.db_connection_pool.close()

    def insert_node_data(self, node_data):
        try:
            query = "INSERT INTO nodes (Id, seismic_state, longitude, latitude, energy, space, gps_state, " \
                    "detector_state, angle, timestamp) " \
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW()) " \
                    "ON DUPLICATE KEY UPDATE seismic_state = VALUES(seismic_state), " \
                    "longitude = VALUES(longitude), " \
                    "latitude = VALUES(latitude), " \
                    "energy = VALUES(energy), " \
                    "space = VALUES(space), " \
                    "gps_state = VALUES(gps_state), " \
                    "detector_state = VALUES(detector_state), " \
                    "angle = VALUES(angle), " \
                    "timestamp = VALUES(timestamp)"

            # 获取数据库连接
            db_connection = self.db_connection_pool.get_connection()
            db_cursor = db_connection.cursor()

            # 执行插入或更新节点数据的代码
            db_cursor.execute(query, node_data)
            # 提交事务
            db_connection.commit()

            # 关闭数据库连接
            db_cursor.close()
            db_connection.close()
        except mysql.connector.errors.IntegrityError as e:
            if e.errno == 1062:
                pass

    def insert_earthquake_data(self, node_id, timestamp, data):
        try:
            query = "INSERT INTO earthquake_data (node_id, timestamp, data) VALUES (%s, %s, %s)"
            values = [(node_id, timestamp, value) for value in data]

            # 获取数据库连接
            db_connection = self.db_connection_pool.get_connection()
            db_cursor = db_connection.cursor()

            # 执行批量插入
            db_cursor.executemany(query, values)
            # 提交事务
            db_connection.commit()

            # 关闭数据库连接
            db_cursor.close()
            db_connection.close()
        except mysql.connector.errors.DataError as e:
            if e.errno == 1292:
                # 处理时间戳错误
                # 可以进行适当的错误处理或日志记录
                pass

    def receive_data_frame(self, client_socket, address):
        print(f"来自{address[0]}:{address[1]}的数据帧连接")
        while True:
            data = client_socket.recv(1024)
            if not data:
                print(f"{address[0]}:{address[1]}断开连接")
                break
            node_data = self.analyze_data_frame(data)
            if node_data:
                self.insert_node_data(node_data)
                print("节点数据插入成功：", node_data)

    def receive_earthquake_data(self, client_socket, address):
        print(f"来自{address[0]}:{address[1]}的地震数据连接")
        while True:
            timestamp_data = datetime.datetime.now()
            if not timestamp_data:
                print(f"{address[0]}:{address[1]}断开连接")
                break
            try:
                data = client_socket.recv(1024).decode('utf-8')
                data_values = data.split(',')
                float_data = []
                for value in data_values:
                    try:
                        float_value = float(value)
                        float_data.append(float_value)
                    except ValueError:
                        print("无法将字符串转换为浮点数:", value)
                self.insert_earthquake_data(self.node_id, timestamp_data, float_data)
            except UnicodeDecodeError:
                print("解码数据时出现错误：", float_data)
                continue

    def handle_client(self, client_socket, address):
        data_frame_thread = threading.Thread(target=self.receive_data_frame, args=(client_socket, address))
        earthquake_data_thread = threading.Thread(target=self.receive_earthquake_data, args=(client_socket, address))

        data_frame_thread.start()
        earthquake_data_thread.start()

        data_frame_thread.join()
        earthquake_data_thread.join()

        client_socket.close()
        print("客户端已断开连接。")

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"服务器正在监听{self.host}:{self.port}")
        self.connect_to_database()
        while True:
            client_socket, address = self.server_socket.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, address))
            client_thread.start()

    def stop_server(self):
        if self.server_socket:
            self.server_socket.close()
        self.disconnect_from_database()


# MySQL数据库连接配置
db_config = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "123456",
    "database": "seismic"
}

# 创建服务器对象并启动服务器
if __name__ == "__main__":
    host = "192.168.1.109"  # 服务器主机地址
    port = 8888  # 服务器端口
    server = Server(host, port, db_config)
    server.start_server()
