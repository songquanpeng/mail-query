import glob
import time
from util import parse

# priority: subject > form, to, date > content > attachments' filename > attachments' content
attributes = ['subject', 'from', 'to', 'date', 'content', 'name', 'content']
weights = [20, 10, 10, 10, 5, 6, 1]
assert len(attributes) == len(weights)


def sort_by_score(scores: list, limit: int) -> list:
    indexes = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:limit]
    result = []
    for index in indexes:
        if scores[index] > 0:
            result.append(index)
    return result


def query(keyword: str, mails: list, limit=-1, option=None) -> list:
    """
    Keyword query
    :param keyword: as name
    :param mails: we will query this givens mails list
    :param limit: how many results do you want, -1 means no limit, default is -1
    :param option: a seven items boolean list, indicates whether the corresponding attributes should be considered
    :return: an index list
    """
    limit = len(mails) if limit is -1 else limit
    option = [True for _ in range(len(weights))] if option is None else option
    assert len(option) == len(attributes)
    scores = [0 for x in range(len(mails))]
    for index in range(len(attributes)):
        attribute = attributes[index]
        enable = option[index]
        if not enable:
            continue
        if index < 5:
            for i in range(len(mails)):
                mail = mails[i]
                count = mail[attribute].count(keyword)
                scores[i] += count * weights[index]
        else:
            for i in range(len(mails)):
                mail = mails[i]
                count = 0
                for attachment in mail["attachments"]:
                    count = attachment[attribute].count(keyword)
                scores[i] += count * weights[index]
    return sort_by_score(scores, limit)


def main():
    files = glob.glob("./data/*.eml")
    mails = []
    for file in files:
        mails.append(parse(file))
    keyword = input("Please input keyword: ")
    start = time.time()
    result = query(keyword, mails)
    end = time.time()
    print(f"{len(result)} results ({round(end - start, 2)} seconds)")
    for i in result:
        print(mails[i]["subject"])
    print()


if __name__ == '__main__':
    while True:
        main()
