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

print("[✓] All WSA compatibility fixes applied successfully!")
