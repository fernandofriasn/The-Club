import os
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import json
import gzip
import tvlogo
import chardet

daddyLiveChannelsFileName = '247channels.html'
daddyLiveChannelsURL = 'https://thedaddy.to/24-7-channels.php'

tvLogosFilename = 'tvlogos.html'
tvLogosURL = 'https://github.com/tv-logo/tv-logos/tree/main/countries/'

epgs = [
    {'filename': 'epgShareall.xml', 'url': 'https://epgshare01.online/epgshare01/epg_ripper_ALL_SOURCES1.xml.gz'}
]

def delete_file_if_exists(file_path):
    if os.path.isfile(file_path):
        os.remove(file_path)
        print(f'File {file_path} deleted.')

def fetch_with_debug(filename, url):
    try:
        print(f'Downloading {url}...')
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        with open(filename, 'wb') as file:
            file.write(response.content)
        
        print(f'File {filename} downloaded successfully.')
    except requests.exceptions.RequestException as e:
        print(f'Error downloading {url}: {e}')

def search_streams(file_path, keyword):
    matches = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file.read(), 'html.parser')
            links = soup.find_all('a', href=True)

            for link in links:
                if keyword.lower() in link.text.lower():
                    href = link['href']
                    stream_number = href.split('-')[-1].replace('.php', '')
                    stream_name = link.text.strip()
                    match = (stream_number, stream_name)
                    
                    if match not in matches:
                        matches.append(match)
    except FileNotFoundError:
        print(f'The file {file_path} does not exist.')
    return matches

def search_channel_ids(file_path, search_string):
    id_matches = []
    try:
        if file_path.endswith('.gz'):
            with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                tree = ET.parse(f)
        else:
            tree = ET.parse(file_path)
        
        root = tree.getroot()
        search_words = search_string.lower().split()
        
        for channel in root.findall('.//channel'):
            channel_id = channel.get('id')
            channel_name_element = channel.find('display-name')
            channel_name = channel_name_element.text if channel_name_element is not None else ""
            
            if any(word in channel_name.lower() for word in search_words):
                id_matches.append({'id': channel_id, 'source': file_path})
    except (FileNotFoundError, ET.ParseError, gzip.BadGzipFile) as e:
        print(f'Error processing {file_path}: {e}')
    return id_matches

def generate_m3u8(matches, payload):
    if not matches:
        print("No matches found. Skipping M3U8 generation.")
        return
    
    with open("outall.m3u8", 'w', encoding='utf-8') as file:
        file.write('#EXTM3U url-tvg="https://raw.githubusercontent.com/michael1900/daddylive/main/epgShareall.xml"\n')
        
        for channel in matches:
            channel_id = channel[0]
            channel_name = channel[1]
            
            # Cerca il logo nel payload
            logo_matches = tvlogo.search_tree_items(channel_name, payload)
            
            if logo_matches and "path" in (logo_matches[0]):
                tvicon_path = f'https://raw.githubusercontent.com{payload.get("initial_path", "")}/{logo_matches[0]["path"]}'
            else:
                # Logo di default se non trovato
                tvicon_path = "https://raw.githubusercontent.com/michael1900/daddylive/refs/heads/main/bg/ddy-logo.jpg"

            file.write(f"#EXTINF:-1 tvg-id=\"{channel_id}\" tvg-name=\"{channel_name}\" tvg-logo=\"{tvicon_path}\" group-title=\"TV\", {channel_name}\n")
            file.write(f'#EXTVLCOPT:http-referrer=https://cookiewebplay.xyz/\n')
            file.write(f'#EXTVLCOPT:http-user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 17_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1\n')
            file.write(f'#EXTVLCOPT:http-origin=https://cookiewebplay.xyz\n')
            file.write(f"https://xyzdddd.mizhls.ru/lb/premium{channel_id}/index.m3u8\n\n")
    
    print("M3U8 file generated successfully.")


# Cleanup and Fetch Data
delete_file_if_exists(daddyLiveChannelsFileName)
delete_file_if_exists(tvLogosFilename)
for epg in epgs:
    delete_file_if_exists(epg['filename'])

fetch_with_debug(daddyLiveChannelsFileName, daddyLiveChannelsURL)
fetch_with_debug(tvLogosFilename, tvLogosURL)
for epg in epgs:
    fetch_with_debug(epg['filename'], epg['url'])

# Process Data
matches = search_streams(daddyLiveChannelsFileName, "")
payload = tvlogo.extract_payload_from_file(tvLogosFilename)
generate_m3u8(matches, payload)
