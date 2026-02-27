"""
TriCaster MCP Server
Controls a Vizrt TriCaster via its HTTP API (v1 shortcut/dictionary/trigger/datalink endpoints).

Reference: Vizrt Automation, Integration & Control User Guide v8-5
"""

import http.client
import xml.etree.ElementTree as ET
from urllib.parse import urlencode, quote
import mcp.server.stdio
from mcp.server import Server
from mcp.types import Tool, TextContent
import json

TRICASTER_HOST = "192.168.1.94"
TRICASTER_PORT = 80
TIMEOUT = 5


# ---------------------------------------------------------------------------
# Low-level HTTP helpers
# ---------------------------------------------------------------------------

def _get(path: str) -> str:
    """Send an HTTP GET to the TriCaster. Uses Connection: close to handle HTTP/1.0."""
    conn = http.client.HTTPConnection(TRICASTER_HOST, TRICASTER_PORT, timeout=TIMEOUT)
    try:
        conn.request("GET", path, headers={"Connection": "close"})
        resp = conn.getresponse()
        body = resp.read().decode("utf-8", errors="replace").strip()
        return body
    finally:
        conn.close()


def _post(path: str, body: str) -> str:
    """Send an HTTP POST (XML shortcut) to the TriCaster."""
    conn = http.client.HTTPConnection(TRICASTER_HOST, TRICASTER_PORT, timeout=TIMEOUT)
    try:
        encoded = body.encode("utf-8")
        headers = {
            "Content-Type": "text/xml",
            "Content-Length": str(len(encoded)),
            "Connection": "close",
        }
        conn.request("POST", path, body=encoded, headers=headers)
        resp = conn.getresponse()
        return resp.read().decode("utf-8", errors="replace").strip()
    finally:
        conn.close()


def shortcut(name: str, value: str | None = None, **kwargs) -> str:
    """Send a shortcut command via GET."""
    params = {"name": name}
    if value is not None:
        params["value"] = str(value)
    params.update({k: str(v) for k, v in kwargs.items()})
    return _get(f"/v1/shortcut?{urlencode(params)}")


def dictionary(key: str) -> str:
    """Read a state dictionary (XML) from the TriCaster."""
    return _get(f"/v1/dictionary?key={quote(key)}")


def trigger(name: str, value: str | None = None) -> str:
    """Send a trigger command."""
    params = {"name": name}
    if value is not None:
        params["value"] = str(value)
    return _get(f"/v1/trigger?{urlencode(params)}")


def datalink_set(key: str, value: str) -> str:
    """Set a DataLink key/value."""
    return _get(f"/v1/datalink?{urlencode({'key': key, 'value': value})}")


def datalink_get_all() -> str:
    """Get all current DataLink key/value pairs (XML)."""
    return _get("/v1/datalink")


# ---------------------------------------------------------------------------
# MCP Server setup
# ---------------------------------------------------------------------------

