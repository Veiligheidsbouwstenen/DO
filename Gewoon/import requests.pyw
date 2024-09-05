import requests

proxies = {
  "http": None,
  "https": None
}

response = requests.post('https://digitaal-ondertekenen-openapi.vlaanderen.be/authenticate', proxies=proxies, data={
  "grant_type": "client_credentials",
  "client_id": "Thunder",
  "client_secret": "1C65FC9C5EA8C5A1B16236EE4F49107E51F258BE2C1A4D44DF6AFA2F8C19E361"
}, headers={"Content-Type": "application/x-www-form-urlencoded"})

print(response.text)
