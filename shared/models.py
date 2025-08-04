from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Word:
    id: Optional[int] = None
    word: str = ""
    translation: str = ""
    english_translation: str = ""
    memory_tip: str = ""
    user_note: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self):
        return {
            'id': self.id,
            'word': self.word,
            'translation': self.translation,
            'english_translation': self.english_translation,
            'memory_tip': self.memory_tip,
            'user_note': self.user_note,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id'),
            word=data.get('word', ''),
            translation=data.get('translation', ''),
            english_translation=data.get('english_translation', ''),
            memory_tip=data.get('memory_tip', ''),
            user_note=data.get('user_note', ''),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        )