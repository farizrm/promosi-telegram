import asyncio
import random
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telethon import TelegramClient
from telethon.sessions import StringSession

# --- SETUP DUMMY SERVER AGAR UPTIMEROBOT BISA BEKERJA 24/7 ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<h1>🚀 Mesin Promosi Micifind Aktif 24/7!</h1>")
        
    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# --- KONFIGURASI TELETHON ---
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
TARGET_BOT = '@bot_anonim_saingan' # Ganti dengan targetmu
PROMO_MESSAGE = "Mau Match dengan orang se-kota? Cobain bot anonim baru ini deh @micifindbot. Bisa match dengan partner sekota! ✨"

# Mengambil semua String Session dari Environment Render
SESSIONS = []
for i in range(1, 11):
    session_string = os.environ.get(f"SESSION_{i}")
    if session_string:
        SESSIONS.append((f"Akun_{i}", session_string))

# --- ALUR KERJA USERBOT ---
async def run_promoter(nama_akun, session_string):
    client = TelegramClient(StringSession(session_string), API_ID, API_HASH)
    await client.start()
    print(f"✅ [{nama_akun}] Berhasil terhubung ke Telegram!")

    # Pancingan awal
    try:
        await client.send_message(TARGET_BOT, '/start')
    except Exception:
        pass
    await asyncio.sleep(5)

    while True:
        try:
            await client.send_message(TARGET_BOT, '/next')
            print(f"🔄 [{nama_akun}] Mencari partner target...")
            
            await asyncio.sleep(random.uniform(3.0, 6.0))
            
            await client.send_message(TARGET_BOT, PROMO_MESSAGE)
            print(f"🚀 [{nama_akun}] Pesan promosi berhasil dikirim!")
            
            await asyncio.sleep(random.uniform(1.0, 3.0))
            await client.send_message(TARGET_BOT, '/stop')
            
            # Cooldown acak (10 - 25 detik)
            cooldown = random.uniform(10.0, 25.0)
            print(f"💤 [{nama_akun}] Cooldown {cooldown:.1f} detik...")
            await asyncio.sleep(cooldown)

        except Exception as e:
            print(f"❌ [{nama_akun}] Error: {e}")
            await asyncio.sleep(60) # Istirahat jika kena limit

# --- EKSEKUSI MULTI-AKUN ---
async def main():
    if not SESSIONS:
        print("⚠️ Tidak ada SESSION yang ditemukan di Environment!")
        return

    print(f"Mempersiapkan eksekusi untuk {len(SESSIONS)} akun secara bersamaan...")
    tasks = [run_promoter(nama, string_ses) for nama, string_ses in SESSIONS]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())