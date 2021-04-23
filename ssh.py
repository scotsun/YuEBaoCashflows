from sshtunnel import SSHTunnelForwarder

tunnel = SSHTunnelForwarder(
        "34.67.124.229",
        ssh_username="apple",
        ssh_pkey="/Users/apple/Desktop/CSSE433/project-cli-keys/key-instance-1",
        ssh_private_key_password="csse433",
        remote_bind_address=("127.0.0.1", 27017)
    )
tunnel.start()
host = "localhost"
port = tunnel.local_bind_port
