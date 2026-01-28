import sys
from db import (
    init_db,
    add_client,
    get_client_id,
    add_monitored_url
)


def usage():
    print("""
Usage:
  python manage.py add-client <client_name>
  python manage.py add-url <client_name> <url> <interval_sec>
""")


def main():
    init_db()

    if len(sys.argv) < 2:
        usage()
        return

    command = sys.argv[1]

    if command == "add-client":
        if len(sys.argv) != 3:
            usage()
            return

        client_name = sys.argv[2]
        add_client(client_name)

    elif command == "add-url":
        if len(sys.argv) != 5:
            usage()
            return

        client_name = sys.argv[2]
        url = sys.argv[3]
        interval = sys.argv[4]

        if not interval.isdigit():
            print("interval_sec must be a number")
            return

        client_id = get_client_id(client_name)
        if not client_id:
            print(f"Client not found: {client_name}")
            return

        add_monitored_url(client_id, url, int(interval))

    else:
        print(f"Unknown command: {command}")
        usage()


if __name__ == "__main__":
    main()
