import socket
import ssl
import threading
import hashlib
import sys

from logger import logger

import tomllib

with open("config.toml", "rb") as f:
    config = tomllib.load(f)

SERVER_PORT = config["server"]["port"]
LOCAL_LISTEN_PORT = config["client"]["listen_port"]

LOCAL_APP_PORT = config["client"]["app_port"]
LISTEN_PORT = config["server"]["listen_port"]

def get_cert_fingerprint(binary_cert):
    return hashlib.sha256(binary_cert).hexdigest().upper()

def forward(src, dst):
    try:
        while True:
            data = src.recv(4096)

            if not data:
                break

            dst.sendall(data)

    except Exception as e:
        logger.warning(f"Forwarding stopped: {e}")

    finally:
        src.close()
        dst.close()


def run_server():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_3

    try:
        context.load_cert_chain(certfile="server.crt", keyfile="server.key")
        context.verify_mode = ssl.CERT_REQUIRED
        context.load_verify_locations(cafile="client.crt")

    except FileNotFoundError:
        logger.error("Certificate files not found: server.crt, server.key, client.crt")
        return

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", LISTEN_PORT))
    server.listen(5)

    logger.info(f"Server waiting for TLSv1.3 connections on port {LISTEN_PORT}")

    while True:
        raw_socket, addr = server.accept()

        try:
            ssl_socket = context.wrap_socket(raw_socket, server_side=True)

            client_cert = ssl_socket.getpeercert(binary_form=True)
            fingerprint = get_cert_fingerprint(client_cert)

            logger.ipc(f"peer fingerprint: {fingerprint}")
            logger.info(f"connected to secure socket from {addr}")
            logger.info(f"network encryption protocol: {ssl_socket.version()}")

            local_app_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            local_app_socket.connect(("127.0.0.1", LOCAL_APP_PORT))

            threading.Thread(target=forward, args=(ssl_socket, local_app_socket), daemon=True).start()

            threading.Thread(target=forward, args=(local_app_socket, ssl_socket), daemon=True).start()

        except Exception as e:
            logger.warning(f"TLS handshake or connection failed: {e}")


def run_client():
    server_ip = input("Server IP or DDNS: ").strip()

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.minimum_version = ssl.TLSVersion.TLSv1_3
    context.check_hostname = False

    try:
        context.load_cert_chain(certfile="client.crt", keyfile="client.key")
        context.verify_mode = ssl.CERT_REQUIRED
        context.load_verify_locations(cafile="server.crt")

    except FileNotFoundError:
        logger.error("Certificate files not found: client.crt, client.key, server.crt")
        return

    local_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    local_server.bind(("127.0.0.1", LOCAL_LISTEN_PORT))
    local_server.listen(5)

    logger.info(
        f"Client ready. Configure the local app to connect to 127.0.0.1:{LOCAL_LISTEN_PORT}"
    )

    while True:
        local_socket, addr = local_server.accept()

        try:
            raw_server_socket = socket.create_connection((server_ip, SERVER_PORT))

            ssl_server_socket = context.wrap_socket(
                raw_server_socket,
                server_hostname="DeskflowServer"
            )

            server_cert = ssl_server_socket.getpeercert(binary_form=True)
            fingerprint = get_cert_fingerprint(server_cert)

            logger.ipc(f"peer fingerprint: {fingerprint}")
            logger.info("connected to secure socket")
            logger.info(f"network encryption protocol: {ssl_server_socket.version()}")

            threading.Thread(target=forward, args=(local_socket, ssl_server_socket), daemon=True).start()

            threading.Thread(target=forward, args=(ssl_server_socket, local_socket), daemon=True).start()

        except Exception as e:
            logger.warning(f"Failed to establish secure tunnel: {e}")
            local_socket.close()


if __name__ == "__main__":
    while True:
        print("\n=== Running ===")
        print("1. Run as SERVER")
        print("2. Run as CLIENT")
        print("3. Exit")

        option = input("Choose an option (1-3): ").strip()

        if option == "1":
            logger.info("Starting server")
            run_server()
            break

        if option == "2":
            logger.info("Starting client")
            run_client()
            break

        if option == "3":
            logger.info("Exiting")
            sys.exit(0)

        logger.warning("Invalid option")