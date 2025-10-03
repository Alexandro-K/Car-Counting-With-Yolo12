import os
import glob

folder = "result"

os.makedirs(folder, exist_ok=True)

files = glob.glob(os.path.join(folder, "*"))
for f in files:
    try:
        os.remove(f)
        print(f"File {f} dihapus.")
    except Exception as e:
        print(f"Gagal hapus{f}: {e}")

print("Folder result berhasil dikosongkan.")
