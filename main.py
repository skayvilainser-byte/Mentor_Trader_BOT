import discord
from discord.ext import commands
import google.generativeai as genai
import requests
import os

# --- KONFIGURASI API ---
# Di server (Koyeb), kita akan memasukkan token ini di bagian Environment Variables
# Agar lebih aman, kita menggunakan os.getenv
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Inisialisasi Gemini AI
genai.configure(api_key=GEMINI_API_KEY)
# Menggunakan model 1.5 Flash yang cepat dan cerdas dalam membaca gambar
model = genai.GenerativeModel('gemini-1.5-flash')

# Inisialisasi Bot Discord
intents = discord.Intents.default()
intents.message_content = True  # Penting: agar bot bisa baca pesan dan gambar
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Sistem Aktif! {bot.user} siap melakukan analisis IQ 500.')
    # Set status bot agar terlihat profesional
    await bot.change_presence(activity=discord.Game(name="Analisis Market M5 | !analisa"))

@bot.command()
async def analisa(ctx):
    # Cek apakah ada lampiran (attachment) berupa gambar
    if not ctx.message.attachments:
        await ctx.send("❌ **Error:** Silakan unggah screenshot chart terlebih dahulu bersama perintah `!analisa`.")
        return

    async with ctx.typing():
        attachment = ctx.message.attachments[0]
        
        # Cek format file
        if any(attachment.filename.lower().endswith(ext) for ext in ['png', 'jpg', 'jpeg', 'webp']):
            # Download gambar
            response = requests.get(attachment.url)
            image_data = response.content
            
            # --- INSTRUKSI SISTEM IQ 500 ---
            prompt = (
                "Kamu adalah Mentor Trader AI dari ESTSS Market dengan IQ 500. "
                "Analisis gambar chart candlestick ini dengan sangat mendalam. "
                "Tentukan: 1. Tren Utama, 2. Level Support/Resistance, 3. Indikator Visual. "
                "Berikan saran mutlak: BUY, SELL, atau WAIT. "
                "Sertakan target Take Profit (TP) dan Stop Loss (SL) yang logis. "
                "Gunakan bahasa Indonesia yang tajam, profesional, dan sedikit misterius."
            )

            try:
                # Proses gambar ke Gemini
                image_parts = [{"mime_type": "image/jpeg", "data": image_data}]
                ai_response = model.generate_content([prompt, image_parts[0]])

                # Buat tampilan hasil yang rapi (Embed)
                embed = discord.Embed(
                    title="📊 HASIL ANALISIS MARKET - ESTSS INTEL",
                    description=ai_response.text,
                    color=0x00ff00 # Warna hijau untuk kesan profit
                )
                embed.set_footer(text="Gunakan sebagai referensi. Risiko trading di tangan Anda.")
                embed.set_thumbnail(url=attachment.url)
                
                await ctx.send(embed=embed)
            
            except Exception as e:
                await ctx.send(f"⚠️ Terjadi kesalahan saat analisis: {str(e)}")
        else:
            await ctx.send("❌ Format file tidak didukung. Gunakan JPG atau PNG.")

# Menjalankan bot
if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
