# Installing body mods with AltUI

This is a step-by-step guide for getting other bodies for Jodi into the **Body Shape** tab of AltUI, where they show up as chips next to "Standard" and can be switched at any time. It covers where body mods come from, how to convert them with `bodypak.pyz`, where the files go, and what to do when something does not work. There is a complete walk-through for Windows and one for Linux.

## 1. Why a conversion is needed

Every body mod for *The Killing Antidote* – whether it comes from Nexus Mods or the Steam Workshop – is a *replacer*: its pak contains a file that sits at the same path as the game's own body, `Project/Character/Jodi/Body/Female`. The engine maps a path to exactly one pak, so with two body mods installed one of them silently wins, and nothing – no mod, no menu – can switch between them while the game runs.

`bodypak.pyz` rewrites such a pak into a regular TKA mod pak named `Body_<Name>.pak`. Inside, the mesh lives under its own path (`/Game/Mod/Body_<Name>/Female`) instead of the game's, and a small mod table is added so the game lists the pak like any other mod. AltUI reads that list, shows one chip per `Body_*` mod and loads the chosen mesh onto Jodi. Any number of converted bodies can be installed side by side.

The mesh itself is copied byte for byte, so the result is exactly the body the modder made. Anything the mesh needs from the same pak (materials, or an animation blueprint that shapes the body by scaling bones) travels with it. Files the mesh does *not* use – typically skin textures shipped in the same pak – are left out; the converter tells you when that happens.

## 2. What you need

