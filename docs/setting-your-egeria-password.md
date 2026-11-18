# Setting your Egeria password

pyegeria signs in to Egeria as a user, with that user's password. This page explains where pyegeria looks for the
password, how to set it, and **a change coming in pyegeria 6.4**.

## What's changing

| | pyegeria 6.3.x (now) | pyegeria 6.4 |
|---|---|---|
| The pyegeria **library** (your own code, notebooks, Dr.Egeria from Python) | No built-in password. If none is set, signing in fails with a clear message. | The same. |
| The **command-line tools** (`hey_egeria` and the other CLIs) | If you set no password, they fall back to the QuickStart demo password. | **No fallback.** If you set no password, the command fails with the message below. |

So if you use the CLIs today without setting a password, they work only because of that demo-password fallback.
**Set your password now** (any of the ways below), and nothing changes for you in 6.4.

When no password is set, you'll see this (in the library now, and in the CLIs from 6.4):

```
No password to sign in to Egeria as 'erinoverview': pass one, set EGERIA_USER_PASSWORD (or the settings'
user_pwd), or set a bearer token with set_bearer_token(). pyegeria has no default password.
```

The sign-in stops before anything is sent to Egeria. Earlier versions sent the request and got a 401 back. Code
that catches that 401 should catch `PyegeriaInvalidParameterException` instead.

## Where pyegeria looks for the password

pyegeria uses the first of these that is set:

1. **A value you pass explicitly**: `--password` (most CLIs) or `--user_pass` (the Dr.Egeria CLIs) on the command
   line, or `user_pwd=` when you create a client in code.
2. **The `EGERIA_USER_PASSWORD` environment variable.**
3. **`config.json`**: the `"user_pwd"` entry under `"User Profile"`.
4. **A `.env` file**: an `EGERIA_USER_PASSWORD=` line in a `.env` in your working directory (or in
   `PYEGERIA_ROOT_PATH`).

The user works the same way, with `--userid`, `EGERIA_USER`, `"user_name"` and `EGERIA_USER=`.

## How to set it

Pick the one that suits how you work.

**For one shell session** (nothing is saved):

```bash
export EGERIA_USER=erinoverview
export EGERIA_USER_PASSWORD='your-password'
hey_egeria cat show glossary glossaries
```

**For a project** (saved in a `.env` file in the directory you run from):

```bash
# .env
EGERIA_USER=erinoverview
EGERIA_USER_PASSWORD=your-password
```

Keep it private: `chmod 600 .env`, and add `.env` to your `.gitignore` so it's never committed.

**In `config.json`** (if you already keep your pyegeria settings there):

```json
{
  "User Profile": {
    "user_name": "erinoverview",
    "user_pwd": "your-password"
  }
}
```

**For a single command**:

```bash
hey_egeria --userid erinoverview --password 'your-password' cat show glossary glossaries
```

A password on the command line can end up in your shell history, so prefer the environment variable or `.env`
for anything you repeat.

**In your own code**:

```python
import os
from pyegeria import EgeriaTech

client = EgeriaTech("qs-view-server", "https://localhost:9443",
                    user_id="erinoverview", user_pwd=os.environ["EGERIA_USER_PASSWORD"])
client.create_egeria_bearer_token()
```

`os.environ["EGERIA_USER_PASSWORD"]` stops at once, with a `KeyError`, if the password isn't set. Don't write
`os.environ.get("EGERIA_USER_PASSWORD", "secret")`, which quietly signs in with a guessed password.

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