server = Server("tricaster-mcp")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        # ── System info ────────────────────────────────────────────────────
        Tool(
            name="get_system_info",
            description="Get TriCaster model, version, session name, and resolution.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="get_tally",
            description=(
                "Get tally state for all inputs — which sources are on Program "
                "and which are on Preview."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),

        # ── Switcher ───────────────────────────────────────────────────────
        Tool(
            name="get_switcher_state",
            description=(
                "Get the current switcher state: Program source, Preview source, "
                "active effect/transition, and T-bar position."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="switch_program",
            description=(
                "Cut directly to a new Program source (no transition). "
                "Common sources: input1–inputN, ddr1, ddr2, gfx1, gfx2, bfr1–bfrN, black."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "Source name, e.g. 'input1', 'ddr1', 'gfx1', 'black'",
                    }
                },
                "required": ["source"],
            },
        ),
        Tool(
            name="switch_preview",
            description="Set the Preview row to a new source without going to air.",
            inputSchema={
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "Source name, e.g. 'input2', 'ddr1', 'gfx2'",
                    }
                },
                "required": ["source"],
            },
        ),
        Tool(
            name="auto_transition",
            description=(
                "Perform an Auto transition on the main switcher background layer "
                "(takes Preview to Program using the current effect)."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="cut_transition",
            description="Perform an instant Cut transition (Program ↔ Preview).",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),

        # ── DSK (downstream keyers) ────────────────────────────────────────
        Tool(
            name="dsk_on",
            description="Bring a DSK (downstream keyer) layer on air.",
            inputSchema={
                "type": "object",
                "properties": {
                    "dsk": {
                        "type": "integer",
                        "description": "DSK number (1 or 2)",
                        "enum": [1, 2],
                    }
                },
                "required": ["dsk"],
            },
        ),
        Tool(
            name="dsk_off",
            description="Take a DSK (downstream keyer) layer off air.",
            inputSchema={
                "type": "object",
                "properties": {
                    "dsk": {
                        "type": "integer",
                        "description": "DSK number (1 or 2)",
                        "enum": [1, 2],
                    }
                },
                "required": ["dsk"],
            },
        ),
        Tool(
            name="dsk_auto",
            description="Auto-transition a DSK layer on or off.",
            inputSchema={
                "type": "object",
                "properties": {
                    "dsk": {"type": "integer", "description": "DSK number (1 or 2)", "enum": [1, 2]}
                },
                "required": ["dsk"],
            },
        ),

        # ── Recording ─────────────────────────────────────────────────────
        Tool(
            name="start_record",
            description="Start recording on the primary recorder (recorder1).",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="stop_record",
            description="Stop recording on the primary recorder (recorder1).",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="get_record_state",
            description="Get the current recording state (active/inactive) and filename.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),

        # ── Streaming ─────────────────────────────────────────────────────
        Tool(
            name="start_stream",
            description="Start streaming on the primary streamer.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="stop_stream",
            description="Stop streaming on the primary streamer.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="get_stream_state",
            description="Get the current streaming state (active/inactive).",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),

        # ── Fade to Black ─────────────────────────────────────────────────
        Tool(
            name="fade_to_black",
            description=(
                "Fade the program output to black using an auto transition. "
                "Call again to fade back up from black."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="take_to_black",
            description="Instantly cut the program output to black (no transition).",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),

        # ── Audio mixer ───────────────────────────────────────────────────
        Tool(
            name="set_audio_mute",
            description=(
                "Mute or unmute an audio channel. "
                "Channel names: 'master', 'input1'–'input8', 'ddr1', 'ddr2', 'aux1', 'phones'."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "channel": {
                        "type": "string",
                        "description": "Channel name, e.g. 'master', 'input1', 'ddr1'",
                    },
                    "mute": {
                        "type": "boolean",
                        "description": "True to mute, False to unmute",
                    },
                },
                "required": ["channel", "mute"],
            },
        ),
        Tool(
            name="set_audio_volume",
            description=(
                "Set the volume (gain) of an audio channel. "
                "Value is a float; 0 = unity gain, negative = lower, positive = louder. "
                "Channel names: 'master', 'input1'–'input8', 'ddr1', 'ddr2', 'aux1', 'phones'."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "channel": {
                        "type": "string",
                        "description": "Channel name, e.g. 'master', 'input1', 'ddr1'",
                    },
                    "volume": {
                        "type": "number",
                        "description": "Volume level as a float (0 = unity)",
                    },
                },
                "required": ["channel", "volume"],
            },
        ),

        # ── DDR (media players) ───────────────────────────────────────────
        Tool(
            name="ddr_play",
            description="Play a DDR (media player).",
            inputSchema={
                "type": "object",
                "properties": {
                    "ddr": {"type": "integer", "description": "DDR number (1 or 2)", "enum": [1, 2]}
                },
                "required": ["ddr"],
            },
        ),
        Tool(
            name="ddr_stop",
            description="Stop/pause a DDR (media player).",
            inputSchema={
                "type": "object",
                "properties": {
                    "ddr": {"type": "integer", "description": "DDR number (1 or 2)", "enum": [1, 2]}
                },
                "required": ["ddr"],
            },
        ),
        Tool(
            name="ddr_set_loop",
            description="Enable or disable loop mode on a DDR (media player).",
            inputSchema={
                "type": "object",
                "properties": {
                    "ddr": {"type": "integer", "description": "DDR number (1 or 2)", "enum": [1, 2]},
                    "enabled": {"type": "boolean", "description": "True to enable loop, False to disable"},
                },
                "required": ["ddr", "enabled"],
            },
        ),
        Tool(
            name="ddr_set_autoplay",
            description="Enable or disable autoplay mode on a DDR (media player).",
            inputSchema={
                "type": "object",
                "properties": {
                    "ddr": {"type": "integer", "description": "DDR number (1 or 2)", "enum": [1, 2]},
                    "enabled": {"type": "boolean", "description": "True to enable autoplay, False to disable"},
                },
                "required": ["ddr", "enabled"],
            },
        ),

        # ── Macros ────────────────────────────────────────────────────────
        Tool(
            name="list_macros",
            description="List all available macros (system and session) by name and ID.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="run_macro",
            description="Execute a macro by name.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Macro name as shown in the macro list"}
                },
                "required": ["name"],
            },
        ),

        # ── Raw / advanced ────────────────────────────────────────────────
        Tool(
            name="send_shortcut",
            description=(
                "Send any raw shortcut command to the TriCaster. "
                "Use this for advanced/custom control not covered by other tools."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Shortcut name, e.g. 'main_background_auto'"},
                    "value": {"type": "string", "description": "Optional value for the shortcut"},
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="get_dictionary",
            description=(
                "Read any TriCaster state dictionary by key. "
                "Common keys: switcher, tally, buffer, macros_list, switcher_ui_effects, filebrowser."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "Dictionary key, e.g. 'switcher', 'tally'"}
                },
                "required": ["key"],
            },
        ),
        Tool(
            name="get_datalink",
            description="Get all current DataLink key/value pairs (live data fields like scores, time, etc.).",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="set_datalink",
            description="Set a DataLink key to a value (e.g. update a score or text field).",
            inputSchema={
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "DataLink key name"},
                    "value": {"type": "string", "description": "Value to set"},
                },
                "required": ["key", "value"],
            },
        ),
    ]


