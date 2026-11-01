# Android Physical Device Testing & USB Debugging Guide

This guide provides step-by-step instructions for testing the **Smart Invoice Processor Flutter mobile application** on a real physical Android phone connected to your Windows laptop via USB.

---

## 1. Architecture & Networking Overview

The Smart Invoice Processor mobile app communicates with the shared **FastAPI backend** running locally on your laptop:

```
+-----------------------------------------------------------+
|                   Physical Android Phone                  |
|                                                           |
|  +-----------------------------------------------------+  |
|  |     Smart Invoice Flutter App (Material 3)          |  |
|  +-----------------------------------------------------+  |
|                           |                               |
|                  http://127.0.0.1:8000                    |
+---------------------------|-------------------------------+
                            |
                     USB CABLE (ADB)
          adb reverse tcp:8000 tcp:8000
                            |
+---------------------------|-------------------------------+
|                    Windows Laptop                         |
|                                                           |
|  +-----------------------------------------------------+  |
|  |     FastAPI Backend (api.main:app on port 8000)     |  |
|  +-----------------------------------------------------+  |
|        |                |                 |               |
|  SQLite Database   ChromaDB Vectors   Google Gemini API   |
+-----------------------------------------------------------+
```

By leveraging **ADB Reverse Port Forwarding**, requests from the phone to `127.0.0.1:8000` are seamlessly routed over the USB cable directly to port 8000 on your laptop. No special Wi-Fi configuration or complex router setup is required!

---

## 2. Prerequisites

1. **Android Phone:** Running Android 7.0 (API level 24) or newer.
2. **USB Cable:** Data-capable USB cable (must transfer data, not charge-only).
3. **Android Platform Tools (ADB):** Installed with Android SDK or standalone from Google.
4. **Flutter SDK:** Flutter 3.19+ installed and on system PATH.

---

## 3. Physical Android Phone Preparation

### Step 3.1: Enable Developer Options
1. On your Android phone, open **Settings**.
2. Scroll to the bottom and select **About phone**.
3. Tap **Build number** rapidly **7 times** until you see the prompt: *"You are now a developer!"*.
4. Enter your lock-screen PIN or password if prompted.

### Step 3.2: Enable USB Debugging
1. In **Settings**, go to **System** -> **Developer options** (or search "Developer options").
2. Scroll down to the **Debugging** section.
3. Toggle on **USB debugging**.
4. *(Optional but recommended)*: Enable **Stay awake** (screen will never sleep while charging).

### Step 3.3: Connect Phone to Laptop via USB
1. Plug your phone into your Windows laptop using the USB cable.
2. On your phone, swipe down the notification shade and ensure USB mode is set to **File Transfer** (MTP) rather than "Charging only".
3. A popup prompt will appear on your phone:
   > **"Allow USB debugging?"**
   > *The computer's RSA key fingerprint is: ...*
4. Check the box **"Always allow from this computer"** and tap **Allow**.

### Step 3.4: Verify ADB Connection
Open PowerShell or Command Prompt on your laptop and run:

```powershell
adb devices
```

Expected output:
```
List of devices attached
RFCW81XYZ123    device
```

If the status says `unauthorized`, unlock your phone and accept the RSA prompt. If empty, check your USB cable or reinstall the Google USB Driver from Android Studio SDK Manager.

---

## 4. Setup Port Forwarding (USB Reverse Tunnel)

With your phone connected, run the following command to forward phone port `8000` to laptop port `8000`:

```powershell
# Forward FastAPI backend port
adb reverse tcp:8000 tcp:8000

# (Optional) Forward Vite React dev server port for mobile browser testing
adb reverse tcp:5173 tcp:5173
```

To verify the active reverse tunnels:
```powershell
adb reverse --list
```
Output:
```
(reverse) tcp:8000 tcp:8000
(reverse) tcp:5173 tcp:5173
```

---

## 5. Step-by-Step Running Guide

### Step 5.1: Start the FastAPI Backend
In your project root (`C:\gitrepo\p1`), start the FastAPI server:

```powershell
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

Verify in your laptop browser by visiting:
- [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) (Swagger UI)
- [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health) (JSON Health Status)

### Step 5.2: Launch the Flutter App on Phone
Open a second terminal window, navigate to `mobile_flutter`, and run:

```powershell
cd C:\gitrepo\p1\mobile_flutter

# Get dependencies
flutter pub get

