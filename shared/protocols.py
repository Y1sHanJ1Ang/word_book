import json
from datetime import datetime
from enum import Enum
from typing import Dict, Any, List
from .models import Word

class MessageType(Enum):
    SYNC_REQUEST = "sync_request"
    SYNC_RESPONSE = "sync_response"
    WORD_UPDATE = "word_update"
    HEARTBEAT = "heartbeat"

class SyncProtocol:
    @staticmethod
    def create_message(msg_type: MessageType, data: Any = None) -> str:
        message = {
            "type": msg_type.value,
            "data": data,
            "timestamp": str(datetime.now().isoformat())
        }
        return json.dumps(message, ensure_ascii=False)
    
    @staticmethod
    def parse_message(message: str) -> Dict[str, Any]:
        return json.loads(message)
    
    @staticmethod
    def create_sync_response(words: List[Word]) -> str:
        words_data = [word.to_dict() for word in words]
        return SyncProtocol.create_message(MessageType.SYNC_RESPONSE, words_data)
    
    @staticmethod
    def parse_sync_response(message: str) -> List[Word]:
        parsed = SyncProtocol.parse_message(message)
        if parsed["type"] == MessageType.SYNC_RESPONSE.value:
            return [Word.from_dict(word_data) for word_data in parsed["data"]]
        return []