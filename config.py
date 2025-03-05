import os
import logging
import dotenv
import certifi
import ssl
import urllib3

# ✅ Load environment variables from a .env file (if exists)
dotenv.load_dotenv()

# ✅ Configure logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # ✅ Log to console
    ],
)
logger = logging.getLogger(__name__)

# ✅ Secure SSL configuration
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['SSL_CERT_DIR'] = certifi.where()
ssl_context = ssl.create_default_context(cafile=certifi.where())
http = urllib3.PoolManager(cert_reqs="CERT_REQUIRED", ca_certs=certifi.where())

# ✅ External API Keys (Load from Environment)
OPENCAGE_API_KEY = os.getenv("OPENCAGE_API_KEY", "")

if not OPENCAGE_API_KEY:
    logger.warning("⚠️  OPENCAGE_API_KEY is missing! Geolocation features may not work.")

# ✅ Define Global App Settings
APP_PORT = int(os.getenv("APP_PORT", 8051))  # Default port
APP_DEBUG = os.getenv("APP_DEBUG", "True").lower() in ["true", "1"]

logger.info(f"🌍 App running on port {APP_PORT} (Debug mode: {APP_DEBUG})")

