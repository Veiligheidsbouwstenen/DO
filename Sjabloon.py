import tkinter as tk
from tkinter import messagebox, Toplevel
from tkinter import ttk
import requests

# Basis URL's voor de API
ti_url = "https://digitaal-ondertekenen-openapi-ti.vlaanderen.be"
prd_url = "https://digitaal-ondertekenen-openapi.vlaanderen.be"

# Endpoints voor verificatie
client_credentials_endpoint = "/authenticate"
password_credentials_endpoint = "/authenticate"
enterprise_templates_endpoint = "/v4/settings/templates/5000/1"

# Globale variabele om access_token op te slaan
access_token = None

# Functie voor authenticatie
def authenticate():
    global access_token
    base_url = ti_url if environment.get() == "T&I" else prd_url
    client_id = client_id_entry.get()
    client_secret = client_secret_entry.get()
    username = username_entry.get()
    password = password_entry.get()

    # Authenticatie voor Client Credentials
    client_auth_response = authenticate_client_credentials(base_url, client_id, client_secret)
    print(f"Client Credentials antwoord: {client_auth_response.status_code}, {client_auth_response.text}")

    if client_auth_response.status_code == 200:
        client_status_var.set("GESLAAGD")
        access_token = client_auth_response.json().get("access_token")
        client_tree.tag_configure('client_success', background='green')
    else:
        client_status_var.set(f"GEFAALD ({client_auth_response.status_code})")
        client_tree.tag_configure('client_fail', background='red')

    # Authenticatie voor Password Credentials
    password_auth_response = authenticate_password_credentials(base_url, client_id, client_secret, username, password)
    print(f"Wachtwoordaanmelding antwoord: {password_auth_response.status_code}, {password_auth_response.text}")

    if password_auth_response.status_code == 200:
        password_status_var.set("GESLAAGD")
        access_token = password_auth_response.json().get("access_token")
        password_tree.tag_configure('password_success', background='green')
    else:
        password_status_var.set(f"GEFAALD ({password_auth_response.status_code})")
        password_tree.tag_configure('password_fail', background='red')

# Functie voor authenticatie van Client Credentials
def authenticate_client_credentials(base_url, client_id, client_secret):
    url = f"{base_url}{client_credentials_endpoint}"
    response = requests.post(
        url,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret
        }
    )
    return response

# Functie voor authenticatie van Password Credentials
def authenticate_password_credentials(base_url, client_id, client_secret, username, password):
    url = f"{base_url}{password_credentials_endpoint}"
    response = requests.post(
        url,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "password",
            "username": username,
            "password": password,
            "client_id": client_id,
            "client_secret": client_secret
        }
    )
    return response

def get_enterprise_templates():
    global access_token

    if access_token:
        base_url = ti_url if environment.get() == "T&I" else prd_url
        url = f"{base_url}{enterprise_templates_endpoint}"
        print(f"Retrieving enterprise templates from URL: {url}")

        response = requests.get(
            url,
            headers={"Authorization": f"Bearer {access_token}"}
        )

        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")

        if response.status_code == 200:
            templates = response.json()
            show_templates_window(templates)
        else:
            show_popup("Fout", f"Kan geen sjablonen ophalen: {response.status_code}")
            print(f"Fout bij het ophalen van sjablonen: {response.status_code}, {response.text}")
    else:
        show_popup("Fout", "U moet eerst authentiseren om sjablonen op te halen.")

def show_templates_window(templates):
    templates_window = Toplevel(app)
    templates_window.title("Enterprise Sjablonen")
    templates_window.configure(bg='black')

    style = ttk.Style()
    style.theme_use("clam")

    style.configure("Treeview.Heading", font=("Arial", 14, "bold"), background="black", foreground="red")
    style.configure("Treeview", font=("Arial", 12, "bold"), background="black", foreground="green", fieldbackground="black", rowheight=30)

    tree = ttk.Treeview(templates_window, columns=("Naam", "ID"), style="Treeview")
    tree.heading('#1', text='Naam', anchor='center')
    tree.heading('#2', text='ID', anchor='center')

    for template in templates:
        tree.insert('', 'end', text='', values=(template['template_name'], template['template_id']), tags='success')

    tree.pack(expand=True, fill='both')

    close_button = tk.Button(templates_window, text="Afsluiten", command=templates_window.destroy, font=("Arial", 12))
    close_button.pack(pady=10)

