# WSA Custom Kernels (KernelSU-Next & Built-in SuSFS)

Kho lưu trữ mã nguồn và quy trình tự động biên dịch Linux Kernel tùy chỉnh cho **Windows Subsystem for Android (WSA)**, hỗ trợ cả **Kernel 5.15** (Android 13) và **Kernel 5.10** (Android 11 / 12L) trên kiến trúc **x86_64** (và tương thích ARM64).

---

## 🌟 Tính Năng Nổi Bật

1. **KernelSU-Next v3.4.2:**
   - Hệ thống quản lý quyền Root nhân Linux thế hệ mới.
   - Hỗ trợ đầy đủ App Profile, Mount Namespace isolation, SELinux policy rules.
   - Nhận diện trực tiếp **KernelSU-Next Manager** (`com.rifsxd.ksunext`) và KernelSU Official Manager (`me.weishu.kernelsu`).
   - Đồng bộ UAPI version 5 giúp Manager nhận diện hoàn toàn quyền root và nạp Module không bị xung đột.

2. **Built-in SuSFS (v2.4.0) (In-Tree Kernel Mode):**
   - Không cần tải module LKM bên ngoài; toàn bộ tính năng ẩn Root và giả lập tệp hệ thống được nhúng trực tiếp vào nhân:
     - `CONFIG_KSU_SUSFS_SUS_PATH`: Ẩn các thư mục/tệp nhạy cảm (su, magisk, ksu...).
     - `CONFIG_KSU_SUSFS_SUS_MOUNT`: Ẩn mount point khỏi `/proc/mounts` và giả lập mnt_id.
     - `CONFIG_KSU_SUSFS_SUS_KSTAT`: Giả lập stat/kstat tệp hệ thống.
     - `CONFIG_KSU_SUSFS_SPOOF_UNAME`: Tùy chỉnh thông tin kernel `uname`.
     - `CONFIG_KSU_SUSFS_OPEN_REDIRECT`: Chuyển hướng truy cập tệp an toàn.
     - `CONFIG_KSU_SUSFS_SUS_MAP`: Bảo vệ ánh xạ bộ nhớ VMA khỏi bị quét.
     - `CONFIG_KSU_SUSFS_HIDE_KSU_SUSFS_SYMBOLS`: Tự động ẩn toàn bộ symbol ksu/susfs trong `/proc/kallsyms`.

3. **Module BRENE Universal (x86_64 & arm64):**
   - Tích hợp công cụ dòng lệnh `ksu_susfs` v2.4.0 bản gốc biên dịch trực tiếp cho x86_64 qua Android NDK.
   - Bảng điều khiển WebUI trực quan trong KernelSU-Next Manager để bật/tắt các lớp ẩn root.

---

## 📦 Danh Sách Kernel Trong [Release Revision 1](https://github.com/hpbzareth/wsa-ksun/releases/tag/r1)

| Tên File | Phiên Bản Kernel | Tính Năng Tích Hợp | Khuyến Nghị Cho |
| :--- | :--- | :--- | :--- |
| **`kernel-5.15-susfs`** (hoặc `kernel`) | 5.15.104.4 | KernelSU + Built-in SuSFS v2.4.0 | Người dùng Android 13 cần ẩn root tối đa |
| **`kernel-5.15-ksunext-v3.4.2`** | 5.15.104.4 | KernelSU-Next v3.4.2 chuẩn | Người dùng Android 13 cần root chuẩn |
| **`kernel-5.10-susfs`** | 5.10.136.2 | KernelSU + Built-in SuSFS v2.4.0 | Người dùng Android 11 / 12L cần ẩn root |
| **`kernel-5.10-ksunext-v3.4.2`** | 5.10.136.2 | KernelSU-Next v3.4.2 chuẩn | Người dùng Android 11 / 12L cần root chuẩn |
| **`BRENE-Universal-x86_64-arm64.zip`** | Module KSU | Bộ ẩn root nâng cao + WebUI (x86_64 & arm64) | Flash trong tab Mô-đun của KernelSU-Next |
| **`ksu_module_susfs.zip`** | Module KSU | Module companion SuSFS chuẩn | Flash trong tab Mô-đun của KernelSU-Next |

---

## 🚀 Hướng Dẫn Cài Đặt Universal (Bản 5.10 & 5.15)

### Bước 1: Xác định phiên bản WSA đang sử dụng
1. Mở ứng dụng **Cài đặt Hệ thống con Windows dành cho Android (WSA Settings)**.
2. Chọn thẻ **Giới thiệu (About)** để xem phiên bản Android:
   - Nếu WSA chạy **Android 13** (WSA bản 2211 trở lên, ví dụ các bản 23xx, 24xx): Chọn **Kernel 5.15**.
   - Nếu WSA chạy **Android 11 hoặc 12L** (các bản WSA đời cũ): Chọn **Kernel 5.10**.

