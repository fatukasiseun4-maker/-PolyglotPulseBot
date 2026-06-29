import os
import logging
import random
from datetime import datetime
from typing import Dict, List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
import aiohttp
import asyncio

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Language mappings
LANGUAGES = {
    'en': {'name': 'English', 'flag': '🇬🇧', 'fact': 'English is the most widely spoken language with over 1.5 billion speakers.'},
    'es': {'name': 'Spanish', 'flag': '🇪🇸', 'fact': 'Spanish is the second most spoken language with over 500 million native speakers.'},
    'fr': {'name': 'French', 'flag': '🇫🇷', 'fact': 'French is known as the language of love and diplomacy.'},
    'de': {'name': 'German', 'flag': '🇩🇪', 'fact': 'German is the most spoken native language in the European Union.'},
    'it': {'name': 'Italian', 'flag': '🇮🇹', 'fact': 'Italian is considered the language of music and art.'},
    'pt': {'name': 'Portuguese', 'flag': '🇵🇹', 'fact': 'Portuguese is the official language of 9 countries.'},
    'ru': {'name': 'Russian', 'flag': '🇷🇺', 'fact': 'Russian is the most spoken Slavic language with over 250 million speakers.'},
    'ja': {'name': 'Japanese', 'flag': '🇯🇵', 'fact': 'Japanese has three writing systems: Hiragana, Katakana, and Kanji.'},
    'ko': {'name': 'Korean', 'flag': '🇰🇷', 'fact': 'Korean was created in the 15th century by King Sejong the Great.'},
    'zh': {'name': 'Chinese', 'flag': '🇨🇳', 'fact': 'Chinese is the most spoken language with over 1.3 billion speakers.'},
    'ar': {'name': 'Arabic', 'flag': '🇸🇦', 'fact': 'Arabic is written from right to left and has 28 letters.'},
    'hi': {'name': 'Hindi', 'flag': '🇮🇳', 'fact': 'Hindi is one of the 22 official languages of India.'},
    'nl': {'name': 'Dutch', 'flag': '🇳🇱', 'fact': 'Dutch is the closest major language to English.'},
    'pl': {'name': 'Polish', 'flag': '🇵🇱', 'fact': 'Polish has 7 grammatical cases and complex pronunciation.'},
    'tr': {'name': 'Turkish', 'flag': '🇹🇷', 'fact': 'Turkish is an agglutinative language with very long words.'},
    'vi': {'name': 'Vietnamese', 'flag': '🇻🇳', 'fact': 'Vietnamese is a tonal language with 6 tones.'},
    'th': {'name': 'Thai', 'flag': '🇹🇭', 'fact': 'Thai has 44 consonants and 32 vowels.'},
    'id': {'name': 'Indonesian', 'flag': '🇮🇩', 'fact': 'Indonesian is the most widely spoken language in Southeast Asia.'},
    'ms': {'name': 'Malay', 'flag': '🇲🇾', 'fact': 'Malay is one of the oldest languages in Southeast Asia.'},
    'fil': {'name': 'Filipino', 'flag': '🇵🇭', 'fact': 'Filipino is based on Tagalog and is the national language of the Philippines.'},
    'sw': {'name': 'Swahili', 'flag': '🇰🇪', 'fact': 'Swahili is spoken by over 100 million people across East Africa.'},
    'ur': {'name': 'Urdu', 'flag': '🇵🇰', 'fact': 'Urdu is written in the Perso-Arabic script.'},
    'he': {'name': 'Hebrew', 'flag': '🇮🇱', 'fact': 'Hebrew was revived after being extinct for 1700 years.'},
    'el': {'name': 'Greek', 'flag': '🇬🇷', 'fact': 'Greek has over 3400 years of written history.'},
    'sv': {'name': 'Swedish', 'flag': '🇸🇪', 'fact': 'Swedish is closely related to Danish and Norwegian.'}
}

# Cultural facts
CULTURAL_FACTS = [
    "The word 'hello' comes from the Old English word 'hēlā' meaning 'whole'.",
    "The longest word in English has 189,819 letters!",
    "'E' is the most commonly used letter in English.",
    "In France, they say 'je t'aime' for 'I love you' - how romantic! 💕",
    "The Spanish phrase 'te quiero' means both 'I love you' and 'I want you'.",
    "In Japanese, 'ありがとう' (arigatō) means 'thank you'.",
    "The Portuguese word 'saudade' has no direct English translation.",
    "In Russian, 'спасибо' (spasibo) means 'thank you'.",
    "The Swahili word 'hakuna matata' means 'no worries'! 🦁",
    "In German, 'Fernweh' describes the desire to travel to faraway places.",
    "The Danish concept of 'hygge' means creating a warm, cozy atmosphere.",
    "In Italian, 'prego' means both 'you're welcome' and 'please'.",
    "The Korean word '정' (jeong) describes a deep emotional bond.",
    "In Arabic, 'سلام' (salam) means 'peace'.",
    "The Thai phrase 'สวัสดี' (sawasdee) is a greeting.",
    "Learning a new language opens up a whole new world of opportunities!",
    "Bilingual people have better problem-solving skills.",
    "The most translated document in the world is the Universal Declaration of Human Rights.",
    "There are over 7,000 languages spoken in the world today.",
]

