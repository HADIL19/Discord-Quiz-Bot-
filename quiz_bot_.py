import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import json
from datetime import datetime
import asyncio

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="?", intents=intents)
token = os.getenv("DISCORD_TOKEN", "YOUR_BOT_TOKEN_HERE")

QUESTIONS_FILE = "questions.json"
ALREADY_ANSWERED_FILE = "already_answered.json"

# ==================== HELPER FUNCTIONS ====================

def load_json(filepath):
    """Load JSON file"""
    if not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_json(filepath, data):
    """Save data to JSON file"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_today_key():
    """Get today's date as a key"""
    return datetime.now().strftime("%Y-%m-%d")

def has_user_answered_today(user_id, category):
    """Check if user already answered this category today"""
    today = get_today_key()
    answered_data = load_json(ALREADY_ANSWERED_FILE)
    
    if today not in answered_data:
        return False
    
    user_key = str(user_id)
    if user_key not in answered_data[today]:
        return False
    
    return category in answered_data[today][user_key]

def mark_user_answered(user_id, category):
    """Mark that user answered this category today"""
    today = get_today_key()
    answered_data = load_json(ALREADY_ANSWERED_FILE)
    
    if today not in answered_data:
        answered_data[today] = {}
    
    user_key = str(user_id)
    if user_key not in answered_data[today]:
        answered_data[today][user_key] = []
    
    if category not in answered_data[today][user_key]:
        answered_data[today][user_key].append(category)
    
    save_json(ALREADY_ANSWERED_FILE, answered_data)

def get_question_for_today(category):
    """Get today's question for a category"""
    print(f"\n[DEBUG] Getting question for category: {category}")
    
    questions_data = load_json(QUESTIONS_FILE)
    
    if category not in questions_data:
        print(f"[ERROR] Category '{category}' not found")
        return None
    
    questions = questions_data[category]
    print(f"[DEBUG] Total questions in {category}: {len(questions)}")
    
    # Check if there's already a question "in_use"
    for q in questions:
        if q.get("state") == "in_use":
            print(f"[DEBUG] Found existing 'in_use' question: ID {q['id']}")
            return q
    
    # Find a "not_used" question
    available_questions = [q for q in questions if q.get("state") == "not_used"]
    print(f"[DEBUG] Available 'not_used' questions: {len(available_questions)}")
    
    if not available_questions:
        print("[ERROR] No questions available")
        return None
    
    # Select first available and mark as "in_use"
    selected_question = available_questions[0]
    selected_question["state"] = "in_use"
    
    print(f"[DEBUG] Selected question ID {selected_question['id']}")
    save_json(QUESTIONS_FILE, questions_data)
    
    return selected_question

async def mark_question_as_used_after_delay(category, question_id, delay_seconds=60):
    """Auto-mark question as used after delay"""
    print(f"[TIMER] Starting {delay_seconds}s timer for {category} question ID {question_id}")
    
    await asyncio.sleep(delay_seconds)
    
    questions_data = load_json(QUESTIONS_FILE)
    
    if category not in questions_data:
        return
    
    for q in questions_data[category]:
        if q['id'] == question_id and q.get('state') == 'in_use':
            q['state'] = 'used'
            save_json(QUESTIONS_FILE, questions_data)
            print(f"\n[AUTO] ✅ {category} Q{question_id} marked as 'used' after {delay_seconds}s")
            break

# ==================== BUTTON VIEW ====================

