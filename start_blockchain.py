import os
import time
import subprocess
from slickrpc import Proxy

rpc_port = int(os.environ.get("COIN_RPC_PORT", 7000))
ac_name = "ZOMBIE"

# Set up regular node directory and configuration
node_dir = "/data/node_0"
os.makedirs(node_dir, exist_ok=True)
conf_path = f"{node_dir}/{ac_name}.conf"
with open(conf_path, "w") as conf:
    conf.write(f"rpcuser=test\nrpcpassword=test\nrpcport={rpc_port}\n")
    conf.write("rpcbind=0.0.0.0\nrpcallowip=0.0.0.0/0\n")

print("config is ready")

# Start Komodod node in regular mode
start_args = [
    "./komodod",
    f"-ac_name={ac_name}",
    "-ac_cc=2",
    "-ac_sapling=1",
    "-ac_supply=0",
    "-ac_reward=25600000000",
    "-ac_halving=388885",
    "-ac_private=1",
    "-ac_cbmaturity=1",
    "-ac_blocktime=10",
    f"-conf={conf_path}",
    f"-rpcport={rpc_port}",
    "-port=6000",
    f"-datadir={node_dir}",
    "-testnode=1",
    "-whitelist=127.0.0.1",
    "-daemon",
]

subprocess.call(start_args)
print("Started node in regular mode")
time.sleep(5)

# Set up RPC connection
rpc = Proxy(f"http://test:test@127.0.0.1:{rpc_port}")

# Check if RPC is ready
while True:
    try:
        getinfo_output = rpc.getinfo()
        print(f"Node ready: {getinfo_output}")
        break
    except Exception as e:
        print(f"⏳ Waiting for node to start RPC... {e}")
        time.sleep(2)

new_address = rpc.getnewaddress()
print("New address:", new_address)

# Retrieve the public key using validateaddress via RPC
address_info = rpc.validateaddress(new_address)
pubkey = address_info.get("pubkey")
if not pubkey:
    raise Exception("Public key not found in validateaddress output")
print("Retrieved pubkey:", pubkey)

print("Stopping the current node...")
response = rpc.stop()
print("Zombie chain stopped " + response)
time.sleep(10)

start_args = [
    "./komodod",
    f"-ac_name={ac_name}",
    "-ac_cc=2",
    "-ac_supply=0",
    "-ac_reward=25600000000",
    "-ac_halving=388885",
    "-ac_cbmaturity=1",
    "-ac_blocktime=10",
    "-ac_private=1",
    "-testnode=1",
    "-ac_sapling=1",
    "-whitelist=127.0.0.1",
    f"-conf={conf_path}",
    f"-rpcport={rpc_port}",
    "-port=6000",
    f"-datadir={node_dir}",
    f"-pubkey={pubkey}",
    "-daemon",
]
subprocess.call(start_args)
time.sleep(5)

# Maybe remove this call(not really needed)
z_addr = rpc.z_getnewaddress("sapling")
print("z_newaddress " + z_addr)

print("Starting mining on regular node")

rpc.setgenerate(True, 1)

while True:
    try:
        info = rpc.getinfo()
        print(f"Block height: {info['blocks']}, Connections: {info['connections']}")
        time.sleep(60)
    except Exception as e:
        print(f"Error: {e}")
        break
