# 🪟 Ultimate Guide: Fireflies.ai → Obsidian Sync (Windows 11 Pro)

This guide establishes a robust data pipeline based on State Control (Delta Sync) and AI Extraction (GraphQL). On Windows, we replace Systemd with the **Task Scheduler**, but we demand the same flawless, calendar-agnostic ghost execution.

## 🛠️ Phase 1: Foundations (Professional Installation)

Amateurs rely on browser downloads and executables. We use the native Windows package manager to install tools directly via the terminal.

Open **PowerShell as Administrator** and run:

```powershell
# 1. Install the versioning engine (Git)
winget install --id Git.Git -e --source winget

# 2. Install the processing engine (Python 3.12)
winget install --id Python.Python.3.12 -e --source winget

```

*(Confirm with `Y` any prompts on the screen and wait for completion).*

⚠️ **Mandatory:** After installation, close **ALL** PowerShell windows. Windows needs this hard reset to update the environment variables (PATH) and recognize the new commands.

## 📦 Phase 2: Cloning & Isolation (Venv)

Open a **new PowerShell** (as Administrator) and navigate to the folder where your infrastructure will live (e.g., Documents).

```powershell
cd C:\Users\YOUR_USERNAME\Documents

# 1. Pull your engineering from GitHub
git clone https://github.com/marcosaugustoldo/fireflies-obsidian-sync-all.git
cd fireflies-obsidian-sync-all

# 2. Break the Windows security lock for local scripts
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
# (Type 'Y' or 'A' and press Enter to confirm)

# 3. Create the isolation bubble and activate it
python -m venv venv
.\venv\Scripts\activate

# 4. Install dependencies inside the bubble
pip install -r requirements.txt

```

## 🔐 Phase 3: Credentials & Destination (.env)

The automation needs to know your key and where to drop the files.

Create a file named `.env` inside the `fireflies-obsidian-sync-all` folder and fill it:

```ini
FF_API_KEY="YOUR_KEY_HERE"

# WARNING: Use standard forward slashes (/) or double backslashes (\\) on Windows
OBSIDIAN_VAULT_PATH="C:/Users/YOUR_USERNAME/Documents/YourObsidianVault"

```

**The Reality Check (Ledger Creation):**
Still with PowerShell open and the `(venv)` activated, force the first run:

```powershell
python sync_fireflies.py

```

*If the execution finishes without errors and the notes appear in your Obsidian, the foundation is validated. You can close PowerShell.*

---

## 🕒 Phase 4: Silent Orchestration (The Secret Weapon)

Now we tie the execution deep into the Windows core. The secret here is using the `pythonw.exe` binary (with the "W") to guarantee that no black CMD screen flashes while you are working.

1. Open the Windows Start menu, type **Task Scheduler**, and open the application.
2. In the right-hand menu, click **Create Task...** (DO NOT use "Create Basic Task").

### General Tab (Authority)

* **Name:** `Fireflies Obsidian Sync Pro`
* Check the option: **"Run whether user is logged on or not"**. (This grants system-level privileges to the script).
* Check the option: **"Hidden"**.
* Configure for: **Windows 10/11**.

### Triggers Tab (The Clock)

* Click **New...**
* Begin the task: **On a schedule** -> **Daily**.
* Under *Advanced settings*, check **"Repeat task every:"** and select **1 hour**.
* For a duration of: Change to **Indefinitely**.
* Click **OK**.

### Actions Tab (The Precision Strike)

* Click **New...**
* Action: **Start a program**.
* **Program/script:** Place the absolute path to the invisible engine.
`C:\Users\YOUR_USERNAME\Documents\fireflies-obsidian-sync-all\venv\Scripts\pythonw.exe`
* **Add arguments:** Type only:
`sync_fireflies.py`
* **Start in (MANDATORY):** Place the absolute path of the project's root folder. If you forget this, the script won't find the `.env` and will die silently.
`C:\Users\YOUR_USERNAME\Documents\fireflies-obsidian-sync-all\`
* Click **OK**.

### Conditions Tab (Power Safety)

* **Uncheck** the option: *"Start the task only if the computer is on AC power"*. Your script must run even if the laptop is on battery.

### Finalization & Signature

* Click **OK** to save the task.
* Windows will demand the **real password of your Microsoft account** (not the PIN) to authorize this high-level background execution. Enter and confirm.

Your data pipeline on Windows is officially homologated, operating passively, invisibly, and immune to failures.
