import os
import shutil
import hashlib
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter import simpledialog

def organize_files_by_extension(source_dir, extensions_map):
    """
    Organizes files in the given directory (including subdirectories) into subfolders based on their extensions.
    """
    all_files = []
    for root_dir, _, files in os.walk(source_dir):
        all_files.extend([os.path.join(root_dir, file) for file in files])

    total_files = len(all_files)
    progress_bar["value"] = 0
    progress_bar["maximum"] = total_files
    processed_files = 0

    # Ensure folders for all categories are created
    for category, extensions in extensions_map.items():
        folder_path = os.path.join(source_dir, category)
        os.makedirs(folder_path, exist_ok=True)
    # Also ensure the "Others" folder is created
    others_folder_path = os.path.join(source_dir, "Others")
    os.makedirs(others_folder_path, exist_ok=True)

    for file_path in all_files:
        moved = False
        for category, extensions in extensions_map.items():
            if file_path.lower().endswith(tuple(extensions)):
                shutil.move(file_path, os.path.join(source_dir, category, os.path.basename(file_path)))
                moved = True
                break
        if not moved:
            shutil.move(file_path, os.path.join(others_folder_path, os.path.basename(file_path)))

        processed_files += 1
        progress_bar["value"] = processed_files
        root.update_idletasks()

    messagebox.showinfo("Success", "Files have been organized by extension.")

def find_and_remove_duplicates(source_dir):
    """
    Identifies and optionally removes duplicate files in the directory (including subdirectories).
    """
    hash_map = {}
    duplicates = []
    all_files = []
    for root_dir, _, files in os.walk(source_dir):
        all_files.extend([os.path.join(root_dir, file) for file in files])

    total_files = len(all_files)
    progress_bar["value"] = 0
    progress_bar["maximum"] = total_files

    for file_path in all_files:
        file_hash = hash_file(file_path)
        if file_hash in hash_map:
            duplicates.append((file_path, hash_map[file_hash]))
        else:
            hash_map[file_hash] = file_path

        progress_bar["value"] += 1
        root.update_idletasks()

    display_duplicates(duplicates)

def hash_file(file_path):
    """
    Generates an MD5 hash for the file at the given path.
    """
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def display_duplicates(duplicates):
    """
    Displays a grid of duplicate files and allows the user to select which to delete.
    """
    duplicate_window = tk.Toplevel(root)
    duplicate_window.title("Duplicate Files")
    duplicate_window.geometry("800x400")

    frame = tk.Frame(duplicate_window)
    frame.pack(fill="both", expand=True)

    canvas = tk.Canvas(frame)
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    selected_files = []

    def select_file(file_path):
        if file_path in selected_files:
            selected_files.remove(file_path)
        else:
            selected_files.append(file_path)

    def delete_selected():
        for file_path in selected_files:
            os.remove(file_path)
        duplicate_window.destroy()
        messagebox.showinfo("Success", f"Deleted {len(selected_files)} files.")

    def delete_all():
        for duplicate_pair in duplicates:
            os.remove(duplicate_pair[0])
        duplicate_window.destroy()
        messagebox.showinfo("Success", f"Deleted all {len(duplicates)} duplicates.")

    for idx, (file1, file2) in enumerate(duplicates):
        tk.Label(scrollable_frame, text=f"Duplicate Pair {idx + 1}", font=("Arial", 10, "bold")).grid(row=idx, column=0, sticky="w")

        tk.Label(scrollable_frame, text=file1, wraplength=600, justify="left").grid(row=idx, column=1, sticky="w")
        tk.Checkbutton(scrollable_frame, command=lambda f=file1: select_file(f)).grid(row=idx, column=2)

    action_frame = tk.Frame(duplicate_window)
    action_frame.pack(pady=10)

    tk.Button(action_frame, text="Delete Selected", command=delete_selected, bg="red", fg="white").pack(side="left", padx=10)
    tk.Button(action_frame, text="Delete All", command=delete_all, bg="red", fg="white").pack(side="left", padx=10)

