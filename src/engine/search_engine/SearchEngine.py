from re import split
from django.conf import settings
from engine.db_engine.DbEngine import DbEngine


class SearchEngine(object):
    def __init__(self):
        self.db_engine = DbEngine()
        self.queries = self.db_engine.get_all_queries()

    def reload_queries(self):
        """
        Reloads queries from database.
        """

        self.queries = self.db_engine.get_all_queries()

    def search_in_url(self, url, content):
        """
        Search web page content in order to find keywords.

        :param str url: URL of web page being crawled.
        :param str content: content of web page associated with the URL.
        """

        queries = self.search(content)
        for query in queries:
            self.db_engine.add_url(query, url)

    def search(self, content):
        """
        Iterates over all queries and returns those for which number of found
        keywords satisfies search threshold.

        :param str content: content of web page associated with the URL.
        :return: list of queries for which search threshold was satisfied.
        """

        content = split(r'\W*', content.lower())
        queries = set()
        for query in self.queries:
            keywords = self.db_engine.get_keywords(query)
            found = 0
            for keyword in keywords:
                if keyword in content:
                    found += 1
            if len(keywords) > 0 and float(found) / len(
                    keywords) >= settings.KEYWORD_THRESHOLD:
                queries.add(query)
        return queries
