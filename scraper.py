import requests
import json

headers = {"User-Agent": "Mozilla/5.0"}

def ambil_remoteok():
    print("📡 Mengambil dari RemoteOK...")
    r = requests.get("https://remoteok.com/api", headers=headers, timeout=15)
    data = r.json()
    hasil = []
    for item in data:
        if "id" in item and "position" in item:
            hasil.append({
                "judul"     : item.get("position", "-"),
                "perusahaan": item.get("company", "-"),
                "lokasi"    : item.get("location", "Remote"),
                "tags"      : ", ".join(item.get("tags", [])),
                "deskripsi" : item.get("description", ""),
                "url"       : item.get("url", "-"),
                "sumber"    : "RemoteOK"
            })
    print(f"✅ RemoteOK: {len(hasil)} loker")
    return hasil

def ambil_themuse():
    print("📡 Mengambil dari The Muse...")
    hasil = []
    for page in range(1, 6):  # ambil 5 halaman
        try:
            url = f"https://www.themuse.com/api/public/jobs?page={page}&level=Mid%20Level"
            r = requests.get(url, timeout=15)
            data = r.json()
            for item in data.get("results", []):
                lokasi = ""
                if item.get("locations"):
                    lokasi = item["locations"][0].get("name", "Remote")
                hasil.append({
                    "judul"     : item.get("name", "-"),
                    "perusahaan": item.get("company", {}).get("name", "-"),
                    "lokasi"    : lokasi,
                    "tags"      : item.get("categories", [{}])[0].get("name", "") if item.get("categories") else "",
                    "deskripsi" : item.get("contents", ""),
                    "url"       : item.get("refs", {}).get("landing_page", "-"),
                    "sumber"    : "TheMuse"
                })
        except Exception as e:
            print(f"❌ Halaman {page} error: {e}")
    print(f"✅ The Muse: {len(hasil)} loker")
    return hasil

# Gabungkan kedua sumber
semua = ambil_remoteok() + ambil_themuse()

with open("data_loker.json", "w") as f:
    json.dump(semua, f, indent=2)

print(f"\n🎉 Total gabungan: {len(semua)} loker tersimpan!")