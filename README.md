# Universal Custom Kernel Guide for Windows Subsystem for Android (WSA)

Tài liệu hướng dẫn toàn diện (Universal) về cách cài đặt, thay thế và tự build Custom Kernel (**KernelSU, KernelSU-Next, Built-in SuSFS**) cho **mọi phiên bản WSA** (Kernel 5.10 và Kernel 5.15) trên cả 2 kiến trúc **x86_64** và **ARM64**.

---

## 1. Bảng đối chiếu các phiên bản WSA & Kernel

Trước khi thay kernel, bạn cần kiểm tra máy ảo WSA trên máy bạn thuộc thế hệ nào:

```powershell
adb connect 127.0.0.1:58526
adb shell uname -r
adb shell uname -m
```

| Thế hệ WSA | Android Version | Linux Kernel | Cấu hình nguồn Microsoft | File nhị phân đích |
| :--- | :--- | :--- | :--- | :--- |
| **WSA 2211 – 2407** *(Phổ biến nhất)* | **Android 13** | **5.15.x** (`android-lts/latte-2/5.15.104.4`) | `configs/wsa/config-wsa-x64` | `Tools/kernel` |
| **WSA 2204 – 2206** | **Android 12.1 / 12L** | **5.10.x** (`android-lts/latte/5.10.136.2`) | `configs/wsa/config-wsa-5.10` | `Tools/kernel` |
| **WSA 2110 – 2203** | **Android 11** | **5.10.x** (`android-lts/latte/5.10.117.x`) | `configs/wsa/config-wsa-5.10` | `Tools/kernel` |

* **Kiến trúc:**
  * **x86_64** (Intel / AMD): Kernel compile ra là file `bzImage`.
  * **ARM64** (Windows on ARM / Qualcomm Snapdragon): Kernel compile ra là file `Image`.

---

## 2. Tìm thư mục cài đặt WSA trên máy của bạn

Tùy vào phương pháp bạn cài đặt WSA, vị trí file `kernel` sẽ nằm ở một trong hai nơi:

### Dạng 1: Bản giải nén (Unbundled / WSABuilds / MagiskOnWSA)
* Thư mục là nơi bạn đã giải nén (ví dụ: `C:\WSA`, `D:\WSA_2407...`).
* File kernel nằm tại: `<Thư_mục_WSA>\Tools\kernel`.

### Dạng 2: Bản cài qua Microsoft Store hoặc MSIX Bundle
Chạy lệnh PowerShell sau để lấy chính xác đường dẫn thư mục cài đặt:
```powershell
(Get-AppxPackage -Name "*WindowsSubsystemForAndroid*").InstallLocation
```

---

## 3. Cách 1: Thay Kernel tự động bằng PowerShell Script (1-Click)

Chạy script sau trong PowerShell dưới quyền **Administrator**:

```powershell
# 1. Điền đường dẫn file kernel bạn vừa tải về từ GitHub Release
$NewKernelPath = "C:\path\to\kernel"   # <-- Sửa đường dẫn này

# 2. Tự động xác định thư mục WSA
$WsaApp = Get-AppxPackage -Name "*WindowsSubsystemForAndroid*"
if ($WsaApp) {
    $WsaDir = $WsaApp.InstallLocation
} else {
    $WsaDir = "C:\WSA_2407.40000.4.0_x64"   # <-- Điền thư mục giải nén nếu dùng Unbundled
}

$KernelTarget = Join-Path $WsaDir "Tools\kernel"
$KernelBackup = Join-Path $WsaDir "Tools\kernel.bak"

Write-Host "[+] WSA Directory: $WsaDir" -ForegroundColor Cyan
Write-Host "[+] Kernel Target: $KernelTarget" -ForegroundColor Cyan

# 3. Tắt sạch hoàn toàn WSA
Write-Host "[*] Đang tắt WSA..." -ForegroundColor Yellow
$WsaClient = Join-Path $WsaDir "WsaClient.exe"
if (Test-Path $WsaClient) {
    & $WsaClient /shutdown
}
taskkill /f /im WsaClient.exe 2>$null
taskkill /f /im WsaService.exe 2>$null
Start-Sleep -Seconds 3

# 4. Sao lưu bản cũ nếu chưa có
if (-not (Test-Path $KernelBackup)) {
    Write-Host "[+] Tạo bản sao lưu kernel.bak..." -ForegroundColor Green
    Copy-Item $KernelTarget $KernelBackup -Force
}

# 5. Thay kernel mới
Write-Host "[+] Cài đặt kernel mới..." -ForegroundColor Green
Copy-Item $NewKernelPath $KernelTarget -Force

Write-Host "[✓] Hoàn tất! Hãy mở lại WSA để trải nghiệm." -ForegroundColor Green
```

---

## 4. Cách 2: Thay Kernel thủ công từng bước

1. **Đổi tên:** Đổi tên file kernel bạn vừa tải về từ tab **Releases** thành tên là **`kernel`** (không có đuôi file).
2. **Tắt WSA:** Vào **WSA Settings** > **System** > chọn **Turn off** (hoặc chạy lệnh `WsaClient.exe /shutdown`).
3. **Sao lưu:** Vào `<Thư_mục_WSA>\Tools\`, copy file `kernel` thành `kernel.bak`.
4. **Dán đè:** Copy file `kernel` mới vào `<Thư_mục_WSA>\Tools\kernel`.
5. **Khởi động:** Mở lại WSA Settings hoặc bất kỳ ứng dụng Android nào.

---

## 5. Cài đặt Manager APK & Kiểm tra quyền Root / SuSFS

Tùy vào bản Kernel bạn chọn sử dụng trong tab **Releases**:

* **Nếu dùng bản `kernel-5.15-susfs` (Built-in SuSFS):**
  * Tích hợp sẵn mã nguồn SuSFS v2.4.0 in-tree trong nhân Linux.
  * Cài đặt **KernelSU Manager** hoặc **KernelSU-Next Manager**:
    ```powershell
    adb install KernelSU_Manager.apk
    ```
  * Mở app Manager: Trạng thái sẽ báo **Đang hoạt động (Built-in)** và hiển thị phiên bản **SuSFS: v2.4.0**.
  * Chạy lệnh kiểm tra:
    ```powershell
    adb shell su -c id
    ```
    Kết quả trả về `uid=0(root) gid=0(root)` là hệ thống đã hoạt động hoàn hảo.

* **Nếu dùng bản `kernel-5.15-ksunext` (KernelSU-Next v3.4.2):**
  * Cài đặt [KernelSU-Next Manager APK](https://github.com/KernelSU-Next/KernelSU-Next/releases).
  * Mở app, trạng thái báo **Đang hoạt động (BUILT-IN (GKI2))**.

---

## 6. Khôi phục nhanh (Rollback)

Nếu kernel mới gặp lỗi không tương thích:
```powershell
taskkill /f /im WsaClient.exe 2>$null
Move-Item -Force "<Thư_mục_WSA>\Tools\kernel.bak" "<Thư_mục_WSA>\Tools\kernel"
```
Mở lại WSA, hệ thống sẽ khôi phục lại trạng thái ban đầu ngay lập tức.
