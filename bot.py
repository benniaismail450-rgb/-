import os
import flask
import telebot
from PIL import Image
import io

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "9183110084:AAEzpNrZtyZnRUNEvNDHyh1GmLoq6rbz9xw").strip()
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
app = flask.Flask(__name__)

user_images = {}

@app.route("/")
def index():
    return "Bot is running perfectly!", 200

@app.route("/webhook", methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "OK", 200
    else:
        return "Forbidden", 403

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "مرحباً بك يا إسماعيل في بوت تعديل الخلفيات السريع! 🖼️✨\n\n"
        "1️⃣ أرسل لي أي صورة.\n"
        "2️⃣ سأقوم بتجهيزها وإعطائك قائمة بـ 10 خيارات لخلفيات ملونة رائعة!"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(content_types=['photo', 'document'])
def handle_image(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "⏳ جارِ استلام الصورة ومعالجتها...")
    
    try:
        if message.content_type == 'photo':
            file_info = bot.get_file(message.photo[-1].file_id)
        else:
            file_info = bot.get_file(message.document.file_id)
            
        downloaded_file = bot.download_file(file_info.file_path)
        
        # حفظ الصورة الأصلية للمعالجة السريعة
        input_image = Image.open(io.BytesIO(downloaded_file)).convert("RGBA")
        user_images[chat_id] = input_image
        
        bot.send_photo(chat_id, input_image, caption="✂️ **تم استلام الصورة بنجاح!**\n\n"
                                                  "الآن اختر رقماً من 1 إلى 10 لتطبيق الخلفية الملونة الجديدة:\n\n"
                                                  "1️⃣ خلفية أزرق فيسبوك\n"
                                                  "2️⃣ خلفية أحمر فخم\n"
                                                  "3️⃣ خلفية أخضر طبيعي\n"
                                                  "4️⃣ خلفية أسود أنيق\n"
                                                  "5️⃣ خلفية رمادي حديث\n"
                                                  "6️⃣ خلفية برتقالي ساطع\n"
                                                  "7️⃣ خلفية بنفسجي جذاب\n"
                                                  "8️⃣ خلفية سماوي فاتح\n"
                                                  "9️⃣ خلفية ذهبي كلاسيكي\n"
                                                  "🔟 خلفية وردي هادئ\n\n"
                                                  "👇 **أرسل الرقم فقط الآن (من 1 إلى 10):**", parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ:\n`{str(e)}`", parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text and message.text.isdigit())
def apply_background(message):
    chat_id = message.chat.id
    choice = int(message.text.strip())
    
    if chat_id not in user_images:
        bot.reply_to(message, "⚠️ يرجى إرسال الصورة أولاً قبل اختيار رقم الخلفية!")
        return
        
    if not (1 <= choice <= 10):
        bot.reply_to(message, "❌ أرجو إرسال رقم صحيح من 1 إلى 10 فقط.")
        return
        
    background_colors = {
        1: (24, 119, 242, 255),
        2: (217, 48, 37, 255),
        3: (52, 168, 83, 255),
        4: (20, 20, 20, 255),
        5: (128, 128, 128, 255),
        6: (255, 109, 0, 255),
        7: (103, 58, 183, 255),
        8: (3, 169, 244, 255),
        9: (255, 215, 0, 255),
        10: (233, 30, 99, 255)
    }
    
    try:
        fore_img = user_images[chat_id]
        bg_color = background_colors[choice]
        
        # إنشاء خلفية جديدة باللون المختار ودمجها
        bg_img = Image.new("RGBA", fore_img.size, bg_color)
        combined = Image.alpha_composite(bg_img, fore_img)
        final_img = combined.convert("RGB")
        
        output_io = io.BytesIO()
        final_img.save(output_io, format="JPEG")
        output_io.seek(0)
        
        bot.send_photo(chat_id, output_io, caption=f"✅ **تم تطبيق الخلفية رقم ({choice}) بنجاح!**", parse_mode="Markdown")
        
    except Exception as e:
        bot.reply_to(message, f"حدث خطأ أثناء دمج الخلفية: {str(e)}")

if __name__ == "__main__":
    RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")
    if RENDER_URL:
        bot.remove_webhook()
        bot.set_webhook(url=f"{RENDER_URL}/webhook")
        
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