# Run on your connected Android phone
flutter run -d <device-id> --dart-define=API_BASE_URL=http://127.0.0.1:8000/api
```

*(Tip: If only one physical phone is connected, you can simply run `flutter run`)*.

---

## 6. Alternative: Testing Over Local Wi-Fi (No USB Cable Required)

If you prefer testing wirelessly across your local home or office Wi-Fi network:

1. **Ensure Phone and Laptop are connected to the SAME Wi-Fi network.**
2. **Find your laptop's local LAN IP address:**
   ```powershell
   ipconfig
   ```
   Look for the `IPv4 Address` under your active Wi-Fi adapter (e.g., `192.168.1.45`).
3. **Allow port 8000 through Windows Firewall:**
   ```powershell
   New-NetFirewallRule -DisplayName "FastAPI Dev Server" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
   ```
4. **Launch the Flutter app specifying your laptop's Wi-Fi IP:**
   ```powershell
   flutter run --dart-define=API_BASE_URL=http://192.168.1.45:8000/api
   ```
   *(Alternatively, you can open the app on your phone, navigate to **Settings**, and type `http://192.168.1.45:8000/api` into the Backend URL field!)*

---

## 7. Alternative: Testing on Android Emulator

If you are running the Android Virtual Device (AVD) emulator:
- Android emulators run on an internal virtual network where `10.0.2.2` represents your laptop's `127.0.0.1`.
- Run with:
  ```powershell
  flutter run -d emulator --dart-define=API_BASE_URL=http://10.0.2.2:8000/api
  ```

---

## 8. Physical Device Test Checklist

Use this checklist to thoroughly test every feature on your physical phone:

| # | Test Case | Action | Expected Result | Pass/Fail |
|---|-----------|--------|-----------------|-----------|
| **1** | **Splash & Connectivity** | Launch mobile app | Green status indicator, connects to FastAPI and navigates to Dashboard | [ ] |
| **2** | **Executive Dashboard** | View KPI card | Total spending displayed in INR (₹), counts match verified invoices | [ ] |
| **3** | **Invoice Listing** | Tap "Invoices" tab | List of invoices displayed with vendor names, invoice numbers, and INR totals | [ ] |
| **4** | **Filter & Search** | Type vendor name in search bar | Real-time filtering reflects matching supplier records | [ ] |
| **5** | **Invoice Inspection** | Tap any invoice card | Detail view opens with metadata, confidence score, and itemized line items | [ ] |
| **6** | **Duplicate Resolution** | Inspect suspected duplicate | Banner displays warning; "Mark Genuine" or "Confirm Duplicate" updates state | [ ] |
| **7** | **Invoice PDF Upload** | Tap "Upload PDF" action | Phone native file picker opens; select a PDF; extraction runs and previews result | [ ] |
| **8** | **Ask AI Assistant** | Tap "Ask AI" tab | Tap suggestion chip (e.g. "What did we spend on AWS?"); Gemini responds with SQL totals & citations | [ ] |
| **9** | **Expense Analytics** | Tap "Analytics" tab | Interactive monthly bar chart renders; top supplier spend rankings displayed | [ ] |
| **10** | **Rate Mode Switch** | Toggle "Latest ECB Rates" | Aggregated spending recalculated dynamically based on live reference rates | [ ] |
| **11** | **RPA Folder Scan** | Go to Automation -> Scan | Triggers local folder monitor; displays count of new and duplicate files | [ ] |
| **12** | **Currency Preference** | Go to Settings -> Tap "USD" | Preferred currency updates to USD across all mobile screens | [ ] |

---

## 9. Troubleshooting & FAQ

### Issue: `DioException [connection error]: Connection refused`
- **Cause:** Port forwarding was not established or FastAPI is stopped.
- **Fix:**
  1. Confirm FastAPI is running: `uvicorn api.main:app --host 0.0.0.0 --port 8000`.
  2. Run: `adb reverse tcp:8000 tcp:8000`.
  3. Verify with: `adb reverse --list`.

### Issue: `CLEARTEXT_COMMUNICATION_NOT_PERMITTED`
- **Cause:** Android 9+ blocks unencrypted HTTP traffic by default.
- **Fix:** The app's `android/app/src/main/AndroidManifest.xml` and `src/debug/AndroidManifest.xml` have already been pre-configured with `android:usesCleartextTraffic="true"` to allow local debug traffic to `http://127.0.0.1:8000` and `http://10.0.2.2:8000`.

### Issue: `Device unauthorized`
- **Fix:** Disconnect the USB cable, reconnect it, unlock your phone screen, and tap "Always allow from this computer" on the RSA dialog.

### Issue: File picker returns null on Android
- **Cause:** Storage permission not granted.
- **Fix:** In phone Settings -> Apps -> Smart Invoice -> Permissions -> Allow Storage / Files access.

