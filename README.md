# TriCaster MCP Server

An MCP (Model Context Protocol) server that lets Claude control a Vizrt TriCaster via its HTTP API.

Tested against: **TriCaster Mini S, v8-5, 1080p29.97**

---

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- A TriCaster on the same network with its HTTP API accessible (default port 80)

---

## Installation

```bash
git clone <repo-url>
cd TriCaster_MCP
```

No additional setup needed — `uv` handles the virtualenv and dependencies automatically on first run.

---

## Configuration

Edit the `TRICASTER_HOST` constant at the top of `server.py` to point at your TriCaster's IP address:

```python
TRICASTER_HOST = "192.168.1.94"   # ← change this
```

---

## Claude Desktop setup

Add the following to your `claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
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
```

Replace `/path/to/uv` with the output of `which uv`, and `/path/to/TriCaster_MCP` with the actual clone location.

Restart Claude Desktop after saving.

---

## Available tools

| Tool | Description |
|---|---|
| `get_system_info` | TriCaster model, version, session, resolution |
| `get_tally` | Which sources are on Program / Preview |
| `get_switcher_state` | Full switcher XML (sources, effects, T-bar) |
| `switch_program` | Cut directly to a new Program source |
| `switch_preview` | Arm a new Preview source |
| `auto_transition` | Auto transition (Preview → Program) |
| `cut_transition` | Instant cut (swap Program ↔ Preview) |
| `fade_to_black` | Fade to black (call again to restore) |
| `take_to_black` | Instant cut to black |
| `dsk_on` / `dsk_off` / `dsk_auto` | DSK 1/2 on-air control |
| `set_audio_mute` | Mute/unmute an audio channel |
| `set_audio_volume` | Set channel volume (0 = unity gain) |
| `ddr_play` / `ddr_stop` | DDR media player playback |
| `ddr_set_loop` | DDR loop mode on/off |
| `ddr_set_autoplay` | DDR autoplay mode on/off |
| `start_record` / `stop_record` | Recording control |
| `get_record_state` | Current recording state |
| `start_stream` / `stop_stream` | Streaming control |
| `get_stream_state` | Current streaming state |
| `list_macros` | List all available macros |
| `run_macro` | Execute a macro by name |
| `get_dictionary` | Read any TriCaster state dictionary (raw XML) |
| `get_datalink` | Get all DataLink key/value pairs |
| `set_datalink` | Set a DataLink key (e.g. scores, lower-thirds text) |
| `send_shortcut` | Send any raw shortcut command (advanced) |

### Audio channel names
`master`, `input1`–`input8`, `ddr1`, `ddr2`, `aux1`, `phones`

### Common source names
`input1`–`input8`, `ddr1`, `ddr2`, `gfx1`, `gfx2`, `bfr1`–`bfr15`, `black`

---

## Technical notes

- Uses the TriCaster HTTP API v1 (`/v1/shortcut`, `/v1/dictionary`, `/v1/trigger`, `/v1/datalink`)
- Communicates over HTTP/1.0 using Python's stdlib `http.client` with `Connection: close`
- No third-party HTTP library required — only dependency is `mcp`
