import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter import ttk
import os
from test_post import post_to_elasticsearch

class ElasticUploaderGUI:
    """GUI interface for uploading JSON files to Elasticsearch."""
    
    # GUI Configuration
    WINDOW_TITLE = "Elasticsearch Upload Interface"
    WINDOW_SIZE = "600x400"
    FONT_FAMILY = "Arial"
    FONT_SIZE = 12

    def __init__(self, search_gui=None):
        """Initialize the upload GUI."""
        self.search_gui = search_gui  # Store reference to search GUI
        self.root = tk.Tk()
        self.setup_window()
        self.create_widgets()

    def setup_window(self) -> None:
        """Configure the main window properties."""
        self.root.title(self.WINDOW_TITLE)
        self.root.geometry(self.WINDOW_SIZE)
        self.root.minsize(500, 400)  # Add minimum window size
        # Configure grid weights for resizing
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

    def create_widgets(self) -> None:
        """Create and configure all GUI widgets."""
        self._create_top_buttons()  # Add this line
        self._create_directory_frame()
        self._create_upload_button()
        self._create_progress_bar()
        self._create_results_area()

    def _create_top_buttons(self) -> None:
        """Create top navigation buttons."""
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill=tk.X, pady=5)

        # Search button at top-right
        search_btn = tk.Button(
            button_frame,
            text="Chuyển sang Search",
            command=self._back_to_search,
            font=(self.FONT_FAMILY, self.FONT_SIZE)
        )
        search_btn.pack(side=tk.RIGHT, padx=10)

    def _back_to_search(self) -> None:
        """Close uploader and show search window."""
        self.root.destroy()
        if self.search_gui:
            self.search_gui.root.deiconify()  # Show search window

    def _create_directory_frame(self) -> None:
        """Create the directory selection frame."""
        frame = ttk.Frame(self.root, padding="10")
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Configure frame grid weights
        frame.grid_columnconfigure(1, weight=1)
        
        # Label
        tk.Label(frame, 
                text="Chọn thư mục chứa file JSON:", 
                font=(self.FONT_FAMILY, self.FONT_SIZE)
        ).grid(row=0, column=0, padx=5)

        # Directory entry with normal state first
        self.dir_path = tk.StringVar()
        self.dir_entry = ttk.Entry(
            frame, 
            textvariable=self.dir_path,
            font=(self.FONT_FAMILY, self.FONT_SIZE),
            width=40  # Set a reasonable default width
        )
        self.dir_entry.grid(row=0, column=1, padx=5, sticky='ew')
        
        # Browse button
        self.browse_btn = ttk.Button(
            frame,
            text="Duyệt...",
            command=self.browse_directory,
            style='Custom.TButton'
        )
        self.browse_btn.grid(row=0, column=2, padx=5)

    def _create_upload_button(self) -> None:
        """Create the upload execution button."""
        self.upload_btn = ttk.Button(
            self.root,
            text="Upload lên Elasticsearch",
            command=self.upload_files,
            style='Custom.TButton'
        )
        self.upload_btn.pack(pady=10)

    def _create_progress_bar(self) -> None:
        """Create the progress bar."""
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.root,
            variable=self.progress_var,
            maximum=100,
            style='Custom.Horizontal.TProgressbar'
        )
        self.progress_bar.pack(fill=tk.X, padx=10, pady=5)

    def _create_results_area(self) -> None:
        """Create the scrolled text area for results."""
        self.results_area = scrolledtext.ScrolledText(
            self.root,
            width=60,
            height=15,
            font=(self.FONT_FAMILY, self.FONT_SIZE),
            cursor="arrow"
        )
        self.results_area.pack(padx=10, pady=5)

    def browse_directory(self) -> None:
        """Handle directory selection."""
        directory = filedialog.askdirectory(title="Chọn thư mục chứa file JSON")
        if directory:
            self.dir_entry.config(state='normal')  # Temporarily enable entry
            self.dir_path.set(directory)
            self.dir_entry.config(state='readonly')  # Make readonly after setting text
            self.root.update()  # Force update of the display

    def upload_files(self) -> None:
        """Execute the file upload process."""
        directory = self.dir_path.get()
        if not directory:
            messagebox.showerror("Lỗi", "Vui lòng chọn thư mục trước!")
            return

        json_files = [f for f in os.listdir(directory) if f.endswith('.json')]
        total_files = len(json_files)

        if (total_files == 0):
            messagebox.showwarning("Cảnh báo", "Không tìm thấy file JSON trong thư mục!")
            return

        self.results_area.delete(1.0, tk.END)
        self.results_area.insert(tk.END, f"Tổng số file cần xử lý: {total_files}\n\n")

        for i, file_name in enumerate(json_files, 1):
            file_path = os.path.join(directory, file_name)
            
            # Hiển thị thông tin tiến trình hiện tại
            progress_info = f"Đang xử lý file {i}/{total_files}: {file_name}\n"
            self.results_area.insert(tk.END, progress_info)
            self.results_area.see(tk.END)
            
            success, message = post_to_elasticsearch(file_path)
            status = "✅" if success else "❌"
            self.results_area.insert(tk.END, f"{status} {message}\n")
            self.results_area.insert(tk.END, "-" * 50 + "\n")
            self.results_area.see(tk.END)
            
            # Cập nhật thanh tiến trình
            progress = (i / total_files) * 100
            self.progress_var.set(progress)
            self.progress_bar.update_idletasks()
            self.root.update()

        messagebox.showinfo("Hoàn thành", f"Đã xử lý xong {total_files} file!")

    def run(self) -> None:
        """Start the GUI application."""
        # Configure styles
        style = ttk.Style()
        style.configure('Custom.TButton', font=(self.FONT_FAMILY, self.FONT_SIZE))
        style.configure('Custom.Horizontal.TProgressbar', thickness=20)
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        self.root.mainloop()

    def _on_closing(self) -> None:
        """Handle window closing event."""
        self.root.destroy()
        if self.search_gui:
            self.search_gui.root.deiconify()

if __name__ == "__main__":
    app = ElasticUploaderGUI()
    app.run()
