# 🛡️ chatMJFWbot

A Telegram chat moderation bot that helps keep your group clean from unwanted content.

## 🧩 Features

- Detects and deletes messages containing banned words
- Multilingual banned words list (🇬🇧 English / 🇷🇺 Russian)
- Logs violations and actions
- Allows temporary bans for 1 hour via command
- Stores chat language settings in MySQL
- Automatically creates necessary tables if not present

## ⚙️ Tech Stack

- Python 3.10+
- python-telegram-bot v20+
- pymysql
- dotenv
- Logging
- MySQL (MariaDB)

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/chatMJFWbot.git
cd chatMJFWbot
```

### 2. Create `.env` file

```env
TELEGRAM_API_TOKEN=your_telegram_token
```

### 3. Add `banned_words.json`

Example content:
```json
{
  "en": ["badword1", "badword2"],
  "ru": ["плохослово1", "плохослово2"]
}
```

### 4. Configure MySQL in the script or via environment

Default:
- host: localhost
- user: root
- password: (empty)
- database: chatMJFWbot

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the bot

```bash
python chatMJFWbot.py
```

## 📬 Contact

- Telegram: [@ivan_mudriakov](https://t.me/ivan_mudriakov)
- Email: [mr.john.freeman.works.rus@gmail.com](mailto:mr.john.freeman.works.rus@gmail.com)

---

👮 Created with care by Ivan Mudriakov. Let's keep Telegram clean together!
