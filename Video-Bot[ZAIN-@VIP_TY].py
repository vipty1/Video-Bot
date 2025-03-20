import os
import math
import traceback
import asyncio
from telethon import TelegramClient, events
import ffmpeg
import time
try:
    from pyud import analyze_audio_quality
except ImportError:
    os.system("pip install pyud")

api_id = 'Your Api'
api_hash = 'Your Hash'
bot_token = 'Your Token'

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

class VideoCompressorBot:
    def __init__(self):
        @client.on(events.NewMessage(pattern='/start'))
        async def send_welcome(event):
            try:
                await client.send_message(event.chat_id, "👋 مرحباً بك! هذا البوت سيقوم بضغط الفيديوهات وتحسين الصوت بجودة عالية! \n🎥 أرسل لي أي فيديو لبدء الضغط.")
            except Exception as e:
                print(f"Error in send_welcome: {e}")
                traceback.print_exc()

        @client.on(events.NewMessage)
        async def handle_video(event):
            if event.video:
                await client.send_message(event.chat_id, "📥 يتم الآن تحميل الفيديو...")
                await self.download_and_process_video(event)

    async def download_and_process_video(self, event):
        try:
            start_time = time.time()
            video_file = await client.download_media(event.video)
            original_size = os.path.getsize(video_file)
            await client.send_message(event.chat_id, f"📊 حجم الملف الأصلي: {self.convert_size(original_size)}")
            estimated_time = self.estimate_processing_time(original_size)
            await client.send_message(event.chat_id, f"🔧 يتم الآن معالجة الفيديو وتحسين الجودة الصوتية... تقدير الوقت: {estimated_time}.")
            audio_quality = self.analyze_audio_quality(video_file)
            if audio_quality < 0.5:
                await client.send_message(event.chat_id, "🎶 يتم الآن تحسين الصوت...")
            output_file = self.process_video(video_file)
            if output_file:
                compressed_size = os.path.getsize(output_file)
                await client.send_message(event.chat_id, f"📊 حجم الملف بعد التعديل: {self.convert_size(compressed_size)}")
                reduction_percentage = 100 * (original_size - compressed_size) / original_size
                await client.send_message(event.chat_id, f"📉 نسبة التعديل: {reduction_percentage:.2f}%")
                await client.send_file(event.chat_id, output_file)
                self.cleanup_files([video_file, output_file])
                elapsed_time = time.time() - start_time
                await client.send_message(event.chat_id, f"🕒 تم إتمام المعالجة في {elapsed_time:.2f} ثانية.")
            else:
                await client.send_message(event.chat_id, "❌ حدث خطأ أثناء معالجة الفيديو.")
        except Exception as e:
            print(f"Error in download_and_process_video: {e}")
            traceback.print_exc()

    def analyze_audio_quality(self, video_file):
        try:
            if 'pyud' in globals():
                audio_quality = analyze_audio_quality(video_file)
                return audio_quality
            else:
                return 1.0  # Default value if pyud is not available
        except Exception as e:
            print(f"Error in analyze_audio_quality: {e}")
            traceback.print_exc()
            return 1.0

    def process_video(self, input_file):
        try:
            output_file = f"compressed_{os.path.basename(input_file)}"
            # معالجة الفيديو باستخدام مكتبة ffmpeg
            ffmpeg.input(input_file).output(output_file, vcodec='libx264', crf=28, acodec='aac', ac=2, ab='128k', ar='44100').run()
            return output_file
        except Exception as e:
            print(f"Error in process_video: {e}")
            traceback.print_exc()
            return None

    def cleanup_files(self, files):
        try:
            for file in files:
                if os.path.exists(file):
                    os.remove(file)
        except Exception as e:
            print(f"Error in cleanup_files: {e}")
            traceback.print_exc()

    def convert_size(self, size_bytes):
        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_name[i]}"

    def estimate_processing_time(self, size_bytes):
        processing_speed = 5 * 1024 * 1024
        estimated_time_seconds = size_bytes / processing_speed
        if estimated_time_seconds < 60:
            return f"{int(estimated_time_seconds)} ثانية"
        else:
            return f"{int(estimated_time_seconds // 60)} دقيقة"

def run_bot():
    video_bot = VideoCompressorBot()
    print("🤖 Bot is running...")
    client.run_until_disconnected()

if __name__ == '__main__':
    try:
        run_bot()
    except Exception as e:
        print(f"Error in main: {e}")
        traceback.print_exc()