| | |
|---|---|
| **AltUI** installed and working | `AltUI.pak` in `TheKillingAntidote/Mods/`, `AltUI_Hook_P.pak` in `TheKillingAntidote/Content/Paks/~mods/`, and **B** opens the panel in a level. See the [README](README.md#installation). |
| **`bodypak.pyz`** | From the [latest release](../../releases/latest) (also inside `AltUI-<version>.zip`). Use **1.3.1 or newer** – older versions drop the animation blueprint some bodies rely on (section 8). Put the file anywhere, e.g. your Downloads folder. |
| **Python 3.8 or newer** | Nothing else: no packages, no Unreal tools. Windows: [python.org](https://www.python.org/downloads/windows/) installer, tick **"Add python.exe to PATH"**. Linux: `python3` from your distribution (almost always already there). |
| **The body mod's `.pak` file** | Section 3. |
| **A terminal** | `bodypak.pyz` takes its arguments on the command line. Double-clicking it does nothing useful – a window flashes and closes. Windows: PowerShell or Command Prompt. Linux: any terminal. |

Check Python first:

```
python --version        # Windows
python3 --version       # Linux
```

Anything from `Python 3.8.0` upwards is fine. On Windows, if `python` opens the Microsoft Store instead of printing a version, Python is not installed yet (or not on PATH) – install it from python.org and open a *new* terminal afterwards. `py --version` is a second way to reach Python on Windows if the installer put the *py launcher* in.

## 3. Getting the body mod's `.pak`

You need the mod's `.pak` file on disk.

**Nexus Mods.** Download the mod's archive ("Manual download" is enough). Extract it; inside is one `.pak` file, sometimes in a subfolder, sometimes with a `_P` suffix (`Something_P.pak`). That file is the input. Do not copy it into the game yet.

**Steam Workshop.** Subscribe to the body mod and start Steam once so it downloads. Subscribed items are stored outside the game folder:

| | |
|---|---|
| Windows | `C:\Program Files (x86)\Steam\steamapps\workshop\content\2254890\<item id>\` |
| Linux | `~/.local/share/Steam/steamapps/workshop/content/2254890/<item id>/` |

`2254890` is the game's Steam app id; `<item id>` is the number at the end of the Workshop page's URL (`…/filedetails/?id=1234567890` → folder `1234567890`). If your Steam library is on another drive, `steamapps` is under that library folder instead. Inside the item folder is the `.pak`.

Two things to know about Workshop bodies:

* The game loads subscribed Workshop paks directly, so while you stay subscribed the original replacer stays active and AltUI shows that body under the **Standard** chip. You can leave it that way – the converted copy on its own chip is the same body, and the other chips work on top of it – or unsubscribe if you want the vanilla body back under Standard.
* If you do unsubscribe: **convert first.** Unsubscribing makes Steam delete the item folder, and with it the `.pak` you need as input.

## 4. Converting

The command is the same on every platform; only the Python command name and the path style differ:

```
python  bodypak.pyz <Original.pak> [--name Body_<Name>] [--title "Display name"] [--out <folder>] [--force]     (Windows)
python3 bodypak.pyz <Original.pak> [--name Body_<Name>] [--title "Display name"] [--out <folder>] [--force]     (Linux)
```

| Option | Meaning | Default |
|---|---|---|
| `<Original.pak>` | The body mod's pak (section 3). Quote the path if it contains spaces. | required |
| `--name Body_<Name>` | File name of the converted pak and its internal mod name. Must start with `Body_` and may contain only letters, digits and `_` (`Body_[A-Za-z0-9_]+`). No spaces, no hyphens, no dots. | Taken from the input file name: every character that is not a letter, digit or `_` becomes `_`, and `Body_` is put in front. `Curvy-Body-v1.2_P.pak` → `Body_Curvy_Body_v1_2_P`. |
| `--title "…"` | The text on the chip in the Body Shape tab and in the game's "Installed DLC" list. Any text, spaces allowed. | The name without `Body_`. |
| `--out <folder>` | Where to write the result. Created if it does not exist. | Next to the input pak. |
| `--force` | Overwrite an existing `Body_<Name>.pak`. | Without it the converter stops if the target exists. |

Choose a short `--name` and a readable `--title`; the default name is derived from the file name and is rarely what you want to read on a chip.

The converter writes two files into the output folder:

* `Body_<Name>.pak` – the converted mod, ready to copy into the game.
* `Body_<Name>_convert.json` – a log: source path and checksum, pak version, the list of files in the new pak, which companion assets were taken, which files were left out, and the verification result (`"status": "ok"`). Not needed by the game; keep it or delete it. If you ever report a problem, attach it.

### Reading the output

A plain body (mesh only):

```
Body_Curvy.pak (1761307 bytes, Female.uasset, Female.uexp, TKA_Mod_Table.uasset, TKA_Mod_Table.uexp) -> copy to <game>/TheKillingAntidote/Mods/
```

A body that ships an animation blueprint the mesh depends on – the converter finds it and takes it along, rewritten to the new path:

```
Body_Slim.pak (833601 bytes, Female.uasset, Female.uexp, Project/Character/Jodi/Body/ABP_Slim.uasset, Project/Character/Jodi/Body/ABP_Slim.uexp, TKA_Mod_Table.uasset, TKA_Mod_Table.uexp) -> copy to <game>/TheKillingAntidote/Mods/
companion asset used by the mesh: /Game/Project/Character/Jodi/Body/ABP_Slim -> /Game/Mod/Body_Slim/Project/Character/Jodi/Body/ABP_Slim
```

A pak that also contains files the mesh does not use – here a skin texture and eyelashes. They are not part of the body and are left out; the line is informational:

```
Body_Example.pak (1981917 bytes, Female.uasset, Female.uexp, TKA_Mod_Table.uasset, TKA_Mod_Table.uexp) -> copy to <game>/TheKillingAntidote/Mods/
not used by the mesh, left out: Jodi/Body/Skin/Skin_Tan.uasset, Jodi/Body/Skin/Skin_Tan.ubulk, Jodi/Body/Skin/Skin_Tan.uexp, Makeup/Eyelashes_Long.uasset, Makeup/Eyelashes_Long.ubulk, Makeup/Eyelashes_Long.uexp
```

If you want those extras (a skin that comes with the body, say), keep the original pak installed as well – it then also acts as the "Standard" body (section 5) – or look for the skin as a separate mod.

Before it finishes, the converter reads the new pak back and compares every byte with what it meant to write. If that check fails it says `verify failed: …` and exits with an error; a pak that prints the `-> copy to` line has passed.

## 5. Installing the converted pak

1. Copy `Body_<Name>.pak` into `TheKillingAntidote/Mods/` – the same folder `AltUI.pak` is in. (`Content/Paks/~mods/` works as well, but keep bodies in `Mods/` so they are easy to find.) Do **not** rename the file: the game derives the mod's name from the file name, and AltUI only picks up paks whose name starts with `Body_`.
2. Decide what **Standard** should be. As long as the *original* replacer pak is still installed – in `Mods/`, in `Content/Paks/~mods/`, or as a Workshop subscription – it keeps replacing the game's body, and AltUI shows it as **Standard** while the converted copy sits on its own chip. That is fine if you never want the vanilla body; if you do, remove the original from `Mods/` / `~mods/` (or unsubscribe).

   If that is what you want – one body as the permanent default and others to switch to – leave one replacer in `Content/Paks/~mods/` on purpose. It becomes **Standard**; the chips still work on top of it.
3. Start the game. In the **main menu**, the "Installed DLC" list now contains an entry with the title you chose. That is the game itself confirming the pak was mounted and the mod table read; if it is missing there, AltUI cannot see it either (section 8).
4. Load a level, press **B**, open **Body Shape**. Above the sliders is a row of chips: **Standard** plus one chip per installed `Body_*` pak.

Repeat for every body you want. Each needs its own `--name`.

## 6. In the game

* **Clicking a chip** swaps Jodi's mesh immediately. Skin, makeup, eyes and worn clothes are re-applied on the new body; the breast / waist sliders keep working (every known body mod keeps the game's morph targets).
* **Standard** is whatever the game loads on its own – the vanilla body, or a replacer you deliberately left in `~mods/`.
* The choice is **remembered** (in `Saved/SaveGames/AltUI.sav`, AltUI's own save – nothing is written into the game's saves) and re-applied about a second after every level load.
* **Looks** store the body together with clothes, hair, makeup and sliders, so applying a look also switches the body.
* If the saved body's pak is no longer installed, a short notice **"Body mod not found: Body_<Name>"** appears once after loading and the standard body is used. The setting is kept – put the pak back and the body returns – or click another chip to change it.
* Without AltUI the converted paks are harmless but do nothing: the mesh sits under a path the game never loads. They are not a replacement for the original replacer if you uninstall AltUI.

## 7. Walk-throughs

### 7a. Windows – a Nexus body

Example: a body from Nexus Mods whose archive contains `SlimBody_P.pak`; we call it "Slim". This one is a body whose shape comes from an animation blueprint in the pak, so the converter's `companion asset` line shows up.

Assumptions: Steam in its default location, `bodypak.pyz` and the downloaded mod archive in `Downloads`. Adjust the paths if yours differ – **Steam → right-click the game → Manage → Browse local files** opens the game folder; `TheKillingAntidote\Mods\` is one level below it.

1. **Extract the mod archive** (right-click → Extract All). You get `SlimBody_P.pak`.

2. **Open PowerShell** in `Downloads`: open the folder in Explorer, click into the address bar, type `powershell`, press Enter. Or press Win+R, type `powershell`, then `cd "$env:USERPROFILE\Downloads"`.

3. **Check Python:**

   ```powershell
   python --version
   ```

   `Python 3.12.x` (or any 3.8+) – good. If the Microsoft Store opens or the command is not found, install Python from python.org with "Add python.exe to PATH" ticked, close PowerShell and open it again.

4. **Convert.** Windows' "Extract All" normally unpacks into a new subfolder named after the archive, so the pak is at `Downloads\<archive name>\SlimBody_P.pak`, not in `Downloads` itself. The command below assumes you moved the pak up into `Downloads`; otherwise write the subfolder into the path, in quotes if it contains spaces: `".\Slim Body-1-0\SlimBody_P.pak"`.

   ```powershell
   python .\bodypak.pyz .\SlimBody_P.pak --name Body_Slim --title "Slim"
   ```

   Expected output (without `--out`, the result goes next to the input):

   ```
   C:\Users\you\Downloads\Body_Slim.pak (833601 bytes, Female.uasset, Female.uexp, Project/Character/Jodi/Body/ABP_Slim.uasset, Project/Character/Jodi/Body/ABP_Slim.uexp, TKA_Mod_Table.uasset, TKA_Mod_Table.uexp) -> copy to <game>/TheKillingAntidote/Mods/
   companion asset used by the mesh: /Game/Project/Character/Jodi/Body/ABP_Slim -> /Game/Mod/Body_Slim/Project/Character/Jodi/Body/ABP_Slim
   ```

   `Downloads` now contains `Body_Slim.pak` and `Body_Slim_convert.json`.

5. **Copy the pak into the game:**

   ```powershell
   Copy-Item .\Body_Slim.pak "C:\Program Files (x86)\Steam\steamapps\common\TheKillingAntidote\TheKillingAntidote\Mods\"
   ```

   If PowerShell reports "Access denied", do the copy in Explorer instead – Windows then asks for administrator permission once.

6. **Decide about the original.** If you had put `SlimBody_P.pak` into `Mods\` or `Content\Paks\~mods\` earlier, it stays the Standard body as long as it is there; delete it from there if you want the vanilla body under Standard. The copy in `Downloads` can stay either way.

7. **Start the game.** Main menu → "Installed DLC" lists *Slim*. In a level: **B** → **Body Shape** → chip **Slim**. Click it.

### 7b. Linux – a Steam Workshop body

Example: a body from the Steam Workshop, item id `1234567890` (yours will differ – take it from the Workshop page's URL), file `CurvyBody_P.pak`; we call it "Curvy". The game runs through Proton, but the converter is plain Python and runs natively.

Assumptions: Steam installed as a regular package (paths below); `bodypak.pyz` in `~/Downloads`. If Steam is the **Flatpak**, put `~/.var/app/com.valvesoftware.Steam/.local/share/Steam/` wherever `~/.local/share/Steam/` appears. `~/.steam/steam/` is a symlink to the same place on most systems and works too. If your library is on another drive, replace `~/.local/share/Steam/steamapps` with `<that library>/steamapps`.

1. **Subscribe** to the mod on the Workshop and let Steam download it. Check that the pak is there:

   ```bash
   ls ~/.local/share/Steam/steamapps/workshop/content/2254890/1234567890/
   ```

   → `CurvyBody_P.pak`

2. **Check Python:**

   ```bash
   python3 --version
   ```

3. **Convert** into a folder of your own, so the result is not mixed into Steam's Workshop directory:

   ```bash
   mkdir -p ~/tka-bodies
   python3 ~/Downloads/bodypak.pyz \
       ~/.local/share/Steam/steamapps/workshop/content/2254890/1234567890/CurvyBody_P.pak \
       --name Body_Curvy --title "Curvy" --out ~/tka-bodies
   ```

   Expected output:

   ```
   /home/you/tka-bodies/Body_Curvy.pak (3444372 bytes, Female.uasset, Female.uexp, TKA_Mod_Table.uasset, TKA_Mod_Table.uexp) -> copy to <game>/TheKillingAntidote/Mods/
   ```

   (Some paks are an older pak version stored with zlib; the converter unpacks those and stores the mesh uncompressed, so the result can be larger than the input. Newer paks are copied block for block.)

4. **Copy into the game:**

   ```bash
   cp ~/tka-bodies/Body_Curvy.pak ~/.local/share/Steam/steamapps/common/TheKillingAntidote/TheKillingAntidote/Mods/
   ```

5. **Decide about the subscription.** While you stay subscribed, the original replacer is still loaded and "Standard" shows this same body – the other chips work on top of it, so nothing is broken. If you want the vanilla body under Standard, unsubscribe now – not before step 3, since Steam deletes the folder.

6. **Start the game.** Main menu → "Installed DLC" lists *Curvy*. In a level: **B** → **Body Shape** → chip **Curvy**.

### 7c. Several bodies

Just repeat with a different `--name` each time. On Linux, for example:

```bash
python3 ~/Downloads/bodypak.pyz ~/mods/SlimBody_P.pak   --name Body_Slim   --title "Slim"   --out ~/tka-bodies
python3 ~/Downloads/bodypak.pyz ~/mods/CurvyBody_P.pak  --name Body_Curvy  --title "Curvy"  --out ~/tka-bodies
python3 ~/Downloads/bodypak.pyz ~/mods/AthleticBody.pak --name Body_Athletic --title "Athletic" --out ~/tka-bodies
cp ~/tka-bodies/Body_*.pak ~/.local/share/Steam/steamapps/common/TheKillingAntidote/TheKillingAntidote/Mods/
```

The Body Shape tab then shows **Standard**, **Slim**, **Curvy**, **Athletic** (plus whatever else you converted).

## 8. When the modder updates the body, when you update the converter, and removing

* **New version of a body mod:** download it, run the same command with `--force`, replace the pak in `Mods/`. The name stays the same, so your saved choice and looks keep pointing at it.
* **New `bodypak.pyz`:** only re-convert when the changelog says so. 1.3.1 is such a case: bodies whose shape comes from their own animation blueprint were converted without it by 1.3.0 and older, and looked like the standard body in the game. Re-run the same command with `--force` and replace the pak.
* **Removing a body:** delete `Body_<Name>.pak` from `Mods/`. If it was the selected one, the game shows "Body mod not found: Body_<Name>" once and uses Standard; pick another chip.

## 9. Troubleshooting

### Converter messages

| Message | Meaning / what to do |
|---|---|
| `no body mesh (…/Project/Character/Jodi/Body/Female.uasset) in this pak` | The pak is not a body replacer (a clothing, skin or map mod, or a body mod that works differently). Nothing to convert. |
| `invalid name (allowed: Body_[A-Za-z0-9_]+): …` | `--name` contains a space, hyphen, dot or other character, or does not start with `Body_`. Use letters, digits and `_` only – put the pretty text into `--title`. |
| `target already exists (--force to overwrite): …` | A `Body_<Name>.pak` is already in the output folder. Add `--force`, or pick another `--name` / `--out`. |
| `encrypted entries are not supported: …` | The pak is encrypted. Mod paks normally are not; ask the modder. |
| `Oodle: unsupported Oodle codec …` | The pak was compressed with an Oodle codec other than Kraken (Mermaid, Leviathan …). Every TKA mod pak seen so far is Kraken; please open an issue with the name of the mod. |
| `verify failed: …` | The written pak did not read back correctly. Please open an issue with the `Body_<Name>_convert.json` and the name of the mod. |
| `python: command not found` / the Store opens / `'python' is not recognized` | Python is not installed or not on PATH (section 2). On Windows try `py` instead of `python`; on Linux the command is `python3`. |
| `can't open file '…bodypak.pyz'` | The path to `bodypak.pyz` is wrong for the folder you are in. Use `.\bodypak.pyz` when it is in the current folder, or its full path. |

### In the game

**The main menu's "Installed DLC" does not list the body.** The game has not mounted the pak or could not find its table. Check: the file is in `TheKillingAntidote/Mods/` (the folder next to `Content`, not inside it); the file is still named exactly `Body_<Name>.pak` as printed by the converter – the game looks for the table under a path derived from the file name, and the same name is stored inside the pak, so a renamed file is silently skipped; the converter's output ended with the `-> copy to` line. Restart the game – paks are only mounted at start.

**The chip is there, but clicking it shows the standard body – or hardly any change.** Almost always a body that keeps its shape in an animation blueprint, converted with `bodypak.pyz` 1.3.0 or older (the converter only took the mesh). Re-convert with 1.3.1 or newer: the output must show a `companion asset used by the mesh: … ABP …` line. If it does not and the body still looks standard, the shape comes from something outside the pak and the mod cannot be switched this way – report it.

**Two chips show the same body / "Standard" is not the vanilla body.** The original replacer is still installed – in `Mods/`, in `Content/Paks/~mods/`, or as a Workshop subscription (section 5, step 2).

**"Body mod not found: Body_<Name>" after loading.** The saved body's pak is gone from `Mods/`. Put it back or select another chip.

**The body is right but the skin looks wrong.** The mod shipped its own skin texture next to the mesh, and the converter left it out (it is not part of the body – the "left out" line in the output lists it). Keep the original pak installed as the Standard body, or install the skin as a separate mod.

## 10. What is inside a converted pak

For the curious. `Body_<Name>.pak` is an unencrypted pak in the format of the game's own UnrealPak (version 11) with the mount point `…/TheKillingAntidote/Content/Mod/Body_<Name>/` and these files:

| File | Content |
|---|---|
| `Female.uasset`, `Female.uexp` (+ `Female.ubulk` if the source has one) | The body mesh, copied byte for byte from the original. Only the pak-level metadata around it is new. |
| `<path>/<Asset>.uasset` + `.uexp` for each companion | Assets the mesh imports from the same pak (its animation blueprint, materials). Copied as they are; the mesh's import table is pointed at the new location. |
| `TKA_Mod_Table.uasset`, `.uexp` | The mod table the game reads at start: one row named `Body_<Name>`, caption = your `--title`, description = "Body mod, converted from `<original file>`". |

Supported input: pak versions 3–11, uncompressed, zlib or Oodle. Oodle-compressed data is passed through unchanged; the built-in Oodle decoder (pure Python, ported from [ooz](https://github.com/powzix/ooz), GPL-3) is only used to *read* the mesh's import table so companion assets can be found.
