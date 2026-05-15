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
        self.wfile.write("<h1>🚀 Mesin Promosi Micifind (Auto-Stop Banned) Aktif!</h1>".encode('utf-8'))
        
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

        while True:
            try:
                # 1. Kirim /next
                await client.send_message(TARGET_BOT, '/next')
                print(f"🔄 [{nama_akun}] Command /next dikirim!")
                
                # 2. Diam 1 detik
                await asyncio.sleep(1.0)
                
                # --- SISTEM DETEKSI BANNED ---
                # Mengambil 2 pesan terakhir dalam obrolan untuk dicek
                recent_messages = await client.get_messages(TARGET_BOT, limit=2)
                is_banned = False
                for msg in recent_messages:
                    if msg.text and "You have been banned due to rules violation" in msg.text:
                        is_banned = True
                        break
                
                # Jika terdeteksi banned, tidurkan akun ini selama 25 jam (90000 detik)
                if is_banned:
                    print(f"🚫 [{nama_akun}] TERDETEKSI BANNED! Akun dihentikan selama 25 Jam.")
                    await asyncio.sleep(25 * 3600)
                    print(f"🟢 [{nama_akun}] Masa hukuman 25 Jam selesai! Melanjutkan promosi...")
                    continue # Melompat ke awal loop (kembali ke /next)

                # 3. Kalimat sapaan
                sapaan = random.choice(GREETINGS)
                await client.send_message(TARGET_BOT, sapaan)
                print(f"👋 [{nama_akun}] Sapaan '{sapaan}' dikirim!")
                
                # 4. Tunggu 2 detik
                await asyncio.sleep(2.0)
                
                # 5. Kalimat promosi 
                promo = random.choice(PROMO_MESSAGES)
                await client.send_message(TARGET_BOT, promo)
                print(f"💬 [{nama_akun}] Teks promosi dikirim!")
                
                # 6. Kirim stiker
                if has_sticker:
                    await client.send_file(TARGET_BOT, promo_sticker)
                    print(f"🖼️ [{nama_akun}] Stiker berhasil dikirim!")
                
                # 7. Kirim /stop
                await client.send_message(TARGET_BOT, '/stop')
                print(f"🛑 [{nama_akun}] Command /stop dikirim!")
                
                # 8. Looping terus menerus
                print(f"🔁 [{nama_akun}] Looping ke /next selanjutnya...\n")

            except Exception as e:
                print(f"❌ [{nama_akun}] Error saat mengirim: {e}")
                # Jika terkena limit FloodWait dari API Telegram
                await asyncio.sleep(15)

    except Exception as e:
        print(f"🔴 [{nama_akun}] Gagal Login: {e}")

async def main():
    if not SESSIONS:
        print("⚠️ Tidak ada SESSION yang ditemukan di Environment!")
        return

    print(f"Menjalankan mesin promosi untuk {len(SESSIONS)} akun...\n")
    tasks = [run_promoter(nama, string_ses) for nama, string_ses in SESSIONS]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())
