import os, re

print("[+] Applying WSA compatibility fixes for SuSFS...")

# 1. Fix fs/namespace.c
with open('fs/namespace.c', 'r', encoding='utf-8') as f:
    c = f.read()
if 'linux/susfs_def.h' not in c:
    c = c.replace(
        '#include "internal.h"',
        '#include "internal.h"\n#ifdef CONFIG_KSU_SUSFS\n#include <linux/susfs_def.h>\n#endif\n#ifdef CONFIG_KSU_SUSFS_SUS_MOUNT\nextern bool susfs_is_current_ksu_domain(void);\nextern struct static_key_true susfs_is_sdcard_android_data_not_decrypted;\n#define CL_COPY_MNT_NS BIT(25)\n#endif\n'
    )
    with open('fs/namespace.c', 'w', encoding='utf-8') as f:
        f.write(c)
    print("[+] Fixed fs/namespace.c header")

# 2. Fix fs/proc/task_mmu.c
with open('fs/proc/task_mmu.c', 'r', encoding='utf-8') as f:
    c = f.read()
if 'linux/susfs_def.h' not in c:
    c = c.replace(
        '#include "internal.h"',
        '#include "internal.h"\n#if defined(CONFIG_KSU_SUSFS_SUS_KSTAT) || defined(CONFIG_KSU_SUSFS_SUS_MAP) || defined(CONFIG_KSU_SUSFS_OPEN_REDIRECT)\n#include <linux/susfs_def.h>\n#endif\n#ifndef VMA_PAD_START\n#define VMA_PAD_START(vma) (vma->vm_end)\n#endif\n'
    )
    with open('fs/proc/task_mmu.c', 'w', encoding='utf-8') as f:
        f.write(c)
    print("[+] Fixed fs/proc/task_mmu.c header & VMA_PAD_START")