# ---------------------------------------------------------------------------
# Tool handlers
# ---------------------------------------------------------------------------

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        result = _handle(name, arguments)
    except Exception as e:
        result = f"Error communicating with TriCaster: {e}"
    return [TextContent(type="text", text=result)]


def _handle(name: str, args: dict) -> str:
    # ── System info ─────────────────────────────────────────────────────
    if name == "get_system_info":
        return _get("/v1/version")

    if name == "get_tally":
        xml = dictionary("tally")
        return _parse_tally(xml)

    # ── Switcher ─────────────────────────────────────────────────────────
    if name == "get_switcher_state":
        return dictionary("switcher")

    if name == "switch_program":
        source = args["source"]
        resp = shortcut("main_a_row_named_input", source)
        return f"Program cut to '{source}'. Response: {resp}"

    if name == "switch_preview":
        source = args["source"]
        resp = shortcut("main_b_row_named_input", source)
        return f"Preview set to '{source}'. Response: {resp}"

    if name == "auto_transition":
        resp = shortcut("main_background_auto")
        return f"Auto transition executed. Response: {resp}"

    if name == "cut_transition":
        resp = shortcut("main_background_cut")
        return f"Cut transition executed. Response: {resp}"

    # ── DSK ──────────────────────────────────────────────────────────────
    if name == "dsk_on":
        dsk = args["dsk"]
        resp = shortcut(f"main_dsk{dsk}_on")
        return f"DSK{dsk} brought on air. Response: {resp}"

    if name == "dsk_off":
        dsk = args["dsk"]
        resp = shortcut(f"main_dsk{dsk}_off")
        return f"DSK{dsk} taken off air. Response: {resp}"

    if name == "dsk_auto":
        dsk = args["dsk"]
        resp = shortcut(f"main_dsk{dsk}_auto")
        return f"DSK{dsk} auto transition. Response: {resp}"

    # ── Recording ────────────────────────────────────────────────────────
    if name == "start_record":
        resp = shortcut("record_toggle", "1")
        return f"Record start sent. Response: {resp}"

    if name == "stop_record":
        resp = shortcut("record_toggle", "0")
        return f"Record stop sent. Response: {resp}"

    if name == "get_record_state":
        return _get_shortcut_state("record_toggle", "Recording")

    # ── Streaming ────────────────────────────────────────────────────────
    if name == "start_stream":
        resp = shortcut("streaming_toggle", "1")
        return f"Stream start sent. Response: {resp}"

    if name == "stop_stream":
        resp = shortcut("streaming_toggle", "0")
        return f"Stream stop sent. Response: {resp}"

    if name == "get_stream_state":
        return _get_shortcut_state("streaming_toggle", "Streaming")

    # ── Fade to Black ────────────────────────────────────────────────────
    if name == "fade_to_black":
        resp = shortcut("main_ftb_auto")
        return f"Fade to black executed. Response: {resp}"

    if name == "take_to_black":
        resp = shortcut("main_ftb_take")
        return f"Take to black executed. Response: {resp}"

    # ── Audio mixer ──────────────────────────────────────────────────────
    if name == "set_audio_mute":
        channel = args["channel"]
        mute_val = "true" if args["mute"] else "false"
        resp = shortcut(f"{channel}_mute", mute_val)
        state = "muted" if args["mute"] else "unmuted"
        return f"Channel '{channel}' {state}. Response: {resp}"

    if name == "set_audio_volume":
        channel = args["channel"]
        volume = args["volume"]
        resp = shortcut(f"{channel}_volume", str(volume))
        return f"Channel '{channel}' volume set to {volume}. Response: {resp}"

    # ── DDR ──────────────────────────────────────────────────────────────
    if name == "ddr_play":
        ddr = args["ddr"]
        resp = shortcut(f"ddr{ddr}_play")
        return f"DDR{ddr} play. Response: {resp}"

    if name == "ddr_stop":
        ddr = args["ddr"]
        resp = shortcut(f"ddr{ddr}_stop")
        return f"DDR{ddr} stop. Response: {resp}"

    if name == "ddr_set_loop":
        ddr = args["ddr"]
        val = "true" if args["enabled"] else "false"
        resp = shortcut(f"ddr{ddr}_loop_mode_toggle", val)
        state = "enabled" if args["enabled"] else "disabled"
        return f"DDR{ddr} loop {state}. Response: {resp}"

    if name == "ddr_set_autoplay":
        ddr = args["ddr"]
        val = "true" if args["enabled"] else "false"
        resp = shortcut(f"ddr{ddr}_autoplay_mode_toggle", val)
        state = "enabled" if args["enabled"] else "disabled"
        return f"DDR{ddr} autoplay {state}. Response: {resp}"

    # ── Macros ───────────────────────────────────────────────────────────
    if name == "list_macros":
        xml = dictionary("macros_list")
        return _parse_macros(xml)

    if name == "run_macro":
        macro_name = args["name"]
        resp = trigger("macro", macro_name)
        return f"Macro '{macro_name}' triggered. Response: {resp}"

    # ── Raw / advanced ───────────────────────────────────────────────────
    if name == "send_shortcut":
        sc_name = args["name"]
        value = args.get("value")
        resp = shortcut(sc_name, value)
        return f"Shortcut '{sc_name}' sent. Response: {resp}"

    if name == "get_dictionary":
        return dictionary(args["key"])

    if name == "get_datalink":
        return datalink_get_all()

    if name == "set_datalink":
        resp = datalink_set(args["key"], args["value"])
        return f"DataLink '{args['key']}' set to '{args['value']}'. Response: {resp}"

    return f"Unknown tool: {name}"


