import os
import json
from tkinter import ttk, filedialog, Tk, StringVar, Menu
import tkinter as tk
import requests
import pdfplumber
import docx
from PIL import Image
import pytesseract
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from sklearn.feature_extraction.text import TfidfVectorizer
from huggingface_hub import InferenceClient
from transformers import pipeline
from huggingface_hub import login
login()



messages = [
    {"role": "user", "content": "Who are you?"},
]
pipe = pipeline("text-generation", model="meta-llama/Meta-Llama-3-70B-Instruct")
pipe(messages)


HUGGINGFACEHUB_API_TOKEN = "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"
HUGGINGFACEHUB_API_TOKEN = "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"
API_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B"
headers = {"Authorization": f"Bearer {HUGGINGFACEHUB_API_TOKEN}"}

# Initialize TfidfVectorizer
vectorizer = TfidfVectorizer()

class Datagarden:
    def __init__(self):
        self.conversation = []
        self.context = {}

    def add_message(self, message):
        self.conversation.append(message)
        self.update_context(message)

    def update_context(self, message):
        # Update the context with the new message
        self.context['last_message'] = message

    def save_conversation(self):
        with open('conversation.json', 'w') as f:
            json.dump(self.conversation, f)

    def save_context(self):
        with open('context.json', 'w') as f:
            json.dump(self.context, f)

class Bot:
    def __init__(self):
        self.datagarden = Datagarden()
        self.load_history()

    def load_history(self):
        try:
            with open('conversation.json', 'r') as f:
                self.datagarden.conversation = json.load(f)
            with open('context.json', 'r') as f:
                self.datagarden.context = json.load(f)
        except FileNotFoundError:
            pass

    def save_history(self):
        self.datagarden.save_conversation()
        self.datagarden.save_context()

    def add_to_history(self, message):
        self.datagarden.add_message(message)

    def truncate_conversation_history(self, max_tokens=4096, filename=None):
        # Start with an empty list for the truncated history
        truncated_history = []
        # Count the number of tokens in the conversation history
        total_tokens = sum(len(msg["content"]) for msg in self.datagarden.conversation)

        # If the total number of tokens exceeds max_tokens
        if total_tokens > max_tokens:
            truncated_tokens = 0
            for msg in reversed(self.datagarden.conversation):
                msg_tokens = len(msg["content"])
                if truncated_tokens + msg_tokens > max_tokens:
                    break
                truncated_history.insert(0, msg)
                truncated_tokens += msg_tokens

            if filename:
                with open(filename, "w") as f:
                    json.dump(truncated_history, f)
            return truncated_history
        else:
            return self.datagarden.conversation

class PersonalizedAIApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.bot = Bot()  # Instance of Bot class
        self.title("PersonalizedAIApp")
        self.conversation_history = []  # Initialize the conversation history list here

        self.build_ui()
        self.mainloop()

    def build_ui(self):
        # Create UI elements here
        content = ttk.Frame(self)
        content.grid(column=0, row=0)

        # Create input label and text entry widget
        input_label = ttk.Label(content, text="Enter your message or load a document/image:")
        input_label.grid(column=0, row=0, padx=10, pady=10, sticky=tk.W)
        self.input_text = tk.Text(content, wrap=tk.WORD, height=5, width=50)
        self.input_text.grid(column=0, row=1, padx=10, pady=10)

        # Create "Load Document" button
        load_doc_btn = ttk.Button(content, text="Load Document", command=self.load_document)
        load_doc_btn.grid(column=1, row=1, padx=10, pady=10)

        # Create emotion label and dropdown menu
        emotion_label = ttk.Label(content, text="Select your emotion:")
        emotion_label.grid(column=0, row=2, padx=10, pady=10, sticky=tk.W)
        self.emotion_var = tk.StringVar()
        emotion_dropdown = ttk.Combobox(content, textvariable=self.emotion_var, values=["Happy", "Sad", "Angry", "Neutral", "Excited", "Worried"])
        emotion_dropdown.grid(column=0, row=3, padx=10, pady=10, sticky=tk.W)

        # Create domain label and dropdown menu
        domain_label = ttk.Label(content, text="Select domain:")
        domain_label.grid(column=0, row=4, padx=10, pady=10, sticky=tk.W)
        self.domain_var = tk.StringVar()
        domain_dropdown = ttk.Combobox(content, textvariable=self.domain_var, values=["General", "Finance", "Health", "Education", "Technology", "Entertainment"])
        domain_dropdown.grid(column=0, row=5, padx=10, pady=10, sticky=tk.W)

        # Create "Send" button
        send_btn = ttk.Button(content, text="Send", command=self.on_send_click)
        send_btn.grid(column=0, row=6, padx=10, pady=10)

        # Create response label and text widget
        response_label = ttk.Label(content, text="AI's response:")
        response_label.grid(column=0, row=7, padx=10, pady=10, sticky=tk.W)
        self.response_text = tk.Text(content, wrap=tk.WORD, height=5, width=50, state=tk.DISABLED)
        self.response_text.grid(column=0, row=8, padx=10, pady=10)

        # Create "Load History" button into UI elements
        load_history_btn = ttk.Button(content, text="Load History", command=self.bot.load_history)
        load_history_btn.grid(column=1, row=8, padx=10, pady=10)

        self.input_text.bind("<Button-3>", self.show_context_menu)
        self.response_text.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        widget = event.widget
        context_menu = tk.Menu(self, tearoff=0)
        if widget == self.input_text:
            context_menu.add_command(label="Copy", command=lambda: self.copy(widget))
            context_menu.add_command(label="Cut", command=lambda: self.cut(widget))
            context_menu.add_command(label="Paste", command=lambda: self.paste(widget))
            context_menu.add_command(label="Delete", command=lambda: self.delete(widget))
            context_menu.add_command(label="Select All", command=lambda: self.select_all(widget))
        elif widget == self.response_text:
            context_menu.add_command(label="Copy", command=lambda: self.copy(widget))
            context_menu.add_command(label="Select All", command=lambda: self.select_all(widget))
        context_menu.tk_popup(event.x_root, event.y_root)

    def copy(self, widget):
        try:
            widget.clipboard_clear()
            widget.clipboard_append(widget.selection_get())
        except tk.TclError:
            pass

    def paste(self, widget):
        try:
            widget.insert(tk.INSERT, widget.clipboard_get())
        except tk.TclError:
            pass

    def cut(self, widget):
        try:
            widget.clipboard_clear()
            widget.clipboard_append(widget.selection_get())
            widget.delete("sel.first", "sel.last")
        except tk.TclError:
            pass

    def delete(self, widget):
        try:
            widget.delete("sel.first", "sel.last")
        except tk.TclError:
            pass

    def select_all(self, widget):
        try:
            widget.tag_add("sel", "1.0", "end")
        except tk.TclError:
            pass
    
    def on_send_click(self):
        self.user_input = self.input_text.get("1.0", tk.END).strip()
        if self.user_input:
            self.send_message()
            ai_response = self.get_api_response(self.user_input)

            self.response_text.config(state=tk.NORMAL)
            self.response_text.delete("1.0", tk.END)
            self.response_text.insert("1.0", ai_response)
            self.response_text.config(state=tk.DISABLED)
            
            if ai_response:
                print("AI response:", ai_response)
            else:
                print("No response from API")

    def extract_text_from_pdf(self, file_path):
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text()
        return text

    def extract_text_from_docx(self, file_path):
        text = ""
        doc = docx.Document(file_path)
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text

    def extract_text_from_image(self, file_path):
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        return text

    def extract_text_from_python(self, file_path):
        with open(file_path, 'r') as file:
            text = file.read()
            return text

    def load_document(self):
        self.file_path = filedialog.askopenfilename(filetypes=[
            ("PDF Files", "*.pdf"), 
            ("Word Documents", "*.docx"), 
            ("Python Files", "*.py"), 
            ("Images", "*.jpg;*.png;*.jpeg")
        ])

        if self.file_path.endswith(".pdf"):
            text = self.extract_text_from_pdf(self.file_path)
        elif self.file_path.endswith(".docx"):
            text = self.extract_text_from_docx(self.file_path)
        elif self.file_path.endswith(".py"):
            text = self.extract_text_from_python(self.file_path)
        else:
            text = self.extract_text_from_image(self.file_path)
        
        self.input_text.delete(1.0, tk.END)
        self.input_text.insert(tk.END, text)

    def process_message(self, message):
        user_message = {'role': 'user', 'content': message}
        self.bot.add_to_history(user_message)
        
        # Include the entire conversation history in the message vectorization process
        history_content = " ".join([msg["content"] for msg in self.bot.datagarden.conversation])
        message_vector = vectorizer.fit_transform([history_content]).toarray()[0]

        if len(self.bot.datagarden.conversation) > 1000:
            self.bot.datagarden.conversation = self.bot.truncate_conversation_history(max_tokens=4096, filename="data/truncated_history.json")

    def get_api_response(self, prompt):
        def query(payload):
            response = requests.post(API_URL, headers=headers, json=payload)
            return response.json()

        self.bot.datagarden.conversation.append({"role": "user", "content": prompt})
        truncated_history = self.bot.truncate_conversation_history()
        print(f"Full conversation history: {self.bot.datagarden.conversation}")
        print(f"Truncated conversation history: {truncated_history}")

        data = {
            "inputs": prompt,
        }
        result = query(data)

        if "generated_text" in result:
            ai_response = {"role": "assistant", "content": result["generated_text"]}
            self.bot.datagarden.conversation.append(ai_response)
            return ai_response["content"]
        else:
            print(f"Unexpected API response: {result}")
            return "Error: Could not get a response from the API."

def main():
    app = PersonalizedAIApp()
    app.mainloop()

if __name__ == "__main__":
    main()