# 3. Fix fs/notify/fdinfo.c
with open('fs/notify/fdinfo.c', 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace(
    'static void fanotify_fdinfo(struct seq_file *m, struct fsnotify_mark *mark)',
    'static void fanotify_fdinfo(struct seq_file *m, struct fsnotify_mark *mark, struct file *file)'
)
with open('fs/notify/fdinfo.c', 'w', encoding='utf-8') as f:
    f.write(c)
print("[+] Fixed fs/notify/fdinfo.c fanotify signature")

# 4. Fix KernelSU runtime/ksud.h missing <linux/compat.h>
ksud_paths = ['KernelSU/kernel/runtime/ksud.h', 'drivers/kernelsu/runtime/ksud.h']
for kp in ksud_paths:
    if os.path.exists(kp):
        with open(kp, 'r', encoding='utf-8') as f:
            c = f.read()
        if 'linux/compat.h' not in c:
            c = '#include <linux/compat.h>\n' + c
            with open(kp, 'w', encoding='utf-8') as f:
                f.write(c)
            print(f"[+] Fixed {kp} missing <linux/compat.h>")

# 5. Fix TIF_SECCOMP on x86_64 in KernelSU policy/app_profile.c
ap_paths = ['KernelSU/kernel/policy/app_profile.c', 'drivers/kernelsu/policy/app_profile.c']
for ap in ap_paths:
    if os.path.exists(ap):
        with open(ap, 'r', encoding='utf-8') as f:
            c = f.read()
        if 'if (likely(test_thread_flag(TIF_SECCOMP)))' in c:
            c = c.replace('if (likely(test_thread_flag(TIF_SECCOMP)))\n        disable_seccomp();', 'disable_seccomp();')
            with open(ap, 'w', encoding='utf-8') as f:
                f.write(c)
            print(f"[+] Fixed {ap} TIF_SECCOMP on x86_64")

# 6. Inject weak fallback implementations for preinit symbols in fs/exec.c
if os.path.exists('fs/exec.c'):
    with open('fs/exec.c', 'r', encoding='utf-8') as f:
        c = f.read()
    weak_impl = """int __attribute__((weak)) ksu_setup_preinit_file(struct filename **filename_ptr, struct user_arg_ptr *argv_user) {
    return -EINVAL;
}
int __attribute__((weak)) ksu_preinit_handle_post_execveat(int *fd, struct filename **filename_ptr,
                void *argv_user, void *envp_user,
                int *flags, int *retval, int *preinit_fd) {
    return 0;
}"""
    if "extern int ksu_setup_preinit_file" in c:
        c = re.sub(
            r'extern int ksu_setup_preinit_file\([^)]+\);\s*extern int ksu_preinit_handle_post_execveat\([^)]+\);',
            weak_impl,
            c
        )
        with open('fs/exec.c', 'w', encoding='utf-8') as f:
            f.write(c)
        print("[+] Fixed fs/exec.c with weak preinit fallback implementations")

# 7. Support KernelSU-Next Manager (com.rifsxd.ksunext)
kbuild_paths = ['KernelSU/kernel/Kbuild', 'drivers/kernelsu/Kbuild']
for kp in kbuild_paths:
    if os.path.exists(kp):
        with open(kp, 'r', encoding='utf-8') as f:
            c = f.read()
        c = c.replace('KSU_PACKAGE_NAME ?= me.weishu.kernelsu', 'KSU_PACKAGE_NAME ?= com.rifsxd.ksunext')
        c = c.replace('KSU_EXPECTED_SIZE ?= 0x033b', 'KSU_EXPECTED_SIZE ?= 0x03e6')
        c = c.replace('KSU_EXPECTED_HASH ?= c371061b19d8c7d7d6133c6a9bafe198fa944e50c1b31c9d8daa8d7f1fc2d2d6',
                      'KSU_EXPECTED_HASH ?= 79e590113c4c4c0c222978e413a5faa801666957b1212a328e46c00c69821bf7')
        with open(kp, 'w', encoding='utf-8') as f:
            f.write(c)
        print(f"[+] Configured {kp} for com.rifsxd.ksunext")

apk_sign_paths = ['KernelSU/kernel/manager/apk_sign.c', 'drivers/kernelsu/manager/apk_sign.c']
for ap in apk_sign_paths:
    if os.path.exists(ap):
        with open(ap, 'r', encoding='utf-8') as f:
            c = f.read()
        target = 'return check_v2_signature(path, EXPECTED_SIZE, EXPECTED_HASH);'
        replacement = 'return check_v2_signature(path, EXPECTED_SIZE, EXPECTED_HASH) || check_v2_signature(path, 0x03e6, "79e590113c4c4c0c222978e413a5faa801666957b1212a328e46c00c69821bf7") || check_v2_signature(path, 0x033b, "c371061b19d8c7d7d6133c6a9bafe198fa944e50c1b31c9d8daa8d7f1fc2d2d6");'
        if target in c:
            c = c.replace(target, replacement)
            with open(ap, 'w', encoding='utf-8') as f:
                f.write(c)
            print(f"[+] Enhanced {ap} for dual manager verification")

throne_paths = ['KernelSU/kernel/manager/throne_tracker.c', 'drivers/kernelsu/manager/throne_tracker.c']
for tp in throne_paths:
    if os.path.exists(tp):
        with open(tp, 'r', encoding='utf-8') as f:
            c = f.read()
        c = c.replace(
            'strncmp(pkg, KSU_PACKAGE_NAME, sizeof(KSU_PACKAGE_NAME)) == 0',
            '(strncmp(pkg, "com.rifsxd.ksunext", 18) == 0 || strncmp(pkg, "me.weishu.kernelsu", 17) == 0 || strncmp(pkg, KSU_PACKAGE_NAME, sizeof(KSU_PACKAGE_NAME)) == 0)'
        )
        c = c.replace(
            'strcmp(np->package, KSU_PACKAGE_NAME) == 0',
            '(strcmp(np->package, "com.rifsxd.ksunext") == 0 || strcmp(np->package, "me.weishu.kernelsu") == 0 || strcmp(np->package, KSU_PACKAGE_NAME) == 0)'
        )
        with open(tp, 'w', encoding='utf-8') as f:
            f.write(c)
        print(f"[+] Enhanced {tp} for dual manager tracking")

# 8. Align KERNEL_SU_UAPI_VERSION to 5 (for KernelSU-Next Manager v3.4.2 compatibility)
for root, dirs, files in os.walk('.'):
    for fname in files:
        if fname == 'supercall.h':
            fpath = os.path.join(root, fname)
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                sc = f.read()
            if 'KERNEL_SU_UAPI_VERSION = 6;' in sc:
                sc = sc.replace('static const __u32 KERNEL_SU_UAPI_VERSION = 6;', 'static const __u32 KERNEL_SU_UAPI_VERSION = 5;')
                sc = sc.replace('KERNEL_SU_UAPI_VERSION = 6;', 'KERNEL_SU_UAPI_VERSION = 5;')
                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(sc)
                print(f"[+] Replaced KERNEL_SU_UAPI_VERSION to 5 in {fpath}")

print("[✓] All WSA compatibility fixes applied successfully!")
