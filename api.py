import requests
import os


class CDNManager:
    def __init__(self, username, password):
        self.username = username
        self.password = password

        self.get_headers = {"AccessKey": password}
        self.put_headers = {"AccessKey": password, "Checksum": ""}

    def new_medrash(self, file):
        url = f"https://storage.bunnycdn.com/{self.username}/medrash/{file}"
        filepath = f"{os.getcwd()}/static/medrash/{file}"
        f = open(filepath, mode="rb").read()
        upload = requests.put(url, data=f, headers=self.put_headers)

    def new_team_logo(self, file):
        url = f"https://storage.bunnycdn.com/{self.username}/sports_logos/{file}"
        filepath = f"{os.getcwd()}/static/sport_logos/{file}"
        f = open(filepath, mode="rb").read()
        upload = requests.put(url, data=f, headers=self.put_headers)

    def new_cover_image(self, file):
        url = f"https://storage.bunnycdn.com/{self.username}/images/{file}"
        filepath = f"{os.getcwd()}/static/images/{file}"
        f = open(filepath, mode="rb").read()
        upload = requests.put(url, data=f, headers=self.put_headers)


if __name__ == "__main__":
    cdn = CDNManager(username="herald", password="")
