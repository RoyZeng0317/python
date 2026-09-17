import datetime
import ipaddress
import os
import socket

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

CERT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "certs")
CERT_PATH = os.path.join(CERT_DIR, "cert.pem")
KEY_PATH = os.path.join(CERT_DIR, "key.pem")


def _local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def ensure_cert():
    """Return (cert_path, key_path), generating a persistent self-signed cert on first run."""
    if os.path.exists(CERT_PATH) and os.path.exists(KEY_PATH):
        return CERT_PATH, KEY_PATH

    os.makedirs(CERT_DIR, exist_ok=True)

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    local_ip = _local_ip()
    hostname = socket.gethostname()

    subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, local_ip)])

    san_entries = [x509.DNSName("localhost"), x509.IPAddress(ipaddress.ip_address("127.0.0.1"))]
    try:
        san_entries.append(x509.IPAddress(ipaddress.ip_address(local_ip)))
    except ValueError:
        pass
    if hostname:
        san_entries.append(x509.DNSName(hostname))
        san_entries.append(x509.DNSName(f"{hostname}.local"))

    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(days=1))
        .not_valid_after(now + datetime.timedelta(days=3650))
        .add_extension(x509.SubjectAlternativeName(san_entries), critical=False)
        .sign(key, hashes.SHA256())
    )

    with open(KEY_PATH, "wb") as f:
        f.write(
            key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )

    with open(CERT_PATH, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    return CERT_PATH, KEY_PATH
