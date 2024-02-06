from tkinter import Tk, Scrollbar, Button, Canvas, Frame, Checkbutton, IntVar, Label, filedialog, messagebox
import os
import subprocess
import hashlib
import sys

def find_duplicates(path):
    unique_files = {}
    duplicates = {}

    for folder, sub_folders, files in os.walk(path):
        for file in files:
            file_path = os.path.join(folder, file)
            try:
                file_hash = hashlib.md5(open(file_path, "rb").read()).hexdigest()
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                continue

            if file_hash in unique_files:
                if file_hash not in duplicates:
                    duplicates[file_hash] = [unique_files[file_hash]]
                duplicates[file_hash].append(file_path)
            else:
                unique_files[file_hash] = file_path

    return duplicates

def toggle_group(group_frame):
    if group_frame.winfo_viewable():
        group_frame.grid_remove()
    else:
        group_frame.grid()

def open_file(file_path):
    try:
        if os.name == 'nt':  # Windows
            os.startfile(file_path)
        elif os.name == 'posix':  # macOS, Linux
            opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
            subprocess.call([opener, file_path])
    except Exception as e:
        print(f"Error opening {file_path}: {e}")

def delete_selected_files():
    for var, file_info in zip(check_vars, all_files):
        if var.get() == 1:
            file_path = file_info[0]  # Get the file path from the tuple
            try:
                os.remove(file_path)
                print(f"{file_path} has been deleted")
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
    display_duplicates()  # Refresh the display after deletion

def select_all(value=1):
    for var in check_vars:
        var.set(value)

def display_duplicates():
    for widget in frame.winfo_children():
        widget.destroy()

    global check_vars, all_files
    check_vars = []
    all_files = []

    for group_id, duplicate_files in enumerate(duplicates.values()):
        group_title_frame = Frame(frame)
        group_title_frame.pack(fill="x", expand=True)
        group_title = f"Group {group_id + 1} - {len(duplicate_files)} Files"
        toggle_btn = Button(group_title_frame, text=group_title, command=lambda f=group_title_frame: toggle_group(f))
        toggle_btn.pack(side="left", fill="x", expand=True)

        group_frame = Frame(frame, relief="groove", bd=1)
        group_frame.pack(fill="x", expand=True, pady=2)
        
        for file_path in duplicate_files:
            file_row_frame = Frame(group_frame)
            file_row_frame.pack(fill="x", expand=True)

            var = IntVar(value=0)
            cb = Checkbutton(file_row_frame, text=file_path, variable=var)
            cb.pack(side="left", fill="x", expand=True)

            # Pack an empty frame to push the Open button to the far right
            spacer_frame = Frame(file_row_frame)
            spacer_frame.pack(side="left", fill="x", expand=True)

            open_btn = Button(file_row_frame, text="Open", command=lambda path=file_path: open_file(path))
            open_btn.pack(side="right")

            check_vars.append(var)
            all_files.append((file_path, file_row_frame))

        # Initially hide the group frame
        group_frame.grid_remove()

def delete_duplicates_keep_first():
    for duplicate_files in duplicates.values():
        # Skip the first file in each group
        for file_path in duplicate_files[1:]:  # Start from the second item
            try:
                os.remove(file_path)
                print(f"Deleted duplicate: {file_path}")
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")
    # Refresh the display after deletion
    display_duplicates()

def start_new_search():
    global duplicates, check_vars, all_files
    for widget in frame.winfo_children():
        widget.destroy()  # Clear the current list of duplicates
    duplicates = {}  # Reset the duplicates dictionary
    check_vars.clear()  # Clear the list of checkbox variables
    all_files.clear()  # Clear the list of all files
    # Prompt for a new directory selection and search for duplicates
    new_path = filedialog.askdirectory(title="Select a folder")
    if new_path:  # Check if a directory was selected
        duplicates = find_duplicates(new_path)
        display_duplicates()
    else:
        print("No directory selected.")



# Setup the GUI
root = Tk()
root.title("Select Duplicate Files to Delete and Open")

canvas = Canvas(root)
scrollbar = Scrollbar(root, orient="vertical", command=canvas.yview)
scrollable_frame = Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

frame = scrollable_frame

# Buttons frame
buttons_frame = Frame(root)

# Global action buttons
delete_button = Button(buttons_frame, text="Delete Selected", command=delete_selected_files)
select_all_button = Button(buttons_frame, text="Select All", command=lambda: select_all(1))
deselect_all_button = Button(buttons_frame, text="Deselect All", command=lambda: select_all(0))
delete_all_except_first_button = Button(buttons_frame, text="Keep only First", command=delete_duplicates_keep_first)
exit_button = Button(buttons_frame, text="Exit", command=root.destroy)
start_new_search_button = Button(buttons_frame, text="Start New Search", command=start_new_search)


delete_button.pack(side="left", padx=5)
select_all_button.pack(side="left", padx=5)
deselect_all_button.pack(side="left", padx=5)
delete_all_except_first_button.pack(side="left", padx=5)
exit_button.pack(side="left", padx=5)
start_new_search_button.pack(side="left", padx=5)

# Pack the buttons frame at the bottom and center
buttons_frame.pack(side="bottom", pady=10, anchor="center")

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Get directory and find duplicates, display duplicates in the UI
path = filedialog.askdirectory(title="Select a folder")
if path:  # Check if a directory was selected
    duplicates = find_duplicates(path)
    display_duplicates()
else:
    print("No directory selected. Exiting.")
    root.destroy()

# Start the GUI event loop
root.mainloop()
