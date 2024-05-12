import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import os

def custom_style():
    style = {
        "bg": "black",
        "fg": "white",
        "font": ("Arial", 14),
        "button": {"bg": "dark green", "fg": "white", "activebackground": "green", "font": ("Arial", 14)}
    }
    return style

def browse_file():
    global input_file_path
    input_file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
    if input_file_path:
        file_label.config(text=os.path.basename(input_file_path))

def browse_folder():
    global output_dir
    output_dir = filedialog.askdirectory()
    if output_dir:
        folder_label.config(text=output_dir)

def run_script():
    sheet_name = sheet_name_entry.get()
    if not (input_file_path, output_dir, sheet_name):
        messagebox.showerror("Error", "Geleive alles in te vullen en te selecteren.", background='black', foreground='white')
        return

    data = pd.read_excel(input_file_path, sheet_name=sheet_name)
    if 'LastLoggedIn' in data.columns:
        data['LastLoggedIn'] = pd.to_datetime(data['LastLoggedIn']).dt.strftime('%d-%m-%Y %H:%M:%S')
    speciesdata = data["ID"].unique()

    for i in speciesdata:
        filtered_data = data[data["ID"] == i]
        filtered_data.to_excel(f"{output_dir}/{i}.xlsx", index=False)
    
    os.startfile(output_dir)
    messagebox.showinfo("Voltooid", "Proces is perfect doorlopen!", background='black', foreground='white')

root = tk.Tk()
root.title("Jaarlijkse opschoonactie Digitaal Ondertekenen")
style = custom_style()

root.config(bg=style["bg"])
root.geometry('800x250')  # Adjust window size to make sure all elements are visible

file_label = tk.Label(root, text="Geen bestand geselecteerd", bg=style["bg"], fg=style["fg"], font=style["font"])
file_label.pack(pady=(10, 0), fill=tk.X)

buttons_frame = tk.Frame(root, bg=style["bg"])
buttons_frame.pack(pady=(10, 10))

tk.Button(buttons_frame, text="Selecteer het Excel bestand", command=browse_file, **style["button"]).pack(side=tk.LEFT, padx=(10, 20))
tk.Button(buttons_frame, text="Selecteer de map waar alles opgeslagen wordt", command=browse_folder, **style["button"]).pack(side=tk.LEFT)

folder_label = tk.Label(root, text="Geen map geselecteerd", bg=style["bg"], fg=style["fg"], font=style["font"])
folder_label.pack(pady=(0, 10), fill=tk.X)

sheet_name_frame = tk.Frame(root, bg=style["bg"])
sheet_name_frame.pack(fill=tk.X, pady=(0, 20))

tk.Label(sheet_name_frame, text="Bladnaam:", bg=style["bg"], fg=style["fg"], font=style["font"]).pack(side=tk.LEFT, padx=(20, 0))

sheet_name_entry = tk.Entry(sheet_name_frame, font=("Arial", 14), bg='black', fg='white', insertbackground='white', width=80)
sheet_name_entry.pack(side=tk.LEFT, padx=(0, 20))
sheet_name_entry.config(highlightbackground='red', highlightcolor='red', highlightthickness=1)

tk.Button(root, text="Starten", command=run_script, **style["button"]).pack(pady=(0, 10))

root.mainloop()
