from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from sync.sync_client import SyncClient
import random

class WordCard(BoxLayout):
    def __init__(self, word=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.word = word
        self.is_flipped = False
        
        self.word_label = Label(
            text=word.word if word else "点击同步获取单词",
            font_size='24sp',
            text_size=(None, None),
            halign='center'
        )
        self.add_widget(self.word_label)
        
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=0.3)
        
        self.flip_btn = Button(text='翻面', size_hint_x=0.5)
        self.flip_btn.bind(on_press=self.flip_card)
        button_layout.add_widget(self.flip_btn)
        
        self.next_btn = Button(text='下一个', size_hint_x=0.5)
        self.next_btn.bind(on_press=self.next_word)
        button_layout.add_widget(self.next_btn)
        
        self.add_widget(button_layout)
        
    def flip_card(self, instance):
        if not self.word:
            return
            
        if not self.is_flipped:
            content = f"中文: {self.word.translation}\n\n"
            content += f"英文: {self.word.english_translation}\n\n"
            content += f"记忆: {self.word.memory_tip}\n\n"
            content += f"笔记: {self.word.user_note}"
            self.word_label.text = content
            self.is_flipped = True
        else:
            self.word_label.text = self.word.word
            self.is_flipped = False
            
    def next_word(self, instance):
        app = App.get_running_app()
        app.next_random_word()

class SyncDialog(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = 'WiFi同步设置'
        self.size_hint = (0.8, 0.6)
        
        content = BoxLayout(orientation='vertical')
        
        content.add_widget(Label(text='输入PC端IP地址:', size_hint_y=0.3))
        
        self.ip_input = TextInput(
            text='192.168.1.100',
            multiline=False,
            size_hint_y=0.3
        )
        content.add_widget(self.ip_input)
        
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=0.4)
        
        sync_btn = Button(text='开始同步')
        sync_btn.bind(on_press=self.start_sync)
        button_layout.add_widget(sync_btn)
        
        cancel_btn = Button(text='取消')
        cancel_btn.bind(on_press=self.dismiss)
        button_layout.add_widget(cancel_btn)
        
        content.add_widget(button_layout)
        self.content = content
        
    def start_sync(self, instance):
        ip = self.ip_input.text.strip()
        if ip:
            app = App.get_running_app()
            app.sync_words(ip)
        self.dismiss()

class WordBookApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.words = []
        self.current_word_index = 0
        self.sync_client = SyncClient()
        
    def build(self):
        main_layout = BoxLayout(orientation='vertical')
        
        title = Label(
            text='单词本',
            font_size='32sp',
            size_hint_y=0.15,
            bold=True
        )
        main_layout.add_widget(title)
        
        self.word_card = WordCard()
        main_layout.add_widget(self.word_card)
        
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=0.15)
        
        sync_btn = Button(text='同步数据')
        sync_btn.bind(on_press=self.show_sync_dialog)
        button_layout.add_widget(sync_btn)
        
        word_list_btn = Button(text='单词列表')
        word_list_btn.bind(on_press=self.show_word_list)
        button_layout.add_widget(word_list_btn)
        
        main_layout.add_widget(button_layout)
        
        return main_layout
        
    def show_sync_dialog(self, instance):
        sync_dialog = SyncDialog()
        sync_dialog.open()
        
    def sync_words(self, ip):
        try:
            self.words = self.sync_client.sync_from_server(ip)
            if self.words:
                self.show_popup("同步成功", f"同步了 {len(self.words)} 个单词")
                self.next_random_word()
            else:
                self.show_popup("同步失败", "无法连接到服务器或没有数据")
        except Exception as e:
            self.show_popup("同步失败", str(e))
            
    def next_random_word(self):
        if not self.words:
            return
            
        word = random.choice(self.words)
        self.word_card.word = word
        self.word_card.is_flipped = False
        self.word_card.word_label.text = word.word
        
    def show_word_list(self, instance):
        if not self.words:
            self.show_popup("提示", "请先同步数据")
            return
            
        content = BoxLayout(orientation='vertical')
        
        scroll = ScrollView()
        word_layout = GridLayout(cols=1, size_hint_y=None)
        word_layout.bind(minimum_height=word_layout.setter('height'))
        
        for word in self.words:
            word_btn = Button(
                text=f"{word.word} - {word.translation}",
                size_hint_y=None,
                height='48dp'
            )
            word_btn.bind(on_press=lambda x, w=word: self.select_word(w))
            word_layout.add_widget(word_btn)
            
        scroll.add_widget(word_layout)
        content.add_widget(scroll)
        
        close_btn = Button(text='关闭', size_hint_y=0.2)
        content.add_widget(close_btn)
        
        popup = Popup(
            title='单词列表',
            content=content,
            size_hint=(0.9, 0.8)
        )
        
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
        
    def select_word(self, word):
        self.word_card.word = word
        self.word_card.is_flipped = False
        self.word_card.word_label.text = word.word
        
    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text=message))
        
        close_btn = Button(text='确定', size_hint_y=0.3)
        content.add_widget(close_btn)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, 0.4)
        )
        
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

if __name__ == '__main__':
    WordBookApp().run()