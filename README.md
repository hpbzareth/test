# Hướng Dẫn Cài Đặt Custom Kernel Cho Mọi Phiên Bản WSA (Universal Guide)

Tài liệu này hướng dẫn chi tiết cách cài đặt hoặc thay thế Custom Kernel (KernelSU, KernelSU-Next, SuSFS, Kprobes...) cho **Windows Subsystem for Android (WSA)** áp dụng cho **mọi phiên bản WSA**, **mọi kiến trúc (x86_64 / ARM64)** và **mọi phương thức cài đặt** (Cài qua Windows Store, qua MSIX hoặc qua các bản giải nén Unbundled / WSABuilds / MagiskOnWSA).

---

## 1. Xác định phiên bản & Kiến trúc

Trước khi thay kernel, bạn cần biết WSA trên máy mình đang sử dụng kiến trúc và phiên bản kernel nào:

1. **Khởi động WSA** và mở PowerShell, chạy:
   ```powershell
   adb connect 127.0.0.1:58526
   adb shell uname -m
   adb shell uname -r
   ```
2. **Đối chiếu:**
   * **Kiến trúc (`uname -m`):**
     * `x86_64` (máy tính chip Intel / AMD): File kernel build ra là `bzImage`.
     * `aarch64` (máy tính Windows on ARM như Snapdragon): File kernel build ra là `Image`.
   * **Phiên bản Kernel (`uname -r`):**
     * `5.15.x`: Dành cho các bản WSA Android 13 (WSA v2211 trở lên, ví dụ 23xx, 24xx).
     * `5.10.x`: Dành cho các bản WSA Android 12.1 hoặc cũ hơn.

---

## 2. Tìm thư mục cài đặt WSA trên máy của bạn

Tùy vào cách bạn cài đặt WSA, đường dẫn sẽ rơi vào một trong hai dạng sau:

### Dạng 1: Cài đặt từ gói giải nén (Unbundled / WSABuilds / MagiskOnWSA)
* Thư mục là nơi bạn đã giải nén file ZIP lúc cài (ví dụ: `C:\WSA`, `D:\Android\WSA_2407...`).
* File kernel nằm tại: `<Thư_mục_WSA>\Tools\kernel`.

### Dạng 2: Cài đặt qua Store hoặc Add-AppxPackage (MSIX Bundle)
Chạy lệnh PowerShell sau để hệ thống tự in ra chính xác thư mục cài đặt WSA trên máy bạn:
```powershell
(Get-AppxPackage -Name "*WindowsSubsystemForAndroid*").InstallLocation
```
*(Đường dẫn thông thường: `C:\Program Files\WindowsApps\MicrosoftCorporationII.WindowsSubsystemForAndroid_<version>...`)*

---

## 3. Cách 1: Thay Kernel tự động bằng Script PowerShell (Khuyên dùng)

Lưu lại hoặc copy đoạn script sau vào PowerShell (chạy dưới quyền **Administrator**). Script sẽ **tự động dò tìm thư mục WSA, tắt tiến trình an toàn, sao lưu kernel cũ và chép kernel mới**:

```powershell
# 1. Nhập đường dẫn file bzImage / Image mới bạn vừa tải về
$NewKernelPath = "C:\path\to\bzImage"   # <-- SỬA ĐƯỜNG DẪN NÀY

# 2. Tự động xác định thư mục WSA
$WsaApp = Get-AppxPackage -Name "*WindowsSubsystemForAndroid*"
if ($WsaApp) {
    $WsaDir = $WsaApp.InstallLocation
} else {
    # Nếu không tìm thấy qua Appx, hãy chỉ định thư mục giải nén của bạn
    $WsaDir = "C:\WSA"   # <-- Thay đổi nếu bạn dùng bản giải nén
}

$KernelTarget = Join-Path $WsaDir "Tools\kernel"
$KernelBackup = Join-Path $WsaDir "Tools\kernel.bak"

Write-Host "[+] Thư mục WSA: $WsaDir" -ForegroundColor Cyan
Write-Host "[+] Vị trí Kernel: $KernelTarget" -ForegroundColor Cyan

# 3. Tắt hoàn toàn WSA
Write-Host "[*] Đang tắt WSA..." -ForegroundColor Yellow
$WsaClient = Join-Path $WsaDir "WsaClient.exe"
if (Test-Path $WsaClient) {
    & $WsaClient /shutdown
}
taskkill /f /im WsaClient.exe 2>$null
taskkill /f /im WsaService.exe 2>$null

# Đợi máy ảo vmmemWSA tắt hẳn
Start-Sleep -Seconds 3

# 4. Sao lưu Kernel cũ (nếu chưa có bản sao lưu)
if (-not (Test-Path $KernelBackup)) {
    Write-Host "[*] Đang tạo bản sao lưu kernel.bak..." -ForegroundColor Green
    Copy-Item $KernelTarget $KernelBackup -Force
}

# 5. Thay thế Kernel mới
Write-Host "[*] Đang cài đặt Kernel mới..." -ForegroundColor Green
Copy-Item $NewKernelPath $KernelTarget -Force

Write-Host "[✓] Hoàn tất! Hãy khởi động lại WSA để áp dụng." -ForegroundColor Green
```

