import sys
import os
import logging
import threading

logging.basicConfig(format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)
log = logging.getLogger("launcher")

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bots'))

def run_admin():
    try:
        import admin_bot
        admin_bot.main()
    except Exception as e:
        log.error("Admin: " + str(e))

def run_recommendation():
    try:
        import recommendation_bot
        recommendation_bot.main()
    except Exception as e:
        log.error("Reco: " + str(e))

def run_supplier():
    try:
        import supplier_bot
        supplier_bot.main()
    except Exception as e:
        log.error("Supplier: " + str(e))

t1 = threading.Thread(target=run_admin, daemon=True)
t2 = threading.Thread(target=run_recommendation, daemon=True)
t3 = threading.Thread(target=run_supplier, daemon=True)

t1.start()
t2.start()
t3.start()

try:
    import customer_bot
    customer_bot.main()
except Exception as e:
    log.error("Customer: " + str(e))
