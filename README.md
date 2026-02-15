# 🎮 Discord Quiz Bot

A feature-rich Discord bot that delivers daily quiz questions across multiple categories with automatic question rotation, user tracking, and vertical button layouts.

## ✨ Features

- 🎯 **4 Quiz Categories**: Web Dev, Mobile Dev, AI, Cybersecurity
- 🔄 **Smart Question Rotation**: Questions cycle through not_used → in_use → used states
- ⏱️ **Auto-Expiration**: Questions automatically marked as "used" after 60 seconds
- 🔒 **One Answer Per Day**: Users can answer each category once per day
- 📚 **Vertical Buttons**: Clean, stacked button layout for easy selection
- 🎨 **Color Feedback**: Green ✅ for correct, Red ❌ for wrong answers
- 👁️ **Ephemeral Messages**: Quiz questions visible only to the requester
- 📊 **State Tracking**: Monitor question usage with `/states` command
- 🛠️ **Testing Tools**: Reset commands for easy development

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Discord Bot Token ([Get one here](https://discord.com/developers/applications))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/discord-quiz-bot.git
   cd discord-quiz-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your bot token**
   
   Create a `.env` file in the project root:
   ```env
   DISCORD_TOKEN=your_bot_token_here
   ```

4. **Setup Discord Bot**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Enable these **Privileged Gateway Intents**:
     - ✅ MESSAGE CONTENT INTENT
     - ✅ SERVER MEMBERS INTENT
   - Invite bot with `bot` + `applications.commands` scopes

5. **Run the bot**
   ```bash
   python quiz_bot_fixed.py
   ```

## 📖 Usage

### Commands

```
/quiz <category>      Get a quiz question for the selected category
/states               View current question states (not_used/in_use/used)
/reset_states         Reset all questions to "not_used" (testing)
/reset_answers        Clear answer tracking (testing)
```

### Categories

- **Web Dev** - Web development questions
- **Mobile Dev** - Mobile development questions
- **AI** - Artificial intelligence questions
- **Cybersecurity** - Security-related questions

### Example

```discord
User: /quiz AI
Bot: [Shows question with 4 buttons]

AI Quiz
Why does overfitting reduce performance on unseen data?

[A) It increases training accuracy        ]
[B) It memorizes training data instead... ] ← Click here
[C) It reduces model size                 ]
[D) It simplifies features                ]

Result: 🎉 Correct! The answer was B!
```

## 🔧 Configuration

### Question Timer

By default, questions expire after **60 seconds** (for development). To change this, edit line 340:

```python
# Current: 60 seconds
asyncio.create_task(mark_question_as_used_after_delay(
    category_name, 
    question['id'], 
    delay_seconds=60
))

# For production (end of day):
delay_seconds=21600  # 6 hours
```

### Adding Questions

Edit `questions.json`:

```json
{
  "Web Dev": [
    {
      "id": 5,
      "question": "Your question here?",
      "options": {
        "A": "Option A",
        "B": "Option B",
        "C": "Option C",
        "D": "Option D"
      },
      "answer": "B",
      "state": "not_used"
    }
  ]
}
```

## 📁 Project Structure

```
discord-quiz-bot/
├── quiz_bot_fixed.py           # Main bot file
├── questions.json              # Question bank
├── requirements.txt            # Python dependencies
├── .env                       # Bot token (create this)
├── .env.example               # Template for .env
├── .gitignore                 # Git ignore rules
├── README.md                  # This file
├── already_answered.json      # Auto-generated (user tracking)
├── leaderboard.json          # Auto-generated (optional)
└── daily_start_time.json     # Auto-generated (optional)
```

## 🎯 How It Works

### Question States

Questions cycle through three states:

1. **not_used** - Fresh question, never shown before
2. **in_use** - Currently active question for the day
3. **used** - Previously shown, won't appear again

### Flow Diagram

```
User requests /quiz AI
         ↓
Check: Already answered today?
    ├─ Yes → "Come back tomorrow!"
    └─ No  → Continue
         ↓
Get question (not_used → in_use)
         ↓
Display with 4 buttons
         ↓
Start 60-second timer
         ↓
User clicks button
    ├─ Correct → Green ✅
    └─ Wrong   → Red ❌ + Green ✅ on correct
         ↓
Mark user as answered
         ↓
After 60 seconds → Mark question as "used"
```

## 🧪 Testing

### Test Question Rotation

```bash
# Terminal 1: Run bot
python quiz_bot_fixed.py

# Terminal 2: Watch console
# In Discord:
/quiz AI                  # Get question 1
# Wait 60 seconds...
# Console shows: [AUTO] ✅ AI Q1 marked as 'used'
/quiz AI                  # Get question 2 (different!)
/states                   # Verify states
```

### Test One Answer Per Day

```discord
/quiz AI
[Answer the question]
/quiz AI                  # Should show: "Already answered today!"
/reset_answers            # Clear for retesting
/quiz AI                  # Works again!
```

## 🛠️ Troubleshooting

### Bot doesn't start
- Check `.env` file has correct token
- Verify no extra spaces in token
- Check Python version (3.8+)

### Commands don't appear
- Wait 2-5 minutes for Discord to sync
- Verify bot has `applications.commands` scope
- Try re-inviting the bot

### "No questions available"
- All questions are "used"
- Use `/reset_states` to reset
- Add more questions to `questions.json`

### Questions not rotating
- Check console for timer messages
- Verify bot stays online for 60+ seconds
- Use `/states` to monitor question states

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 TODO / Future Features

- [ ] Leaderboard with time tracking
- [ ] Weekly/monthly stats
- [ ] Custom quiz schedules per server
- [ ] Difficulty levels
- [ ] Streak tracking
- [ ] Achievement badges
- [ ] Export quiz results
- [ ] Multi-language support
- [ ] Question categories management UI

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [discord.py](https://github.com/Rapptz/discord.py)
- Question bank curated for educational purposes
- Thanks to all contributors and testers!

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/discord-quiz-bot/issues)
- **Documentation**: Check the [Wiki](https://github.com/yourusername/discord-quiz-bot/wiki)

## ⚠️ Important Notes

- **Never commit your `.env` file** - it contains your bot token
- **Keep your bot token secret** - treat it like a password
- Questions expire after 60 seconds by default (configurable)
- Each user can answer each category once per day
- Auto-generated JSON files are in `.gitignore`

---

Made with ❤️ for Discord quiz enthusiasts

**Star ⭐ this repo if you find it helpful!**