def show_popup(title, message):
    popup = Toplevel(app)
    popup.title(title)
    popup.configure(bg='black')

    tk.Label(popup, text=message, bg='black', fg='white', font=("Arial", 14)).pack(padx=20, pady=20)

    close_button = tk.Button(popup, text="Afsluiten", command=popup.destroy, font=("Arial", 12))
    close_button.pack(pady=10)

def close_app():
    app.destroy()

# Maak de hoofdapplicatievenster
app = tk.Tk()
app.title("Digitaal Ondertekenen API Tool")
app.configure(bg='black')

# Frame voor de radiobuttons
environment_frame = tk.Frame(app, bg='black')
environment_frame.pack()

environment = tk.StringVar(value="PRD")

def change_background():
    for button in environment_frame.winfo_children():
        button.configure(bg='green', fg='white')
    selected_button = environment_frame.winfo_children()[int(environment.get() == "T&I")]
    selected_button.configure(bg='black', fg='white')

tk.Radiobutton(environment_frame, text="T&I", variable=environment, value="T&I", bg='black', fg='white', command=change_background).pack(side=tk.LEFT)
tk.Radiobutton(environment_frame, text="Productie", variable=environment, value="PRD", bg='black', fg='white', command=change_background).pack(side=tk.LEFT)

# Labels en Entry velden voor credentials
font_style = ("Arial", 12)
entry_bg = 'green'
entry_fg = 'white'
entry_width = 80

# Maak de invoervelden groter
tk.Label(app, text="Client ID", bg='black', fg='white', font=font_style).pack()
client_id_entry = tk.Entry(app, font=font_style, bg=entry_bg, fg=entry_fg, width=entry_width)
client_id_entry.pack()

tk.Label(app, text="Client Secret", bg='black', fg='white', font=font_style).pack()
client_secret_entry = tk.Entry(app, font=font_style, bg=entry_bg, fg=entry_fg, width=entry_width)
client_secret_entry.pack()

tk.Label(app, text="Technical User", bg='black', fg='white', font=font_style).pack()
username_entry = tk.Entry(app, font=font_style, bg=entry_bg, fg=entry_fg, width=entry_width)
username_entry.pack()

tk.Label(app, text="Wachtwoord Technical User", bg='black', fg='white', font=font_style).pack()
password_entry = tk.Entry(app, font=font_style, bg=entry_bg, fg=entry_fg, width=entry_width)
password_entry.pack()

# Resultaat labels
result_frame = tk.Frame(app, bg='black')
result_frame.pack(pady=10)

# Frame voor de Treeview-widgets
treeview_frame = tk.Frame(app, bg='black')
treeview_frame.pack()

client_tree = ttk.Treeview(treeview_frame, columns=("Status",), show="headings", style="Treeview")
client_tree.heading('#1', text='Client', anchor='center')
client_tree.pack(side=tk.LEFT, padx=(0, 5), fill=tk.BOTH, expand=True)

password_tree = ttk.Treeview(treeview_frame, columns=("Status",), show="headings", style="Treeview")
password_tree.heading('#1', text='Wachtwoord', anchor='center')
password_tree.pack(side=tk.LEFT, padx=(5, 0), fill=tk.BOTH, expand=True)

client_status_var = tk.StringVar()
password_status_var = tk.StringVar()

client_tree.insert('', 'end', values=(client_status_var.get(),), tags=('client_success', 'client_fail'))
password_tree.insert('', 'end', values=(password_status_var.get(),), tags=('password_success', 'password_fail'))


# Stijl instellen voor de Treeview
style = ttk.Style()
style.theme_use("clam")

style.configure("Treeview.Heading", font=("Arial", 14, "bold"), background="black", foreground="red")
style.configure("Treeview", font=("Arial", 12), background="black", foreground="white", fieldbackground="black")

# Frame voor knoppen
button_frame = tk.Frame(app, bg='black')
button_frame.pack()

# Knoppen voor authenticatie, sjablonen en afsluiten
auth_button = tk.Button(button_frame, text="Testen", command=authenticate, font=font_style)
auth_button.pack(side=tk.LEFT, padx=5, pady=5)

templates_button = tk.Button(button_frame, text="Sjablonen", command=get_enterprise_templates, font=font_style)
templates_button.pack(side=tk.LEFT, padx=5, pady=5)

close_button = tk.Button(button_frame, text="Afsluiten", command=close_app, font=font_style)
close_button.pack(side=tk.LEFT, padx=5, pady=5)

# Resultaatlabels
result_label = tk.Label(app, text="", bg='black', fg='white', font=font_style)
result_label.pack()

app.mainloop()
