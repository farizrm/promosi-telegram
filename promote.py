import asyncio
import random
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telethon import TelegramClient
from telethon.sessions import StringSession

# --- SETUP DUMMY SERVER UNTUK UPTIMEROBOT ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<h1>🚀 Mesin Promosi Micifind (15 Akun) Aktif!</h1>")
        
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
PROMO_MESSAGE = "Halo! Mau match dengan teman Se-Kota? Cobain @micifindbot yuk. Bisa cari partner satu kota/provinsi, fiturnya bersih & no delay! ✨"

# Nama file stiker yang sudah kamu upload ke GitHub (harus 1 folder dengan script ini)
STICKER_FILE = "stiker.webp" 

# Mengumpulkan semua sesi yang ada di Environment
SESSIONS = []
for i in range(1, 16): # Range 1 sampai 15
    session_string = os.environ.get(f"SESSION_{i}")
    if session_string:
        SESSIONS.append((f"Akun_{i}", session_string))

async def run_promoter(nama_akun, session_string):
    try:
        client = TelegramClient(StringSession(session_string), API_ID, API_HASH)
        await client.start()
        print(f"✅ [{nama_akun}] Berhasil terhubung!")

        # Pancingan awal agar bot target merespons
        await client.send_message(TARGET_BOT, '/search')
        await asyncio.sleep(5)

        while True:
            try:
                # Perintah mencari partner
                await client.send_message(TARGET_BOT, '/next')
                print(f"🔄 [{nama_akun}] Mencari partner...")
                
                # Menunggu partner ditemukan (Jeda acak agar terlihat natural)
                await asyncio.sleep(random.uniform(5.0, 10.0))
                
                # 1. Kirim pesan promosi teks
                await client.send_message(TARGET_BOT, PROMO_MESSAGE)
                print(f"💬 [{nama_akun}] Teks promosi terkirim!")
                
                # Jeda 1-2 detik layaknya manusia mengetik/memilih stiker
                await asyncio.sleep(random.uniform(1.0, 2.0))
                
                # 2. Kirim Stiker Promosi
                if os.path.exists(STICKER_FILE):
                    await client.send_file(TARGET_BOT, STICKER_FILE)
                    print(f"🖼️ [{nama_akun}] Stiker berhasil dikirim!")
                else:
                    print(f"⚠️ [{nama_akun}] File stiker ({STICKER_FILE}) tidak ditemukan di server!")
                
                # Jeda sebentar sebelum stop
                await asyncio.sleep(random.uniform(2.0, 4.0))
                await client.send_message(TARGET_BOT, '/stop')
                
                # COOLDOWN: Sangat penting agar akun tidak diblokir Telegram
                # Dengan 15 akun, jeda 30-60 detik per akun sudah sangat aman
                wait_time = random.uniform(30.0, 60.0)
                print(f"💤 [{nama_akun}] Istirahat {wait_time:.1f} detik...")
                await asyncio.sleep(wait_time)

            except Exception as e:
                print(f"❌ [{nama_akun}] Kendala saat looping: {e}")
                await asyncio.sleep(60)
    except Exception as e:
        print(f"🔴 [{nama_akun}] Gagal Login: {e}")

async def main():
    if not SESSIONS:
        print("⚠️ Tidak ada SESSION yang ditemukan di Environment!")
        return

    print(f"Menjalankan mesin promosi untuk {len(SESSIONS)} akun secara paralel...")
    tasks = [run_promoter(nama, string_ses) for nama, string_ses in SESSIONS]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())
