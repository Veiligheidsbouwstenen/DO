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

def authenticate():
    global access_token
    base_url = ti_url if environment.get() == "T&I" else prd_url
    client_id = client_id_entry.get()
    client_secret = client_secret_entry.get()

    url = f"{base_url}{client_credentials_endpoint}"
    print(f"Authenticating with URL: {url}")

    response = requests.post(
        url,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret
        }
    )

    print(f"Client Credentials antwoord: {response.status_code}, {response.text}")

    if response.status_code == 200:
        access_token = response.json().get("access_token")
        result_label.config(bg="green", text="Client GESLAAGD")

        if username_entry.get() and password_entry.get():
            check_password_credentials(client_id, client_secret, base_url)
    else:
        result_label.config(bg="red", text=f"Client GEFAALD ({response.status_code})")
        print(f"Fout bij authenticatie: {response.status_code}, {response.text}")

def check_password_credentials(client_id, client_secret, base_url):
    global access_token

    username = username_entry.get()
    password = password_entry.get()

    print("Checking Password Credentials")

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

    print(f"Wachtwoordaanmelding antwoord: {response.status_code}, {response.text}")

    if response.status_code == 200:
        access_token = response.json().get("access_token")
        result_label.config(bg="green", text="Pass GESLAAGD")
    else:
        result_label.config(bg="red", text=f"Pass GEFAALD ({response.status_code})")
        print(f"Fout bij wachtwoordaanmelding: {response.status_code}, {response.text}")

def show_popup(title, message):
    popup = Toplevel(app)
    popup.title(title)
    popup.configure(bg='black')

    tk.Label(popup, text=message, bg='black', fg='white', font=("Arial", 14)).pack(padx=20, pady=20)

    close_button = tk.Button(popup, text="Afsluiten", command=popup.destroy, font=("Arial", 12))
    close_button.pack(pady=10)

def close_app():
    app.destroy()

access_token = None

def check_package():
    package_window = Toplevel(app)
    package_window.title("Package Status Check")
    package_window.configure(bg='black')

    tk.Label(package_window, text="Package ID", bg='black', fg='white', font=("Arial", 12)).pack(padx=20, pady=10)

    package_id_entry = tk.Entry(package_window, font=("Arial", 12), bg='green', fg='white', width=40)
    package_id_entry.pack(padx=20, pady=10)

    # Style configuration for Treeview
    style = ttk.Style(package_window)
    style.theme_use("default")

    # Define style for the treeview header and rows
    style.configure("Treeview.Heading", background="red", foreground="white", font=("Arial", 12, "bold"))
    style.configure("Treeview", background="black", fieldbackground="black", foreground="white", font=("Arial", 12))

    tree_frame = tk.Frame(package_window, bg='black')
    tree_frame.pack(padx=20, pady=10, fill='x', expand=True)

    tree = ttk.Treeview(tree_frame, columns=("Package Name", "Package Owner Name", "Package Status", "Next Signer"), show="headings")
    tree.heading("Package Name", text="Package Name")
    tree.heading("Package Owner Name", text="Package Owner Name")
    tree.heading("Package Status", text="Package Status")
    tree.heading("Next Signer", text="Next Signer")

    for col in tree["columns"]:
        tree.column(col, width=120, anchor="w")

    tree.pack(expand=True, fill='both')

    def get_package_status():
        package_id = package_id_entry.get()
        base_url = ti_url if environment.get() == "T&I" else prd_url
        url = f"{base_url}/v4/enterprise/packages/{package_id}"
        response = requests.get(
            url,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if response.status_code == 200:
            details = response.json()
            tree.delete(*tree.get_children())  # Clear existing data
            tree.insert("", "end", values=(
                details.get('package_name', 'N/A'),
                details.get('package_owner_name', 'N/A'),  # Changed to match updated heading
                details.get('package_status', 'N/A'),
                details.get('next_signer', 'N/A')
            ))
        else:
            messagebox.showerror("Fout", f"API call mislukt: {response.status_code} {response.text}")

    button_frame = tk.Frame(package_window, bg='black')
    button_frame.pack(padx=20, pady=10, fill='x', expand=True)

    go_button = tk.Button(button_frame, text="GO", command=get_package_status, font=("Arial", 12))
    go_button.pack(side=tk.LEFT, padx=5, pady=5)

    close_button = tk.Button(button_frame, text="Afsluiten", command=package_window.destroy, font=("Arial", 12))
    close_button.pack(side=tk.LEFT, padx=5, pady=5)

# Maak de hoofdapplicatievenster
app = tk.Tk()
app.title("Digitaal Ondertekenen API Tool")
app.configure(bg='black')

# Radiobuttons voor omgevingsselectie
environment = tk.StringVar(value="PRD")
tk.Radiobutton(app, text="T&I", variable=environment, value="T&I", bg='black', fg='white').pack()
tk.Radiobutton(app, text="Productie", variable=environment, value="PRD", bg='black', fg='white').pack()

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

tk.Label(app, text="Username", bg='black', fg='white', font=font_style).pack()
username_entry = tk.Entry(app, font=font_style, bg=entry_bg, fg=entry_fg, width=entry_width)
username_entry.pack()

tk.Label(app, text="Password", bg='black', fg='white', font=font_style).pack()
password_entry = tk.Entry(app, font=font_style, bg=entry_bg, fg=entry_fg, width=entry_width)
password_entry.pack()

# Resultaat label
result_label = tk.Label(app, text="Het authenticeren antwoord wordt hier neergezet.", bg='black', fg='white', font=font_style)
result_label.pack()

# Frame voor knoppen
button_frame = tk.Frame(app, bg='black')
button_frame.pack()

# Knoppen voor authenticatie, sjablonen en afsluiten
auth_button = tk.Button(button_frame, text="Testen", command=authenticate, font=font_style)
auth_button.pack(side=tk.LEFT, padx=5, pady=5)

package_check_button = tk.Button(button_frame, text="Package Check", command=check_package, font=("Arial", 12))
package_check_button.pack(side=tk.LEFT, padx=5, pady=5)

close_button = tk.Button(button_frame, text="Afsluiten", command=close_app, font=font_style)
close_button.pack(side=tk.LEFT, padx=5, pady=5)

app.mainloop()