import sqlite3
import os
from datetime import datetime
from typing import List, Optional
from shared.models import Word

class WordDatabase:
    def __init__(self, db_path: str = "word_book.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL UNIQUE,
                translation TEXT NOT NULL,
                english_translation TEXT,
                memory_tip TEXT,
                user_note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_word(self, word: Word) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now()
        cursor.execute('''
            INSERT INTO words (word, translation, english_translation, memory_tip, user_note, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (word.word, word.translation, word.english_translation, 
              word.memory_tip, word.user_note, now, now))
        
        word_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return word_id
    
    def get_word(self, word_id: int) -> Optional[Word]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM words WHERE id = ?', (word_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Word(
                id=row[0], word=row[1], translation=row[2],
                english_translation=row[3], memory_tip=row[4],
                user_note=row[5], created_at=datetime.fromisoformat(row[6]),
                updated_at=datetime.fromisoformat(row[7])
            )
        return None
    
    def get_all_words(self) -> List[Word]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM words ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        
        words = []
        for row in rows:
            words.append(Word(
                id=row[0], word=row[1], translation=row[2],
                english_translation=row[3], memory_tip=row[4],
                user_note=row[5], created_at=datetime.fromisoformat(row[6]),
                updated_at=datetime.fromisoformat(row[7])
            ))
        
        return words
    
    def update_word(self, word: Word) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE words 
            SET word=?, translation=?, english_translation=?, memory_tip=?, user_note=?, updated_at=?
            WHERE id=?
        ''', (word.word, word.translation, word.english_translation,
              word.memory_tip, word.user_note, datetime.now(), word.id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def delete_word(self, word_id: int) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM words WHERE id = ?', (word_id,))
        success = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return success
    
    def search_words(self, keyword: str) -> List[Word]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM words 
            WHERE word LIKE ? OR translation LIKE ? OR user_note LIKE ?
            ORDER BY created_at DESC
        ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
        
        rows = cursor.fetchall()
        conn.close()
        
        words = []
        for row in rows:
            words.append(Word(
                id=row[0], word=row[1], translation=row[2],
                english_translation=row[3], memory_tip=row[4],
                user_note=row[5], created_at=datetime.fromisoformat(row[6]),
                updated_at=datetime.fromisoformat(row[7])
            ))
        
        return words