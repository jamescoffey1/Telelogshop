import os
from app import app

if __name__ == "__main__":
    # Start the Flask web server (bot runs in webhook mode)
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Flask app on port {port} (webhook mode)")
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
