import sys
import csv
from db import get_connection, get_client_id, init_db


def generate_csv_report(client_name: str):
    init_db()

    client_id = get_client_id(client_name)
    if not client_id:
        print(f"Client not found: {client_name}")
        return

    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT
            c.name AS client_name,
            m.url AS url,
            e.status_code,
            e.status_type,
            e.occurred_at
        FROM error_events e
        JOIN monitored_urls m ON e.url_id = m.id
        JOIN clients c ON m.client_id = c.id
        WHERE c.id = ?
        ORDER BY e.occurred_at DESC
    """

    cursor.execute(query, (client_id,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print(f"No errors found for client: {client_name}")
        return

    file_path = f"reports/{client_name}_error_report.csv"

    with open(file_path, mode="w", newline="", encoding="utf-8") as file:


        writer = csv.writer(file)
        writer.writerow([
            "client_name",
            "url",
            "status_code",
            "status_type",
            "occurred_at"
        ])
        writer.writerows(rows)

    print(f"Report generated: {file_path}")


def main():
    if len(sys.argv) != 2:
        print("Usage:")
        print("  python generate_report.py <client_name>")
        return

    client_name = sys.argv[1]
    generate_csv_report(client_name)


if __name__ == "__main__":
    main()