# Store user preferences
user_preferences: Dict[int, Dict] = {}
translation_history: Dict[int, List[Dict]] = {}

# ==================== COMMAND HANDLERS ====================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    user_id = user.id
    
    # Set default preferences
    if user_id not in user_preferences:
        user_preferences[user_id] = {
            'target_lang': 'en',
            'history_enabled': True
        }
    
    welcome_message = (
        f"🌍 *Welcome to PolyglotPulseBot, {user.first_name}!* 🎉\n\n"
        "I'm your personal language translator and cultural guide!\n\n"
        "🔤 *Translate* text between 25+ languages\n"
        "🌏 *Discover* interesting cultural facts\n"
        "📚 *Learn* phrases and expressions\n"
        "📊 *Track* your translation history\n\n"
        "📌 *Quick Start:*\n"
        "• Send me any text - I'll translate it\n"
        "• Use /setlang to choose your language\n"
        "• Use /fact for cultural facts\n\n"
        "🛠 *Commands:*\n"
        "/start - Start the bot\n"
        "/help - Show help\n"
        "/setlang - Set your language\n"
        "/mylang - Check your language\n"
        "/languages - List all languages\n"
        "/translate - Translate text\n"
        "/fact - Cultural fact\n"
        "/history - View history\n"
        "/clear - Clear history"
    )
    
    keyboard = [
        [InlineKeyboardButton("🌍 Set Language", callback_data="set_lang")],
        [InlineKeyboardButton("📖 View Languages", callback_data="view_langs")],
        [InlineKeyboardButton("🌏 Random Fact", callback_data="random_fact")],
        [InlineKeyboardButton("📊 My History", callback_data="view_history")],
        [InlineKeyboardButton("❓ Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = (
        "🔍 *How to use PolyglotPulseBot:*\n\n"
        "1️⃣ *Direct Translation*\n"
        "Just send any text and I'll translate it.\n\n"
        "2️⃣ *Set Your Language*\n"
        "Use /setlang to choose your target language.\n\n"
        "3️⃣ *Cultural Facts*\n"
        "Use /fact to discover interesting facts.\n\n"
        "4️⃣ *Translation History*\n"
        "Use /history to see your translations.\n\n"
        "5️⃣ *Specific Translation*\n"
        "Use /translate [text] to translate text.\n\n"
        "🛠 *All Commands:*\n"
        "/start - Welcome\n"
        "/help - This help\n"
        "/setlang - Set language\n"
        "/mylang - Check language\n"
        "/languages - List all languages\n"
        "/translate - Translate text\n"
        "/fact - Cultural fact\n"
        "/history - Translation history\n"
        "/clear - Clear history\n\n"
        "💡 *Tip:* Reply to any message with /translate!"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def set_language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /setlang command"""
    keyboard = []
    row = []
    for i, (code, data) in enumerate(LANGUAGES.items()):
        button_text = f"{data['flag']} {data['name']}"
        row.append(InlineKeyboardButton(button_text, callback_data=f"lang_{code}"))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🌍 *Select your preferred language:*\n\n"
        "Choose the language you want messages translated to:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def my_language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /mylang command"""
    user_id = update.effective_user.id
    pref = user_preferences.get(user_id, {})
    lang_code = pref.get('target_lang', 'en')
    lang_data = LANGUAGES.get(lang_code, {'name': 'English', 'flag': '🇬🇧', 'fact': ''})
    
    await update.message.reply_text(
        f"📌 *Your current language:*\n"
        f"{lang_data['flag']} {lang_data['name']} ({lang_code})\n\n"
        f"📖 *Did you know?*\n"
        f"{lang_data.get('fact', 'Language is fascinating!')}\n\n"
        f"Use /setlang to change your preferred language.",
        parse_mode='Markdown'
    )

async def list_languages_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /languages command"""
    lang_list = []
    for code, data in LANGUAGES.items():
        lang_list.append(f"{data['flag']} {data['name']} (`{code}`)")
    
    chunks = [lang_list[i:i+15] for i in range(0, len(lang_list), 15)]
    
    for chunk in chunks:
        message = "🌍 *Supported Languages:*\n\n" + "\n".join(chunk)
        await update.message.reply_text(message, parse_mode='Markdown')

async def translate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /translate command"""
    if not context.args:
        if update.message.reply_to_message and update.message.reply_to_message.text:
            text = update.message.reply_to_message.text
            await perform_translation(update, text)
        else:
            await update.message.reply_text(
                "❌ Please provide text to translate.\n"
                "Example: `/translate Hello world`\n"
                "Or reply to a message with /translate",
                parse_mode='Markdown'
            )
        return
    
    text = ' '.join(context.args)
    await perform_translation(update, text)

async def fact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /fact command"""
    fact = random.choice(CULTURAL_FACTS)
    keyboard = [
        [InlineKeyboardButton("🔄 Another Fact", callback_data="random_fact")],
        [InlineKeyboardButton("🌍 Set Language", callback_data="set_lang")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🌏 *Cultural Fact:*\n\n{fact}\n\n"
        f"💡 Send me any text to translate!",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /history command"""
    user_id = update.effective_user.id
    history = translation_history.get(user_id, [])
    
    if not history:
        await update.message.reply_text(
            "📊 *Translation History:*\n\n"
            "You haven't translated anything yet! "
            "Send me some text to start building your history.",
            parse_mode='Markdown'
        )
        return
    
    history_text = "📊 *Your Translation History:*\n\n"
    for i, entry in enumerate(reversed(history[-10:]), 1):
        history_text += f"{i}. {entry['original'][:30]} → {entry['translated'][:30]}\n"
        history_text += f"   {entry['language']} | {entry['timestamp']}\n\n"
    
    history_text += f"\n📌 *Total translations:* {len(history)}"
    
    keyboard = [
        [InlineKeyboardButton("🗑️ Clear History", callback_data="clear_history")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        history_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /clear command"""
    user_id = update.effective_user.id
    if user_id in translation_history:
        translation_history[user_id] = []
        await update.message.reply_text("🗑️ *Translation history cleared!*", parse_mode='Markdown')
    else:
        await update.message.reply_text("📊 *No history to clear.*", parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular text messages"""
    if not update.message or not update.message.text:
        return
    
    text = update.message.text
    await perform_translation(update, text)

async def perform_translation(update: Update, text: str):
    """Perform the actual translation"""
    user_id = update.effective_user.id
    pref = user_preferences.get(user_id, {})
    target_lang = pref.get('target_lang', 'en')
    
    # Show typing indicator
    await update.message.chat.send_action(action="typing")
    
    # Translate the text
    translated_text = await translate_text(text, target_lang)
    
    lang_data = LANGUAGES.get(target_lang, {'name': 'English', 'flag': '🇬🇧', 'fact': ''})
    
    # Save to history
    if user_id not in translation_history:
        translation_history[user_id] = []
    translation_history[user_id].append({
        'original': text,
        'translated': translated_text,
        'language': f"{lang_data['flag']} {lang_data['name']}",
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    # Keep only last 100 translations
    if len(translation_history[user_id]) > 100:
        translation_history[user_id] = translation_history[user_id][-100:]
    
    response = (
        f"🔤 *Translation to {lang_data['flag']} {lang_data['name']}:*\n\n"
        f"{translated_text}\n\n"
        f"📝 *Original:*\n"
        f"`{text[:200]}{'...' if len(text) > 200 else ''}`"
    )
    
    keyboard = [
        [InlineKeyboardButton("🔄 Change Language", callback_data="set_lang")],
        [InlineKeyboardButton("📖 View Languages", callback_data="view_langs")],
        [InlineKeyboardButton("🌏 Random Fact", callback_data="random_fact")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        response,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def translate_text(text: str, target_lang: str) -> str:
    """Translate text using free API"""
    try:
        # Using MyMemory Translation API
        url = f"https://api.mymemory.translated.net/get?q={text}&langpair=en|{target_lang}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'responseData' in data and 'translatedText' in data['responseData']:
                        return data['responseData']['translatedText']
        
        return f"⚠️ Could not translate. Original text:\n\n{text}"
    except asyncio.TimeoutError:
        logger.error("Translation timeout")
        return f"⏰ Translation timeout. Original text:\n\n{text}"
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return f"⚠️ Translation error. Original text:\n\n{text}"

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = query.from_user.id
    
    if data == "set_lang":
        # Show language selection
        keyboard = []
        row = []
        for i, (code, lang_data) in enumerate(LANGUAGES.items()):
            button_text = f"{lang_data['flag']} {lang_data['name']}"
            row.append(InlineKeyboardButton(button_text, callback_data=f"lang_{code}"))
            if len(row) == 3:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🌍 *Select your preferred language:*",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif data == "view_langs":
        lang_list = []
        for code, lang_data in LANGUAGES.items():
            lang_list.append(f"{lang_data['flag']} {lang_data['name']} (`{code}`)")
        
        chunks = [lang_list[i:i+15] for i in range(0, len(lang_list), 15)]
        for chunk in chunks:
            message = "🌍 *Supported Languages:*\n\n" + "\n".join(chunk)
            await query.edit_message_text(message, parse_mode='Markdown')
    
    elif data == "random_fact":
        fact = random.choice(CULTURAL_FACTS)
        keyboard = [
            [InlineKeyboardButton("🔄 Another Fact", callback_data="random_fact")],
            [InlineKeyboardButton("🌍 Set Language", callback_data="set_lang")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"🌏 *Cultural Fact:*\n\n{fact}",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif data == "view_history":
        history = translation_history.get(user_id, [])
        if not history:
            await query.edit_message_text(
                "📊 *Translation History:*\n\nYou haven't translated anything yet!",
                parse_mode='Markdown'
            )
            return
        
        history_text = "📊 *Your Translation History:*\n\n"
        for i, entry in enumerate(reversed(history[-5:]), 1):
            history_text += f"{i}. {entry['original'][:30]} → {entry['translated'][:30]}\n"
        history_text += f"\n📌 *Total: {len(history)} translations*"
        
        keyboard = [
            [InlineKeyboardButton("🗑️ Clear History", callback_data="clear_history")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            history_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif data == "clear_history":
        if user_id in translation_history:
            translation_history[user_id] = []
            await query.edit_message_text("🗑️ *History cleared!*", parse_mode='Markdown')
        else:
            await query.edit_message_text("📊 *No history to clear.*", parse_mode='Markdown')
    
    elif data == "help":
        help_text = (
            "🔍 *How to use PolyglotPulseBot:*\n\n"
            "1️⃣ Send any text - I'll translate it\n"
            "2️⃣ Use /setlang to choose your language\n"
            "3️⃣ Use /fact for cultural facts\n"
            "4️⃣ Use /history for translation history\n\n"
            "🛠 *Commands:*\n"
            "/start - Welcome\n"
            "/help - This help\n"
            "/setlang - Set language\n"
            "/mylang - Check language\n"
            "/languages - List all\n"
            "/translate - Translate\n"
            "/fact - Cultural fact\n"
            "/history - History\n"
            "/clear - Clear history"
        )
        await query.edit_message_text(help_text, parse_mode='Markdown')
    
    elif data.startswith("lang_"):
        lang_code = data.split("_")[1]
        lang_data = LANGUAGES.get(lang_code, {'name': 'Unknown', 'flag': '🌍', 'fact': ''})
        
        if user_id not in user_preferences:
            user_preferences[user_id] = {}
        user_preferences[user_id]['target_lang'] = lang_code
        
        await query.edit_message_text(
            f"✅ *Language set to {lang_data['flag']} {lang_data['name']}!*\n\n"
            f"📖 *Fun fact:* {lang_data['fact']}\n\n"
            f"Now send me any text and I'll translate it!",
            parse_mode='Markdown'
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ Sorry, an error occurred. Please try again later.\n"
            "If the problem persists, contact the bot administrator."
        )

def main():
    """Start the bot"""
    # Get token from environment variable
    token = os.environ.get('TELEGRAM_TOKEN')
    
    if not token:
        logger.error("❌ TELEGRAM_TOKEN environment variable not set!")
        logger.error("Please set it in Railway: Variables -> TELEGRAM_TOKEN")
        return
    
    logger.info("🌍 Starting PolyglotPulseBot...")
    
    try:
        # Create application
        application = Application.builder().token(token).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("setlang", set_language_command))
        application.add_handler(CommandHandler("mylang", my_language_command))
        application.add_handler(CommandHandler("languages", list_languages_command))
        application.add_handler(CommandHandler("translate", translate_command))
        application.add_handler(CommandHandler("fact", fact_command))
        application.add_handler(CommandHandler("history", history_command))
        application.add_handler(CommandHandler("clear", clear_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_handler(CallbackQueryHandler(handle_callback))
        application.add_error_handler(error_handler)
        
        # Start the bot
        logger.info("✅ Bot started successfully! Ready to translate! 🌍")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        raise

if __name__ == "__main__":
    main()
