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
        self.wfile.write("<h1>🚀 Mesin Promosi Micifind (Smart Human-Like) Aktif!</h1>".encode('utf-8'))
        
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

STICKER_PACK_SHORT_NAME = "micifindbot"

# Variasi Sapaan
GREETINGS = ["ceco", "haii", "halo", "hii", "allooo"]

# Variasi Teks Promosi
PROMO_MESSAGES = [
    "Lagi bosen? Cobain @micifindbot yuk. Bisa cari partner satu kota, fiturnya bersih & no delay! ✨",
    "Eh cobain @micifindbot deh, bot anonim baru bisa milih temen se-kota/provinsi. Lebih rapi tampilannya 👌",
    "Bosen yg ini delay trs? Pindah ke @micifindbot aja kak, cari partner se-kota lebih gampang 🚀",
    "Mau match sama org terdekat? di @micifindbot bisa filter kota lho, cobain aja gratis kok ✨"
]

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

        # Menarik data Stiker Resmi
        try:
            sticker_set = await client(GetStickerSetRequest(
                stickerset=InputStickerSetShortName(short_name=STICKER_PACK_SHORT_NAME)
            ))
            promo_sticker = sticker_set.documents[0] 
            has_sticker = True
        except Exception as e:
            print(f"⚠️ [{nama_akun}] Gagal memuat stiker pack: {e}")
            has_sticker = False

        # --- LANGKAH 1: INISIALISASI PERTAMA KALI JALAN ---
        await client.send_message(TARGET_BOT, '/stop')
        await asyncio.sleep(1.0)
        await client.send_message(TARGET_BOT, '/search')
        print(f"🚀 [{nama_akun}] Memulai pencarian awal (/stop -> /search)...")

        last_checked_msg_id = 0

        # --- LOOPING UTAMA BOT CERDAS ---
        while True:
            try:
                partner_found = False
                
                # FASE A: Menunggu pesan "Partner found" atau Peringatan
                while not partner_found:
                    await asyncio.sleep(1.5) # Cek pesan baru setiap 1.5 detik
                    recent_messages = await client.get_messages(TARGET_BOT, limit=3)
                    
                    for msg in recent_messages:
                        if msg.id <= last_checked_msg_id:
                            continue # Abaikan pesan yang sudah pernah dibaca
                            
                        text = msg.text or ""
                        
                        # Deteksi Banned
                        if "You have been banned due to rules violation" in text:
                            print(f"🚫 [{nama_akun}] TERDETEKSI BANNED! Tidur 25 Jam.")
                            await asyncio.sleep(25 * 3600) # Tidur 25 jam
                            last_checked_msg_id = msg.id
                            await client.send_message(TARGET_BOT, '/search') # Cari partner lagi setelah bangun
                            break
                            
                        # Deteksi Limit Harian
                        elif "you have reached the daily chat limit for today" in text.lower():
                            print(f"⚠️ [{nama_akun}] LIMIT HARIAN! Tidur 24 Jam.")
                            await asyncio.sleep(24 * 3600) # Tidur 24 jam
                            last_checked_msg_id = msg.id
                            await client.send_message(TARGET_BOT, '/search')
                            break
                            
                        # Deteksi Partner Found
                        elif "Partner found" in text or "partner found" in text.lower():
                            partner_found = True
                            last_checked_msg_id = msg.id
                            print(f"🎯 [{nama_akun}] Partner Ditemukan! Memulai interaksi...")
                            break
                            
                # FASE B: Mengeksekusi Promosi (Jika Partner Found)
                if partner_found:
                    # 1. Diam 2 detik lalu kirim sapaan
                    await asyncio.sleep(2.0)
                    sapaan = random.choice(GREETINGS)
                    await client.send_message(TARGET_BOT, sapaan)
                    print(f"👋 [{nama_akun}] Sapaan '{sapaan}' dikirim.")
                    
                    # 2. Diam 4 detik lalu kirim promosi + stiker
                    await asyncio.sleep(4.0)
                    promo = random.choice(PROMO_MESSAGES)
                    await client.send_message(TARGET_BOT, promo)
                    if has_sticker:
                        try:
                            await client.send_file(TARGET_BOT, promo_sticker)
                        except:
                            pass
                    print(f"💬 [{nama_akun}] Promosi + Stiker terkirim!")
                    
                    # 3. FASE C: Menunggu Reaksi Partner (Maksimal 5 Detik)
                    partner_kabur = False
                    print(f"⏳ [{nama_akun}] Menunggu reaksi partner selama 5 detik...")
                    
                    for i in range(5): # Looping 5x (1 detik per loop)
                        await asyncio.sleep(1.0)
                        cek_pesan = await client.get_messages(TARGET_BOT, limit=2)
                        
                        for m in cek_pesan:
                            if m.id <= last_checked_msg_id: continue
                            
                            teks_reaksi = m.text or ""
                            if "Your partner has stopped the chat" in teks_reaksi:
                                partner_kabur = True
                                last_checked_msg_id = m.id
                                break
                                
                        if partner_kabur:
                            break # Berhenti mengecek jika partner sudah kabur

                    # 4. FASE D: Keputusan berdasarkan tindakan partner
                    if partner_kabur:
                        print(f"🛑 [{nama_akun}] Partner ketakutan dan kabur. Mengetik /search...")
                        await client.send_message(TARGET_BOT, '/search')
                    else:
                        print(f"⏭️ [{nama_akun}] 5 Detik berlalu. Meninggalkan partner (/next)...")
                        await client.send_message(TARGET_BOT, '/next')
                        
                    print(f"🔁 [{nama_akun}] Menunggu partner baru...\n")

            except Exception as e:
                print(f"❌ [{nama_akun}] Error: {e}")
                await asyncio.sleep(15)

    except Exception as e:
        print(f"🔴 [{nama_akun}] Gagal Login: {e}")

async def main():
    if not SESSIONS:
        print("⚠️ Tidak ada SESSION yang ditemukan di Environment!")
        return

    print(f"Menjalankan mesin promosi CERDAS untuk {len(SESSIONS)} akun...\n")
    tasks = [run_promoter(nama, string_ses) for nama, string_ses in SESSIONS]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())
