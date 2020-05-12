import glob
import time
from get_mail_content import parse

# priority: subject > form, to, date > content > attachments' filename > attachments' content
weights = [20, 10, 5, 6, 1]


def sort_by_score(mails: list, scores: list, limit: int) -> list:
    indexes = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:limit]
    result = []
    for index in indexes:
        if scores[index] > 0:
            result.append(index)
    return result


def query(keyword: str, mails: list, limit=-1) -> list:
    """
    Keyword query
    :param keyword: as name
    :param mails: we will query this givens mails list
    :param limit: how many result do you want, -1 means no limit, default is -1
    :return: an index list
    """
    limit = len(mails) if limit is -1 else limit
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
    keyword = input("Please input keyword: ")
    start = time.time()
    result = query(keyword, mails)
    end = time.time()
    print(f"{len(result)} results ({end - start} seconds)")
    for i in result:
        print(mails[i]["subject"])
    print()


if __name__ == '__main__':
    while True:
        main()
