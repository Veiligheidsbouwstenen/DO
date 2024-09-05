import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import os
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font

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
    if not (input_file_path and output_dir and sheet_name):
        messagebox.showerror("Error", "Gelieve alles in te vullen en te selecteren.")
        return

    try:
        data = pd.read_excel(input_file_path, sheet_name=sheet_name)
        if 'LastLoggedIn' in data.columns:
            data['LastLoggedIn'] = pd.to_datetime(data['LastLoggedIn']).dt.strftime('%d-%m-%Y %H:%M:%S')
        speciesdata = data["ID"].unique()

        for i in speciesdata:
            filtered_data = data[data["ID"] == i]
            output_path = f"{output_dir}/{i}.xlsx"
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                filtered_data.to_excel(writer, index=False)
                workbook = writer.book
                worksheet = writer.sheets['Sheet1']

                for column_cells in worksheet.columns:
                    length = max(len(as_text(cell.value)) for cell in column_cells) + 2
                    worksheet.column_dimensions[get_column_letter(column_cells[0].column)].width = length

                for cell in worksheet["1:1"]:
                    cell.font = Font(bold=True)

        os.startfile(output_dir)
        messagebox.showinfo("Voltooid", "Proces is perfect doorlopen!")
    except Exception as e:
        messagebox.showerror("Error", f"Er is een fout opgetreden: {str(e)}")

def as_text(value):
    if value is None:
        return ""
    return str(value)

def close_application():
    root.destroy()

root = tk.Tk()
root.title("Jaarlijkse opschoonactie Digitaal Ondertekenen")
style = custom_style()

root.config(bg=style["bg"])
root.geometry('1000x200')  # Adjust window size to make sure all elements are visible

# Create grid layout
file_button = tk.Button(root, text="Selecteer het Excel bestand", command=browse_file, **style["button"])
file_label = tk.Label(root, text="Geen bestand geselecteerd", bg=style["bg"], fg=style["fg"], font=style["font"])
folder_button = tk.Button(root, text="Selecteer de map waar alles opgeslagen wordt", command=browse_folder, **style["button"])
folder_label = tk.Label(root, text="Geen map geselecteerd", bg=style["bg"], fg=style["fg"], font=style["font"])
label_sheet_name = tk.Label(root, text="Bladnaam:", bg=style["bg"], fg=style["fg"], font=style["font"])
sheet_name_entry = tk.Entry(root, font=("Arial", 14), bg='black', fg='white', insertbackground='white', width=40)
start_button = tk.Button(root, text="Starten", command=run_script, **style["button"])
close_button = tk.Button(root, text="Sluiten", command=close_application, **style["button"])

# Position with grid
file_button.grid(row=0, column=0, padx=(10, 20), pady=(10, 0), sticky='w')
file_label.grid(row=0, column=1, padx=(10, 20), pady=(10, 0), sticky='w')
folder_button.grid(row=1, column=0, padx=(10, 20), pady=(10, 0), sticky='w')
folder_label.grid(row=1, column=1, padx=(10, 20), pady=(10, 0), sticky='w')
label_sheet_name.grid(row=2, column=0, padx=(10, 20), pady=(10, 0), sticky='w')
sheet_name_entry.grid(row=2, column=1, padx=(10, 20), pady=(10, 0), sticky='ew')
start_button.grid(row=3, column=0, padx=(10, 20), pady=(10, 0), sticky='w')
close_button.grid(row=3, column=1, padx=(10, 20), pady=(10, 0), sticky='w')

root.mainloop()
