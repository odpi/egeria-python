<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the ODPi Egeria project. -->

# Setting Up Login Secrets on Linux Terminal

This guide explains how to securely configure authentication credentials for pyegeria on Linux systems.

## Overview

pyegeria uses environment variables to manage authentication credentials:
- `EGERIA_USER`: Your Egeria username (default: `erinoverview`)
- `EGERIA_USER_PASSWORD`: Your Egeria password (default: `secret`)

There are multiple methods to set these credentials, depending on your security requirements and use case.

---

## Method 1: Using a .env File (Recommended for Development)

The `.env` file approach keeps credentials in a single location and loads them automatically.

### Steps:

1. **Navigate to your project directory:**
   ```bash
   cd /path/to/egeria-python
   ```

2. **Create or edit a `.env` file:**
   ```bash
   nano .env
   # or use your preferred editor: vim, gedit, etc.
   ```

3. **Add your credentials:**
   ```bash
   EGERIA_USER=myusername
   EGERIA_USER_PASSWORD=mypassword
   
   # Optional: Configure other Egeria settings
   EGERIA_PLATFORM_URL=https://localhost:9443
   EGERIA_VIEW_SERVER=qs-view-server
   ```

4. **Save and exit** (in nano: Ctrl+O, Enter, Ctrl+X)

5. **Secure the file permissions:**
   ```bash
   chmod 600 .env
   ```
   This ensures only you can read/write the file.

6. **Verify it's ignored by git:**
   Ensure `.env` is in your `.gitignore` to prevent committing secrets:
   ```bash
   echo ".env" >> .gitignore
   ```

### Using the .env file:

pyegeria automatically loads `.env` from your current working directory. You can also specify a custom env file:

```python
from pyegeria import load_app_config

# Load from default .env location
load_app_config()

# Or specify a custom env file
load_app_config(env_file="/path/to/custom.env")
```

---

## Method 2: Export Environment Variables (Session-Level)

For temporary use during a terminal session:

```bash
export EGERIA_USER=myusername
export EGERIA_USER_PASSWORD=mypassword
```

**Pros:** Simple, no files needed  
**Cons:** Variables are lost when you close the terminal

To verify they're set:
```bash
echo $EGERIA_USER
echo $EGERIA_USER_PASSWORD
```

---

## Method 3: Add to Shell Profile (Persistent Across Sessions)

To make credentials available in all terminal sessions:

### For Bash (~/.bashrc or ~/.bash_profile):

1. **Edit your bash profile:**
   ```bash
   nano ~/.bashrc
   # On some systems, use ~/.bash_profile instead
   ```

2. **Add exports at the end of the file:**
   ```bash
   # Egeria credentials
   export EGERIA_USER=myusername
   export EGERIA_USER_PASSWORD=mypassword
   export EGERIA_PLATFORM_URL=https://localhost:9443
   ```

3. **Save and reload:**
   ```bash
   source ~/.bashrc
   ```

### For Zsh (~/.zshrc):

1. **Edit your zsh profile:**
   ```bash
   nano ~/.zshrc
   ```

2. **Add exports:**
   ```bash
   # Egeria credentials
   export EGERIA_USER=myusername
   export EGERIA_USER_PASSWORD=mypassword
   ```

3. **Save and reload:**
   ```bash
   source ~/.zshrc
   ```

**⚠️ Security Warning:** This method stores passwords in plain text in your home directory. While the file is readable only by you (by default), it's less secure than using dedicated secret management tools.

---

## Method 4: Using a Dedicated Config Directory (Recommended for Production)

For better organization and security:

1. **Create a config directory:**
   ```bash
   mkdir -p ~/egeria-config
   chmod 700 ~/egeria-config  # Restrict access to owner only
   ```

2. **Create an environment file:**
   ```bash
   nano ~/egeria-config/.env
   ```

3. **Add credentials:**
   ```bash
   EGERIA_USER=myusername
   EGERIA_USER_PASSWORD=mypassword
   EGERIA_PLATFORM_URL=https://localhost:9443
   EGERIA_VIEW_SERVER=qs-view-server
   ```

4. **Secure the file:**
   ```bash
   chmod 600 ~/egeria-config/.env
   ```

5. **Set the config directory path:**
   ```bash
   export PYEGERIA_CONFIG_DIRECTORY=~/egeria-config
   ```

6. **Load in your application:**
   ```python
   from pyegeria import load_app_config
   
   load_app_config(env_file="~/egeria-config/.env")
   ```

---

## Method 5: Using Secret Management Tools (Most Secure)

For production environments, use dedicated secret management:

### Using pass (Password Store):

1. **Install pass:**
   ```bash
   sudo apt-get install pass  # Debian/Ubuntu
   sudo yum install pass      # RedHat/CentOS
   ```

