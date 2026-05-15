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
        self.wfile.write("<h1>🚀 Mesin Promosi Micifind (15 Akun) Aktif!</h1>".encode('utf-8'))
        
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

# --- MASUKKAN SHORT NAME STICKER PACK KAMU DI SINI ---
# Contoh jika link stikernya t.me/addstickers/micifind_promo
# Maka tulis "micifind_promo" di bawah ini:
STICKER_PACK_SHORT_NAME = "micifindbot"

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

        # Pancingan awal agar bot target merespons
        await client.send_message(TARGET_BOT, '/search')
        await asyncio.sleep(5)

        while True:
            try:
                # Perintah mencari partner
                await client.send_message(TARGET_BOT, '/next')
                print(f"🔄 [{nama_akun}] Mencari partner...")
                
                await asyncio.sleep(random.uniform(5.0, 10.0))
                
                # 1. Kirim pesan promosi teks
                await client.send_message(TARGET_BOT, PROMO_MESSAGE)
                print(f"💬 [{nama_akun}] Teks promosi terkirim!")
                
                await asyncio.sleep(random.uniform(1.0, 2.0))
                
                # 2. Kirim Stiker Promosi Resmi
                if has_sticker:
                    await client.send_file(TARGET_BOT, promo_sticker)
                    print(f"🖼️ [{nama_akun}] Stiker promosi berhasil dikirim!")
                
                await asyncio.sleep(random.uniform(2.0, 4.0))
                await client.send_message(TARGET_BOT, '/stop')
                
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