def browse_directory():
    directory = filedialog.askdirectory()
    if directory:
        directory_entry.delete(0, tk.END)
        directory_entry.insert(0, directory)

def organize_files():
    source_dir = directory_entry.get().strip()
    if not os.path.isdir(source_dir):
        messagebox.showerror("Error", "Please select a valid directory.")
        return

    extensions_map = parse_extensions_map()
    organize_files_by_extension(source_dir, extensions_map)

def remove_duplicates():
    source_dir = directory_entry.get().strip()
    if not os.path.isdir(source_dir):
        messagebox.showerror("Error", "Please select a valid directory.")
        return

    find_and_remove_duplicates(source_dir)

def parse_extensions_map():
    extensions_map = {}
    for row in category_entries:
        category = row[0].get().strip()
        extensions = row[1].get().strip().split(",")
        if category and extensions:
            extensions_map[category] = [ext.strip() for ext in extensions]
    return extensions_map

def add_new_category():
    new_row = [tk.Entry(category_frame, width=20), tk.Entry(category_frame, width=40)]
    new_row[0].grid(row=len(category_entries) + 1, column=0, padx=5, pady=5)
    new_row[1].grid(row=len(category_entries) + 1, column=1, padx=5, pady=5)
    category_entries.append(new_row)

# Create the main application window
root = tk.Tk()
root.title("File Organizer and Duplicate Remover")
root.geometry("700x500")
root.configure(bg="#f0f8ff")

# Directory selection frame
frame = tk.Frame(root, bg="#f0f8ff")
frame.pack(pady=10)

directory_label = tk.Label(frame, text="Select Directory:", bg="#f0f8ff", font=("Arial", 12))
directory_label.grid(row=0, column=0, padx=5)

directory_entry = tk.Entry(frame, width=50, font=("Arial", 12))
directory_entry.grid(row=0, column=1, padx=5)

browse_button = tk.Button(frame, text="Browse", command=browse_directory, bg="#4682b4", fg="white", font=("Arial", 10))
browse_button.grid(row=0, column=2, padx=5)

# Extensions customization frame
custom_frame = tk.LabelFrame(root, text="Customize Extension Categories", bg="#f0f8ff", font=("Arial", 12, "bold"))
custom_frame.pack(pady=10, fill="x")

category_frame = tk.Frame(custom_frame, bg="#f0f8ff")
category_frame.pack(pady=10)

# Default categories
category_entries = []
default_categories = {
    "Music": ".mp3, .wav, .flac",
    "Videos": ".mp4, .avi, .mkv",
    "Documents": ".pdf, .docx, .txt",
    "Images": ".jpg, .jpeg, .png",
}

for idx, (category, extensions) in enumerate(default_categories.items()):
    entry_category = tk.Entry(category_frame, width=20)
    entry_category.insert(0, category)
    entry_category.grid(row=idx, column=0, padx=5, pady=5)

    entry_extensions = tk.Entry(category_frame, width=40)
    entry_extensions.insert(0, extensions)
    entry_extensions.grid(row=idx, column=1, padx=5, pady=5)

    category_entries.append([entry_category, entry_extensions])

add_category_button = tk.Button(custom_frame, text="Add New Category", command=add_new_category, bg="#32cd32", fg="white", font=("Arial", 10))
add_category_button.pack(pady=5)

# Action buttons
action_frame = tk.Frame(root, bg="#f0f8ff")
action_frame.pack(pady=10)

organize_button = tk.Button(action_frame, text="Organize Files", command=organize_files, bg="#4682b4", fg="white", font=("Arial", 12), width=15)
organize_button.grid(row=0, column=0, padx=10)

remove_duplicates_button = tk.Button(action_frame, text="Remove Duplicates", command=remove_duplicates, bg="#dc143c", fg="white", font=("Arial", 12), width=15)
remove_duplicates_button.grid(row=0, column=1, padx=10)

# Progress bar
progress_bar = ttk.Progressbar(root, orient="horizontal", length=600, mode="determinate")
progress_bar.pack(pady=10)

# Run the application
root.mainloop()
