import socket
import json
from ...shared.models import Word
from ...shared.protocols import SyncProtocol, MessageType

class SyncClient:
    def __init__(self):
        self.socket = None
        
    def sync_from_server(self, host: str, port: int = 8888) -> list:
        words = []
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((host, port))
            
            request = SyncProtocol.create_message(MessageType.SYNC_REQUEST)
            self.socket.send(request.encode('utf-8'))
            
            response_data = b""
            while True:
                chunk = self.socket.recv(4096)
                if not chunk:
                    break
                response_data += chunk
                try:
                    response = response_data.decode('utf-8')
                    words = SyncProtocol.parse_sync_response(response)
                    break
                except json.JSONDecodeError:
                    continue
                    
        except Exception as e:
            print(f"同步失败: {e}")
        finally:
            if self.socket:
                self.socket.close()
                
        return words