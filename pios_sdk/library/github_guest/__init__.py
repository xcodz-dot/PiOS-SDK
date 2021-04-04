from urllib.parse import urljoin

import requests


class Repository:
    def __init__(self, repository: str):
        self.repository = urljoin("https://github.com/", repository)

    def get_file_content(self, filename, branch="master"):
        r = requests.get(urljoin(self.repository, f"/raw/{branch}/", filename))
        return r.content
