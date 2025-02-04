import os
import io
import gzip
import xml.etree.ElementTree as ET
import requests

save_as_gz = True  # Set to True to save an additional .gz version

tvg_ids_file = os.path.join(os.path.dirname(__file__), 'tvg-ids.txt')
output_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'epg.xml')
output_file_gz = output_file + '.gz'

def filter_and_build_epg(urls):
    with open(tvg_ids_file, 'r', encoding='utf-8') as file:
        valid_tvg_ids = set(line.strip() for line in file)

    root = ET.Element('tv')

    for url in urls:
        epg_data = fetch_and_extract_xml(url)
        if epg_data is None:
            continue

        for channel in epg_data.findall('channel'):
            tvg_id = channel.get('id')
            if tvg_id and tvg_id in valid_tvg_ids:  # Evita elementi senza ID
                root.append(channel)

        for programme in epg_data.findall('programme'):
            tvg_id = programme.get('channel')
            if tvg_id and tvg_id in valid_tvg_ids:
                title_element = programme.find('title')
                subtitle_element = programme.find('sub-title')

                if title_element is not None and subtitle_element is not None:
                    title = title_element.text or ""
                    subtitle = subtitle_element.text or ""
                    if title in ['NHL Hockey', 'Live: NFL Football']:
                        title_element.text = f"{title} {subtitle}"
                
                root.append(programme)

    tree = ET.ElementTree(root)
    
    # ✅ Salvataggio sicuro con UTF-8
    with open(output_file, 'wb') as f:
        f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        tree.write(f, encoding='utf-8', xml_declaration=False)  # Disattiva xml_declaration per evitare doppie dichiarazioni

    print(f"New EPG saved to {output_file}")

    if save_as_gz:
        with gzip.open(output_file_gz, 'wb') as f:
            f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
            tree.write(f, encoding='utf-8', xml_declaration=False)

        print(f"New EPG saved to {output_file_gz}")



def fetch_and_extract_xml(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Controlla errori HTTP

        if url.endswith('.gz'):
            try:
                # Usa un buffer in memoria per la decompressione
                with gzip.GzipFile(fileobj=io.BytesIO(response.content)) as gz:
                    return ET.parse(gz).getroot()
            except Exception as e:
                print(f"Failed to decompress and parse XML from {url}: {e}")
                return None
        else:
            return ET.fromstring(response.content)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None
    except ET.ParseError as e:
        print(f"XML Parse Error from {url}: {e}")
        return None


    tree = ET.ElementTree(root)
    tree.write(output_file, encoding='utf-8', xml_declaration=True)
    print(f"New EPG saved to {output_file}")

    if save_as_gz:
        with gzip.open(output_file_gz, 'wb') as f:
            tree.write(f, encoding='utf-8', xml_declaration=True)
        print(f"New EPG saved to {output_file_gz}")

m3u4u_epg = os.getenv("M3U4U_EPG")

urls = [
        'https://xmltv.tvkaista.net/guides/superguidatv.it.xml',
]

if __name__ == "__main__":
    filter_and_build_epg(urls)
