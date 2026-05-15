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
        self.wfile.write("<h1>🚀 Mesin Promosi Micifind (Anti-Banned Edition) Aktif!</h1>".encode('utf-8'))
        
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

# SPINTAX: Variasi Sapaan agar terlihat seperti manusia (Bypass Filter Pertama)
GREETINGS = ["Halo", "Haii", "P", "Hi", "Haloo", "haii", "p", "halo"]

# SPINTAX: Variasi Teks Promosi agar tidak terdeteksi sebagai spam massal
PROMO_MESSAGES = [
    "Lagi bosen? Cobain @micifindbot yuk. Bisa cari partner satu kota, fiturnya bersih & no delay! ✨",
    "Eh cobain @micifindbot deh, bot anonim baru bisa milih temen se-kota/provinsi. Lebih rapi tampilannya 👌",
    "Bosen yg ini delay trs? Pindah ke @micifindbot aja kak, cari partner se-kota lebih gampang 🚀",
    "Mau match sama org terdekat? di @micifindbot bisa filter kota lho, cobain aja gratis kok ✨"
]

# --- MASUKKAN SHORT NAME STICKER PACK ---
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

        # Menarik data Stiker Resmi dari Server Telegram
        try:
            sticker_set = await client(GetStickerSetRequest(
                stickerset=InputStickerSetShortName(short_name=STICKER_PACK_SHORT_NAME)
            ))
            promo_sticker = sticker_set.documents[0] 
            has_sticker = True
            print(f"📦 [{nama_akun}] Berhasil memuat Stiker Pack Resmi!")
        except Exception as e:
            print(f"⚠️ [{nama_akun}] Gagal memuat stiker pack: {e}")
            has_sticker = False

        # Pancingan awal agar bot target merespons
        await client.send_message(TARGET_BOT, '/start')
        await asyncio.sleep(5)

        while True:
            try:
                # 1. Perintah mencari partner
                await client.send_message(TARGET_BOT, '/next')
                print(f"🔄 [{nama_akun}] Mencari partner...")
                
                # Tunggu partner ditemukan (Jeda agak lama agar bot target siap)
                await asyncio.sleep(random.uniform(5.0, 8.0))
                
                # 2. KIRIM SAPAAN MANUSIA (Trik Bypass Anti-Spam)
                sapaan = random.choice(GREETINGS)
                await client.send_message(TARGET_BOT, sapaan)
                print(f"👋 [{nama_akun}] Mengirim sapaan: '{sapaan}'")
                
                # Jeda seolah-olah sedang mengetik pesan panjang
                await asyncio.sleep(random.uniform(2.5, 4.5))
                
                # 3. KIRIM PESAN PROMOSI (Pilih acak dari daftar)
                pesan_promo = random.choice(PROMO_MESSAGES)
                await client.send_message(TARGET_BOT, pesan_promo)
                print(f"💬 [{nama_akun}] Teks promosi terkirim!")
                
                # Jeda sejenak sebelum kirim stiker
                await asyncio.sleep(random.uniform(1.0, 2.0))
                
                # 4. KIRIM STIKER RESMI
                if has_sticker:
                    await client.send_file(TARGET_BOT, promo_sticker)
                    print(f"🖼️ [{nama_akun}] Stiker promosi berhasil dikirim!")
                
                # Jeda agar target sempat membaca sebelum kita kabur
                await asyncio.sleep(random.uniform(3.0, 5.0))
                await client.send_message(TARGET_BOT, '/stop')
                
                # 5. COOLDOWN (Pendinginan agar tidak diblokir oleh pihak Telegram sendiri)
                wait_time = random.uniform(35.0, 65.0)
                print(f"💤 [{nama_akun}] Istirahat {wait_time:.1f} detik sebelum siklus berikutnya...\n")
                await asyncio.sleep(wait_time)

            except Exception as e:
                print(f"❌ [{nama_akun}] Kendala saat looping: {e}")
                # Jika terkena limit sementara dari Telegram (FloodWait)
                await asyncio.sleep(120) 
    except Exception as e:
        print(f"🔴 [{nama_akun}] Gagal Login: {e}")

async def main():
    if not SESSIONS:
        print("⚠️ Tidak ada SESSION yang ditemukan di Environment!")
        return

    print(f"Menjalankan mesin promosi Anti-Banned untuk {len(SESSIONS)} akun secara paralel...\n")
    tasks = [run_promoter(nama, string_ses) for nama, string_ses in SESSIONS]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())
