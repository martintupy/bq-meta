import webbrowser
import wsgiref.simple_server
import wsgiref.util

from google_auth_oauthlib.flow import _WSGIRequestHandler, Flow, _RedirectWSGIApp
import requests
from rich.console import Console
from rich.text import Text

from bq_meta import const
from bq_meta.config import Config


class Auth:
    def __init__(self, config: Config, console: Console) -> None:
        self.config = config
        self.console = console

    def login(self):
        flow = Flow.from_client_config(self.config.client_config, scopes=self.config.scopes)
        try:
            webbrowser.get()
            host = "localhost"
            wsgi_app = _RedirectWSGIApp("The authentication flow has completed. You may close this window.")
            wsgi_app.allow_reuse_address = False
            local_server = wsgiref.simple_server.make_server(host, 0, wsgi_app, handler_class=_WSGIRequestHandler)
            flow.redirect_uri = f"http://{host}:{local_server.server_port}/"
            auth_url, _ = flow.authorization_url()
            webbrowser.open(auth_url, new=2)
            self.console.print(
                Text("Browser openned", style=const.info_style).append(f": {auth_url}", style=const.darker_style)
            )
            local_server.handle_request()
            authorization_response = wsgi_app.last_request_uri.replace("http", "https")
            flow.fetch_token(authorization_response=authorization_response)
            local_server.server_close()
        except Exception:
            flow.redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
            auth_url, _ = flow.authorization_url()
            self.console.print(
                Text("Open following link", style=const.request_style).append(f": {auth_url}", style=const.link_style),
            )
            code = self.console.input(
                Text("Enter verification code", style=const.request_style).append(f": ", style=const.darker_style)
            )
            flow.fetch_token(code=code)

        response = requests.get(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            headers={"Authorization": f"Bearer {flow.credentials.token}"},
        )
        self.config.account = response.json()["email"]
        self.config.credentials = flow.credentials.to_json()
        self.console.print(Text("Credentials updated", style=const.info_style))
