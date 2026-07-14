import datetime

import config


def passes_length_rule(article):
    body = article.get("body") or ""
    return len(body) >= config.MIN_BODY_LENGTH


def passes_today_rule(article, today=None):
    if not config.TODAY_ONLY:
        return True
    pub_date = article.get("pubdate")
    if pub_date is None:
        return False
    today = today or datetime.date.today()
    if isinstance(pub_date, datetime.datetime):
        pub_date = pub_date.date()
    return pub_date == today


def passes_youtube_financial_filter(article):
    if article.get("source") != "youtube":
        return True
    title = article.get("title") or ""
    body = article.get("body") or ""
    text = title + " " + body
    return any(keyword in text for keyword in config.FINANCIAL_KEYWORDS)


RULES = [
    passes_length_rule,
    passes_today_rule,
    passes_youtube_financial_filter,
]


def apply_rules(articles, today=None):
    passed = []
    for article in articles:
        ok = True
        for rule in RULES:
            try:
                if rule is passes_today_rule:
                    result = rule(article, today=today)
                else:
                    result = rule(article)
            except Exception:
                result = False
            if not result:
                ok = False
                break
        if ok:
            passed.append(article)
    return passed
