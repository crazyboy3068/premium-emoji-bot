# 🤖 Premium Emoji Post Generator Bot — সেটআপ গাইড

---

## ✅ ধাপ ১ — BotFather থেকে Bot Token নিন

1. Telegram-এ `@BotFather` সার্চ করুন
2. `/newbot` কমান্ড দিন
3. বটের নাম দিন (যেমন: `Premium Emoji Bot`)
4. Username দিন (যেমন: `my_emoji_bot` — শেষে `bot` থাকতে হবে)
5. আপনাকে একটি **Token** দেবে। এটি সেভ করুন।
   - উদাহরণ: `1234567890:ABCDefGhIJKlmNoPQRsTUVwxyZ`

---

## ✅ ধাপ ২ — আপনার Telegram ID নিন

1. `@userinfobot` সার্চ করে `/start` দিন
2. আপনার **ID** দেখাবে (শুধু সংখ্যা, যেমন: `123456789`)
3. এটি সেভ করুন — এটাই Owner ID

---

## ✅ ধাপ ৩ — Railway.app-এ Deploy করুন (বিনামূল্যে!)

### Railway সেটআপ:

1. **https://railway.app** — এ যান, GitHub দিয়ে Sign Up করুন
2. **New Project** → **Deploy from GitHub repo** চাপুন
3. আপনার বট ফোল্ডারটি GitHub-এ আপলোড করুন (নিচে দেখুন)
4. Railway-তে **Variables** সেকশনে যান এবং এগুলো যোগ করুন:

```
BOT_TOKEN        = আপনার_বট_টোকেন
OWNER_ID         = আপনার_টেলিগ্রাম_আইডি
SECRET_KEY_PEPPER = যেকোনো_র‍্যান্ডম_স্ট্রিং
RATE_LIMIT       = 10
```

5. **Deploy** করুন — কয়েক মিনিটে বট চালু হয়ে যাবে!

---

## ✅ ধাপ ৩ (বিকল্প) — VPS-এ Deploy করুন

```bash
# ১. Python ইনস্টল করুন
sudo apt update && sudo apt install python3 python3-pip -y

# ২. বট ফোল্ডারে যান
cd emoji_bot

# ৩. .env ফাইল তৈরি করুন
cp .env.example .env
nano .env   # এখানে আপনার তথ্য দিন

# ৪. Dependencies ইনস্টল করুন
pip3 install -r requirements.txt

# ৫. বট চালান
python3 bot.py

# ৬. Background-এ চালাতে (systemd):
# /etc/systemd/system/emojibot.service ফাইল তৈরি করুন:
```

**systemd service file:**
```ini
[Unit]
Description=Emoji Bot
After=network.target

[Service]
WorkingDirectory=/path/to/emoji_bot
ExecStart=/usr/bin/python3 bot.py
Restart=always
User=ubuntu

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable emojibot
sudo systemctl start emojibot
sudo systemctl status emojibot  # চলছে কিনা দেখুন
```

---

## ✅ ধাপ ৪ — GitHub-এ কোড আপলোড করুন

1. **https://github.com** — এ অ্যাকাউন্ট খুলুন
2. **New Repository** তৈরি করুন
3. বট ফোল্ডারের সমস্ত ফাইল আপলোড করুন
   - ⚠️ `.env` ফাইল আপলোড করবেন না! শুধু `.env.example` দিন
4. `.gitignore` ফাইলে লিখুন:
   ```
   .env
   *.db
   __pycache__/
   *.pyc
   bot.log
   ```

---

## ✅ ধাপ ৫ — প্রথমবার Admin Setup

1. বট চালু হলে Telegram-এ `/start` দিন
2. `/admin` কমান্ড দিয়ে Admin Panel খুলুন
3. **🔐 Developer Settings** → Secret Key সেট করুন
4. **📦 Emoji Pack Mgmt** → Category-তে Emoji ID যোগ করুন

---

## 📁 ফাইল স্ট্রাকচার

```
emoji_bot/
├── bot.py              ← মূল ফাইল (এটি দিয়ে বট চালু হয়)
├── config.py           ← সেটিংস ও পরিবেশ ভেরিয়েবল
├── requirements.txt    ← প্রয়োজনীয় লাইব্রেরি
├── .env                ← আপনার secret তথ্য (GitHub-এ দেবেন না)
├── .env.example        ← .env এর নমুনা
├── Procfile            ← Railway/Render এর জন্য
├── database/
│   ├── db.py           ← সমস্ত Database অপারেশন
│   └── bot.db          ← SQLite ডেটাবেস (auto-তৈরি হবে)
├── handlers/
│   ├── start.py        ← /start ও Main Menu
│   ├── create_post.py  ← Random ও Custom Mode
│   ├── emoji_packs.py  ← Emoji Packs ব্রাউজ
│   ├── my_account.py   ← User Stats
│   ├── help_center.py  ← Help ও FAQ
│   ├── developer.py    ← Developer Info
│   └── admin.py        ← সম্পূর্ণ Admin Panel
├── keyboards/
│   └── keyboards.py    ← সমস্ত Button Layout
├── middlewares/
│   ├── rate_limit.py   ← Rate Limiting
│   └── user_tracker.py ← Auto User Registration
└── services/
    └── emoji_service.py ← Emoji Detection ও Replacement
```

---

## ❓ সাধারণ সমস্যা

| সমস্যা | সমাধান |
|--------|--------|
| `ModuleNotFoundError` | `pip3 install -r requirements.txt` আবার চালান |
| Bot not responding | `.env`-এ `BOT_TOKEN` সঠিক আছে কিনা দেখুন |
| Admin panel not showing | `.env`-এ `OWNER_ID` আপনার সঠিক ID কিনা দেখুন |
| Database error | `database/` ফোল্ডার আছে কিনা দেখুন |

---

## 💡 Premium Emoji ID কোথায় পাবেন?

- Telegram-এ `@stickers` বট থেকে
- Premium sticker pack-এ ডান ক্লিক → "Copy Emoji ID"
- Admin Panel → Emoji Pack Mgmt → Add Emoji ID দিয়ে যোগ করুন
