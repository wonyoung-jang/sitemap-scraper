import requests
import argparse
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


def url_to_filename(url):
    """
    Converts a URL to a valid filename.
    """
    return url.replace("http://", "").replace("https://", "").replace("/", "_").replace(".", "_")


def get_sitemap_xml(url):
    """
    Get the sitemap of a website given its URL.
    Example: site.com/sitemap.xml
    Args:
        url (str): The URL of the website.
    Returns:
        str: The URL of the sitemap
    """
    return url.strip("/") + "/sitemap.xml"


def get_sitemap_content(url):
    """
    Get the content of the sitemap given its URL.rrrrrp
    Args:
        url (str): The URL of the sitemap.
    Returns:
        str: The content of the sitemap.
    """
    try:
        response = requests.get(url)
        return response.text
    except requests.exceptions.RequestException as e:
        print(e)
        return f"Request failed: {e}"


def parse_sitemap(content, base_url):
    """
    Parse the content of a sitemap and extract the URLs.
    Args:
        content (str): The content of the sitemap.
        base_url (str): The base URL of the sitemap.
    Returns:
        list: A list of URLs extracted from the sitemap.
    """
    soup = BeautifulSoup(content, features="xml")
    urls = []
    for loc in soup.find_all("loc"):
        url = loc.text.strip()
        if url.endswith(".xml"):
            # If the URL ends with .xml, it's a nested sitemap
            nested_sitemap_url = urljoin(base_url, url)
            nested_sitemap_content = get_sitemap_content(nested_sitemap_url)
            nested_urls = parse_sitemap(nested_sitemap_content, nested_sitemap_url)
            urls.extend(nested_urls)
        else:
            # Remove the protocol (http:// or https://) from the URL
            if url.startswith("https://"):
                url = url.replace("https://", "")
            elif url.startswith("http://"):
                url = url.replace("http://", "")
            urls.append(url)
    return urls


def organize_sitemap(urls):
    """
    Organize the URLs extracted from a sitemap by their depth.
    They should be grouped by the text after the domain, alphanumerically.
    Args:
        urls (list): A list of URLs extracted from a sitemap.
    Returns:
        dict: A dictionary with the URLs organized by depth.
    """
    organized_content = {}
    for url in urls:
        path = urlparse(url).path
        parts = path.strip("/").split("/")
        current_level = organized_content
        for part in parts:
            if part not in current_level:
                current_level[part] = {}
            current_level = current_level[part]
    return organized_content


def generate_sitemap_text(content, level=0):
    """
    Generate the sitemap text recursively.
    Args:
        content (dict): A dictionary with the URLs organized by depth.
        level (int): The current level of indentation.
    Returns:
        str: The generated sitemap text.
    """
    sitemap_text = ""
    logseq_bullet = "- "
    heading_level_of_site_name = 2
    for key in sorted(content.keys()):
        tab_indent = "\t" * level
        heading_level = "#" * (level + heading_level_of_site_name)
        sitemap_text += tab_indent + logseq_bullet + heading_level + " " + key + "/\n"
        sitemap_text += generate_sitemap_text(content[key], level + 1)
    return sitemap_text


def save_to_file(content, filename):
    """
    Save the content to a file.
    Args:
        content (str): The content to save.
        filename (str): The name of the file.
    """
    with open(filename, "w", encoding="utf-8") as file:
        file.write(content)


def main():
    """
    Main function of the script.
    """
    # Parse the command-line arguments
    parser = argparse.ArgumentParser(
        description="Generate a sitemap from a website URL."
    )
    parser.add_argument("url", type=str, help="The URL of the website.")
    parser.add_argument(
        "--output", type=str, default="sitemap.md", help="The output filename."
    )
    args = parser.parse_args()

    # Get the sitemap XML URL
    sitemap_xml = get_sitemap_xml(args.url)

    # Get the content of the sitemap
    sitemap_content = get_sitemap_content(sitemap_xml)

    # Parse the sitemap content
    parsed_content = parse_sitemap(sitemap_content, sitemap_xml)

    # Organize the sitemap content
    organized_content = organize_sitemap(parsed_content)

    # Generate the sitemap text
    sitemap_text = generate_sitemap_text(organized_content)

    # Save the sitemap text to a file
    save_to_file(sitemap_text, args.output)


if __name__ == "__main__":
    main()
