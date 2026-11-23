"""PY-67 read-back (b): when sign-in fails, generate_dr_help main() has no connection (client None) and so says
"no Egeria connection", not "lookup failed"."""
import importlib
import sys


class _FailingSignIn:
    def __init__(self, *a, **k):
        pass

    def create_egeria_bearer_token(self, *a, **k):
        raise ConnectionError("platform unreachable")


def test_a_failed_sign_in_gives_create_help_terms_no_client(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    gen = importlib.import_module("commands.tech.generate_dr_help")
    seen = {}
    monkeypatch.setattr(gen, "ServerClient", _FailingSignIn)
    monkeypatch.setattr(gen, "create_help_terms", lambda client=None, advanced=False: seen.setdefault("client", client) or seen.update(called=True))
    monkeypatch.setattr(sys, "argv", ["generate_dr_help", "--url", "https://nowhere.invalid:9443",
                                      "--userid", "u", "--pass", "p"])
    gen.main()
    assert "client" in seen and seen["client"] is None