### Bước 2: Tải file Kernel
1. Truy cập trang **[Releases](https://github.com/hpbzareth/wsa-ksun/releases/tag/r1)** của repository.
2. Tải bản kernel tương ứng (`kernel-5.15-susfs`, `kernel-5.15-ksunext-v3.4.2`, hoặc các bản `5.10`).
3. Đổi tên file đã tải về thành đúng tên: **`kernel`** (không có phần mở rộng như `.bin`, `.exe` hay `.txt`).

### Bước 3: Tắt hoàn toàn WSA
Trước khi thay kernel, máy ảo WSA phải được tắt hẳn để Windows mở khóa tệp `kernel`:
* **Cách 1 (Đơn giản nhất):** Mở **WSA Settings** > thẻ **Hệ thống (System)** > bấm nút **Tắt (Turn off)**.
* **Cách 2 (Bằng dòng lệnh):**
  Mở PowerShell hoặc Command Prompt:
  ```cmd
  REM Dùng WsaClient để tắt máy ảo
  "%LOCALAPPDATA%\Microsoft\WindowsApps\WsaClient.exe" /shutdown
  ```
  *(Hoặc trỏ tới file `WsaClient.exe` nằm trong thư mục cài đặt WSA của bạn: `<Thư_mục_WSA>\WsaClient\WsaClient.exe /shutdown`)*
* **Cách 3 (Nếu tệp kernel vẫn bị báo đang sử dụng):**
  Mở Command Prompt với quyền Administrator và tạm dừng dịch vụ:
  ```cmd
  net stop WsaService
  ```

### Bước 4: Thay thế file Kernel
1. Mở thư mục chứa bộ cài đặt WSA trên máy tính của bạn (thư mục nơi bạn giải nén WSA, ví dụ thư mục cài qua MagiskOnWSALocal hoặc WSABuilds).
2. Tìm vào thư mục con **`Tools`**:
   - Đường dẫn có dạng: `<Thư_mục_cài_đặt_WSA>\Tools\`
3. Tìm file `kernel` hiện tại, đổi tên thành **`kernel.orig`** hoặc **`kernel.bak`** để sao lưu dự phòng.
4. Chép file `kernel` mới bạn đã đổi tên ở Bước 2 vào thư mục `Tools` này.

### Bước 5: Khởi động lại WSA & Kiểm tra
1. Mở ứng dụng **WSA Settings** hoặc khởi chạy một ứng dụng Android bất kỳ để kích hoạt máy ảo. *(Nếu ở Bước 3 bạn dùng lệnh `net stop WsaService`, hãy chạy `net start WsaService` trước khi mở)*.
2. Cài đặt và mở ứng dụng **KernelSU Next Manager** (`com.rifsxd.ksunext`):
   - Màn hình chính sẽ hiển thị huy hiệu: **Đang hoạt động (BUILT-IN)**.
   - Mục **Phiên bản SuSFS** hiển thị: **Được hỗ trợ | v2.4.0 (GKI)**.
3. Kiểm tra qua kết nối ADB:
   ```cmd
   adb connect 127.0.0.1:58526
   adb shell uname -a
   adb shell su -v
   adb shell su -c id
   ```
   Kết quả trả về `uid=0(root) gid=0(root) context=u:r:ksu:s0` xác nhận quyền Root hoạt động hoàn toàn chính xác.

4. **Cài đặt Module ẩn Root (Khuyên dùng):**
   - Vào thẻ **Mô-đun (Modules)** trong KernelSU-Next Manager.
   - Bấm **Cài đặt (Install)** và chọn tệp **`BRENE-Universal-x86_64-arm64.zip`**.
   - Khởi động lại WSA để module kích hoạt đầy đủ 10 lớp bảo vệ SuSFS và giao diện WebUI.

---

## 🛠️ Cấu Trúc Nhánh (Branches)

* **`main`**: Giữ mã nguồn và workflow build Kernel 5.10 & 5.15 tiêu chuẩn (KernelSU-Next v3.4.2).
* **`susfs`**: Quy trình chuyên sâu build SuSFS Built-in (In-Tree) v2.4.0 tích hợp nhân WSA Linux Kernel.
* **`brene`**: Quy trình biên dịch userspace NDK và đóng gói module BRENE Universal (x86_64 & arm64).

---

## ⚠️ Lưu Ý Dự Phòng
* Luôn giữ bản sao lưu `kernel.orig` trong thư mục `Tools` để có thể trở về nhân nguyên bản bất kỳ lúc nào chỉ bằng một thao tác đổi tên file.
