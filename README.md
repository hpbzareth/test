# Hướng Dẫn Cài Đặt Custom Kernel Cho WSA (Windows Subsystem for Android)

Tài liệu này hướng dẫn chi tiết cách thay thế Kernel gốc của Windows Subsystem for Android (WSA) bằng Custom Kernel (KernelSU-Next / SuSFS / KSU) được build từ GitHub Actions của repository này.

---

## 1. Chuẩn bị

* **Môi trường:** Windows 10 hoặc Windows 11 (kiến trúc x86_64).
* **Bản WSA:** Bản cài đặt giải nén (unbundled), ví dụ: `C:\WSA_2407.40000.4.0_x64` hoặc thư mục cài đặt WSA tương ứng trên máy bạn.
* **ADB:** Đã bật tính năng **Developer Mode** trong cài đặt WSA.

---

## 2. Lấy file Kernel mới từ GitHub Actions

1. Vào tab **Actions** của repository: `https://github.com/hpbzareth/test/actions`.
2. Chọn workflow run mới nhất thành công (dấu tick xanh).
3. Kéo xuống phần **Artifacts** ở cuối trang và tải file **`kernel`**.
4. Giải nén file `.zip` vừa tải về, bạn sẽ nhận được một file nhị phân tên là **`kernel`** (hoặc `bzImage`).
   * *Lưu ý: Đảm bảo tên file chính xác là `kernel` (không có đuôi mở rộng như `.exe` hay `.bin`).*

---

## 3. Các bước thay thế Kernel vào WSA

### Bước 1: Tắt hoàn toàn WSA
WSA phải được tắt hoàn toàn để Windows giải phóng khóa file `kernel`.

* **Cách 1 (Giao diện):** Mở **Cài đặt Hệ thống con Windows dành cho Android (WSA Settings)** > Chọn thẻ **Hệ thống (System)** > Nhấn **Tắt (Turn off)**.
* **Cách 2 (Lệnh PowerShell / CMD với quyền Administrator):**
  ```powershell
  # Tắt client WSA
  C:\WSA_2407.40000.4.0_x64\WsaClient.exe /shutdown

  # Hoặc buộc dừng nếu tiến trình bị treo:
  taskkill /f /im WsaClient.exe 2>$null
  taskkill /f /im WsaService.exe 2>$null
  ```
* *Mẹo:* Mở Task Manager (Ctrl + Shift + Esc) kiểm tra xem tiến trình `vmmemWSA` đã tắt hẳn chưa.

---

### Bước 2: Sao lưu Kernel gốc
Đề phòng trường hợp kernel mới không tương thích hoặc lỗi bootloop, hãy sao lưu kernel hiện tại:
* Vào thư mục: `C:\WSA_2407.40000.4.0_x64\Tools\`
* Tìm file **`kernel`** và tạo một bản sao lưu tên là **`kernel.bak`**:
  ```powershell
  Copy-Item "C:\WSA_2407.40000.4.0_x64\Tools\kernel" "C:\WSA_2407.40000.4.0_x64\Tools\kernel.bak"
  ```

---

### Bước 3: Chép Kernel mới vào thư mục Tools
Copy file **`kernel`** mới vừa tải từ GitHub Actions và dán đè vào thư mục `Tools`:
```powershell
Copy-Item "đường_dẫn_tới_file_tai_ve\kernel" "C:\WSA_2407.40000.4.0_x64\Tools\kernel" -Force
```

---

### Bước 4: Khởi động lại WSA
Mở lại WSA bằng cách khởi chạy bất kỳ ứng dụng Android nào hoặc mở **WsaSettings.exe**:
```powershell
Start-Process "C:\WSA_2407.40000.4.0_x64\WsaSettings.exe"
```

---

## 4. Kiểm tra hoạt động & Quyền Root

### 1. Kiểm tra phiên bản Kernel qua ADB
Mở terminal PowerShell và kết nối ADB tới WSA (cổng mặc định thường là `58526`):
```powershell
adb connect 127.0.0.1:58526
adb shell uname -a
```
*Kết quả in ra sẽ chứa tên build kernel mới (ví dụ: `5.15.104-...-ksunext` hoặc `-wsa-susfs`).*

### 2. Cài đặt Manager App tương ứng
* **KernelSU-Next:** Cài đặt file APK [KernelSU-Next Manager](https://github.com/KernelSU-Next/KernelSU-Next/releases).
* **KernelSU chuẩn:** Cài đặt [KernelSU Manager](https://github.com/tiann/KernelSU/releases).

Sau khi cài đặt, mở app Manager:
* Màn hình chính phải báo: **Đang hoạt động (Working / Built-in GKI2)**.
* Kiểm tra quyền root bằng lệnh:
  ```powershell
  adb shell su -c id
  ```
  Nếu trả về: `uid=0(root) gid=0(root) context=u:r:ksu:s0` là hệ thống đã hoạt động hoàn hảo.

---

## 5. Khắc phục sự cố & Hoàn tác (Rollback)

Nếu sau khi thay kernel, WSA bị treo ở màn hình khởi động hoặc tự động thoát:
1. Tắt tiến trình WSA (`taskkill /f /im WsaClient.exe 2>$null`).
2. Khôi phục lại kernel gốc đã sao lưu:
   ```powershell
   Move-Item -Force "C:\WSA_2407.40000.4.0_x64\Tools\kernel.bak" "C:\WSA_2407.40000.4.0_x64\Tools\kernel"
   ```
3. Mở lại WSA, hệ thống sẽ hoạt động bình thường trở lại.

---

## 6. Lưu ý kỹ thuật khi tự Build Custom Kernel cho WSA
* Phải build trên mã nguồn [microsoft/WSA-Linux-Kernel](https://github.com/microsoft/WSA-Linux-Kernel) (nhánh/tag `android-lts/latte-2/5.15.104.4`).
* Phải nạp file cấu hình chính thức của Microsoft: `configs/wsa/config-wsa-x64` (chứa các driver ảo hóa Hyper-V, `dx_gkrnl` GPU passthrough, `ashmem`, `binder`).
* Trên kiến trúc `x86_64`, khi tích hợp KernelSU-Next cần bật `CONFIG_KSU_X86_PATCH_SYSCALL_DISPATCHER=y`.
