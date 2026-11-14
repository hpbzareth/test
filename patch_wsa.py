import os

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
    target_decl = "extern int ksu_setup_preinit_file(struct filename **filename_ptr, struct user_arg_ptr *argv_user);\nextern int ksu_preinit_handle_post_execveat(int *fd, struct filename **filename_ptr,\n\t\t\t\tvoid *argv_user, void *envp_user,\n\t\t\t\tint *flags, int *retval, int *preinit_fd);"
    weak_impl = """int __attribute__((weak)) ksu_setup_preinit_file(struct filename **filename_ptr, struct user_arg_ptr *argv_user) {
    return -EINVAL;
}
int __attribute__((weak)) ksu_preinit_handle_post_execveat(int *fd, struct filename **filename_ptr,
                void *argv_user, void *envp_user,
                int *flags, int *retval, int *preinit_fd) {
    return 0;
}"""
    if "extern int ksu_setup_preinit_file" in c:
        # replace the two extern declarations with weak implementations
        import re
        c = re.sub(
            r'extern int ksu_setup_preinit_file\([^)]+\);\s*extern int ksu_preinit_handle_post_execveat\([^)]+\);',
            weak_impl,
            c
        )
        with open('fs/exec.c', 'w', encoding='utf-8') as f:
            f.write(c)
        print("[+] Fixed fs/exec.c with weak preinit fallback implementations")

print("[✓] All WSA compatibility fixes applied successfully!")
