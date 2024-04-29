import requests
import json
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
import os  # Voeg de os-module toe

# Basis URL's voor de API
ti_url = "https://digitaal-ondertekenen-openapi-ti.vlaanderen.be"
prd_url = "https://digitaal-ondertekenen-openapi.vlaanderen.be"

# Endpoints voor verificatie en package toevoeging
client_credentials_endpoint = "/authenticate"
password_credentials_endpoint = "/authenticate"
add_package_endpoint = "/v4/packages"  # Nieuw endpoint voor het toevoegen van een pakket
add_document_endpoint = "/v4/packages/{package_id}/documents"  # Endpoint voor het toevoegen van documenten

# Functie om achtergrondkleur van radiobuttons te veranderen op basis van selectie
def update_radiobutton_bg():
    t_and_i_button.config(bg='black' if environment.get() != "T&I" else 'green')
    prd_button.config(bg='black' if environment.get() != "PRD" else 'green')

# Maak de hoofdapplicatievenster
app = tk.Tk()
app.title("Digitaal Ondertekenen API Tool")
app.configure(bg='black')

# Frame voor labels
label_frame = tk.Frame(app, bg='black')
label_frame.pack(padx=20, pady=(10, 5))  # Minder verticale padding hier

# Label voor Package ID
package_id_label = tk.Label(label_frame, text="Package ID:", bg='black', fg='white')
package_id_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

# Label voor Document ID
document_id_label = tk.Label(label_frame, text="Document ID:", bg='black', fg='white')
document_id_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")

# Globale variabelen voor Package ID en Document ID
package_id_var = tk.StringVar(value="")
document_id_var = tk.StringVar(value="")

# Labels voor Package ID en Document ID
package_id_value_label = tk.Label(label_frame, textvariable=package_id_var, bg='black', fg='white')
document_id_value_label = tk.Label(label_frame, textvariable=document_id_var, bg='black', fg='white')

# Functie om de rij met Package ID en Document ID weer te geven
def show_package_document_row():
    package_id = package_id_var.get()
    document_id = document_id_var.get()
    if package_id and document_id:
        package_id_label.grid()
        document_id_label.grid()
        package_id_value_label.grid()
        document_id_value_label.grid()

# Functie om de rij met Package ID en Document ID te verbergen
def hide_package_document_row():
    package_id_label.grid_remove()
    document_id_label.grid_remove()
    package_id_value_label.grid_remove()
    document_id_value_label.grid_remove()

# Frame voor omgevingsselectie
environment_frame = tk.Frame(app, bg='black')
environment_frame.pack(padx=20, pady=(2, 2))  # Minder verticale padding hier

# Radiobuttons voor omgevingsselectie
environment = tk.StringVar(value="PRD")

t_and_i_button = tk.Radiobutton(environment_frame, text="T&I", variable=environment, value="T&I", bg='black', fg='white', command=update_radiobutton_bg)
t_and_i_button.grid(row=0, column=0, padx=5, pady=5, sticky="w")

prd_button = tk.Radiobutton(environment_frame, text="Productie", variable=environment, value="PRD", bg='black', fg='white', command=update_radiobutton_bg)
prd_button.grid(row=0, column=1, padx=5, pady=5, sticky="w")

# Functie voor het bijwerken van achtergrondkleur van radiobuttons
update_radiobutton_bg()

# Globale variabele voor toegangstoken
access_token = None

# Functie om een bestand te kiezen en toe te voegen aan het pakket
def choose_file(package_id):
    file_path = filedialog.askopenfilename()
    if file_path:
        add_document(file_path, package_id)

