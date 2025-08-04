import bluetooth
import threading
import json
from typing import Optional
from ..database.database import WordDatabase
from ...shared.protocols import SyncProtocol, MessageType

class BluetoothSyncServer:
    def __init__(self):
        self.server_socket = None
        self.is_running = False
        self.db = WordDatabase()
        
    def start_server(self):
        try:
            self.server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            port = bluetooth.PORT_ANY
            self.server_socket.bind(("", port))
            self.server_socket.listen(1)
            
            port = self.server_socket.getsockname()[1]
            
            uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
            
            bluetooth.advertise_service(
                self.server_socket, "WordBookSync",
                service_id=uuid,
                service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
                profiles=[bluetooth.SERIAL_PORT_PROFILE]
            )
            
            print(f"蓝牙同步服务器启动，端口: {port}")
            self.is_running = True
            
            while self.is_running:
                try:
                    client_socket, client_info = self.server_socket.accept()
                    print(f"蓝牙客户端连接: {client_info}")
                    
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_info)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except bluetooth.BluetoothError as e:
                    if self.is_running:
                        print(f"蓝牙服务器错误: {e}")
                    break
                    
        except Exception as e:
            print(f"蓝牙服务器启动失败: {e}")
        finally:
            self.stop_server()
            
    def handle_client(self, client_socket, client_info):
        try:
            while self.is_running:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                    
                message = SyncProtocol.parse_message(data)
                response = self.process_message(message)
                
                if response:
                    client_socket.send(response.encode('utf-8'))
                    
        except Exception as e:
            print(f"处理蓝牙客户端时出错: {e}")
        finally:
            client_socket.close()
            print(f"蓝牙客户端 {client_info} 断开连接")
            
    def process_message(self, message) -> Optional[str]:
        msg_type = message.get('type')
        
        if msg_type == MessageType.SYNC_REQUEST.value:
            words = self.db.get_all_words()
            return SyncProtocol.create_sync_response(words)
        
        elif msg_type == MessageType.HEARTBEAT.value:
            return SyncProtocol.create_message(MessageType.HEARTBEAT)
            
        return None
        
    def stop_server(self):
        self.is_running = False
        if self.server_socket:
            self.server_socket.close()

class BluetoothSyncClient:
    def __init__(self):
        self.socket = None
        self.is_connected = False
        
    def discover_devices(self):
        try:
            print("搜索蓝牙设备...")
            devices = bluetooth.discover_devices(duration=8, lookup_names=True)
            return devices
        except Exception as e:
            print(f"搜索蓝牙设备失败: {e}")
            return []
            
    def connect_to_server(self, address: str, port: int = 1) -> bool:
        try:
            self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.socket.connect((address, port))
            self.is_connected = True
            return True
        except Exception as e:
            print(f"连接蓝牙服务器失败: {e}")
            return False
            
    def sync_words(self) -> list:
        if not self.is_connected:
            return []
            
        try:
            request = SyncProtocol.create_message(MessageType.SYNC_REQUEST)
            self.socket.send(request.encode('utf-8'))
            
            response = self.socket.recv(1024).decode('utf-8')
            words = SyncProtocol.parse_sync_response(response)
            
            return words
        except Exception as e:
            print(f"蓝牙同步数据失败: {e}")
            return []
            
    def disconnect(self):
        if self.socket:
            self.socket.close()
            self.is_connected = False