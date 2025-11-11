import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import urllib.request
import urllib.parse
import urllib.error
import os
import re
import threading
from html.parser import HTMLParser
import http.client
import ssl
import time

class ImageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.image_urls = []
    
    def handle_starttag(self, tag, attrs):
        if tag == 'img':
            for attr, value in attrs:
                if attr == 'src' and value:
                    self.image_urls.append(value)

class AdvancedImageDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("ChowdhuryVai - Advanced Image Downloader")
        self.root.geometry("800x700")
        self.root.configure(bg='#0a0a0a')
        self.root.resizable(True, True)
        
        # Initialize variables first
        self.download_folder = "downloaded_images"
        self.image_urls = []
        self.download_thread = None
        self.stop_download = False
        
        # Create download folder
        self.create_download_folder()
        
        # Center the window
        self.center_window()
        
        # Create GUI
        self.create_gui()
        
    def center_window(self):
        self.root.update_idletasks()
        width = 800
        height = 700
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
    def create_download_folder(self):
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)
    
    def create_gui(self):
        # Main frame
        main_frame = tk.Frame(self.root, bg='#0a0a0a')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header with branding
        header_frame = tk.Frame(main_frame, bg='#0a0a0a')
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(
            header_frame, 
            text="ChowdhuryVai Image Downloader", 
            font=("Courier", 20, "bold"),
            fg='#00ff00',
            bg='#0a0a0a'
        )
        title_label.pack(pady=10)
        
        subtitle_label = tk.Label(
            header_frame,
            text="Advanced Web Image Extraction Tool",
            font=("Courier", 10),
            fg='#00ffff',
            bg='#0a0a0a'
        )
        subtitle_label.pack()
        
        # URL input section
        url_frame = tk.Frame(main_frame, bg='#0a0a0a')
        url_frame.pack(fill=tk.X, pady=10)
        
        url_label = tk.Label(
            url_frame,
            text="Website URL:",
            font=("Courier", 10, "bold"),
            fg='#ffffff',
            bg='#0a0a0a'
        )
        url_label.pack(anchor=tk.W)
        
        self.url_entry = tk.Entry(
            url_frame,
            font=("Courier", 10),
            bg='#1a1a1a',
            fg='#00ff00',
            insertbackground='#00ff00',
            width=70
        )
        self.url_entry.pack(fill=tk.X, pady=5)
        self.url_entry.insert(0, "https://")
        
        # Options frame
        options_frame = tk.Frame(main_frame, bg='#0a0a0a')
        options_frame.pack(fill=tk.X, pady=10)
        
        # Filter options
        filter_label = tk.Label(
            options_frame,
            text="Image Filters:",
            font=("Courier", 10, "bold"),
            fg='#ffffff',
            bg='#0a0a0a'
        )
        filter_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.filter_var = tk.StringVar(value="all")
        
        filter_frame = tk.Frame(options_frame, bg='#0a0a0a')
        filter_frame.grid(row=1, column=0, columnspan=3, sticky=tk.W)
        
        tk.Radiobutton(
            filter_frame, 
            text="All Images", 
            variable=self.filter_var, 
            value="all",
            font=("Courier", 9),
            fg='#ffffff',
            bg='#0a0a0a',
            selectcolor='#1a1a1a'
        ).pack(side=tk.LEFT)
        
        tk.Radiobutton(
            filter_frame, 
            text="JPG Only", 
            variable=self.filter_var, 
            value="jpg",
            font=("Courier", 9),
            fg='#ffffff',
            bg='#0a0a0a',
            selectcolor='#1a1a1a'
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Radiobutton(
            filter_frame, 
            text="PNG Only", 
            variable=self.filter_var, 
            value="png",
            font=("Courier", 9),
            fg='#ffffff',
            bg='#0a0a0a',
            selectcolor='#1a1a1a'
        ).pack(side=tk.LEFT)
        
        # Download folder
        folder_label = tk.Label(
            options_frame,
            text="Download Folder:",
            font=("Courier", 10, "bold"),
            fg='#ffffff',
            bg='#0a0a0a'
        )
        folder_label.grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        
        folder_frame = tk.Frame(options_frame, bg='#0a0a0a')
        folder_frame.grid(row=3, column=0, columnspan=3, sticky=tk.W+tk.E)
        
        self.folder_var = tk.StringVar(value=self.download_folder)
        self.folder_entry = tk.Entry(
            folder_frame,
            textvariable=self.folder_var,
            font=("Courier", 9),
            bg='#1a1a1a',
            fg='#00ff00',
            insertbackground='#00ff00',
            width=50
        )
        self.folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_btn = tk.Button(
            folder_frame,
            text="Browse",
            command=self.browse_folder,
            font=("Courier", 9, "bold"),
            bg='#006600',
            fg='#ffffff',
            activebackground='#008800',
            activeforeground='#ffffff'
        )
        browse_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Control buttons
        button_frame = tk.Frame(main_frame, bg='#0a0a0a')
        button_frame.pack(fill=tk.X, pady=20)
        
        self.extract_btn = tk.Button(
            button_frame,
            text="Extract Images",
            command=self.start_extraction,
            font=("Courier", 10, "bold"),
            bg='#0066cc',
            fg='#ffffff',
            activebackground='#0088ff',
            activeforeground='#ffffff',
            width=15,
            height=2
        )
        self.extract_btn.pack(side=tk.LEFT, padx=5)
        
        self.download_btn = tk.Button(
            button_frame,
            text="Download All",
            command=self.start_download,
            font=("Courier", 10, "bold"),
            bg='#cc6600',
            fg='#ffffff',
            activebackground='#ff8800',
            activeforeground='#ffffff',
            width=15,
            height=2,
            state=tk.DISABLED
        )
        self.download_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = tk.Button(
            button_frame,
            text="Clear",
            command=self.clear_all,
            font=("Courier", 10, "bold"),
            bg='#cc0000',
            fg='#ffffff',
            activebackground='#ff0000',
            activeforeground='#ffffff',
            width=15,
            height=2
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Progress section
        progress_frame = tk.Frame(main_frame, bg='#0a0a0a')
        progress_frame.pack(fill=tk.X, pady=10)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        self.status_label = tk.Label(
            progress_frame,
            text="Ready to extract images...",
            font=("Courier", 9),
            fg='#ffff00',
            bg='#0a0a0a'
        )
        self.status_label.pack()
        
        # Results section
        results_frame = tk.Frame(main_frame, bg='#0a0a0a')
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        results_label = tk.Label(
            results_frame,
            text="Extracted Images:",
            font=("Courier", 10, "bold"),
            fg='#ffffff',
            bg='#0a0a0a'
        )
        results_label.pack(anchor=tk.W)
        
        # Text area with scrollbar for results
        text_frame = tk.Frame(results_frame, bg='#0a0a0a')
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.results_text = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            font=("Courier", 9),
            bg='#1a1a1a',
            fg='#00ff00',
            insertbackground='#00ff00',
            width=80,
            height=15
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Footer with contact information
        footer_frame = tk.Frame(main_frame, bg='#0a0a0a')
        footer_frame.pack(fill=tk.X, pady=(20, 0))
        
        footer_text = "Telegram ID: https://t.me/darkvaiadmin | Telegram Channel: https://t.me/windowspremiumkey | Website: https://crackyworld.com/"
        
        footer_label = tk.Label(
            footer_frame,
            text=footer_text,
            font=("Courier", 8),
            fg='#888888',
            bg='#0a0a0a',
            justify=tk.CENTER
        )
        footer_label.pack()
        
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_var.set(folder)
            self.download_folder = folder
    
    def start_extraction(self):
        url = self.url_entry.get().strip()
        if not url or url == "https://":
            messagebox.showerror("Error", "Please enter a valid URL")
            return
        
        # Disable button during extraction
        self.extract_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Extracting images...")
        
        # Start extraction in a separate thread
        thread = threading.Thread(target=self.extract_images, args=(url,))
        thread.daemon = True
        thread.start()
    
    def extract_images(self, url):
        try:
            # Create a custom header to avoid blocking
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Create request with headers
            req = urllib.request.Request(url, headers=headers)
            
            # Disable SSL verification for problematic sites
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Open URL with custom SSL context
            with urllib.request.urlopen(req, context=ssl_context) as response:
                html_content = response.read().decode('utf-8', errors='ignore')
            
            # Parse HTML for images
            parser = ImageParser()
            parser.feed(html_content)
            
            # Get base URL for relative paths
            parsed_url = urllib.parse.urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            # Process image URLs
            self.image_urls = []
            for img_url in parser.image_urls:
                # Convert relative URLs to absolute
                if img_url.startswith('//'):
                    img_url = f"{parsed_url.scheme}:{img_url}"
                elif img_url.startswith('/'):
                    img_url = f"{base_url}{img_url}"
                elif not img_url.startswith(('http://', 'https://')):
                    # Handle relative paths without leading slash
                    img_url = f"{base_url}/{img_url}"
                
                # Apply filters
                if self.filter_var.get() == "all":
                    self.image_urls.append(img_url)
                elif img_url.lower().endswith(f".{self.filter_var.get()}"):
                    self.image_urls.append(img_url)
                elif img_url.lower().endswith(f".{self.filter_var.get()}e"):
                    self.image_urls.append(img_url)
            
            # Update UI in main thread
            self.root.after(0, self.update_extraction_results)
            
        except Exception as e:
            self.root.after(0, lambda: self.show_error(f"Extraction failed: {str(e)}"))
    
    def update_extraction_results(self):
        # Re-enable button
        self.extract_btn.config(state=tk.NORMAL)
        
        if not self.image_urls:
            self.status_label.config(text="No images found")
            messagebox.showinfo("Info", "No images found on the website")
            return
        
        # Update status
        self.status_label.config(text=f"Found {len(self.image_urls)} images")
        
        # Update results text
        self.results_text.delete(1.0, tk.END)
        for i, url in enumerate(self.image_urls, 1):
            self.results_text.insert(tk.END, f"{i}. {url}\n")
        
        # Enable download button
        self.download_btn.config(state=tk.NORMAL)
        
        messagebox.showinfo("Success", f"Found {len(self.image_urls)} images. Ready to download.")
    
    def start_download(self):
        if not self.image_urls:
            messagebox.showwarning("Warning", "No images to download")
            return
        
        # Reset progress
        self.progress_var.set(0)
        self.stop_download = False
        
        # Disable buttons during download
        self.extract_btn.config(state=tk.DISABLED)
        self.download_btn.config(state=tk.DISABLED)
        
        # Start download in a separate thread
        self.download_thread = threading.Thread(target=self.download_images)
        self.download_thread.daemon = True
        self.download_thread.start()
    
    def download_images(self):
        total = len(self.image_urls)
        successful = 0
        failed = 0
        
        for i, url in enumerate(self.image_urls):
            if self.stop_download:
                break
                
            # Update progress
            progress = (i / total) * 100
            self.root.after(0, lambda p=progress: self.progress_var.set(p))
            self.root.after(0, lambda idx=i, tot=total: self.status_label.config(text=f"Downloading {idx+1}/{tot}"))
            
            try:
                # Get filename from URL
                parsed_url = urllib.parse.urlparse(url)
                filename = os.path.basename(parsed_url.path)
                if not filename or '.' not in filename:
                    # Generate a filename if none found
                    filename = f"image_{i+1}.jpg"
                
                # Ensure unique filename
                counter = 1
                base_name, ext = os.path.splitext(filename)
                if not ext:
                    ext = '.jpg'
                
                final_filename = filename
                final_path = os.path.join(self.download_folder, final_filename)
                
                while os.path.exists(final_path):
                    final_filename = f"{base_name}_{counter}{ext}"
                    final_path = os.path.join(self.download_folder, final_filename)
                    counter += 1
                
                # Download image
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                req = urllib.request.Request(url, headers=headers)
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                
                with urllib.request.urlopen(req, context=ssl_context) as response:
                    image_data = response.read()
                    
                with open(final_path, 'wb') as f:
                    f.write(image_data)
                
                successful += 1
                
                # Update results text with download status
                self.root.after(0, lambda idx=i: self.update_download_status(idx, "✓"))
                
            except Exception as e:
                failed += 1
                self.root.after(0, lambda idx=i: self.update_download_status(idx, "✗"))
            
            # Small delay to avoid overwhelming the server
            time.sleep(0.1)
        
        # Final update
        self.root.after(0, lambda s=successful, f=failed: self.download_completed(s, f))
    
    def update_download_status(self, index, status):
        try:
            # Get current text
            current_text = self.results_text.get(1.0, tk.END)
            lines = current_text.split('\n')
            
            # Update the specific line
            if index < len(lines) and lines[index].strip():
                # Remove any existing status symbol and add new one
                line = lines[index]
                if line.startswith(('✓', '✗')):
                    line = line[2:]  # Remove existing status
                lines[index] = f"{status} {line}"
                new_text = '\n'.join(lines)
                
                # Replace text
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(1.0, new_text)
        except Exception:
            pass
    
    def download_completed(self, successful, failed):
        # Update progress to 100%
        self.progress_var.set(100)
        
        # Re-enable buttons
        self.extract_btn.config(state=tk.NORMAL)
        self.download_btn.config(state=tk.NORMAL)
        
        # Show completion message
        if self.stop_download:
            self.status_label.config(text="Download cancelled")
            messagebox.showinfo("Info", "Download was cancelled")
        else:
            self.status_label.config(text=f"Download completed: {successful} successful, {failed} failed")
            messagebox.showinfo("Success", f"Download completed!\nSuccessful: {successful}\nFailed: {failed}\n\nImages saved to: {self.download_folder}")
    
    def clear_all(self):
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, "https://")
        self.results_text.delete(1.0, tk.END)
        self.progress_var.set(0)
        self.status_label.config(text="Ready to extract images...")
        self.image_urls = []
        self.download_btn.config(state=tk.DISABLED)
    
    def show_error(self, message):
        self.extract_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Extraction failed")
        messagebox.showerror("Error", message)

def main():
    root = tk.Tk()
    app = AdvancedImageDownloader(root)
    root.mainloop()

if __name__ == "__main__":
    main()