---

## 4. Cách 2: Thay Kernel thủ công (Từng bước)

Nếu bạn muốn thao tác bằng tay:

1. **Chuẩn bị:** Đổi tên file kernel vừa build/tải về (`bzImage` hoặc `Image`) thành tên là **`kernel`** (không có đuôi file).
2. **Tắt hoàn toàn WSA:**
   * Mở ứng dụng **WSA Settings** > mục **System** > chọn **Turn off**.
   * Đảm bảo tiến trình `vmmemWSA` trong Task Manager đã tắt hoàn toàn.
3. **Sao lưu:**
   * Vào thư mục `<Thư_mục_WSA>\Tools\`.
   * Copy file `kernel` thành `kernel.bak`.
4. **Thay thế:**
   * Dán đè file `kernel` mới vào thư mục `<Thư_mục_WSA>\Tools\`.
5. **Khởi động lại:**
   * Mở lại bất kỳ app Android nào hoặc chạy `WsaSettings.exe`.

> [!NOTE]
> **Đối với người dùng cài WSA qua WindowsApps:**
> Thư mục `C:\Program Files\WindowsApps` mặc định bị Windows khóa quyền sửa đổi. Nếu gặp lỗi *Access Denied*, bạn cần cấp quyền chỉnh sửa cho tài khoản của mình bằng lệnh:
> ```powershell
> takeown /f "<Thư_mục_WSA>\Tools" /r /d y
> icacls "<Thư_mục_WSA>\Tools" /grant administrators:F /t
> ```

---

## 5. Xác minh hoạt động & Quản lý Root

1. **Kiểm tra thông tin kernel đã nạp:**
   ```powershell
   adb connect 127.0.0.1:58526
   adb shell uname -a
   ```
   Xem tên phiên bản hiển thị đúng tên build của bạn hay chưa.

2. **Cài đặt Manager tương ứng:**
   * **KernelSU-Next:** Tải APK từ [KernelSU-Next Releases](https://github.com/KernelSU-Next/KernelSU-Next/releases).
   * **KernelSU chuẩn:** Tải APK từ [KernelSU Releases](https://github.com/tiann/KernelSU/releases).
   * Cài đặt vào WSA:
     ```powershell
     adb install <ten_file_manager>.apk
     ```
3. **Kiểm tra quyền Root:**
   Mở ứng dụng Manager đã cài trên WSA:
   * Trạng thái báo: **Đang hoạt động (Working / Built-in GKI2)**.
   * Chạy lệnh kiểm tra root qua terminal:
     ```powershell
     adb shell su -c id
     ```
     Kết quả trả về `uid=0(root) gid=0(root)` chứng tỏ hệ thống đã root thành công.

---

## 6. Khôi phục (Rollback) khi gặp lỗi

Nếu kernel mới không tương thích khiến WSA không thể khởi động hoặc bị crash:
1. Tắt tiến trình:
   ```powershell
   taskkill /f /im WsaClient.exe 2>$null
   ```
2. Đổi tên `kernel.bak` trở lại thành `kernel`:
   ```powershell
   Move-Item -Force "<Thư_mục_WSA>\Tools\kernel.bak" "<Thư_mục_WSA>\Tools\kernel"
   ```
3. Khởi động lại WSA bình thường.
