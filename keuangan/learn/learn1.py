import psycopg2
import sys
import pprint

def main():
conn = psycopg2.connect("host='database.neon.microvac' dbname='sideka_keuangan_20171120' user='postgres' password='postgres' port=5094")
cur = conn.cursor()

query = "select * from siskeudes_penganggarans"
cur.execute(query)
records = cur.fetchall()
pprint.pprint(records)

if __name__ == "__main__":
    main()