# ---------------------------------------------------------------------------
# XML parsing helpers
# ---------------------------------------------------------------------------

def _get_shortcut_state(shortcut_name: str, label: str) -> str:
    """Read a single shortcut value from the shortcut_states dictionary."""
    try:
        xml = dictionary("shortcut_states")
        root = ET.fromstring(xml)
        for el in root:
            if el.get("name") == shortcut_name:
                val = el.get("value", "unknown")
                state = "active" if val not in ("0", "false", "") else "inactive"
                return f"{label}: {state} (raw value: {val!r})"
        return f"{label}: unknown (shortcut '{shortcut_name}' not found in shortcut_states)"
    except ET.ParseError:
        return f"{label}: parse error reading shortcut_states"


def _parse_tally(xml: str) -> str:
    """Parse tally XML and return a readable summary."""
    try:
        root = ET.fromstring(xml)
        on_pgm = [c.get("name") for c in root if c.get("on_pgm") == "true"]
        on_prev = [c.get("name") for c in root if c.get("on_prev") == "true"]
        lines = [
            "=== Tally State ===",
            f"On Program: {', '.join(on_pgm) if on_pgm else '(none)'}",
            f"On Preview: {', '.join(on_prev) if on_prev else '(none)'}",
        ]
        return "\n".join(lines)
    except ET.ParseError:
        return xml  # return raw if parse fails


def _parse_macros(xml: str) -> str:
    """Parse macros_list XML into a readable list."""
    try:
        root = ET.fromstring(xml)
        macros = []
        for m in root.iter("macro"):
            macro_name = m.get("name", "")
            macro_id = m.get("id", "")
            macros.append(f"  {macro_name} (id: {macro_id})")
        if not macros:
            return "No macros found, or unexpected XML format.\n\nRaw:\n" + xml
        return "=== Available Macros ===\n" + "\n".join(macros)
    except ET.ParseError:
        return xml


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
