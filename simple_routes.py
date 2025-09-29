import logging
from flask import request, jsonify, render_template, redirect, url_for, flash, session
from config import Config
from telegram import Update
import asyncio
import threading

logger = logging.getLogger(__name__)

def register_routes(app, bot_application, bot_loop):
    """Register Flask routes, including Telegram webhook"""

    @app.route(f'/telegram-webhook/{Config.WEBHOOK_SECRET}', methods=['POST'])
    def telegram_webhook():
        """Handle Telegram webhook updates"""
        try:
            update_data = request.get_json()
            if not update_data:
                logger.error("No update data received")
                return '', 400

            logger.debug(f"Received webhook update: {update_data}")

            if not bot_application:
                logger.error("Bot application not initialized")
                return '', 500

            # Parse the update
            update = Update.de_json(update_data, bot_application.bot)

            # Schedule update processing
            if bot_loop and not bot_loop.is_closed():
                asyncio.run_coroutine_threadsafe(
                    bot_application.process_update(update),
                    bot_loop
                )
                logger.debug("Successfully scheduled webhook update")
            else:
                logger.error("Bot loop not available or closed")
                return '', 500

            return '', 200

        except Exception as e:
            logger.error(f"Error processing Telegram webhook: {str(e)}")
            import traceback
            traceback.print_exc()
            return '', 500

    @app.route('/webhook/delete', methods=['POST'])
    def delete_webhook():
        """Delete Telegram webhook"""
        try:
            result = {'success': False, 'error': None}

            def delete_async():
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    # Delete webhook
                    success = loop.run_until_complete(bot_application.bot.delete_webhook())
                    result['success'] = success
                    if not success:
                        result['error'] = "Failed to delete webhook"
                except Exception as e:
                    result['error'] = str(e)
                finally:
                    loop.close()

            thread = threading.Thread(target=delete_async)
            thread.start()
            thread.join(timeout=10)

            if result['success']:
                return jsonify({'success': True})
            else:
                return jsonify({'error': result['error'] or 'Timeout deleting webhook'}), 500

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
