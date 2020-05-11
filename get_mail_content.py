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
    content = ""
    last_is_plain_text = False
    for part in message.walk():
        charset = part.get_content_charset()
        print("charset: ", charset)
        if not part.is_multipart():
            content_type = part.get_content_type()
            file_name = part.get_filename()
            if file_name:
                file_name = str(make_header(decode_header(file_name)))
                file_data = part.get_payload(decode=True)
                if file_name.endswith(".txt"):
                    file_data = file_data.decode("utf-8")
                mail["attachments"].append({"name": file_name, "content": file_data})
            else:
                if not last_is_plain_text:
                    if content_type in ['text/plain']:
                        last_is_plain_text = True
                    content = part.get_payload(decode=True)
                    if charset:
                        content = content.decode(charset)

    mail["content"] = content
    return mail


def main():
    files = glob.glob("./data/*.eml")
    for file in files:
        mail = parse(file)
        print(mail)


if __name__ == '__main__':
    main()
