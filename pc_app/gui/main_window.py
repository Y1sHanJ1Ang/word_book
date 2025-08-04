import customtkinter as ctk
from tkinter import messagebox
import random
from ..database.database import WordDatabase
from ..api.dictionary_api import DictionaryAPI
from ...shared.models import Word

class MainWindow:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("单词本")
        self.root.geometry("800x600")
        
        self.db = WordDatabase()
        self.api = DictionaryAPI()
        self.current_word = None
        self.card_flipped = False
        
        self.setup_ui()
        
    def setup_ui(self):
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        self.sidebar = ctk.CTkFrame(self.root, width=200)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.sidebar.grid_propagate(False)
        
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        
        self.setup_sidebar()
        self.setup_main_area()
        
    def setup_sidebar(self):
        title = ctk.CTkLabel(self.sidebar, text="单词本", font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=20)
        
        self.add_btn = ctk.CTkButton(self.sidebar, text="添加单词", command=self.show_add_word)
        self.add_btn.pack(pady=5, padx=20, fill="x")
        
        self.list_btn = ctk.CTkButton(self.sidebar, text="单词列表", command=self.show_word_list)
        self.list_btn.pack(pady=5, padx=20, fill="x")
        
        self.card_btn = ctk.CTkButton(self.sidebar, text="单词卡", command=self.show_word_card)
        self.card_btn.pack(pady=5, padx=20, fill="x")
        
        self.sync_btn = ctk.CTkButton(self.sidebar, text="同步数据", command=self.sync_data)
        self.sync_btn.pack(pady=5, padx=20, fill="x")
        
    def setup_main_area(self):
        self.clear_main_frame()
        welcome_label = ctk.CTkLabel(self.main_frame, text="欢迎使用单词本", 
                                   font=ctk.CTkFont(size=24, weight="bold"))
        welcome_label.pack(expand=True)
        
    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
    def show_add_word(self):
        self.clear_main_frame()
        
        title = ctk.CTkLabel(self.main_frame, text="添加单词", font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=20)
        
        form_frame = ctk.CTkFrame(self.main_frame)
        form_frame.pack(pady=20, padx=40, fill="both", expand=True)
        
        ctk.CTkLabel(form_frame, text="单词:").pack(pady=5)
        self.word_entry = ctk.CTkEntry(form_frame, width=300)
        self.word_entry.pack(pady=5)
        
        query_btn = ctk.CTkButton(form_frame, text="自动查询", command=self.auto_query_word)
        query_btn.pack(pady=5)
        
        ctk.CTkLabel(form_frame, text="中文翻译:").pack(pady=5)
        self.translation_entry = ctk.CTkTextbox(form_frame, width=300, height=80)
        self.translation_entry.pack(pady=5)
        
        ctk.CTkLabel(form_frame, text="英文释义:").pack(pady=5)
        self.english_entry = ctk.CTkTextbox(form_frame, width=300, height=80)
        self.english_entry.pack(pady=5)
        
        ctk.CTkLabel(form_frame, text="记忆方法:").pack(pady=5)
        self.memory_entry = ctk.CTkTextbox(form_frame, width=300, height=80)
        self.memory_entry.pack(pady=5)
        
        ctk.CTkLabel(form_frame, text="自定义笔记:").pack(pady=5)
        self.note_entry = ctk.CTkTextbox(form_frame, width=300, height=80)
        self.note_entry.pack(pady=5)
        
        save_btn = ctk.CTkButton(form_frame, text="保存单词", command=self.save_word)
        save_btn.pack(pady=20)
        
    def auto_query_word(self):
        word = self.word_entry.get().strip()
        if not word:
            messagebox.showwarning("警告", "请先输入单词")
            return
            
        try:
            result = self.api.query_word(word)
            self.translation_entry.delete("1.0", "end")
            self.translation_entry.insert("1.0", result['translation'])
            
            self.english_entry.delete("1.0", "end")
            self.english_entry.insert("1.0", result['english_translation'])
            
            self.memory_entry.delete("1.0", "end")
            self.memory_entry.insert("1.0", self.api.generate_memory_tip(word, result['translation']))
            
        except Exception as e:
            messagebox.showerror("错误", f"查询失败: {str(e)}")
            
    def save_word(self):
        word_text = self.word_entry.get().strip()
        if not word_text:
            messagebox.showwarning("警告", "请输入单词")
            return
            
        word = Word(
            word=word_text,
            translation=self.translation_entry.get("1.0", "end-1c"),
            english_translation=self.english_entry.get("1.0", "end-1c"),
            memory_tip=self.memory_entry.get("1.0", "end-1c"),
            user_note=self.note_entry.get("1.0", "end-1c")
        )
        
        try:
            self.db.add_word(word)
            messagebox.showinfo("成功", "单词添加成功")
            self.word_entry.delete(0, "end")
            self.translation_entry.delete("1.0", "end")
            self.english_entry.delete("1.0", "end")
            self.memory_entry.delete("1.0", "end")
            self.note_entry.delete("1.0", "end")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
            
    def show_word_list(self):
        self.clear_main_frame()
        
        title = ctk.CTkLabel(self.main_frame, text="单词列表", font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=20)
        
        search_frame = ctk.CTkFrame(self.main_frame)
        search_frame.pack(pady=10, padx=20, fill="x")
        
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="搜索单词...")
        self.search_entry.pack(side="left", padx=10, pady=10, fill="x", expand=True)
        
        search_btn = ctk.CTkButton(search_frame, text="搜索", command=self.search_words)
        search_btn.pack(side="right", padx=10, pady=10)
        
        self.word_listbox = ctk.CTkScrollableFrame(self.main_frame)
        self.word_listbox.pack(pady=10, padx=20, fill="both", expand=True)
        
        self.load_word_list()
        
    def search_words(self):
        keyword = self.search_entry.get().strip()
        if keyword:
            words = self.db.search_words(keyword)
        else:
            words = self.db.get_all_words()
        self.display_word_list(words)
        
    def load_word_list(self):
        words = self.db.get_all_words()
        self.display_word_list(words)
        
    def display_word_list(self, words):
        for widget in self.word_listbox.winfo_children():
            widget.destroy()
            
        for word in words:
            word_frame = ctk.CTkFrame(self.word_listbox)
            word_frame.pack(fill="x", pady=5, padx=10)
            
            word_label = ctk.CTkLabel(word_frame, text=f"{word.word} - {word.translation}", 
                                    font=ctk.CTkFont(size=14))
            word_label.pack(side="left", padx=10, pady=10)
            
            edit_btn = ctk.CTkButton(word_frame, text="编辑", width=60,
                                   command=lambda w=word: self.edit_word(w))
            edit_btn.pack(side="right", padx=5, pady=5)
            
            delete_btn = ctk.CTkButton(word_frame, text="删除", width=60,
                                     command=lambda w=word: self.delete_word(w))
            delete_btn.pack(side="right", padx=5, pady=5)
            
    def edit_word(self, word):
        pass
        
    def delete_word(self, word):
        if messagebox.askyesno("确认", f"确定要删除单词 '{word.word}' 吗?"):
            self.db.delete_word(word.id)
            self.load_word_list()
            messagebox.showinfo("成功", "单词删除成功")
            
    def show_word_card(self):
        self.clear_main_frame()
        
        title = ctk.CTkLabel(self.main_frame, text="随机单词卡", font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=20)
        
        self.card_frame = ctk.CTkFrame(self.main_frame, width=400, height=300)
        self.card_frame.pack(pady=20, expand=True)
        self.card_frame.pack_propagate(False)
        
        self.card_content = ctk.CTkLabel(self.card_frame, text="点击 '下一个单词' 开始", 
                                       font=ctk.CTkFont(size=18))
        self.card_content.pack(expand=True)
        
        button_frame = ctk.CTkFrame(self.main_frame)
        button_frame.pack(pady=20)
        
        self.flip_btn = ctk.CTkButton(button_frame, text="翻面", command=self.flip_card)
        self.flip_btn.pack(side="left", padx=10)
        
        self.next_btn = ctk.CTkButton(button_frame, text="下一个单词", command=self.next_card)
        self.next_btn.pack(side="left", padx=10)
        
        if hasattr(self, 'current_word') and self.current_word:
            delete_btn = ctk.CTkButton(button_frame, text="删除此单词", 
                                     command=self.delete_current_word)
            delete_btn.pack(side="left", padx=10)
            
    def next_card(self):
        words = self.db.get_all_words()
        if not words:
            self.card_content.configure(text="暂无单词，请先添加单词")
            return
            
        self.current_word = random.choice(words)
        self.card_flipped = False
        self.card_content.configure(text=self.current_word.word)
        
    def flip_card(self):
        if not self.current_word:
            return
            
        if not self.card_flipped:
            content = f"中文: {self.current_word.translation}\n\n"
            content += f"英文: {self.current_word.english_translation}\n\n"
            content += f"记忆: {self.current_word.memory_tip}\n\n"
            content += f"笔记: {self.current_word.user_note}"
            self.card_content.configure(text=content)
            self.card_flipped = True
        else:
            self.card_content.configure(text=self.current_word.word)
            self.card_flipped = False
            
    def delete_current_word(self):
        if not self.current_word:
            return
            
        if messagebox.askyesno("确认", f"确定要删除单词 '{self.current_word.word}' 吗?"):
            self.db.delete_word(self.current_word.id)
            messagebox.showinfo("成功", "单词删除成功")
            self.next_card()
            
    def sync_data(self):
        messagebox.showinfo("提示", "数据同步功能开发中...")
        
    def run(self):
        self.root.mainloop()