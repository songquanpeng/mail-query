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
    if not connection:
        connection = sqlite3.connect(database_path)
        cursor = connection.cursor()
        cursor.execute(create_mails_table)
    return cursor


def close():
    global connection
    global cursor
    if cursor:
        cursor.close()
    if connection:
        connection.commit()
        connection.close()


def insert(mail: dict):
    global cursor
    if not cursor:
        init()
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


def query(keyword: str, limit=-1, option=None, more=True) -> list:
    if not cursor:
        init()
    start = time.time()
    print("Processing query ...", end=" ")
    option = [True] * 7 if option is None else option
    sql = ""
    if more:
        sql += f'select id, path, subject, sender, receiver, "date", content from mails where "subject" like "%{keyword}%" '
    else:
        sql += f'select path from mails where "subject" like "%{keyword}%" '
    sql += (f'or "from" like "%{keyword}%" ' if option[1] else "")
    sql += (f'or "to" like "%{keyword}%" ' if option[2] else "")
    sql += (f'or "date" like "%{keyword}%" ' if option[3] else "")
    sql += (f'or "content" like "%{keyword}%" ' if option[4] else "")
    sql += (f'or "attachment_name" like "%{keyword}%" ' if option[5] else "")
    sql += (f'or "attachment_content" like "%{keyword}%" ' if option[6] else "")
    if limit >= 1:
        sql += f'limit {limit}'
    rows = cursor.execute(sql)
    result = []
    for row in rows:
        if more:
            mail = {
                "id": row[0],
                "path": row[1],
                "subject": row[2],
                "sender": row[3],
                "receiver": row[4],
                "date": row[5],
                "content": row[6][:200]
            }
            result.append(mail)
        else:
            result.append(row[0])
    end = time.time()
    print(f"Done, time cost: {end - start}")
    return result


def get_mail_by_path(path: str) -> dict:
    if not cursor:
        init()
    sql = f'select * from mails where "path"="{path}"'
    result = cursor.execute(sql).fetchone()
    mail = {
        "id": result[0],
        "path": result[1],
        "subject": result[2],
        "sender": result[3],
        "receiver": result[4],
        "date": result[5],
        "content": result[6],
        "attachments_name": result[7],
        "attachments_content": result[8]
    }
    return mail


def main():
    init()
    result = query("com")
    print(result)
    close()
    pass


if __name__ == '__main__':
    main()
