import sqlite3
import time

create_mails_table = """
CREATE TABLE IF NOT EXISTS "mails"(
"id"	INTEGER PRIMARY KEY AUTOINCREMENT,
"path"	TEXT NOT NULL UNIQUE,
"subject"	TEXT,
"sender"	TEXT,
"receiver"	TEXT,
"date"	TEXT,
"content"	TEXT,
"attachment_name"	TEXT,
"attachment_content"	TEXT
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
    attachment_name = ""
    attachment_content = ""
    for attachment in mail["attachments"]:
        attachment_name += attachment['name'] + "\n"
        attachment_content += attachment['content'] + "\n"
    try:
        cursor.execute(
            """insert into mails (path, subject, sender, receiver, 'date', content, attachment_name, attachment_content) 
            values (?,?,?,?,?,?,?,?)""", (mail['path'], mail['subject'], mail['from'], mail['to'], mail['date'],
                                          mail['content'], attachment_name, attachment_content))
    except sqlite3.IntegrityError as e:
        print(e)


def query(keyword: str, limit=-1, option=None) -> list:
    start = time.time()
    print("Processing query ...", end=" ")
    option = [True] * 7 if option is None else option
    sql = f'select path from mails where "subject" like "%{keyword}%" '
    sql += (f'or "from" like "%{keyword}%" ' if option[1] else "")
    sql += (f'or "to" like "%{keyword}%" ' if option[2] else "")
    sql += (f'or "date" like "%{keyword}%" ' if option[3] else "")
    sql += (f'or "content" like "%{keyword}%" ' if option[4] else "")
    sql += (f'or "attachment_name" like "%{keyword}%" ' if option[5] else "")
    sql += (f'or "attachment_content" like "%{keyword}%" ' if option[6] else "")
    if limit >= 1:
        sql += f'limit {limit}'
    paths = cursor.execute(sql)
    result = []
    for path in paths:
        result.append(path[0])
    end = time.time()
    print(f"Done, time cost: {end - start}")
    return result


def main():
    init()
    result = query("com")
    print(result)
    close()
    pass


if __name__ == '__main__':
    main()
