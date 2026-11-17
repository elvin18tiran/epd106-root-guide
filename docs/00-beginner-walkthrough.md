# 00 — Beginner's Walkthrough (start here)

**This is the hand-holding version.** It assumes you have *never* used ADB, don't know what a
"partition" is, and just want to carefully follow steps. It explains the *why* behind each step so
you understand what you're doing. The other docs (01–06) are the terse reference — come here first.

Take your time. Read a whole section before typing anything. There is no rush.

---

## 0. Before you touch anything

**What you'll end up with:** a rooted, ad-free, de-bloated e-reader you fully control — custom
sleep screen, your own font, a custom boot animation, sharper e-ink text, and KOReader set up for
comfortable reading.

**What this is, in plain words:**
- **Rooting** = getting "administrator" access to your own device, so you can change things the
  manufacturer locked down.
- It does **not** require unlocking the bootloader on this reader (explained below), which is what
  makes it unusually safe.

**What you need:**
- The **Xiaomi MiReader / Moaan EPD106** (check: *Settings → About* shows model `EPD106`).
- A **Windows PC** (these steps are for Windows; Mac/Linux work too with equivalent commands).
- The **USB cable** that came with it.
- About **2–3 hours** the first time, unhurried.
- **Patience.** Read each step. Don't skip the backup.

### ⚠️ The three rules that keep you safe

1. **BACK UP FIRST** (Section 4). Never skip it.
2. **Patch YOUR OWN boot image** (Section 6), never someone else's — even from this guide. Different
   units have different kernels; a foreign boot image can cause a boot loop.
3. **NEVER touch the bootloader partition.** This reader's chip has *no low-level recovery* — a bad
   bootloader flash = a **permanently dead device** with no fix. Everything in this guide avoids the
   bootloader. If a tutorial anywhere tells you to flash the bootloader or "logo" to change the
   startup logo, **don't.**

> **Can this brick (break) my device?** The *rooting* steps here are recoverable — if a boot fails,
> Section 7 un-bricks it with your data intact (we actually did this during development). The only
> unrecoverable thing is the bootloader, which we never touch. Your books and files live in a
> separate area and are never at risk.

---

## 1. The concepts (2-minute read, worth it)

Your reader is a small Android computer. Its storage is split into **partitions** (think: labelled
drawers):

| Partition | What's inside | Do we touch it? |
|---|---|---|
| **boot** | the Linux kernel + a tiny startup filesystem | **Yes** — this is where root is installed |
| **system** | Android + the built-in apps | Only via "systemless" overlays (safe) |
| **recovery** | a minimal rescue mode | We *use* it to install things |
| **bootloader** | the very first code that runs | **NEVER** (no recovery if broken) |
| **data / UDISK** | your books, settings, everything personal | Never flashed; we only back it up |

- **ADB** ("Android Debug Bridge") is a program on your PC that lets you send commands to the reader
  over the USB cable. You type `adb something` in a terminal and the reader does it.
- **Recovery mode** is a separate mini-system you can boot into. It has an option *"Apply update
  from ADB"* that installs a `.zip` you send from the PC. **This is how we install root** — no
  bootloader unlock needed.
- **Magisk** is the tool that provides root. It works by putting a patched copy of the **boot**
  partition on the device.

