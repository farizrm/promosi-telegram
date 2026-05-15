import asyncio
import random
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.types import InputStickerSetShortName

# --- SETUP DUMMY SERVER UNTUK UPTIMEROBOT ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write("<h1>🚀 Mesin Promosi Micifind (Mode Agresif + Stiker Resmi) Aktif!</h1>".encode('utf-8'))
        
    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# --- KONFIGURASI PROMOSI ---
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
TARGET_BOT = '@chatbot' # Ganti dengan bot anonim target

# NAMA PENDEK STIKER PACK (Pastikan sudah sesuai)
STICKER_PACK_SHORT_NAME = "micifindbot"

# Variasi Sapaan (Spintax)
GREETINGS = ["hii", "halo", "P", "kiw", "allooo"]

# Variasi Teks Promosi
PROMO_MESSAGES = [
    "Lagi bosen? Cobain @micifindbot yuk. Bisa cari partner satu kota, fiturnya bersih & no delay! ✨",
    "Eh cobain @micifindbot deh, bot anonim baru bisa milih temen se-kota/provinsi. Lebih rapi tampilannya 👌",
    "Bosen yg ini delay trs? Pindah ke @micifindbot aja kak, cari partner se-kota lebih gampang 🚀",
    "Mau match sama org terdekat? di @micifindbot bisa filter kota lho, cobain aja gratis kok ✨"
]

# Mengumpulkan Sesi
SESSIONS = []
for i in range(1, 16): 
    session_string = os.environ.get(f"SESSION_{i}")
    if session_string:
        SESSIONS.append((f"Akun_{i}", session_string))

async def run_promoter(nama_akun, session_string):
    try:
        client = TelegramClient(StringSession(session_string), API_ID, API_HASH)
        await client.start()
        print(f"✅ [{nama_akun}] Berhasil terhubung!")

        # Menarik data Stiker Resmi dari Server Telegram (Hanya dilakukan 1x di awal)
        try:
            sticker_set = await client(GetStickerSetRequest(
                stickerset=InputStickerSetShortName(short_name=STICKER_PACK_SHORT_NAME)
            ))
            promo_sticker = sticker_set.documents[0] # Mengambil stiker urutan pertama
            has_sticker = True
            print(f"📦 [{nama_akun}] Berhasil memuat Stiker Pack Resmi!")
        except Exception as e:
            print(f"⚠️ [{nama_akun}] Gagal memuat stiker pack: {e}")
            has_sticker = False

        while True:
            try:
                # 1. Kirim /next
                await client.send_message(TARGET_BOT, '/next')
                print(f"🔄 [{nama_akun}] Command /next dikirim!")
                
                # 2. Kirim sapaan (Hii/halo/P/kiw/allooo)
                sapaan = random.choice(GREETINGS)
                await client.send_message(TARGET_BOT, sapaan)
                print(f"👋 [{nama_akun}] Sapaan '{sapaan}' dikirim!")
                
                # 3. Tunggu 2 detik
                await asyncio.sleep(2.0)
                
                # 4. Kirim kalimat promosi (Terserah yang mana aja dari daftar)
                promo = random.choice(PROMO_MESSAGES)
                await client.send_message(TARGET_BOT, promo)
                print(f"💬 [{nama_akun}] Teks promosi dikirim!")
                
                # 5. Kirim stiker resmi (Tanpa jeda setelah teks, langsung eksekusi)
                if has_sticker:
                    await client.send_file(TARGET_BOT, promo_sticker)
                    print(f"🖼️ [{nama_akun}] Stiker berhasil dikirim!")
                
                # 6. Diam 1 detik (Lalu loop terus menerus ke langkah 1)
                await asyncio.sleep(1.0)
                print(f"🔁 [{nama_akun}] Looping ke /next...\n")

            except Exception as e:
                print(f"❌ [{nama_akun}] Error saat mengirim: {e}")
                # Jika diblokir atau kena limit Telegram (FloodWait)
                await asyncio.sleep(15)

    except Exception as e:
        print(f"🔴 [{nama_akun}] Gagal Login: {e}")

async def main():
    if not SESSIONS:
        print("⚠️ Tidak ada SESSION yang ditemukan di Environment!")
        return

    print(f"Menjalankan mesin promosi mode AGGRESIF untuk {len(SESSIONS)} akun...\n")
    tasks = [run_promoter(nama, string_ses) for nama, string_ses in SESSIONS]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())
