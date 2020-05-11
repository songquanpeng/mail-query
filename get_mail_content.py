import glob

from email.header import decode_header, make_header
from email.parser import BytesParser


def parse(path):
    with open(path, 'rb') as eml_file:
        parser = BytesParser()
        message = parser.parse(eml_file)
        subject = str(make_header(decode_header(message.get("subject"))))
        sender = str(make_header(decode_header(message.get("from"))))
        receiver = str(make_header(decode_header(message.get("to"))))
        date = message.get("date")
    mail = {
        "subject": subject,
        "from": sender,
        "to": receiver,
        "date": date,
        "content": "",
        "attachments": [
            {
                "filename": "",
                "content": ""
            }
        ]
    }
    return mail


if __name__ == '__main__':
    files = glob.glob("./data/*.eml")
    for file in files:
        print(f"mail: {file}")
        m = parse(file)
        print(m)