**Why no bootloader unlock?** Normally you'd unlock the bootloader (which wipes the device) to
root. This reader's firmware is signed with Google's *public* test keys. Because the keys are
public, *you* can sign your own install `.zip` and recovery will accept it. So: no unlock, no wipe.
(If you try `fastboot oem unlock`, it just fails — that's expected and fine.)

---

## 2. Set up your PC (install the tools)

You'll install five things. Do them in order.

### 2a. ADB & Fastboot (the platform-tools)
1. Download **"SDK Platform-Tools for Windows"** from the official Android site
   (`developer.android.com/tools/releases/platform-tools`).
2. Unzip it to a simple folder, e.g. `C:\platform-tools`.
3. **Test it:** open **Command Prompt** (press Start, type `cmd`, Enter). Type:
   ```
   cd C:\platform-tools
   adb version
   ```
   You should see a version number. If you see *"'adb' is not recognized"*, you're not in the right
   folder — redo the `cd` line.

> **Tip:** run every `adb` command from inside `C:\platform-tools` (do the `cd C:\platform-tools`
> each time you open a new Command Prompt), so Windows can find `adb`.

### 2b. USB driver (so Windows sees the reader)
Most Windows 10/11 PCs recognise it automatically. If `adb devices` (later) shows nothing, install
the **"Google USB Driver"** (also on the Android developer site) or Xiaomi's USB driver.

### 2c. Java 8 runtime (for signing)
The signing tool needs **Java 8** specifically. Install the **JRE 8** (search "Adoptium Temurin 8
JRE" or Oracle JRE 8). You don't need to add it to PATH; just note where it installed, e.g.
`C:\Program Files\Java\jre1.8.0_xxx\bin\java.exe`.

### 2d. Python 3
Install from `python.org`. **Important:** on the first install screen, tick **"Add Python to
PATH."** Then test in Command Prompt: `python --version`.

### 2e. The device toolkit + Magisk
1. Download the toolkit: go to `github.com/delbertbeta/edp106`, click the green **Code** button →
   **Download ZIP**, and unzip it (e.g. to `C:\edp106`).
2. Download **Magisk v28.1**: `github.com/topjohnwu/Magisk/releases` → the `Magisk-v28.1.apk` file.
   Save it to `C:\platform-tools` (handy later).

---

## 3. Prepare the reader (enable debugging)

1. **Enable Developer Options.** On this reader, open the vendor **Settings → Device Settings →
   Developer Option** (it may already be visible). On stock Android you'd tap *Build number* seven
   times — here it's usually a menu item.
2. Inside Developer Options, turn on **USB debugging**.
3. **Plug the reader into the PC** with the USB cable. On the reader, if a box asks about USB mode,
   choose **"Transfer files"** (MTP).
4. In Command Prompt (in `C:\platform-tools`), type:
   ```
   adb devices
   ```
   The **first time**, the reader shows a popup *"Allow USB debugging?"* — tick **"Always allow"**
   and tap **OK**. Run `adb devices` again. You should see something like:
   ```
   List of devices attached
   1234ABCD5678   device
   ```
   If it says `unauthorized`, you missed the popup — unplug, replug, watch the reader, tap Allow.
   If it says nothing, it's the USB driver (2b) or cable.

**You're connected. Everything below is typed in this Command Prompt.**

---

## 4. BACK UP EVERYTHING (do not skip)

This copies your books, settings, and apps to the PC. It changes nothing on the reader.

Make a folder `C:\reader-backup`, then:
```
adb pull /sdcard/ C:\reader-backup\sdcard
```
That copies all your books and KOReader data. (If it errors on one weird filename and stops, that's
the "control character in a filename" problem — copy the other folders one at a time instead, e.g.
`adb pull "/sdcard/General Books" C:\reader-backup\sdcard\General_Books`.)

Save the list of installed apps and settings (so you can undo the debloat later):
```
adb shell pm list packages -u > C:\reader-backup\packages.txt
adb shell settings list secure > C:\reader-backup\settings-secure.txt
adb shell getprop > C:\reader-backup\props.txt
```

> Keep `C:\reader-backup` safe. This is your "undo button" for everything data-related.

---

## 5. A note on how we'll run multi-step commands

Some steps need several commands run **as root on the reader**. Typing them as one long line is
error-prone (a real gotcha: `adb shell su -c "a; b; c"` only runs `a` as root — the rest silently
fail). So instead, when a step says *"make a script"*, you'll:

1. Open **Notepad**, paste the script text, and **Save As** with the exact filename given, type
   **"All Files"**, and encoding **UTF-8**. Save it in `C:\platform-tools`.
2. Send it to the reader and run it:
   ```
   adb push C:\platform-tools\thescript.sh /data/local/tmp/thescript.sh
   adb shell su -c "sh /data/local/tmp/thescript.sh"
   ```

This avoids every quoting trap. (You won't need this until *after* root, in Section 8.)

---

## 6. Root it (the main event)

Four stages: **dump your boot → patch it → sign it → flash it.** Go slowly.

### Stage A — Dump YOUR boot image (read-only, safe)
This copies your reader's own boot partition to a file, so you patch *your* exact one.
```
adb reboot recovery
```
The reader reboots into recovery. **On the reader screen:** you'll see a menu (or a lying-down
Android robot — if so, hold **Power** and tap **Volume Up** once to show the menu). Select
**"Apply update from ADB."** The screen will say it's waiting for a sideload. Now on the PC:
```
adb sideload C:\edp106\root\toolkit\dump_kernel_to_system_signed.zip
```
When it finishes, on the reader select **"Reboot system now."** After it boots, pull the dumped
file to the PC:
```
adb pull /system/bimg.img C:\platform-tools\my-boot.img
```
`my-boot.img` is **your** stock boot. **Copy it somewhere safe** — it's your personal restore file.

### Stage B — Patch your boot with Magisk
1. Install the Magisk app you downloaded:
   ```
   adb install C:\platform-tools\Magisk-v28.1.apk
   ```
2. Copy your boot image onto the reader so the app can see it:
   ```
   adb push C:\platform-tools\my-boot.img /sdcard/Download/my-boot.img
   ```
3. **On the reader:** open the **Magisk** app → tap **Install** (next to "Magisk") → **Select and
   Patch a File** → browse to `Download/my-boot.img` → **Let's Go**. It creates a patched file in
   `Download/` named like `magisk_patched-28100_xxxxx.img`.
4. Pull that patched file to the PC (replace the name with the exact one it created):
   ```
   adb pull "/sdcard/Download/magisk_patched-28100_xxxxx.img" C:\platform-tools\patched.img
   ```

> If the Magisk app's on-screen patching is glitchy on e-ink, the toolkit also has a command-line
> patcher — see [docs/02-rooting.md](02-rooting.md) Stage 2. For most people the app is easier.

### Stage C — Build the two install zips (on the PC)
You'll make a **ROOT** zip (installs root) and a **RESTORE** zip (your safety net). The toolkit has
a helper; run it from Command Prompt (one line, adjust the Java path to yours):
```
cd C:\edp106\root
"C:\Program Files\Java\jre1.8.0_xxx\bin\java.exe" -jar toolkit\signapk-1.0.jar -w toolkit\testkey.x509.pem toolkit\testkey.pk8 <unsigned.zip> <signed.zip>
```
Building the unsigned zip (template + your boot) is a small Python step — the exact script is
`scripts/build-flash-zip.py` in this repo, with the command shown in
[docs/02-rooting.md](02-rooting.md) Stage 3. Make:
- **ROOT-install.zip** — using `patched.img`
- **RESTORE-stock.zip** — using `my-boot.img` (your safety net; build it *before* flashing)

**Check each zip** before flashing: open it, confirm the `boot.img` inside is the right one.

### Stage D — Flash root
With both zips built and `RESTORE-stock.zip` ready as your safety net:
```
adb reboot recovery
```
On the reader: **"Apply update from ADB."** Then on the PC:
```
adb sideload C:\edp106\root\work\ROOT-install.zip
```
On the reader: **"Reboot system now."**

- **If it boots to your home screen → you're rooted. 🎉** Continue to Stage E.
- **If it won't boot → go to Section 7.** Don't panic, don't factory reset.

### Stage E — Finish setup & grant root
1. Open the **Magisk** app. If it says *"Requires Additional Setup,"* tap **OK** — it reconfigures
   and reboots once. This is normal; root won't work until it's done.
2. Give the computer root access: in Command Prompt type `adb shell su -c "id"`. A **Superuser
   Request** popup appears on the reader — tap **Grant**. (If the popup won't accept the tap because
   of an on-screen overlay, open Magisk → **Superuser** tab and toggle **Shell** on instead.)
3. Verify: `adb shell su -c "id"` should print `uid=0(root) ...`. **Done — you have root.**

---

## 7. If a boot goes wrong (un-brick)

If after flashing root the reader shows **"Can't load Android system"** or just won't start:

**Do NOT tap "Factory reset."** Your data is fine. Use your safety net:
```
adb reboot recovery
```
On the reader: **"Apply update from ADB."** Then:
```
adb sideload C:\edp106\root\work\RESTORE-stock.zip
```
Reboot — the reader goes back to exactly how it was (root removed, data intact). Then you can try
the root steps again, carefully.

**Common problems:**
- *`adb` not recognised* → you're not in `C:\platform-tools`; `cd` there first.
- *device `unauthorized`* → unplug/replug, tap **Allow** on the reader.
- *device shows nothing* → USB driver or cable (Section 2b); try a different USB port.
- *copying a book over Windows Explorer dings but nothing appears* → that's flaky Windows MTP; use
  `adb push "C:\path\book.epub" "/sdcard/General Books/"` instead.

---

## 8. The fun part — the mods

You're rooted. These are optional and each is independent and removable. They're detailed in the
reference docs:

- **[05 — Debloat & KOReader](05-debloat-and-koreader.md):** remove bloatware (reversible), set up
  KOReader for Kindle-like reading, swap the keyboard, add a dictionary.
- **[04 — Custom sleep screen](04-sleep-screen.md):** replace the animal sleep images with your own
  "lost & found" screen and rotating artwork. (Read the ⚠️ about the method that *bricks* — use the
  safe overlay method only.)
- **[06 — Power tweaks](06-power-tweaks.md):** sharper e-ink text, Fast refresh mode, block vendor
  telemetry, swap the system font, and a custom boot animation.

Each tweak is its own Magisk module or overlay. To undo any one:
`adb shell su -c "rm -rf /data/adb/modules/<name>"` then reboot.

---

## 9. Safety rules recap

- ✅ You backed up first (Section 4).
- ✅ You patched **your own** boot image (Section 6), not a stranger's.
- ✅ You kept `my-boot.img` and `RESTORE-stock.zip` — your restore files.
- 🚫 You never touched the **bootloader** (the one unrecoverable partition).
- 🧘 When unsure, stop and re-read. Nothing here has to be rushed.

Welcome to owning your reader. Enjoy it.
