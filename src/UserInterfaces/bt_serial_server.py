import bluetooth

server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
server_sock.bind(("", bluetooth.PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]

bluetooth.advertise_service(
    server_sock,
    "PyDataLinkStatus",
    service_id="00001101-0000-1000-8000-00805F9B34FB",  # Standard SPP UUID
    service_classes=["00001101-0000-1000-8000-00805F9B34FB"],
    profiles=[bluetooth.SERIAL_PORT_PROFILE]
)

print(f"Waiting for connection on RFCOMM channel {port}...")

client_sock, client_info = server_sock.accept()
print(f"Accepted connection from {client_info}")

try:
    while True:
        client_sock.send("Hello from Raspberry Pi!\n")
except OSError:
    pass

print("Disconnected.")
client_sock.close()
server_sock.close()
