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

Made with ❤️ for Discord quiz enthusiasts

