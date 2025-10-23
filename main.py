import sys
from tcp import run_tcp_server, tcp_client
from udp import run_udp_server, udp_client

def main():
    while True:
        print("\n🌐 OpenChat Menu:")
        print("0 - Exit")
        print("1 - Start TCP Server")
        print("2 - Start UDP Server")
        print("3 - Connect as TCP Client")
        print("4 - Connect as UDP Client")
        
        while True:
            choice = input("Select option: ").strip()

            # 1️⃣ Run TCP server
            if choice == "1":
                run_tcp_server()
                break

            # 2️⃣ Run UDP server
            elif choice == "2":
                run_udp_server()
                break

            # 3️⃣ Connect as TCP client
            elif choice == "3":
                tcp_client(input("Server IP: ").strip())
                break

            # 4️⃣ Connect as UDP client
            elif choice == "4":
                udp_client(input("Server IP: ").strip())
                break

            # 5️⃣ Exit the program safely
            elif choice == "0":
                print("Goodbye 👋")
                sys.exit(0)
            else:
                print("[System] Invalid choice, try again.")

if __name__ == "__main__":
    main()