2. **Initialize pass:**
   ```bash
   gpg --gen-key  # If you don't have a GPG key
   pass init your-gpg-id
   ```

3. **Store secrets:**
   ```bash
   pass insert egeria/username
   pass insert egeria/password
   ```

4. **Retrieve in your script:**
   ```bash
   export EGERIA_USER=$(pass show egeria/username)
   export EGERIA_USER_PASSWORD=$(pass show egeria/password)
   ```

### Using systemd User Services (for background services):

Create a systemd environment file at `~/.config/systemd/user/egeria.env`:

```bash
EGERIA_USER=myusername
EGERIA_USER_PASSWORD=mypassword
```

Reference it in your service file with `EnvironmentFile=-/home/username/.config/systemd/user/egeria.env`

---

## Security Best Practices

1. **Never commit credentials to git:**
   - Always add `.env` files to `.gitignore`
   - Use environment variable references in committed config files

2. **Use restrictive file permissions:**
   ```bash
   chmod 600 ~/.env           # Read/write for owner only
   chmod 700 ~/egeria-config  # Execute/read/write for owner only
   ```

3. **Rotate passwords regularly:**
   - Change passwords periodically
   - Update environment variables and .env files accordingly

4. **Use different credentials per environment:**
   - Development: `dev.env`
   - Testing: `test.env`
   - Production: Secure secret management

5. **Avoid hardcoding credentials:**
   - Never put passwords directly in Python code
   - Always use environment variables or config files

---

## Verifying Your Setup

After configuring credentials, test your setup:

```python
from pyegeria import load_app_config, get_app_config

# Load configuration
load_app_config()
cfg = get_app_config()

# Access credentials (safely - never print passwords!)
print(f"User: {cfg.User_Profile.user_name}")
print(f"Platform URL: {cfg.Environment.egeria_platform_url}")

# Note: Never print passwords in production!
# This is just for initial verification:
if cfg.User_Profile.user_pwd:
    print("Password is set ✓")
```

Or use the validation script:

```bash
python tests/validate_env.py --env .env
```

---

## Troubleshooting

### "Authentication failed" errors:

1. **Verify credentials are loaded:**
   ```bash
   echo $EGERIA_USER
   echo $EGERIA_USER_PASSWORD
   ```

2. **Check .env file location:**
   - pyegeria looks for `.env` in the current working directory
   - Or specify explicitly: `load_app_config(env_file="/path/to/.env")`

3. **Verify file permissions:**
   ```bash
   ls -la .env
   # Should show: -rw------- (600)
   ```

### Variables not persisting:

- If using `export`: Variables are session-only. Add to `~/.bashrc` for persistence
- If using `.env`: Ensure you're running from the correct directory or specifying the path

### Password with special characters:

In `.env` files, you can use quotes if needed:
```bash
EGERIA_USER_PASSWORD='my$p@ssw0rd!'
```

Or escape special characters:
```bash
EGERIA_USER_PASSWORD=my\$p\@ssw0rd\!
```

---

## Example: Complete Setup for Local Development

```bash
# 1. Navigate to project
cd ~/projects/egeria-python

# 2. Create .env file
cat > .env << 'EOF'
# Egeria Authentication
EGERIA_USER=erinoverview
EGERIA_USER_PASSWORD=secret

# Egeria Configuration
EGERIA_PLATFORM_URL=https://localhost:9443
EGERIA_VIEW_SERVER=qs-view-server
EGERIA_VIEW_SERVER_URL=https://localhost:9443

# pyegeria Configuration
PYEGERIA_CONFIG_DIRECTORY=./config
PYEGERIA_CONFIG_FILE=config.json
PYEGERIA_ROOT_PATH=./sample-data
EOF

# 3. Secure the file
chmod 600 .env

# 4. Verify it's in .gitignore
grep -q "^\.env$" .gitignore || echo ".env" >> .gitignore

# 5. Test the configuration
python << 'PYTHON'
from pyegeria import load_app_config, get_app_config
load_app_config()
cfg = get_app_config()
print(f"✓ User configured: {cfg.User_Profile.user_name}")
print(f"✓ Platform URL: {cfg.Environment.egeria_platform_url}")
print("✓ Configuration loaded successfully!")
PYTHON
```

---

## Additional Resources

- Main configuration guide: [config/README.md](config/README.md)
- Environment variables reference: [config/env](config/env)
- Project README: [README.md](README.md)
- Example configuration: [config/config.json](config/config.json)

---

## Quick Reference

| Method | Persistence | Security | Use Case |
|--------|-------------|----------|----------|
| .env file | Per-project | Good | Development |
| export command | Session only | Good | Testing |
| Shell profile | Per-user | Fair | Personal use |
| Config directory | Persistent | Good | Multi-project |
| Secret manager | Persistent | Excellent | Production |

---

License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/),
Copyright Contributors to the ODPi Egeria project.
