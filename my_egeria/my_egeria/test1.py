from textual.app import App

from pyegeria import EgeriaTech

import os
from pyegeria import Egeria, PyegeriaException, EgeriaTech

class Test1App(App):

    def __init___(self):
        # 1. Initialize the Egeria environment variables
        view_server = os.environ.get("VIEW_SERVER", "view-server")
        url = os.environ.get("EGERIA_VIEW_SERVER_URL", "https://localhost:7443")
        user_id = os.environ.get("EGERIA_USER", "peterprofile")
        user_pwd = os.environ.get("EGERIA_USER_PASSWORD", "password")

        # 2. Instantiate the EgeriaTech client wrapper
        egeria_tech = EgeriaTech(view_server, url, user_id, user_pwd)
        egeria_tech.create_egeria_bearer_token()

        # Print every method available in your installed pyegeria client containing 'comment'
        comment_methods = [method for method in dir(egeria_tech) if 'comment' in method.lower()]

        print("Available comment methods on egeria_tech:")
        for method in comment_methods:
            print(f"- {method}")

if __name__ == "__main__":
    app = Test1App()
    app.run()