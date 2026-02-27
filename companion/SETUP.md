# Bitfocus Companion — TriCaster Stream Deck XL Setup

This guide walks you through importing the `tricaster_page.json` config into Bitfocus Companion and getting it working with your Stream Deck XL and TriCaster.

---

## What's included

`tricaster_page.json` is a Companion v3 page export containing a full 4×8 Stream Deck XL layout:

| Row | Contents |
|-----|----------|
| **Row 1** (top) | Open LivePanel · Load Session macro · *(blank)* · Fade to Black · AUTO · CUT · RECORD · STREAM |
| **Row 2** | Program bus — IN1, IN2, IN3, IN4, DDR1, DDR2, GFX1, GFX2 *(red tally feedback)* |
| **Row 3** | Preview bus — IN1, IN2, IN3, IN4, DDR1, DDR2, GFX1, GFX2 *(green tally feedback)* |
| **Row 4** (bottom) | DSK1 · DSK2 · *(blank)* · *(blank)* · MUTE Master · MUTE IN1 · MUTE IN2 · MUTE IN3 |

---

## Prerequisites

- **Bitfocus Companion 3.x** installed and running ([bitfocus.io/companion](https://bitfocus.io/companion))
- **Elgato Stream Deck XL** (32 buttons, 4×8)
- **newtek-tricaster** module added as a connection in Companion
- TriCaster reachable on the network (default IP in this project: `192.168.1.94`)

---

## Step 1 — Add the newtek-tricaster connection

1. Open the Companion web UI (usually `http://localhost:8000`)
2. Go to **Connections** → **Add connection**
3. Search for **TriCaster** and select **NewTek TriCaster**
4. Enter your TriCaster's IP address (`192.168.1.94` or whatever yours is)
5. Click **Save** — the connection should show as **OK**

---

## Step 2 — Find your Connection ID

Every Companion connection has an internal ID (e.g. `newtek-tricaster:abc123`). You need this to link the imported buttons to your TriCaster connection.

1. In the Companion web UI, go to **Connections**
2. Click the **Edit** (pencil) icon next to your TriCaster connection
3. Look at the browser URL — it will contain the connection ID, e.g.:
   ```
   http://localhost:8000/connection/newtek-tricaster:abc123/edit
   ```
   Your connection ID is the part after `/connection/` — e.g. `newtek-tricaster:abc123`

Alternatively, you can find it by exporting any button that already uses the TriCaster connection and inspecting the JSON.

---

## Step 3 — Import the page

1. In Companion, go to **Pages**
2. Click the **Import / Export** button (or the down-arrow icon on the page you want to replace)
3. Choose **Import page**
4. Select `tricaster_page.json` from the `companion/` folder in this repo
5. Choose which page number to import onto, then confirm

The page will import with all 32 buttons, but the buttons won't fire yet — they still reference the placeholder `TRICASTER_INSTANCE_ID`.

---

## Step 4 — Replace the instance ID placeholder

All actions and feedbacks in the imported page reference `TRICASTER_INSTANCE_ID` as the connection. You need to replace this with your actual connection ID from Step 2.

### Option A — Find & Replace in a text editor (easiest)

1. Before importing, open `tricaster_page.json` in a text editor (VS Code, Notepad++, TextEdit, etc.)
2. Use **Find & Replace** (Cmd+H / Ctrl+H) to replace every occurrence of:
   ```
   TRICASTER_INSTANCE_ID
   ```
   with your actual connection ID, e.g.:
   ```
   newtek-tricaster:abc123
   ```
3. Save the file, then import it as described in Step 3

### Option B — Re-assign connections after import

If you've already imported and want to fix it inside Companion:

1. Go to **Pages** → find the imported page
2. For each button, click **Edit**, then update each action and feedback to point to your TriCaster connection
3. This is tedious for 32 buttons — Option A is strongly recommended

---

## Step 5 — Verify source IDs (Program and Preview rows)

The Program and Preview bus buttons use source names like `input1`, `input2`, `ddr1`, `gfx1`, etc. These are populated dynamically by the newtek-tricaster module from your TriCaster session.

If your buttons don't switch sources correctly:

1. Edit one of the Program or Preview buttons in Companion
2. Find the **Source** dropdown in the action options
3. Check whether the source names listed match what's in the config (e.g. `input1`, `ddr1`, `gfx1`)
4. If they differ (some TriCaster sessions use different naming), update the affected buttons to match the names shown in the dropdown

---

## Step 6 — Set your Load Session macro name

The **Load Session** button (Row 1, Column 2) is pre-configured to run a macro named `YOUR_LOAD_SESSION_MACRO`. You need to replace this with the actual name of a macro on your TriCaster.

1. Open the **Load Session** button for editing
2. Find the **customMacro** action
3. Change the macro name to match one of your TriCaster macros
4. If you don't use session-loading macros, you can repurpose or blank this button

---

## Button behavior notes

### RECORD and STREAM (Row 1)

These buttons use a **two-step toggle**:

- **First press** → sends the Start command
- **Second press** → sends the Stop command

The button cycles between steps on each press. If the physical state gets out of sync with what Companion thinks (e.g. if you started recording outside of Companion), press the button twice to re-sync the step counter.

Both buttons show a **red background** when recording/streaming is active (via feedback).

### Audio Mute buttons (Row 4)

The mute buttons (Master, IN1, IN2, IN3) also use a **two-step toggle** — first press mutes, second press unmutes.

> **Note:** The newtek-tricaster module's native `audio_mute` action only supports DDR and effects channels. For input channels and master, the mute buttons send raw TriCaster HTTP shortcuts (`master_mute`, `input1_mute`, etc.) via the `custom` action. This means **mute state feedback is not available** for these buttons — the button step counter tracks the expected state locally, but it won't reflect changes made on the TriCaster hardware panel directly.

### DSK buttons (Row 4)

DSK1 and DSK2 buttons trigger an auto-transition on/off. They show a **yellow background** when the DSK is on air (via `dskOnAir` feedback).

### Fade to Black (Row 1)

This button triggers `main_ftb_auto` — the same as pressing Fade to Black on the TriCaster panel. Press once to fade to black, press again to fade back up. No Companion-side feedback is included (the TriCaster handles the visual state).

---

## Customizing the layout

The page is a standard Companion page export — you can freely edit any button in the Companion UI after importing:

- Change button labels, colors, or sizes
- Add more audio mute channels (use the `custom` action with shortcut name `input4_mute`, `ddr1_mute`, etc.)
- Add DDR play/stop controls using the `ddr_play` / `ddr_stop` module actions
- Add more source buttons if your TriCaster has inputs beyond IN4

---

## Troubleshooting

**Buttons do nothing after import**
→ You haven't replaced `TRICASTER_INSTANCE_ID`. See Step 4.

**Program/Preview buttons don't switch sources**
→ Source names may differ in your session. See Step 5.

**Tally feedback not showing**
→ Confirm the TriCaster connection is showing **OK** in Companion → Connections. The module polls the TriCaster for tally state — if the connection is down, feedback won't update.

**RECORD/STREAM button is out of sync**
→ Press the button twice to cycle back to the correct step. This happens if recording/streaming was started or stopped outside of Companion.

**DSK feedback not working**
→ Confirm the `dskOnAir` feedback `target` value matches your TriCaster's DSK shortcut names (`main_dsk1`, `main_dsk2`). These are standard and should work on Mini S.
