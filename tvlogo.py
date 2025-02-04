import json
import os
from bs4 import BeautifulSoup
import requests

def extract_payload_from_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None

    soup = BeautifulSoup(html_content, 'html.parser')
    script_tag = soup.find('script', type='application/json')

    if script_tag:
        json_text = script_tag.string
        try:
            payload = json.loads(json_text)
            return payload
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return None
    else:
        print("Error: Could not find JSON payload in the HTML.")
        return None

def search_tree_items(search_term, payload):
    results = []

    if payload and 'tree' in payload and 'items' in payload['tree']:
        for item in payload['tree']['items']:
            if search_term.lower() in item['name'].lower():
                results.append(item)
    return results

def download_logo(item, output_dir):
    if item and 'name' in item and 'path' in item:
        logo_name = item['name']
        logo_path = item['path']

        base_url = "https://raw.githubusercontent.com/tv-logo/tv-logos/main/"
        logo_url = base_url + logo_path

        os.makedirs(output_dir, exist_ok=True)

        try:
            response = requests.get(logo_url, stream=True)
            response.raise_for_status()

            filepath = os.path.join(output_dir, logo_name)
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"Logo scaricato con successo: {logo_name}")
        except requests.exceptions.RequestException as e:
            print(f"Errore durante il download del logo {logo_name}: {e}")
    else:
        print("Dati non validi per il download del logo.")

# Esempio di utilizzo (da chiamare dallo script principale)
if __name__ == '__main__':
    filename = 'tv_logos_page.html'  # Sostituisci con il nome del file HTML
    payload = extract_payload_from_file(filename)

    if payload:
        search_term = 'rai 1'  # Termine di ricerca di esempio
        results = search_tree_items(search_term, payload)

        if results:
            print(f"Trovate {len(results)} corrispondenze:")
            for item in results:
                print(item['name'])
                download_logo(item, 'output_logos')  # Sostituisci 'output_logos' con la tua directory
        else:
            print(f"Nessuna corrispondenza trovata per '{search_term}'.")
