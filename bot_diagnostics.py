#!/usr/bin/env python3
"""
Bot diagnostics tool to check Telegram bot status and functionality
"""
import asyncio
import logging
from telegram.ext import Application
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_bot_status():
    """Check if the bot is responding and accessible"""
    print("🔍 Checking Telegram bot status...")
    
    if not Config.TELEGRAM_BOT_TOKEN:
        print("❌ No bot token configured")
        return False
    
    try:
        # Create application instance
        application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
        
        # Initialize and get bot info
        await application.initialize()
        bot_info = await application.bot.get_me()
        
        print(f"✅ Bot is online and responding!")
        print(f"   Username: @{bot_info.username}")
        print(f"   Name: {bot_info.first_name}")
        print(f"   ID: {bot_info.id}")
        print(f"   Can join groups: {bot_info.can_join_groups}")
        
        # Check webhook status
        webhook_info = await application.bot.get_webhook_info()
        if webhook_info.url:
            print(f"📡 Webhook configured: {webhook_info.url}")
        else:
            print("📡 Bot using polling mode (no webhook)")
        
        await application.shutdown()
        return True
        
    except Exception as e:
        print(f"❌ Bot connection failed: {str(e)}")
        return False

async def send_test_message(chat_id):
    """Send a test message to verify bot can send messages"""
    if not Config.TELEGRAM_BOT_TOKEN:
        print("❌ No bot token configured")
        return False
    
    try:
        application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
        await application.initialize()
        
        await application.bot.send_message(
            chat_id=chat_id,
            text="🤖 Test message from bot diagnostics tool"
        )
        
        print(f"✅ Test message sent to chat {chat_id}")
        await application.shutdown()
        return True
        
    except Exception as e:
        print(f"❌ Failed to send test message: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Telegram Bot Diagnostics ===\n")
    
    # Check bot status
    bot_ok = asyncio.run(check_bot_status())
    
    if bot_ok:
        print("\n📋 Bot is ready to receive messages!")
        print("   Try sending /start to @TRIPLELOGSHOP_BOT on Telegram")
        print("\n🔧 To test message sending, provide a chat ID:")
        print("   python bot_diagnostics.py --send-test <chat_id>")
    else:
        print("\n❌ Bot setup needs attention. Check configuration.")