# Functie om een document toe te voegen aan het pakket
def add_document(file_path, package_id):
    base_url = ti_url if "T&I" in client_id_entry.get() else prd_url
    url = f"{base_url}{add_document_endpoint.format(package_id=package_id)}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/octet-stream",
        "Accept": "application/json",
        "x-file-name": os.path.basename(file_path),  # Voeg de bestandsnaam toe aan de headers
        "x-source": "API"  # Voeg de bronkoptekst toe aan de headers
    }
    with open(file_path, "rb") as file:
        response = requests.post(url, headers=headers, data=file)  # Verzend het bestand als onderdeel van de aanvraag
    if response.status_code not in (200, 201):
        print(f"Fout bij het uploaden van document: {response.status_code}, {response.text}")
    else:
        document_id = response.json().get("documentid")
        document_id_var.set(document_id)
        print(f"Document succesvol toegevoegd! Document ID: {document_id}")
        print("Volledige respons:")
        print(response.json())
        show_package_document_row()  # Toon de rij met Package ID en Document ID

# Functie om een documentpakket toe te voegen
def add_package():
    base_url = ti_url if "T&I" in client_id_entry.get() else prd_url
    url = f"{base_url}{add_package_endpoint}"
    package_data = {
        "name": "Document Package",
        "description": "Dit is een testpakket",
        "workflow_type_id": 1,  # Pas dit aan naar je behoeften
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, json=package_data)
    if response.status_code == 200:
        package_id = response.json().get("package_id")
        package_id_var.set(package_id)
        print(f"Pakket succesvol toegevoegd! Package ID: {package_id}")
        choose_file(package_id)  # Roep de functie aan om een bestand toe te voegen na het maken van een pakket
        show_package_document_row()  # Toon de rij met Package ID en Document ID
    else:
        print(f"Fout bij het toevoegen van pakket: {response.status_code}, {response.text}")
        hide_package_document_row()  # Verberg de rij met Package ID en Document ID

# Functie om authenticatie uit te voeren
def authenticate():
    global access_token
    base_url = ti_url if "T&I" in client_id_entry.get() else prd_url
    client_id = client_id_entry.get()
    client_secret = client_secret_entry.get()
    username = username_entry.get()
    password = password_entry.get()

    # Authenticatie voor Client Credentials
    client_auth_response = authenticate_client_credentials(base_url, client_id, client_secret)
    print(f"Client Credentials antwoord: {client_auth_response.status_code}, {client_auth_response.text}")

    if client_auth_response.status_code == 200:
        access_token = client_auth_response.json().get("access_token")
        print("Client Credentials: Geslaagd")
    else:
        print(f"Client Credentials: Gefaald ({client_auth_response.status_code})")

    # Authenticatie voor Password Credentials
    password_auth_response = authenticate_password_credentials(base_url, client_id, client_secret, username, password)
    print(f"Wachtwoordaanmelding antwoord: {password_auth_response.status_code}, {password_auth_response.text}")

    if password_auth_response.status_code == 200:
        access_token = password_auth_response.json().get("access_token")
        print("Password Credentials: Geslaagd")
    else:
        print(f"Password Credentials: Gefaald ({password_auth_response.status_code})")

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

# Labels en Entry velden voor credentials
font_style = ("Arial", 12)
entry_bg = 'green'
entry_fg = 'white'
entry_width = 80

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

# Frame voor knoppen
button_frame = tk.Frame(app, bg='black')
button_frame.pack()

# Knoppen voor authenticatie en het toevoegen van een pakket
auth_button = tk.Button(button_frame, text="Testen", command=authenticate, font=font_style)
auth_button.pack(side=tk.LEFT, padx=5, pady=5)

add_package_button = tk.Button(button_frame, text="Werkstroom aanmaken", command=add_package, font=font_style)
add_package_button.pack(side=tk.LEFT, padx=5, pady=5)

close_button = tk.Button(button_frame, text="Afsluiten", command=app.destroy, font=font_style)
close_button.pack(side=tk.LEFT, padx=5, pady=5)

# Functie om de titel van de applicatie bij te werken
def update_title():
    app.title("Digitaal Ondertekenen API Tool - OK")

# Voeg de functie toe aan de knop voor testen
auth_button.config(command=lambda: [authenticate(), update_title()])

hide_package_document_row()  # Verberg de rij met Package ID en Document ID

app.mainloop()
