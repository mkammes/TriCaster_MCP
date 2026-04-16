# TriCaster MCP Server

An MCP (Model Context Protocol) server that lets Claude control a Vizrt TriCaster via its HTTP API. Once installed, you can talk to Claude in plain English to control your TriCaster — switch sources, trigger transitions, manage recording and streaming, control audio, run macros, and more.

Tested against: **TriCaster Mini S, v8-5, 1080p29.97**

---

<img width="2368" height="2002" alt="image" src="https://github.com/user-attachments/assets/130f0e83-d10e-4f47-ac68-f4ac27c36b23" />

---

## What you need before starting

- **Claude Desktop** installed on your computer (download from [claude.ai/download](https://claude.ai/download))
- **A Vizrt TriCaster** connected to the same network as your computer, with its HTTP API accessible on port 80
- **Python 3.11 or newer** (see instructions below if you don't have it)
- **uv** — a fast Python package manager (see instructions below)
- **Git** — for downloading the project (see instructions below)

---

## Step 1 — Install the required tools

### Install Python

Python is the programming language this server is written in. You need version 3.11 or newer.

**macOS:**
1. Open **Terminal** (press `Cmd+Space`, type `Terminal`, press Enter)
2. Run: `python3 --version`
3. If it says `Python 3.11` or higher, you're good. If not, download the latest Python installer from [python.org/downloads](https://www.python.org/downloads/) and run it.

**Windows:**
1. Open **Command Prompt** (press `Win+R`, type `cmd`, press Enter)
2. Run: `python --version`
3. If it says `Python 3.11` or higher, you're good. If not, download the latest Python installer from [python.org/downloads](https://www.python.org/downloads/). **During installation, check the box that says "Add Python to PATH"** before clicking Install.

---

### Install uv

`uv` is a tool that automatically manages Python dependencies for you. It means you don't need to manually install any libraries — just run the server and `uv` handles everything.

**macOS:**

Open Terminal and run:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
After it finishes, close and reopen Terminal so the change takes effect. Verify it worked by running:
```bash
uv --version
```
You should see a version number like `uv 0.5.x`.

**Windows:**

Open Command Prompt and run:
```
winget install astral-sh.uv
```
Or if you prefer, download the installer from [github.com/astral-sh/uv/releases](https://github.com/astral-sh/uv/releases) — grab the `.msi` file and run it.

After installing, close and reopen Command Prompt. Verify by running:
```
uv --version
```

---

### Install Git

Git is used to download (clone) this project to your computer.

**macOS:**

Git usually comes pre-installed. Open Terminal and run:
```bash
git --version
```
If it's not installed, macOS will prompt you to install it automatically. Follow the on-screen instructions.

**Windows:**

Download Git from [git-scm.com/download/win](https://git-scm.com/download/win) and run the installer. Leave all options at their defaults.

After installing, close and reopen Command Prompt. Verify by running:
```
git --version
```

---

## Step 2 — Download the TriCaster MCP Server

Open Terminal (macOS) or Command Prompt (Windows) and navigate to the folder where you want to store the project. For example, to put it in your Documents folder:

**macOS:**
```bash
cd ~/Documents
git clone https://github.com/mkammes/TriCaster_MCP.git
```

**Windows:**
```
cd %USERPROFILE%\Documents
git clone https://github.com/mkammes/TriCaster_MCP.git
```

This creates a folder called `TriCaster_MCP` containing all the server files. You do **not** need to run any install commands inside it — `uv` will handle everything automatically the first time the server starts.

---

## Step 3 — Set your TriCaster's IP address

You need to tell the server where your TriCaster is on the network. There are two ways to do this:

### Option A — Environment variable (recommended)

Set the `TRICASTER_HOST` environment variable in your Claude Desktop config (see Step 5). This keeps your IP out of the source code and makes it easy to change without editing files.

Add an `"env"` section to the tricaster entry in `claude_desktop_config.json`:

```json
"tricaster": {
  "command": "/path/to/uv",
  "args": [ "run", "--project", "/path/to/TriCaster_MCP", "python", "/path/to/TriCaster_MCP/server.py" ],
  "env": {
    "TRICASTER_HOST": "192.168.1.94"
  }
}
```

You can also set `TRICASTER_PORT` the same way if your TriCaster isn't on port 80.

### Option B — Edit server.py directly

1. Find the folder where you cloned the project (e.g. `Documents/TriCaster_MCP`)
2. Open the file `server.py` in a text editor. On macOS you can right-click it and choose **Open With → TextEdit**. On Windows, right-click and choose **Open With → Notepad**.
3. Near the very top of the file, find this line:
   ```python
   TRICASTER_HOST = os.environ.get("TRICASTER_HOST", "10.10.13.162")
   ```
4. Replace the fallback IP address with the IP address of your TriCaster. You can find the TriCaster's IP address in its network settings on the TriCaster itself, or by checking your router's connected devices list.
5. Save the file.

---

## Step 4 — Find the paths you need for configuration

Before editing the Claude Desktop config file, you need to know two things:
- Where `uv` is installed
- The full path to the `TriCaster_MCP` folder

### Find the uv path

**macOS** — run this in Terminal:
```bash
which uv
```
Example output: `/Users/yourname/.local/bin/uv`

**Windows** — run this in Command Prompt:
```
where uv
```
Example output: `C:\Users\yourname\.local\bin\uv.exe`

Write this path down — you'll need it in the next step.

### Find the TriCaster_MCP folder path

**macOS** — if you cloned into Documents:
```
/Users/yourname/Documents/TriCaster_MCP
```
To find your exact username, run `echo $HOME` in Terminal.

**Windows** — if you cloned into Documents:
```
C:\Users\yourname\Documents\TriCaster_MCP
```
To find your exact username, run `echo %USERPROFILE%` in Command Prompt.

---

## Step 5 — Configure Claude Desktop

Claude Desktop uses a configuration file to know which MCP servers to load. You need to add an entry for the TriCaster server.

### Locate the config file

**macOS:**

The file is at:
```
/Users/yourname/Library/Application Support/Claude/claude_desktop_config.json
```
The `Library` folder is hidden by default. The easiest way to open it:
1. Open **Finder**
2. From the menu bar, click **Go → Go to Folder...**
3. Paste in: `~/Library/Application Support/Claude/`
4. Press Enter
5. Open `claude_desktop_config.json` with TextEdit

**Windows:**

The file is at:
```
C:\Users\yourname\AppData\Roaming\Claude\claude_desktop_config.json
```
The `AppData` folder is hidden by default. The easiest way:
1. Press `Win+R`, type `%APPDATA%\Claude\` and press Enter
2. Open `claude_desktop_config.json` with Notepad

---

### Edit the config file

The file contains JSON. It may already have some content, or it may be empty. You need to add a `"tricaster"` entry inside the `"mcpServers"` section.

**If the file is empty or looks like `{}`**, replace the entire contents with:

```json
{
  "mcpServers": {
    "tricaster": {
      "command": "/path/to/uv",
      "args": [
        "run",
        "--project",
        "/path/to/TriCaster_MCP",
        "python",
        "/path/to/TriCaster_MCP/server.py"
      ]
    }
  }
}
```

**If the file already has other MCP servers**, find the `"mcpServers": {` line and add the tricaster entry alongside the others:

```json
{
  "mcpServers": {
    "some-other-server": {
      ...
    },
    "tricaster": {
      "command": "/path/to/uv",
      "args": [
        "run",
        "--project",
        "/path/to/TriCaster_MCP",
        "python",
        "/path/to/TriCaster_MCP/server.py"
      ]
    }
  }
}
```

**Replace the placeholder paths with your real paths from Step 4.**

---

### macOS example (filled in)

```json
{
  "mcpServers": {
    "tricaster": {
      "command": "/Users/yourname/.local/bin/uv",
      "args": [
        "run",
        "--project",
        "/Users/yourname/Documents/TriCaster_MCP",
        "python",
        "/Users/yourname/Documents/TriCaster_MCP/server.py"
      ]
    }
  }
}
```

---

### Windows example (filled in)

On Windows, use forward slashes (`/`) in the JSON file even though Windows normally uses backslashes:

```json
{
  "mcpServers": {
    "tricaster": {
      "command": "C:/Users/yourname/.local/bin/uv.exe",
      "args": [
        "run",
        "--project",
        "C:/Users/yourname/Documents/TriCaster_MCP",
        "python",
        "C:/Users/yourname/Documents/TriCaster_MCP/server.py"
      ]
    }
  }
}
```

---

### Save and restart Claude Desktop

1. Save the config file
2. Fully quit Claude Desktop (on macOS: right-click the dock icon → Quit; on Windows: right-click the system tray icon → Quit)
3. Reopen Claude Desktop

To verify the server loaded correctly, look for a small hammer icon (🔨) or tools indicator in the Claude Desktop interface. You can also type `"what TriCaster tools do you have?"` and Claude should list the available tools.

---

## Step 6 — Test it

With your TriCaster powered on and connected to the network, try asking Claude:

- *"What is the TriCaster's system info?"*
- *"What's currently on program?"*
- *"Switch program to input 2"*
- *"Start recording"*

If Claude responds with real data from your TriCaster, everything is working.

---

## Troubleshooting

**Claude says it doesn't have TriCaster tools:**
- Make sure you fully quit and restarted Claude Desktop (not just closed the window)
- Double-check the paths in `claude_desktop_config.json` — a typo in any path will silently prevent the server from loading
- Make sure the JSON is valid (no missing commas or mismatched brackets) — you can paste it into [jsonlint.com](https://jsonlint.com) to check

**Claude says "connection error" or "could not reach TriCaster":**
- Verify your TriCaster's IP address is correct in `server.py`
- Make sure your computer and TriCaster are on the same network
- Try opening `http://YOUR_TRICASTER_IP/` in a web browser — you should see the TriCaster LivePanel interface if the API is accessible

**uv command not found:**
- Close and reopen your Terminal/Command Prompt after installing uv
- On macOS, make sure you ran the install script in a terminal session that was restarted

---

## Available tools

Once installed, Claude has access to the following tools for controlling your TriCaster:

| Tool | Description |
|---|---|
| **System** | |
| `get_system_info` | TriCaster model, version, session name, and resolution |
| `get_tally` | Shows which sources are currently on Program and Preview |
| `list_sources` | List all available source names (inputs, DDRs, buffers, graphics, etc.) |
| **Switcher** | |
| `get_switcher_state` | Parsed switcher state: Program, Preview, active effect, T-bar position, DSK states |
| `switch_program` | Cut directly to a new Program source (goes to air immediately) |
| `switch_preview` | Arm a new source on Preview without going to air |
| `auto_transition` | Perform an Auto transition, taking Preview to Program using the current effect |
| `cut_transition` | Perform an instant Cut, swapping Program and Preview |
| `set_transition_effect` | Change the active transition effect (e.g. Dissolve, Wipe) |
| `fade_to_black` | Fade the program output to black; call again to fade back up |
| `take_to_black` | Instantly cut the program output to black |
| **DSK** | |
| `dsk_on` / `dsk_off` / `dsk_auto` | Bring DSK 1 or 2 on air, take it off, or auto-transition it |
| **Audio** | |
| `get_audio_state` | Get current mute and volume state for all audio channels |
| `set_audio_mute` | Mute or unmute an audio channel |
| `set_audio_volume` | Set the volume/gain of an audio channel (0 = unity gain) |
| **DDR (media players)** | |
| `get_ddr_status` | Get playback state, timecode, clip name, loop/autoplay mode for a DDR |
| `ddr_play` / `ddr_stop` | Start or stop playback on DDR media player 1 or 2 |
| `ddr_set_loop` | Enable or disable loop mode on a DDR |
| `ddr_set_autoplay` | Enable or disable autoplay mode on a DDR |
| **Recording & Streaming** | |
| `start_record` / `stop_record` | Start or stop recording (optional `recorder` param for multi-recorder systems) |
| `get_record_state` | Check whether recording is currently active |
| `start_stream` / `stop_stream` | Start or stop streaming |
| `get_stream_state` | Check whether streaming is currently active |
| **Media & Macros** | |
| `browse_media` | Browse available media files on the TriCaster file system |
| `list_macros` | List all macros available on the TriCaster |
| `run_macro` | Execute a macro by name |
| **Advanced** | |
| `get_dictionary` | Read any TriCaster state dictionary (returns raw XML) |
| `get_datalink` | Get all current DataLink key/value pairs (live data fields like scores, lower-thirds) |
| `set_datalink` | Set a DataLink key to a value (e.g. update a score or lower-third text) |
| `send_shortcut` | Send any raw shortcut command to the TriCaster |

### Audio channel names

Use these names with `set_audio_mute` and `set_audio_volume`:

`master`, `input1`, `input2`, `input3`, `input4`, `input5`, `input6`, `input7`, `input8`, `ddr1`, `ddr2`, `aux1`, `phones`

### Common source names

Use `list_sources` to see all sources your TriCaster actually exposes. Typical names:

`input1` through `input8` — physical video inputs
`ddr1`, `ddr2` — DDR media players
`gfx1`, `gfx2` — graphics channels
`bfr1` through `bfr15` — buffers
`black` — black/no source

---

## Technical notes

- Uses the TriCaster HTTP API v1 (`/v1/shortcut`, `/v1/dictionary`, `/v1/trigger`, `/v1/datalink`)
- Communicates over HTTP/1.0 using Python's stdlib `http.client` with `Connection: close`
- No third-party HTTP library required — the only external dependency is `mcp`
- The server runs as a local subprocess launched by Claude Desktop over stdio — no ports are opened on your computer
- TriCaster IP and port are read from `TRICASTER_HOST` / `TRICASTER_PORT` environment variables, with fallback to the values hardcoded in `server.py`
