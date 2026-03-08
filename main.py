import os
import logging
import threading

logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
log = logging.getLogger("launcher")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bots'))

def run_admin():
    try:
        import admin_bot as ab
        log.info("Starting Admin Bot...")
        ab.main()
    except Exception as e:
        log.error("Admin error: " + str(e))

def run_recommendation():
    try:
        import recommendation_bot as rb
        log.info("Starting Recommendation Bot...")
        rb.main()
    except Exception as e:
        log.error("Recommendation error: " + str(e))

def run_supplier():
    try:
        import supplier_bot as sb
        log.info("Starting Supplier Bot...")
        sb.main()
    except Exception as e:
        log.error("Supplier error: " + str(e))

if __name__ == "__main__":
    log.info("NEO PULSE HUB Starting...")

    threads = [
        threading.Thread(target=run_admin, name="Admin", daemon=True),
        threading.Thread(target=run_recommendation, name="Reco", daemon=True),
        threading.Thread(target=run_supplier, name="Supplier", daemon=True),
    ]

    for t in threads:
        t.start()
        log.info("Started: " + t.name)

    try:
        import customer_bot as cb
        log.info("Starting Customer Bot in main thread...")
        cb.main()
    except Exception as e:
        log.error("Customer error: " + str(e))
