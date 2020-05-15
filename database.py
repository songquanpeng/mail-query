import sqlite3
import json
import time

create_attachments_table = """
CREATE TABLE IF NOT EXISTS "attachments" (
"id"	INTEGER PRIMARY KEY AUTOINCREMENT,
"name"	TEXT,
"content"	TEXT
);
"""

create_mails_table = """
CREATE TABLE IF NOT EXISTS "mails"(
"id"	INTEGER PRIMARY KEY AUTOINCREMENT,
"path"	TEXT NOT NULL UNIQUE,
"subject"	TEXT,
"sender"	TEXT,
"receiver"	TEXT,
"date"	TEXT,
"content"	TEXT,
"attachment"	INTEGER,
FOREIGN KEY (attachment) REFERENCES attachments (id)
);
"""
connection = None
cursor = None


def init(database_path='./data.db'):
    # initialize the SQLite database and return the cursor
    global connection
    global cursor
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    cursor.execute(create_attachments_table)
    cursor.execute(create_mails_table)
    return cursor


def close():
    global connection
    global cursor
    cursor.close()
    connection.commit()
    connection.close()


def insert(mail: dict):
    global cursor
    attachment_ids = []
    for attachment in mail["attachments"]:
        cursor.execute(
            "insert into attachments (name, content) values (?, ?)", (attachment['name'], attachment['content']))
        attachment_ids.append(cursor.lastrowid)
    try:
        cursor.execute(
            "insert into mails (subject, sender, receiver, 'date', content, attachment, path) values (?,?,?,?,?,?,?)",
            (mail['subject'], mail['from'],
             mail['to'], mail['date'],
             mail['content'],
             json.dumps(attachment_ids), mail['path']))
    except sqlite3.IntegrityError as e:
        print(e)


def load_mails(option=list) -> list:
    pass


def query(keyword: str, limit=-1, option=None) -> list:
    start = time.time()
    print("Processing query ...", end=" ")
    option = [True] * 7 if option is None else option
    result = cursor.execute(f'''select path from mails 
    where "subject" like "%{keyword}%" 
    or "from" like "%{keyword}%" or "to" like "%{keyword}%" 
    or "date" like "%{keyword}%" or "content" like "%{keyword}%" ''')

    end = time.time()
    print(f"Done, time cost: {end - start}")
    return result


def main():
    init()
    close()
    pass


if __name__ == '__main__':
    main()
