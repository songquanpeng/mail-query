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
db_path = './data.db'


def init(database_path=db_path):
    # initialize the SQLite database and return the connection
    global connection
    if not connection:
        connection = sqlite3.connect(database_path)
        cursor = connection.cursor()
        cursor.execute(create_mails_table)
        connection.commit()
    return connection


def create_connection(database_path=db_path):
    return sqlite3.connect(database_path)


def insert(mail: dict, conn=connection):
    # You must call conn.commit() after all insertions are done
    attachment_name = ""
    attachment_content = ""
    for attachment in mail["attachments"]:
        attachment_name += attachment['name'] + "\n"
        attachment_content += attachment['content'] + "\n"
    try:
        cursor = conn.cursor()
        cursor.execute(
            """insert into mails (path, subject, sender, receiver, 'date', content, attachment_name, attachment_content) 
            values (?,?,?,?,?,?,?,?)""",
            (mail['path'], mail['subject'], mail['from'], mail['to'], mail['date'],
             mail['content'], attachment_name, attachment_content))
    except sqlite3.IntegrityError as e:
        print(e)


def query(keyword: str, limit=-1, option=None, more=False, conn=connection, full_content=False) \
        -> list:
    start = time.time()
    print("Processing query ...", end=" ")
    option = [True] * 7 if option is None else option
    sql = ""
    if more:
        sql += f'select id, path, subject, sender, receiver, "date", content from mails where "subject" like "%{keyword}%" '
    else:
        sql += f'select path from mails where "subject" like "%{keyword}%" '
    sql += (f'or "sender" like "%{keyword}%" ' if option[1] else "")
    sql += (f'or "receiver" like "%{keyword}%" ' if option[2] else "")
    sql += (f'or "date" like "%{keyword}%" ' if option[3] else "")
    sql += (f'or "content" like "%{keyword}%" ' if option[4] else "")
    sql += (f'or "attachment_name" like "%{keyword}%" ' if option[5] else "")
    sql += (f'or "attachment_content" like "%{keyword}%" ' if option[6] else "")
    if limit >= 1:
        sql += f'limit {limit}'
    cursor = conn.cursor()
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
                "content": row[6] if full_content else row[6][:200]
            }
            result.append(mail)
        else:
            result.append(row[0])
    end = time.time()
    print(f"Done, time cost: {end - start}")
    return result


def get_mail_by_path(path: str, conn=connection) -> dict:
    sql = f'select * from mails where "path"="{path}"'
    cursor = conn.cursor()
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
    connection.close()


if __name__ == '__main__':
    main()
