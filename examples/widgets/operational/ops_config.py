import click


class Config(object):
    def __init__(self, server: str = None, url: str = None,
                 view_server: str = 'view-server', view_server_url: str = 'https://localhost:9443',
                 integration_daemon: str = 'integration-daemon', integration_daemon_url: str = 'https://localhost:9443',
                 engine_host: str = 'engine-host', engine_host_url: str = 'https://localhost:9443',
                 admin_user: str = 'garygeeke', admin_user_password: str = 'secret',
                 userid: str = None, password: str = None,
                 timeout: int = 30, paging: bool = False, verbose: bool = False):
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
        self.paging = paging
        self.verbose = verbose


pass_config = click.make_pass_decorator(Config)
