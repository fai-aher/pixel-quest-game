# Pixel Quest — Export Guide

## 🖥️ 1. macOS App (`.app` bundle — no `.exe` on Mac!)

**Tool: [PyInstaller](https://pyinstaller.org)**

```bash
# Install
pip3 install pyinstaller

# Build (run from the pixel_quest_week6 folder)
pyinstaller --onefile --windowed \
  --name "Pixel Quest" \
  --icon icon.png \
  --add-data "sprites:sprites" \
  --add-data "sounds:sounds" \
  main.py
```

Your app will be at `dist/Pixel Quest.app`. Double-click to run!

> **Note:** macOS uses `.app` bundles, not `.exe`. The `--windowed` flag hides the terminal. The `--icon` flag sets your custom icon (PyInstaller converts PNG to `.icns` automatically).

### If icon doesn't apply automatically:
```bash
# Convert PNG to icns manually
mkdir icon.iconset
sips -z 512 512 icon.png --out icon.iconset/icon_512x512.png
iconutil -c icns icon.iconset
# Then use: --icon icon.icns
```

---

## 🤖 2. Android APK (Priority)

**Tool: [Buildozer](https://buildozer.readthedocs.io)** (wraps python-for-android)

### Step 1: Install Buildozer
```bash
pip3 install buildozer cython
brew install autoconf automake libtool pkg-config

# Android SDK/NDK (Buildozer downloads these automatically on first build)
```

### Step 2: Initialize
```bash
cd "/Users/fai.ahertz/Desktop/lectures/Pixel Quest - The Jumping Hero/pixel_quest_week6"
buildozer init
```

### Step 3: Edit `buildozer.spec`
Change these key lines:
```ini
[app]
title = Pixel Quest
package.name = pixelquest
package.domain = com.yourname
source.dir = .
source.include_exts = py,png,mp3,wav,ogg
version = 1.0

# IMPORTANT: use SDL2 + pygame
requirements = python3,pygame,sdl2,sdl2_image,sdl2_mixer,sdl2_ttf

# Icon
icon.filename = icon.png

# Orientation
orientation = landscape

# Android permissions (none needed for this game)
android.permissions =

# Target modern Android
android.api = 33
android.minapi = 21
android.ndk = 25b
```

### Step 4: Build APK
```bash
buildozer -v android debug
```

First build takes ~20-30 min (downloads SDK/NDK). APK will be at:
`bin/pixelquest-1.0-arm64-v8a_armeabi-v7a-debug.apk`

### Step 5: Install on phone
```bash
# Via USB
buildozer android deploy

# Or transfer the APK file to your phone and install manually
# (Enable "Install from unknown sources" in Android settings)
```

### ⚠️ Important for Android:
- Touch controls needed! Add virtual buttons for left/right/jump. Or use:
  ```python
  # In your event loop, add touch support:
  if event.type == pygame.FINGERDOWN:
      # Left side tap = move left, right side = move right, etc.
  ```

---

## 🍎 3. iOS (more complex)

**Tool: [Kivy-ios](https://github.com/kivy/kivy-ios)** or **Buildozer**

```bash
pip3 install kivy-ios
toolchain build python3 pygame sdl2

# Create Xcode project
toolchain create "Pixel Quest" /path/to/pixel_quest_week6

# Open in Xcode, set signing team, build to device
```

> **Requirements:** macOS only, Xcode installed, Apple Developer account ($99/year for App Store, free for personal device testing).

---

## 📋 Quick Reference

| Platform | Tool | Command | Output |
|----------|------|---------|--------|
| **macOS** | PyInstaller | `pyinstaller --onefile --windowed ...` | `dist/Pixel Quest.app` |
| **Android** | Buildozer | `buildozer android debug` | `bin/*.apk` |
| **iOS** | kivy-ios | `toolchain create ...` | Xcode project |

## 🎨 Custom Icon

Your icon is saved as `icon.png` in the project folder. To customize:
- **macOS:** PyInstaller `--icon icon.png` (or `.icns`)
- **Android:** Set `icon.filename = icon.png` in `buildozer.spec`
- **iOS:** Add to Xcode Asset Catalog (requires multiple sizes: 29×29, 40×40, 60×60, 76×76, 83.5×83.5, 1024×1024)

## 🚀 Recommended: Start with macOS

The fastest path to share your game:
1. `pip3 install pyinstaller`
2. Run the PyInstaller command above
3. Share the `dist/Pixel Quest.app` with friends via AirDrop/zip

Then tackle Android when you're ready for the longer build process.
