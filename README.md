# WSA Custom Kernels (KernelSU-Next & Built-in SuSFS)

Kho lưu trữ mã nguồn và quy trình tự động biên dịch Linux Kernel tùy chỉnh cho **Windows Subsystem for Android (WSA)**, hỗ trợ cả **Kernel 5.15** (Android 13) và **Kernel 5.10** (Android 11 / 12L) trên kiến trúc **x86_64** (và tương thích ARM64).

---

## 🌟 Tính Năng Nổi Bật

1. **KernelSU-Next v3.4.2:**
   - Hệ thống quản lý quyền Root nhân Linux thế hệ mới.
   - Hỗ trợ đầy đủ App Profile, Mount Namespace isolation, SELinux policy rules.
   - Nhận diện trực tiếp **KernelSU-Next Manager** (`com.rifsxd.ksunext`) và KernelSU Official Manager (`me.weishu.kernelsu`).

2. **Built-in SuSFS (v2.4.0) (In-Tree Kernel Mode):**
   - Không cần tải module LKM bên ngoài; toàn bộ tính năng ẩn Root và giả lập tệp hệ thống được nhúng trực tiếp vào nhân:
     - `CONFIG_KSU_SUSFS_SUS_PATH`: Ẩn các thư mục/tệp nhạy cảm (su, magisk, ksu...).
     - `CONFIG_KSU_SUSFS_SUS_MOUNT`: Ẩn mount point khỏi `/proc/mounts` và giả lập mnt_id.
     - `CONFIG_KSU_SUSFS_SUS_KSTAT`: Giả lập stat/kstat tệp hệ thống.
     - `CONFIG_KSU_SUSFS_SPOOF_UNAME`: Tùy chỉnh thông tin kernel `uname`.
     - `CONFIG_KSU_SUSFS_OPEN_REDIRECT`: Chuyển hướng truy cập tệp an toàn.
     - `CONFIG_KSU_SUSFS_SUS_MAP`: Bảo vệ ánh xạ bộ nhớ VMA khỏi bị quét.
     - `CONFIG_KSU_SUSFS_HIDE_KSU_SUSFS_SYMBOLS`: Tự động ẩn toàn bộ symbol ksu/susfs trong `/proc/kallsyms`.

---

## 📦 Danh Sách Kernel Trong [Release Revision 1](https://github.com/hpbzareth/wsa-ksun/releases/tag/r1)

| Tên File | Phiên Bản Kernel | Tính Năng Tích Hợp | Khuyến Nghị Cho |
| :--- | :--- | :--- | :--- |
| **`kernel-5.15-susfs`** (hoặc `kernel`) | 5.15.104.4 | KernelSU + Built-in SuSFS v2.4.0 | Người dùng Android 13 cần ẩn root tối đa |
| **`kernel-5.15-ksunext-v3.4.2`** | 5.15.104.4 | KernelSU-Next v3.4.2 chuẩn | Người dùng Android 13 cần root chuẩn |
| **`kernel-5.10-susfs`** | 5.10.136.2 | KernelSU + Built-in SuSFS v2.4.0 | Người dùng Android 11 / 12L cần ẩn root |
| **`kernel-5.10-ksunext`** | 5.10.136.2 | KernelSU-Next chuẩn | Người dùng Android 11 / 12L cần root chuẩn |
| **`ksu_module_susfs.zip`** | Module KSU | Công cụ cấu hình CLI / companion SuSFS | Flash qua tab Mô-đun trong KernelSU-Next |

---

## 🚀 Hướng Dẫn Cài Đặt Universal (Bản 5.10 & 5.15)

### Bước 1: Xác định phiên bản WSA đang sử dụng
1. Mở **Cài đặt Hệ thống con Windows dành cho Android (WSA Settings)**.
2. Chọn thẻ **Giới thiệu (About)** để xem phiên bản Android:
   - Nếu WSA chạy **Android 13** (WSA 2211 trở lên, ví dụ `2407.40000.4.0`): Chọn **Kernel 5.15**.
   - Nếu WSA chạy **Android 11 hoặc 12L** (WSA cũ hơn): Chọn **Kernel 5.10**.

### Bước 2: Tải file Kernel
1. Truy cập trang **[Releases](https://github.com/hpbzareth/wsa-ksun/releases/tag/r1)** của repository.
2. Tải bản kernel tương ứng (`kernel-5.15-susfs`, `kernel-5.15-ksunext-v3.4.2`, hoặc bản `5.10`).
3. Đổi tên file đã tải về thành đúng tên: **`kernel`** (không có phần mở rộng `.bin` hay `.exe`).

### Bước 3: Tắt hoàn toàn WSA
Trước khi thay kernel, WSA phải được dừng hẳn để giải phóng file đang bị khóa:
* **Giao diện:** Vào **WSA Settings** > thẻ **Hệ thống (System)** > bấm **Tắt (Turn off)**.
* **Hoặc PowerShell (Run as Administrator):**
  ```powershell
  # Tắt client WSA
  & "C:\WSA_2407.40000.4.0_x64\WsaClient\WsaClient.exe" /shutdown

  # Hoặc dừng hẳn tiến trình
  taskkill /f /im WsaClient.exe /im WSACrashUploader.exe /im vmwp.exe 2>$null
  ```

### Bước 4: Thay thế file Kernel
1. Mở thư mục cài đặt WSA của bạn, tìm thư mục con **`Tools`**:
   - Ví dụ: `C:\WSA_2407.40000.4.0_x64\Tools\`
2. Đổi tên file `kernel` cũ thành **`kernel.orig`** để sao lưu dự phòng.
3. Chép file `kernel` mới bạn vừa tải ở Bước 2 vào thư mục `Tools`.

### Bước 5: Khởi động lại WSA & Kiểm tra
1. Khởi chạy ứng dụng Android bất kỳ hoặc mở **WsaSettings.exe** để kích hoạt máy ảo.
2. Cài đặt và mở **KernelSU Next Manager** (`com.rifsxd.ksunext`):
   - Màn hình chính sẽ hiển thị huy hiệu xanh: **Đang hoạt động (BUILT-IN)**.
   - Mục **Phiên bản SuSFS** hiển thị: **Được hỗ trợ | v2.4.0 (GKI)**.
3. Kiểm tra bằng ADB:
   ```cmd
   adb connect 127.0.0.1:58526
   adb shell uname -a
   adb shell su -v
   adb shell su -c id
   ```
   Kết quả trả về `uid=0(root)` xác nhận quyền Root đã sẵn sàng.

---

## 🛠️ Cấu Trúc Nhánh (Branches)

* **`main`**: Giữ quy trình ổn định build KernelSU-Next v3.4.2 và các phiên bản tiêu chuẩn.
* **`susfs`**: Quy trình chuyên sâu build SuSFS Built-in (In-Tree) với toàn bộ bản vá tương thích cho Microsoft WSA Linux Kernel.

---

## ⚠️ Lưu Ý Bảo Mật
* Luôn giữ bản sao lưu `kernel.orig` để có thể khôi phục lại nhân gốc bất kỳ lúc nào chỉ bằng một thao tác đổi tên file.
