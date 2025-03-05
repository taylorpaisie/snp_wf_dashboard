import os
import certifi
import ssl
import urllib3

# ✅ Set up SSL certificates for secure requests
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['SSL_CERT_DIR'] = certifi.where()
ssl_context = ssl.create_default_context(cafile=certifi.where())
http = urllib3.PoolManager(cert_reqs="CERT_REQUIRED", ca_certs=certifi.where())
