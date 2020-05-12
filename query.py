import glob
from get_mail_content import parse

# priority: subject > form, to, date > content > attachments' filename > attachments' content
weights = [20, 10, 5, 6, 1]


def sort_by_score(mails: list, scores: list, limit: int) -> list:
    combined = zip(mails, scores)
    result = sorted(combined, key=lambda x: x[1], reverse=True)[:limit]
    return result


def query(keyword: str, mails: list, limit=2) -> list:
    scores = [0 for x in range(len(mails))]
    for i in range(len(mails)):
        mail = mails[i]
        count = mail["subject"].count(keyword)
        scores[i] += count * weights[0]
    for i in range(len(mails)):
        mail = mails[i]
        count = mail["from"].count(keyword)
        count += mail["to"].count(keyword)
        count += mail["date"].count(keyword)
        scores[i] += count * weights[1]
    for i in range(len(mails)):
        mail = mails[i]
        count = mail["content"].count(keyword)
        scores[i] += count * weights[2]
    for i in range(len(mails)):
        mail = mails[i]
        count = 0
        for attachment in mail["attachments"]:
            count = attachment["name"].count(keyword)
        scores[i] += count * weights[3]
    for i in range(len(mails)):
        mail = mails[i]
        count = 0
        for attachment in mail["attachments"]:
            count = attachment["content"].count(keyword)
        scores[i] += count * weights[4]
    return sort_by_score(mails, scores, limit)


def main():
    files = glob.glob("./data/*.eml")
    mails = []
    for file in files:
        mails.append(parse(file))
    print(query(input("Please input keyword: "), mails))


if __name__ == '__main__':
    while True:
        main()
