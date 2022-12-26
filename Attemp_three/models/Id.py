import urllib.parse


def get_id(link: str) -> str:
    parsed_link = urllib.parse.urlparse(link)
    query = urllib.parse.parse_qs(parsed_link.query)
    return query.get('list')[0] if query.get('v') is None else query.get('v')[0]
