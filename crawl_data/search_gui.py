import tkinter as tk
from tkinter import scrolledtext
import webbrowser
from typing import Optional, Callable
from search_engine import SearchEngine

class SearchGUI:
    """GUI interface for the animal search engine."""
    
    # GUI Configuration
    WINDOW_TITLE = "Elasticsearch Query Interface"
    WINDOW_SIZE = "600x400"
    FONT_FAMILY = "Arial"
    FONT_SIZE = 12
    
    def __init__(self):
        """Initialize the search GUI."""
        self.search_engine = SearchEngine()
        self.root = tk.Tk()
        self.setup_window()
        self.create_widgets()
        self.setup_bindings()

    def setup_window(self) -> None:
        """Configure the main window properties."""
        self.root.title(self.WINDOW_TITLE)
        self.root.geometry(self.WINDOW_SIZE)

    def create_widgets(self) -> None:
        """Create and configure all GUI widgets."""
        self._create_top_buttons()  # Add this line
        self._create_search_input()
        self._create_search_button()
        self._create_results_area()

    def _create_top_buttons(self) -> None:
        """Create top navigation buttons."""
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill=tk.X, pady=5)

        # Upload button at top-right
        upload_btn = tk.Button(
            button_frame,
            text="Chuyển sang Upload",
            command=self._open_uploader,
            font=(self.FONT_FAMILY, self.FONT_SIZE)
        )
        upload_btn.pack(side=tk.RIGHT, padx=10)

    def _open_uploader(self) -> None:
        """Open the uploader window and hide search window."""
        self.root.withdraw()  # Hide search window
        from elastic_uploader import ElasticUploaderGUI
        uploader = ElasticUploaderGUI(self)  # Pass search_gui instance
        uploader.run()

    def _create_search_input(self) -> None:
        """Create the search input field and label."""
        font = (self.FONT_FAMILY, self.FONT_SIZE)
        
        tk.Label(self.root, text="Nhập truy vấn của bạn:", font=font).pack(pady=5)
        self.query_input = tk.Entry(self.root, width=50, font=font)
        self.query_input.pack(pady=5)

    def _create_search_button(self) -> None:
        """Create the search execution button."""
        button = tk.Button(
            self.root,
            text="Thực hiện truy vấn",
            command=self.execute_query,
            font=(self.FONT_FAMILY, self.FONT_SIZE)
        )
        button.pack(pady=10)

    def _create_results_area(self) -> None:
        """Create the scrolled text area for results."""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        self.results_area = scrolledtext.ScrolledText(
            self.root,
            width=screen_width,
            height=screen_height,
            cursor="arrow",
            font=(self.FONT_FAMILY, self.FONT_SIZE)
        )
        self.results_area.pack(pady=10)
        self.results_area.tag_configure(
            "link",
            foreground="blue",
            underline=1,
            font=(self.FONT_FAMILY, self.FONT_SIZE)
        )

    def setup_bindings(self) -> None:
        """Set up event bindings for the GUI."""
        self.query_input.bind('<KeyRelease>', self.on_key_release)
        self.query_input.bind('<Control-BackSpace>', self.delete_word)

    def execute_query(self) -> None:
        """Execute the search query and display results."""
        query = self.query_input.get()
        results = self.search_engine.search(query)
        
        self.results_area.delete(1.0, tk.END)
        self.results_area.insert(tk.END, "Kết quả truy vấn:\n\n")
        
        self._display_results(results)

    def _display_results(self, results: list) -> None:
        """Display the search results in the results area."""
        for idx, result in enumerate(results):
            description_lines = result['description'].splitlines()
            if len(description_lines) > 3:
                description_preview = "\n".join(description_lines[:3]) + "\n..."
            else:
                description_preview = "\n".join(description_lines)
            
            # Tạo tag riêng cho từng link
            link_tag = f"link_{idx}"
            self.results_area.tag_configure(
                link_tag,
                foreground="blue",
                underline=1,
                font=(self.FONT_FAMILY, self.FONT_SIZE)
            )
            
            self.results_area.insert(tk.END, "")
            self.results_area.insert(tk.END, result['title'], link_tag)
            
            # Tạo callback riêng cho từng link
            self.results_area.tag_bind(
                link_tag, 
                "<Button-1>", 
                lambda e, url=result['url']: webbrowser.open_new_tab(url)
            )
            
            self.results_area.insert(
                tk.END,
                f" ({result['score']})\n{description_preview}\n\n"
            )

    def on_key_release(self, event: tk.Event) -> None:
        """Handle key release events."""
        if event.char == " ":
            self.execute_query()

    def delete_word(self, event: tk.Event) -> str:
        """Handle Ctrl+Backspace to delete the last word."""
        current_pos = self.query_input.index(tk.INSERT)
        text = self.query_input.get()
        last_space = text[:current_pos].rstrip().rfind(' ')
        
        if last_space == -1:
            self.query_input.delete(0, current_pos)
        else:
            self.query_input.delete(last_space + 1, current_pos)
        
        return "break"

    def run(self) -> None:
        """Start the GUI application."""
        self.root.mainloop()

if __name__ == "__main__":
    app = SearchGUI()
    app.run()
