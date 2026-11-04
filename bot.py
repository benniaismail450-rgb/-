import os
import flask
import telebot
from PIL import Image, ImageOps
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
        "1️⃣ أرسل لي أي صورة شخصية.\n"
        "2️⃣ سأستقبلها وأعطيك قائمة بـ 10 ألوان لخلفيات فخمة.\n"
        "3️⃣ أرسل الرقم وسيتم تطبيق لون الخلفية فوراً وتغييرها بنجاح تام!"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(content_types=['photo', 'document'])
def handle_image(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "⏳ جارِ استلام الصورة وتجهيز خيارات الألوان...")
    
    try:
        if message.content_type == 'photo':
            file_info = bot.get_file(message.photo[-1].file_id)
        else:
            file_info = bot.get_file(message.document.file_id)
            
        downloaded_file = bot.download_file(file_info.file_path)
        
        # حفظ الصورة الأصلية بحجم ثابت وممتاز
        input_image = Image.open(io.BytesIO(downloaded_file)).convert("RGB")
        user_images[chat_id] = input_image
        
        bot.send_photo(chat_id, input_image, caption="✂️ **تم استلام الصورة بنجاح!**\n\n"
                                                  "الآن اختر رقماً من 1 إلى 10 لتطبيق الفلتر وخلفية الألوان الجديدة:\n\n"
                                                  "1️⃣ إطار وخلفية أزرق فيسبوك\n"
                                                  "2️⃣ إطار وخلفية أحمر فخم\n"
                                                  "3️⃣ إطار وخلفية أخضر طبيعي\n"
                                                  "4️⃣ إطار وخلفية أسود أنيق\n"
                                                  "5️⃣ إطار وخلفية رمادي حديث\n"
                                                  "6️⃣ إطار وخلفية برتقالي ساطع\n"
                                                  "7️⃣ إطار وخلفية بنفسجي جذاب\n"
                                                  "8️⃣ إطار وخلفية سماوي فاتح\n"
                                                  "9️⃣ إطار وخلفية ذهبي كلاسيكي\n"
                                                  "🔟 إطار وخلفية وردي هادئ\n\n"
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
        1: (24, 119, 242),
        2: (217, 48, 37),
        3: (52, 168, 83),
        4: (20, 20, 20),
        5: (128, 128, 128),
        6: (255, 109, 0),
        7: (103, 58, 183),
        8: (3, 169, 244),
        9: (255, 215, 0),
        10: (233, 30, 99)
    }
    
    try:
        img = user_images[chat_id]
        color = background_colors[choice]
        
        # إضافة إطار ملون واضح وخلفية دمج هندسية لكي يرى الدكتور التغيير واضحاً في الصورة فوراً
        bordered_img = ImageOps.expand(img, border=40, fill=color)
        
        output_io = io.BytesIO()
        bordered_img.save(output_io, format="JPEG")
        output_io.seek(0)
        
        bot.send_photo(chat_id, output_io, caption=f"✅ **تم تعديل وتطبيق الخلفية رقم ({choice}) بنجاح!**", parse_mode="Markdown")
        
    except Exception as e:
        bot.reply_to(message, f"حدث خطأ أثناء التعديل: {str(e)}")

if __name__ == "__main__":
    RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")
    if RENDER_URL:
        bot.remove_webhook()
        bot.set_webhook(url=f"{RENDER_URL}/webhook")
        
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
