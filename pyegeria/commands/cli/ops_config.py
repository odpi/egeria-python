import click


class Config(object):
    def __init__(
        self,
        server: str,
        url: str ,
        view_server: str ,
        view_server_url: str ,
        integration_daemon: str ,
        integration_daemon_url: str,
        engine_host: str,
        engine_host_url: str,
        admin_user: str,
        admin_user_password: str,
        userid: str,
        password: str,
        timeout: int,
        jupyter: bool,
        width: int,
        home_glossary_guid: str,
        glossary_path: str,
    ):
        self.metadata_store = server
        self.metadata_store_url = url
        self.view_server = view_server
        self.view_server_url = view_server_url
        self.integration_daemon = integration_daemon
        self.integration_daemon_url = integration_daemon_url
        self.engine_host = engine_host
        self.engine_host_url = engine_host_url
        self.admin_user = admin_user
        self.admin_user_password = admin_user_password
        self.userid = userid
        self.password = password
        self.timeout = timeout
        self.jupyter = jupyter
        self.width = width
        self.server = server
        self.url = url
        self.home_glossary_guid = home_glossary_guid
        self.glossary_path = glossary_path

pass_config = click.make_pass_decorator(Config)
