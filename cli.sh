openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout client.key \
  -out client.crt \
  -subj "/CN=DeskflowClient"

openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout server.key \
  -out server.crt \
  -subj "/CN=DeskflowServer"