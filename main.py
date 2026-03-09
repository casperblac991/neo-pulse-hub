import sys
import os
import logging

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
log = logging.getLogger("launcher")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from webhook_server import app, init_db

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 10000))
    log.info("NEO PULSE HUB starting on port " + str(port))
    app.run(host="0.0.0.0", port=port, threaded=True)