class QuizView(discord.ui.View):
    """
    Vertical buttons (row=0,1,2,3)
    Color changes (green/red)
    Disable after click
    One answer per user per category per day
    """
    
    def __init__(self, question, category, user_id, username):
        super().__init__(timeout=None)
        self.question = question
        self.category = category
        self.correct_answer = question["answer"]
        self.user_id = user_id
        self.username = username
        self.answered = False
        self.options = question["options"]
        
        print(f"[DEBUG] Created QuizView with correct answer: {self.correct_answer}")
    
    async def handle_answer(self, interaction: discord.Interaction, button: discord.ui.Button, answer_key: str):
        """Handle button click"""
        
        # Only the user who requested the quiz can answer
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "❌ This is not your quiz! Use `/quiz <category>` to get your own.",
                ephemeral=True
            )
            return
        
        # Prevent double answering
        if self.answered:
            await interaction.response.send_message(
                "❌ You've already answered this question!",
                ephemeral=True
            )
            return
        
        self.answered = True
        
        # Check if correct
        is_correct = (answer_key == self.correct_answer)
        
        # Update all buttons
        for item in self.children:
            if isinstance(item, discord.ui.Button) and item.custom_id:
                button_key = item.custom_id.split("_")[-1]
                
                # Disable all buttons
                item.disabled = True
                
                # Color logic
                if button_key == answer_key:
                    # User's choice
                    if is_correct:
                        item.style = discord.ButtonStyle.success  # Green
                        item.label = f"✅ {item.label}"
                    else:
                        item.style = discord.ButtonStyle.danger  # Red
                        item.label = f"❌ {item.label}"
                elif button_key == self.correct_answer:
                    # Correct answer (show in green if user was wrong)
                    item.style = discord.ButtonStyle.success
                    item.label = f"✅ {item.label}"
        
        # Update the message
        await interaction.response.edit_message(view=self)
        
        # Mark user as answered
        mark_user_answered(self.user_id, self.category)
        
        # Send feedback
        if is_correct:
            await interaction.followup.send(
                f"🎉 Correct! The answer was {self.correct_answer}!",
                ephemeral=True
            )
        else:
            await interaction.followup.send(
                f"❌ Wrong! The correct answer was {self.correct_answer}.",
                ephemeral=True
            )
        
        print(f"[ANSWER] {self.username} selected {answer_key}, correct was {self.correct_answer}")
    
    # Vertical buttons with full labels
    @discord.ui.button(
        label="A)",
        style=discord.ButtonStyle.secondary,
        row=0,
        custom_id="answer_A"
    )
    async def button_a(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_answer(interaction, button, "A")
    
    @discord.ui.button(
        label="B)",
        style=discord.ButtonStyle.secondary,
        row=1,
        custom_id="answer_B"
    )
    async def button_b(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_answer(interaction, button, "B")
    
    @discord.ui.button(
        label="C)",
        style=discord.ButtonStyle.secondary,
        row=2,
        custom_id="answer_C"
    )
    async def button_c(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_answer(interaction, button, "C")
    
    @discord.ui.button(
        label="D)",
        style=discord.ButtonStyle.secondary,
        row=3,
        custom_id="answer_D"
    )
    async def button_d(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_answer(interaction, button, "D")

# ==================== SLASH COMMANDS ====================

@bot.tree.command(name="quiz", description="Get today's quiz question for a category")
@app_commands.describe(category="Choose a quiz category")
@app_commands.choices(category=[
    app_commands.Choice(name="Web Dev", value="Web Dev"),
    app_commands.Choice(name="Mobile Dev", value="Mobile Dev"),
    app_commands.Choice(name="AI", value="AI"),
    app_commands.Choice(name="Cybersecurity", value="Cybersecurity"),
])
async def quiz_command(interaction: discord.Interaction, category: app_commands.Choice[str]):
    """Fetch question for selected category and check if user already answered"""
    
    category_name = category.value
    user_id = interaction.user.id
    username = interaction.user.display_name
    
    print(f"\n[INFO] {username} (ID: {user_id}) requested {category_name} quiz")
    
    # Check if user already answered this category today
    if has_user_answered_today(user_id, category_name):
        await interaction.response.send_message(
            f"⚠️ You've already answered the {category_name} quiz today! Come back tomorrow!",
            ephemeral=True
        )
        return
    
    # Get today's question
    question = get_question_for_today(category_name)
    
    if question is None:
        await interaction.response.send_message(
            f"❌ No questions available for {category_name}. All questions have been used!",
            ephemeral=True
        )
        return
    
    print(f"[SUCCESS] Sending question ID {question['id']}")
    
    # Create embed
    embed = discord.Embed(
        title=f"{category_name} Quiz",
        description=question["question"],
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )
    
    # Add options to embed for better visibility
    options_text = "\n".join([f"{key}) {value}" for key, value in question["options"].items()])
    embed.add_field(name="Options", value=options_text, inline=False)
    embed.set_footer(text=f"Question ID: {question['id']} | Click a button to answer!")
    
    # Create view
    view = QuizView(question, category_name, user_id, username)
    
    # Set button labels with full option text
    for item in view.children:
        if isinstance(item, discord.ui.Button) and item.custom_id:
            option_key = item.custom_id.split("_")[-1]
            item.label = f"{option_key}) {question['options'][option_key]}"
    
    # Send as ephemeral message
    await interaction.response.send_message(
        embed=embed,
        view=view,
        ephemeral=True
    )
    
    print(f"[SUCCESS] Question sent to {username}")
    
    # Start auto-marking timer (1 minute for development)
    asyncio.create_task(mark_question_as_used_after_delay(category_name, question['id'], delay_seconds=60))
    print(f"[TIMER] Auto-marking timer started (60 seconds)")

@bot.tree.command(name="states", description="Show current question states")
async def states_command(interaction: discord.Interaction):
    """Show question states"""
    
    questions_data = load_json(QUESTIONS_FILE)
    
    embed = discord.Embed(
        title="📊 Question States",
        description="Current state of all questions",
        color=discord.Color.purple()
    )
    
    for category, questions in questions_data.items():
        states = {"not_used": 0, "in_use": 0, "used": 0}
        
        for q in questions:
            state = q.get("state", "not_used")
            states[state] = states.get(state, 0) + 1
        
        embed.add_field(
            name=category,
            value=f"🆕 Not Used: {states['not_used']}\n"
                  f"🔵 In Use: {states['in_use']}\n"
                  f"✅ Used: {states['used']}",
            inline=True
        )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="reset_states", description="Reset all questions to not_used")
async def reset_command(interaction: discord.Interaction):
    """Reset all question states"""
    
    questions_data = load_json(QUESTIONS_FILE)
    
    count = 0
    for category in questions_data:
        for q in questions_data[category]:
            q["state"] = "not_used"
            count += 1
    
    save_json(QUESTIONS_FILE, questions_data)
    
    await interaction.response.send_message(
        f"✅ Reset {count} questions to 'not_used' state!",
        ephemeral=True
    )
    
    print(f"[RESET] All {count} questions reset to 'not_used'")

@bot.tree.command(name="reset_answers", description="Reset already_answered.json (for testing)")
async def reset_answers_command(interaction: discord.Interaction):
    """Reset the already answered tracking"""
    
    save_json(ALREADY_ANSWERED_FILE, {})
    
    await interaction.response.send_message(
        "✅ Cleared already_answered.json! You can answer all categories again.",
        ephemeral=True
    )
    
    print("[RESET] Cleared already_answered.json")

# ==================== BOT EVENTS ====================

@bot.event
async def on_ready():
    await bot.tree.sync()
    print("\n" + "="*60)
    print("✅ QUIZ BOT IS READY!")
    print(f"📝 Logged in as: {bot.user}")
    print("="*60)
    print("\n🎮 COMMANDS:")
    print("  /quiz <category>  - Get a quiz question")
    print("  /states           - Show question states")
    print("  /reset_states     - Reset question states")
    print("  /reset_answers    - Reset answer tracking")
    print("\n📋 CATEGORIES:")
    print("  - Web Dev")
    print("  - Mobile Dev")
    print("  - AI")
    print("  - Cybersecurity")
    print("\n✅ FEATURES:")
    print("  • Question state management (not_used → in_use → used)")
    print("  • One answer per category per day")
    print("  • Auto-mark questions as 'used' after 60 seconds")
    print("  • Vertical buttons with color changes")
    print("\n" + "="*60 + "\n")

# ==================== RUN BOT ====================

if __name__ == "__main__":
    if token == "YOUR_BOT_TOKEN_HERE":
        print("\n⚠️  No bot token found!")
        print("Set DISCORD_TOKEN in .env file")
    else:
        bot.run(token)