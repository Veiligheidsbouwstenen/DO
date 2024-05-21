import pandas as pd
import win32com.client
import tkinter as tk
from tkinter import filedialog, Label, Entry, Button, ttk
import threading
import os

def update_outlook_contact_groups(excel_path, sheet_name, email_address, progress_callback, log_messages, stop_event, completion_label):
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    outlook = win32com.client.Dispatch("Outlook.Application")
    namespace = outlook.GetNamespace("MAPI")
    account = next((acc for acc in namespace.Accounts if acc.SmtpAddress == email_address), None)
    
    if not account:
        print(f"Geen account gevonden met het e-mailadres {email_address}")
        return

    contacts_folder = account.DeliveryStore.GetDefaultFolder(10)

    updated_count = 0
    created_count = 0
    grouped = df.groupby('Naam_Outlookgroep')
    total_groups = len(grouped)

    for i, (group_name, group_data) in enumerate(grouped, 1):
        if stop_event.is_set():
            completion_label.config(text="Gestopt", fg="red")
            completion_label.pack(pady=20)
            break

        emails = group_data['E-mailadres'].tolist()
        existing_group = None
        for group in contacts_folder.Items:
            if group.Class == 69 and group.DLName == group_name:
                existing_group = group
                break

        if existing_group:
            existing_group.Delete()
            updated_count += 1

        log_message = f"{'Bijgewerkte' if existing_group else 'Nieuw aangemaakte'} groep: {group_name}"
        log_messages.append(log_message)
        print(log_message)

        new_group = contacts_folder.Items.Add("IPM.DistList")
        new_group.DLName = group_name
        for email in emails:
            member = namespace.CreateRecipient(email)
            if member.Resolve():
                new_group.AddMember(member)

        new_group.Save()
        created_count += 1
        progress_callback(i / total_groups * 100, i, total_groups)

        if i == total_groups:
            completion_label.config(text="Gedaan", fg="green")
            completion_label.pack(pady=20)

    log_file_path = os.path.join(os.path.dirname(excel_path), "OutlookGroepenAanmaak.txt")
    with open(log_file_path, 'w') as log_file:
        log_file.write("\n".join(log_messages))

def on_update_button_click(file_path, sheet_name, email_address, progress_bar, progress_label, button, stop_event, completion_label):
    if button.cget('text') == "Aanmaken groep":
        button.config(text="Stop aanmaken groepen", bg='red')
        log_messages = []
        stop_event.clear()
        completion_label.pack_forget()  # Hide completion label

        def update_progress(percentage, current, total):
            progress_bar['value'] = percentage
            progress_label.config(text=f"{current}/{total} groepen verwerkt ({percentage:.2f}%)")
            root.update_idletasks()

        threading.Thread(target=update_outlook_contact_groups, args=(file_path, sheet_name, email_address, update_progress, log_messages, stop_event, completion_label)).start()
    else:
        stop_event.set()
        button.config(text="Aanmaken groep", bg='darkgreen')

def select_file(entry):
    file_path = filedialog.askopenfilename()
    if file_path:
        entry.delete(0, tk.END)
        entry.insert(0, file_path)

def main():
    global root
    root = tk.Tk()
    root.title("Aanmaken van groepen in Outlook")
    root.configure(bg='black')
    root.geometry('900x500')
    font_settings = ('Arial', 14)

    # Frame voor tabelindeling
    frame = tk.Frame(root, bg='black')
    frame.pack(pady=20)

    # Rij 1: Bestandsselectie
    Button(frame, text="Selecteer het Excel bestand", bg='darkgreen', fg='white', font=font_settings, command=lambda: select_file(file_path_entry)).grid(row=0, column=0, padx=10, pady=5)
    file_path_entry = Entry(frame, width=50, font=font_settings, bg='black', fg='white', insertbackground='white')
    file_path_entry.grid(row=0, column=1, padx=10, pady=5)
    
    # Rij 2: Naam werkblad
    Label(frame, text="Naam Werkblad", bg='black', fg='white', font=font_settings).grid(row=1, column=0, sticky='e', padx=10, pady=5)
    sheet_name_entry = Entry(frame, width=30, font=font_settings, bg='black', fg='white', insertbackground='white')
    sheet_name_entry.grid(row=1, column=1, padx=10, pady=5)

    # Rij 3: E-mailadres Outlook account
    Label(frame, text="E-mailadres Outlook account", bg='black', fg='white', font=font_settings).grid(row=2, column=0, sticky='e', padx=10, pady=5)
    email_address_entry = Entry(frame, width=30, font=font_settings, bg='black', fg='white', insertbackground='white')
    email_address_entry.grid(row=2, column=1, padx=10, pady=5)

    # Rij 4: Knoppen
    update_button = Button(frame, text="Aanmaken groep", bg='darkgreen', fg='white', font=font_settings, width=20,
           command=lambda: on_update_button_click(file_path_entry.get(), sheet_name_entry.get(), email_address_entry.get(), progress_bar, progress_label, update_button, stop_event, completion_label))
    update_button.grid(row=3, column=0, padx=10, pady=5, sticky='e')

    Button(frame, text="Sluiten", bg='darkgreen', fg='white', font=font_settings, width=20, command=root.destroy).grid(row=3, column=1, padx=10, pady=5, sticky='w')

    # Progressbar en labels
    style = ttk.Style()
    style.theme_use('alt')
    style.configure("Horizontal.TProgressbar", background='darkgreen', troughcolor='darkgrey', thickness=30)
    progress_bar = ttk.Progressbar(root, orient='horizontal', length=870, mode='determinate', style="Horizontal.TProgressbar")
    progress_bar.pack(pady=10)

    progress_label = Label(root, text="0/0 groepen verwerkt (0%)", bg='black', fg='white', font=font_settings)
    progress_label.pack()

    completion_label = Label(root, text="", font=('Arial', 40), bg='black')

    stop_event = threading.Event()  # A stop event

    root.mainloop()

if __name__ == "__main__":
    main()
