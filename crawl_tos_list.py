import json
import os
import requests
import sys
import urllib.request


def ensure_url(url):
    if not url.startswith('http://') and not url.startswith('https://'):
        return 'https://' + url
    return url


if __name__ == '__main__':
    tos_dir = 'tos'
    if not os.path.exists(tos_dir):
        os.makedirs(tos_dir)
    products_url = "https://privacyspy.org/api/v2/products.json"
    products_path = "products.json"
    if not os.path.exists(products_path):
        urllib.request.urlretrieve(products_url, products_path)
    with open(products_path, 'r') as json_file:
        content = json.loads(json_file.read())
    for i, product in enumerate(content):
        sys.stdout.write('\r[%d/%d]' % (i + 1, len(content)))
        sys.stdout.flush()
        product_tos_path = os.path.join(tos_dir, product['slug'])
        if not os.path.exists(product_tos_path) and len(product['sources']) > 0:
            with open(product_tos_path, 'w') as product_tos_file:
                product_tos_file.write('\n'.join(product['sources']))
    print()  # newline
