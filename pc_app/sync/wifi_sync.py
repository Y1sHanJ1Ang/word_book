import socket
import threading
import json
from typing import Callable, Optional
from ..database.database import WordDatabase
from ...shared.protocols import SyncProtocol, MessageType

class WiFiSyncServer:
    def __init__(self, port: int = 8888):
        self.port = port
        self.server_socket = None
        self.is_running = False
        self.db = WordDatabase()
        self.clients = []
        
    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server_socket.bind(('0.0.0.0', self.port))
            self.server_socket.listen(5)
            self.is_running = True
            
            print(f"WiFi同步服务器启动，端口: {self.port}")
            
            while self.is_running:
                try:
                    client_socket, address = self.server_socket.accept()
                    print(f"新客户端连接: {address}")
                    
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.error:
                    if self.is_running:
                        print("服务器socket错误")
                    break
                    
        except Exception as e:
            print(f"服务器启动失败: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()
                
    def handle_client(self, client_socket: socket.socket, address):
        try:
            while self.is_running:
                data = client_socket.recv(4096).decode('utf-8')
                if not data:
                    break
                    
                message = SyncProtocol.parse_message(data)
                response = self.process_message(message)
                
                if response:
                    client_socket.send(response.encode('utf-8'))
                    
        except Exception as e:
            print(f"处理客户端 {address} 时出错: {e}")
        finally:
            client_socket.close()
            print(f"客户端 {address} 断开连接")
            
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
            
    def get_server_ip(self) -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

class WiFiSyncClient:
    def __init__(self):
        self.socket = None
        self.is_connected = False
        
    def connect_to_server(self, host: str, port: int = 8888) -> bool:
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            self.socket.connect((host, port))
            self.is_connected = True
            return True
        except Exception as e:
            print(f"连接服务器失败: {e}")
            return False
            
    def sync_words(self) -> list:
        if not self.is_connected:
            return []
            
        try:
            request = SyncProtocol.create_message(MessageType.SYNC_REQUEST)
            self.socket.send(request.encode('utf-8'))
            
            response = self.socket.recv(4096).decode('utf-8')
            words = SyncProtocol.parse_sync_response(response)
            
            return words
        except Exception as e:
            print(f"同步数据失败: {e}")
            return []
            
    def disconnect(self):
        if self.socket:
            self.socket.close()
            self.is_connected = False