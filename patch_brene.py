import os, re, shutil

print("[+] Patching BRENE for Universal x86_64 and arm64...")

os.makedirs("tools", exist_ok=True)
arm64_src = "../../susfs4ksu/ksu_susfs/libs/arm64-v8a/ksu_susfs"
x86_64_src = "../../susfs4ksu/ksu_susfs/libs/x86_64/ksu_susfs"

if os.path.exists(arm64_src):
    shutil.copy2(arm64_src, "tools/susfs_arm64")
    print("[+] Copied susfs_arm64")

if os.path.exists(x86_64_src):
    shutil.copy2(x86_64_src, "tools/susfs_x86_64")
    shutil.copy2(x86_64_src, "tools/susfs")
    print("[+] Copied susfs_x86_64")

with open("customize.sh", "r", encoding="utf-8") as f:
    c = f.read()

new_check = """echo "[i] Installing BRENE Universal for architecture: ${ARCH}"
case "${ARCH}" in
	arm64)
		if [[ -f "${MODPATH}/tools/susfs_arm64" ]]; then
			cp -f "${MODPATH}/tools/susfs_arm64" "${DEST_BIN_DIR}/susfs"
		else
			cp -f "${MODPATH}/tools/susfs" "${DEST_BIN_DIR}/susfs"
		fi
		;;
	x64|x86_64)
		if [[ -f "${MODPATH}/tools/susfs_x86_64" ]]; then
			cp -f "${MODPATH}/tools/susfs_x86_64" "${DEST_BIN_DIR}/susfs"
		else
			cp -f "${MODPATH}/tools/susfs" "${DEST_BIN_DIR}/susfs"
		fi
		;;
	*)
		abort "[❌] Architecture ${ARCH} is not supported!"
		;;
esac"""

if "Only arm64 is supported!" in c:
    c = re.sub(r'if\s*\[\[\s*"\$\{ARCH\}"\s*!=\s*"arm64"\s*\]\];[\s\S]*?fi', new_check, c)
    c = c.replace('cp -f "${MODPATH}/tools/susfs" "${DEST_BIN_DIR}"', '# Binary copied in architecture selector')
    with open("customize.sh", "w", encoding="utf-8") as f:
        f.write(c)
    print("[+] Patched customize.sh successfully!")

if os.path.exists("module.prop"):
    with open("module.prop", "r", encoding="utf-8") as f:
        mp = f.read()
    mp = mp.replace("name=BRENE", "name=BRENE (Universal x86_64 & arm64)")
    with open("module.prop", "w", encoding="utf-8") as f:
        f.write(mp)
    print("[+] Patched module.prop successfully!")
