from unittest.mock import MagicMock, patch

from future.databases.Elasticsearch import Elasticsearch
from future.models import Model


class Doc(Model):
    __table__ = "docs"


def _es():
    with patch("future.databases.Elasticsearch.ElasticsearchPlugin") as plugin_cls:
        plugin = MagicMock()
        plugin_cls.return_value = plugin
        es = Elasticsearch(host="https://localhost:9200", port=9200, username="u", password="p")
        es.client = plugin
        return es


def test_elasticsearch_find_and_all():
    es = _es()
    es.client.get_document.return_value = {"_source": {"id": "1", "title": "hi"}}
    es.client.search_documents.return_value = {"hits": {"hits": [{"_source": {"id": "1", "title": "hi"}}, {"_source": {"id": "2", "title": "yo"}}]}}

    found = es.find(Doc(), "1")
    assert found is not None and found.title == "hi"
    es.client.get_document.assert_called_with("docs", "1")

    rows = es.all(Doc())
    assert len(rows) == 2
    assert rows[1].id == "2"


def test_elasticsearch_get_builds_bool_query():
    es = _es()
    es.client.search_documents.return_value = {"hits": {"hits": [{"_source": {"id": "9", "price": 5}}]}}

    rows = es.get(Doc(), wheres=[("price", ">", 1)], limit=5, orders=[("price", "asc")])
    assert len(rows) == 1
    body = es.client.search_documents.call_args[0][1]
    assert body["size"] == 5
    assert {"range": {"price": {"gt": 1}}} in body["query"]["bool"]["must"]
    assert body["sort"] == [{"price": {"order": "asc"}}]


def test_elasticsearch_save_indexes_document():
    es = _es()
    es.client.index_document.return_value = {"result": "created"}
    result = es.save(Doc(id="1", title="x"))
    assert result["result"] == "created"
    es.client.index_document.assert_called_with("docs", {"id": "1", "title": "x"}, document_id="1")
