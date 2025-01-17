from urllib.parse import urlparse


def get_domain(url, https=False):
    if not url:  # Check if the URL is empty
        return "", ""
    # Ensure the URL has a scheme; default to https if not present
    if not url.startswith(('http://', 'https://')):
        url = f"https://{url}" if https else f"http://{url}"

    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    domain_name = parsed_url.netloc
    return base_url, domain_name