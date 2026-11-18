# Setting your Egeria password

pyegeria signs in to Egeria as a user, with that user's password. This page explains where pyegeria looks for the
password, how to set it, and **the changes in the next releases**.

## What's changing

| | pyegeria 6.3.0 | The next pyegeria release | pyegeria 6.4 |
|---|---|---|---|
| The pyegeria **library** (your own code, notebooks, Dr.Egeria from Python) | Falls back to the QuickStart demo password if none is set. | **No built-in password.** If none is set, signing in fails with the message below. | The same. |
| The **command-line tools** (`hey_egeria` and the other CLIs) | Fall back to the demo password if `EGERIA_USER_PASSWORD` isn't set. | The same. | **No fallback.** They read the password the same way as the library (below), and fail with the message below if none is set. |

If you use the CLIs today without setting `EGERIA_USER_PASSWORD`, they work only because of that demo-password
fallback. **Set `EGERIA_USER_PASSWORD` now** (see "How to set it"), and nothing changes for you in 6.4.

When no password is set, you'll see this (in the library from the next release, and in the CLIs from 6.4):

```
No password to sign in to Egeria as 'erinoverview': pass one, set EGERIA_USER_PASSWORD (or the settings'
user_pwd), or set a bearer token with set_bearer_token(). pyegeria has no default password.
```

The sign-in stops before anything is sent to Egeria. Earlier versions sent the request and got a 401 back. Code
that catches that 401 should catch `PyegeriaInvalidParameterException` instead.

## Where pyegeria looks for the password

The library and the CLIs don't look in the same places until 6.4.

**The library** (your own code, notebooks, Dr.Egeria from Python) uses the first of these that is set:

1. **A value you pass explicitly**: `user_pwd=` when you create a client.
2. **The `EGERIA_USER_PASSWORD` environment variable.**
3. **`config.json`**: the `"user_pwd"` entry under `"User Profile"`.
4. **A `.env` file**: an `EGERIA_USER_PASSWORD=` line in a `.env` in the directory you run from (or the file you
   name with `PyegeriaSettings.with_env_file`).

**The command-line tools, until 6.4**, use only:

1. `--password` (most CLIs) or `--user_pass` (the Dr.Egeria CLIs) on the command line;
2. the `EGERIA_USER_PASSWORD` environment variable;
3. otherwise, the QuickStart demo password.

They don't read `config.json` or `.env` for the password. A password you set only there is **not used** by the
CLIs before 6.4: they still sign in with the demo password. From 6.4 the CLIs use the library's list.

An `EGERIA_USER_PASSWORD` that is set but **empty** counts as set. pyegeria then doesn't look further, in
`config.json` or `.env`, and sign-in is refused. Unset the variable rather than leaving it empty.

The user works the same way, with `--userid`, `EGERIA_USER`, `"user_name"` and `EGERIA_USER=`.

## How to set it

**The one that works everywhere, now and in 6.4: the `EGERIA_USER_PASSWORD` environment variable.**

For one shell session:

```bash
export EGERIA_USER=erinoverview
export EGERIA_USER_PASSWORD='your-password'
hey_egeria cat show glossary glossaries
```

To have it in every shell, put those two `export` lines in your shell's startup file (for example `~/.zshrc` or
`~/.bashrc`), which only you should be able to read.

**For the library only** (your code and notebooks; the CLIs read these from 6.4):

- In a `.env` file in the directory you run from:

  ```bash
  # .env
  EGERIA_USER=erinoverview
  EGERIA_USER_PASSWORD=your-password
  ```

  Keep it private: `chmod 600 .env`, and add `.env` to your `.gitignore` so it's never committed.

- In `config.json`, if you already keep your pyegeria settings there:

  ```json
  {
    "User Profile": {
      "user_name": "erinoverview",
      "user_pwd": "your-password"
    }
  }
  ```

- In your own code:

  ```python
  import os
  from pyegeria import EgeriaTech

  client = EgeriaTech("qs-view-server", "https://localhost:9443",
                      user_id="erinoverview", user_pwd=os.environ["EGERIA_USER_PASSWORD"])
  client.create_egeria_bearer_token()
  ```

  `os.environ["EGERIA_USER_PASSWORD"]` stops at once, with a `KeyError`, if the password isn't set. Don't write
  `os.environ.get("EGERIA_USER_PASSWORD", "secret")`, which quietly signs in with a guessed password.

**For a single CLI command**, `--password` also works (the options go before the sub-command):

```bash
hey_egeria --userid erinoverview --password 'your-password' cat show glossary glossaries
```

A password typed on the command line can end up in your shell history, so prefer the environment variable for
anything you repeat.

## Which password?

On the Egeria QuickStart, every demo user (for example `erinoverview` or `peterprofile`) shares the QuickStart's
standard demo password, which is in the QuickStart's own documentation. On any other Egeria, use the password your
administrator gave you.

## Servers and services are different

`EGERIA_USER` and `EGERIA_USER_PASSWORD` are for running pyegeria **as yourself**, in a shell or a notebook.
A server that uses pyegeria (a web app, an agent, a scheduler) should sign in as **its own service account**,
under its own setting names, and should never set `EGERIA_USER` / `EGERIA_USER_PASSWORD`. Trellis uses
`RE_DAEMON_USER_ID` and `EA_DAEMON_USER_ID`, for example. Otherwise pyegeria's fallback could sign the server in
as a person.
