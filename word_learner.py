import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import random
import os
import json
from openai import OpenAI

class WordLearner:
    def __init__(self, root):
        self.root = root
        self.root.title("只背单词-重构")
        self.root.geometry("900x600")
        self.root.configure(bg="#f0f0f0")

        # 样式配置
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TButton", padding=6, relief="flat", background="#cceeff", font=('Helvetica', 12))
        self.style.map("TButton", background=[('active', '#aaddff')])
        self.style.configure("TLabel", background="#f0f0f0", font=('Helvetica', 14))
        self.style.configure("Header.TLabel", font=('Helvetica', 24, 'bold'))
        
        # 初始化变量
        self.word_dict = {}
        self.buttons = {}
        
        # 创建主界面
        self.create_main_menu()
    
    def create_main_menu(self):
        """创建主菜单界面"""
        self.clear_frame()
        
        ttk.Label(self.root, text="只背单词v1.5", style="Header.TLabel").pack(pady=20)
        
        self.buttons['load'] = ttk.Button(self.root, text="1. 导入单词文件", command=self.load_word_file)
        self.buttons['load'].pack(pady=10)
        
        self.buttons['quick_learn'] = ttk.Button(self.root, text="2. 速记单词", command=lambda: self.set_mode("quick_learn"))
        self.buttons['quick_learn'].pack(pady=10)
        
        self.buttons['practice'] = ttk.Button(self.root, text="3. 练拼写", command=lambda: self.set_mode("practice"))
        self.buttons['practice'].pack(pady=10)

        self.buttons['article'] = ttk.Button(self.root, text="4. 短文生成", command=lambda: self.set_mode("article"))
        self.buttons['article'].pack(pady=10)

        self.update_button_states()
    
    def load_word_file(self):
        """导入单词文件"""
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            try:
                self.word_dict.clear()
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            parts = line.strip().split(maxsplit=1)
                            if len(parts) == 2:
                                self.word_dict[parts[0]] = parts[1]
                
                if self.word_dict:
                    messagebox.showinfo("成功", f"成功导入 {len(self.word_dict)} 个单词")
                else:
                    messagebox.showwarning("注意", "文件为空或格式不正确")
                self.update_button_states()
            except Exception as e:
                messagebox.showerror("错误", f"导入文件失败: {str(e)}")
    
    def update_button_states(self):
        """根据是否有单词数据更新按钮状态"""
        state = "normal" if self.word_dict else "disabled"
        for key in ['quick_learn', 'practice', 'article']:
            if key in self.buttons and self.buttons[key].winfo_exists():
                 self.buttons[key].config(state=state)
    
    def set_mode(self, mode):
        self.mode = mode
        self.clear_frame()
        
        ttk.Label(self.root, text=f"请输入要{'学习' if mode != 'article' else '使用'}的单词数量:").pack(pady=10)
        
        self.word_count_entry = ttk.Entry(self.root, font=("Arial", 14))
        self.word_count_entry.pack(pady=5)
        
        if mode == "quick_learn":
            ttk.Button(self.root, text="开始学习", command=self.start_quick_learn).pack(pady=20)
        elif mode == "practice":
            ttk.Button(self.root, text="开始练习", command=self.start_practice).pack(pady=20)
        elif mode == "article":
            ttk.Button(self.root, text="生成短文", command=self.start_article).pack(pady=20)
            
        ttk.Button(self.root, text="返回主菜单", command=self.create_main_menu).pack(pady=10)

    def start_session(self):
        """通用会话开始逻辑"""
        try:
            count = int(self.word_count_entry.get())
            if not (0 < count <= len(self.word_dict)):
                messagebox.showerror("错误", f"请输入1到{len(self.word_dict)}之间的有效数字")
                return None
            return random.sample(list(self.word_dict.keys()), count)
        except (ValueError, TypeError):
            messagebox.showerror("错误", "请输入有效的数字")
            return None

    # --- 速记单词 ---
    def start_quick_learn(self):
        self.current_words = self.start_session()
        if self.current_words:
            self.current_index = 0
            self.review_words = []
            self.show_word()

    def show_word(self):
        self.clear_frame()
        word = self.current_words[self.current_index]
        
        ttk.Label(self.root, text=word, font=("Arial", 36)).pack(pady=50)
        self.meaning_label = ttk.Label(self.root, text="", font=("Arial", 18), foreground="navy")
        self.meaning_label.pack(pady=20)

        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=20)
        
        self.know_btn = ttk.Button(btn_frame, text="认识", command=lambda: self.handle_response(True))
        self.know_btn.pack(side="left", padx=10)
        self.dont_know_btn = ttk.Button(btn_frame, text="不认识", command=lambda: self.handle_response(False))
        self.dont_know_btn.pack(side="left", padx=10)
        self.skip_btn = ttk.Button(btn_frame, text="熟记", command=self.next_word_or_review)
        self.skip_btn.pack(side="left", padx=10)
        
        ttk.Button(self.root, text="返回主菜单", command=self.create_main_menu).pack(pady=10)

    def handle_response(self, known):
        self.know_btn.config(state="disabled")
        self.dont_know_btn.config(state="disabled")
        self.skip_btn.config(state="disabled")

        word = self.current_words[self.current_index]
        self.meaning_label.config(text=f"{word}: {self.word_dict[word]}")
        
        if not known:
            if word not in self.review_words:
                self.review_words.append(word)
        
        self.root.after(2000, self.next_word_or_review)

    def next_word_or_review(self):
        self.current_index += 1
        if self.current_index >= len(self.current_words):
            if self.review_words:
                messagebox.showinfo("提示", f"将开始复习 {len(self.review_words)} 个不认识的单词")
                self.current_words = self.review_words
                self.current_index = 0
                self.review_words = []
                self.show_word()
            else:
                messagebox.showinfo("完成", "所有单词学习完成!")
                self.create_main_menu()
        else:
            self.show_word()

    # --- 刷单词 ---
    def start_practice(self):
        self.current_words = self.start_session()
        if self.current_words:
            self.current_index = 0
            self.wrong_words = []
            self.show_question()

    def show_question(self):
        self.clear_frame()
        word = self.current_words[self.current_index]
        meaning = self.word_dict[word]
        
        ttk.Label(self.root, text=meaning, font=("Arial", 24)).pack(pady=30)
        ttk.Label(self.root, text="请输入对应的英文单词:").pack(pady=10)
        self.answer_entry = ttk.Entry(self.root, font=("Arial", 14))
        self.answer_entry.pack(pady=5)
        self.answer_entry.bind("<Return>", self.check_answer)

        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="提交", command=self.check_answer).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="跳过", command=self.next_question_or_review).pack(side="left", padx=10)
        ttk.Button(self.root, text="返回主菜单", command=self.create_main_menu).pack(pady=10)

    def check_answer(self, event=None):
        user_answer = self.answer_entry.get().strip()
        correct_word = self.current_words[self.current_index]
        
        if user_answer.lower() == correct_word.lower():
            messagebox.showinfo("正确", "回答正确!")
            self.next_question_or_review()
        else:
            messagebox.showerror("错误", f"正确答案是: {correct_word}")
            if correct_word not in self.wrong_words:
                self.wrong_words.append(correct_word)
            self.next_question_or_review()

    def next_question_or_review(self):
        self.current_index += 1
        if self.current_index >= len(self.current_words):
            if self.wrong_words:
                messagebox.showinfo("提示", f"将开始复习 {len(self.wrong_words)} 个错误的单词")
                self.current_words = self.wrong_words
                self.current_index = 0
                self.wrong_words = []
                self.show_question()
            else:
                messagebox.showinfo("完成", "所有单词练习完成!")
                self.create_main_menu()
        else:
            self.show_question()

    # --- 短文生成 ---
    def start_article(self):
        self.current_words = self.start_session()
        if self.current_words:
            self.generate_article()

    def generate_article(self):
        self.clear_frame()
        ttk.Label(self.root, text="正在生成短文，请稍候...", font=("Arial", 18)).pack(pady=50)
        self.root.update()

        try:
            with open("apikey.txt", "r") as f:
                config = dict(line.strip().split('=', 1) for line in f if '=' in line)
            
            api_key = config.get("apikey")
            base_url = config.get("url")
            model = config.get("model")

            if not all([api_key, base_url, model]):
                raise ValueError("apikey.txt中缺少 apikey, url, 或 model")

            client = OpenAI(api_key=api_key, base_url=base_url)
            prompt = f"Please write a short and natural-sounding story using the following English words: {', '.join(self.current_words)}. The story should include all the given words. After the story, provide a Chinese translation. Underline the given words in the story."
            
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.choices[0].message.content
            self.display_article(content)

        except Exception as e:
            messagebox.showerror("错误", f"生成短文失败: {str(e)}")
            self.create_main_menu()

    def display_article(self, content):
        self.clear_frame()
        parts = content.split("\n\n", 1)
        article = parts[0]
        translation = parts[1] if len(parts) > 1 else "未提供翻译"

        text_frame = ttk.Frame(self.root)
        text_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        article_text = tk.Text(text_frame, wrap="word", font=("Arial", 12), height=15)
        article_text.pack(fill="both", expand=True)
        article_text.insert("end", article)

        for word in self.current_words:
            start_idx = "1.0"
            while True:
                start_idx = article_text.search(word, start_idx, stopindex="end", regexp=False, nocase=True)
                if not start_idx: break
                end_idx = f"{start_idx}+{len(word)}c"
                article_text.tag_add(word, start_idx, end_idx)
                article_text.tag_config(word, underline=True, foreground="blue")
                article_text.tag_bind(word, "<Button-1>", lambda e, w=word: self.show_word_meaning_popup(w))
                start_idx = end_idx
        
        ttk.Separator(text_frame, orient='horizontal').pack(fill='x', pady=10)
        
        translation_text = tk.Text(text_frame, wrap="word", font=("Arial", 12), height=8)
        translation_text.pack(fill="both", expand=True)
        translation_text.insert("end", translation)

        ttk.Button(self.root, text="返回主菜单", command=self.create_main_menu).pack(pady=10)

    def show_word_meaning_popup(self, word):
        meaning = self.word_dict.get(word, "未找到释义")
        messagebox.showinfo("单词释义", f"{word}: {meaning}")

    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = WordLearner(root)
    root.mainloop()
