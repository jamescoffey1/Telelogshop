#!/usr/bin/env python3
"""
Test script to verify Telegram bot functionality
"""
import asyncio
from bot import bot_instance, TELEGRAM_AVAILABLE
from config import Config

async def test_bot_setup():
    """Test bot configuration and setup"""
    if not TELEGRAM_AVAILABLE:
        print("❌ Telegram library not available")
        return False
    
    if not Config.TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not configured")
        return False
    
    try:
        # Initialize the bot application
        application = bot_instance.application
        if not application:
            from telegram.ext import Application
            application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
            bot_instance.application = application
        
        await application.initialize()
        
        # Test bot info
        bot_info = await application.bot.get_me()
        print(f"✅ Bot connected successfully!")
        print(f"   Bot username: @{bot_info.username}")
        print(f"   Bot name: {bot_info.first_name}")
        print(f"   Bot ID: {bot_info.id}")
        
        await application.shutdown()
        return True
        
    except Exception as e:
        print(f"❌ Bot connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing Telegram bot configuration...")
    result = asyncio.run(test_bot_setup())
    if result:
        print("\n🎉 Bot is ready to use!")
        print("\nNext steps:")
        print("1. Start the application: python main.py")
        print("2. Set up webhook (optional) or use polling")
        print("3. Message your bot on Telegram with /start")
    else:
        print("\n❌ Bot setup incomplete. Check configuration.")