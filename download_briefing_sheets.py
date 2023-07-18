import os
import re
from urllib.parse import urlparse
import shutil

import requests
import lxml.html
from dateutil import parser

output_dir = "briefing_sheets"
url_prefix = "https://nats-uk.ead-it.com"

response = requests.get("https://nats-uk.ead-it.com/cms-nats/opencms/en/Publications/briefing-sheets/")
root = lxml.html.document_fromstring(response.content)

for node in root.xpath("//tr")[1:]:
    title = node.xpath("./td")[0].text_content()
    remote_path = node.xpath("./td[3]/a")[0].attrib["href"]
    filename = os.path.basename(remote_path)
    url = url_prefix + remote_path

    response = requests.head(url)
    year = parser.parse(response.headers["Last-Modified"]).year

    year_dir = os.path.join(output_dir, str(year))
    output_path = os.path.join(year_dir, filename)

    if os.path.exists(output_path):
        print("* skipping %s" % filename)
    else:
        print("* NEW BRIEFING SHEET: %s" % filename)
        try:
            os.makedirs(year_dir)
        except FileExistsError:
            pass

        response = requests.get(url, stream=True)

        with open(output_path, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
