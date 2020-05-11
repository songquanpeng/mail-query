import glob
from email.header import decode_header, make_header
from email.parser import BytesParser


def parse(path: str) -> dict:
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
        "attachments": []
    }
    for part in message.walk():
        if not part.is_multipart():
            file_name = part.get_filename()
            if file_name:
                file_name = str(make_header(decode_header(file_name)))
                file_data = part.get_payload(decode=True)
                mail["attachments"].append({"name": file_name, "content": file_data})
                print(file_name)
    return mail


def main():
    files = glob.glob("./data/*.eml")
    for file in files:
        print(f"mail: {file}")
        mail = parse(file)
        print(mail)


if __name__ == '__main__':
    main()
