import tkinter as tk
from tkinter import ttk
import requests

# Basis URL's voor de API
ti_url = "https://digitaal-ondertekenen-openapi-ti.vlaanderen.be"
prd_url = "https://digitaal-ondertekenen-openapi.vlaanderen.be"

# Endpoints voor verificatie en package toevoeging
client_credentials_endpoint = "/authenticate"
password_credentials_endpoint = "/authenticate"
add_package_endpoint = "/v4/packages"  # Nieuw endpoint voor het toevoegen van een pakket

# Maak de hoofdapplicatievenster
app = tk.Tk()
app.title("Digitaal Ondertekenen API Tool")
app.configure(bg='black')

# Radiobuttons voor omgevingsselectie
environment_frame = tk.Frame(app, bg='black')
environment_frame.pack(padx=20, pady=10)
environment = tk.StringVar(value="PRD")

# Functie om achtergrondkleur van radiobuttons te veranderen op basis van selectie
def update_radiobutton_bg():
    if environment.get() == "T&I":
        t_and_i_button.config(bg='green')
        prd_button.config(bg='black')
    else:
        t_and_i_button.config(bg='black')
        prd_button.config(bg='green')

t_and_i_button = tk.Radiobutton(environment_frame, text="T&I", variable=environment, value="T&I", bg='black', fg='white', command=update_radiobutton_bg)
t_and_i_button.pack(side=tk.LEFT)

prd_button = tk.Radiobutton(environment_frame, text="Productie", variable=environment, value="PRD", bg='black', fg='white', command=update_radiobutton_bg)
prd_button.pack(side=tk.LEFT)

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

# Functie om een documentpakket toe te voegen
def add_package():
    base_url = ti_url if environment.get() == "T&I" else prd_url
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
        print("Pakket succesvol toegevoegd!")
        print("Response:", response.json())  # Print de volledige JSON-respons
        # Pas de volgende regel aan op basis van de JSON-structuur van de respons
        # print("Package ID:", response.json()["id"]) 
    else:
        print(f"Fout bij het toevoegen van pakket: {response.status_code}, {response.text}")

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

add_package_button = tk.Button(button_frame, text="Pakket Toevoegen", command=add_package, font=font_style)
add_package_button.pack(side=tk.LEFT, padx=5, pady=5)

close_button = tk.Button(button_frame, text="Afsluiten", command=app.destroy, font=font_style)
close_button.pack(side=tk.LEFT, padx=5, pady=5)

app.mainloop()
