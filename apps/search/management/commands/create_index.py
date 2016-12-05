from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
import requests
from django.conf import settings
import json


class Command(BaseCommand):
    help = "Create index"
    args = ""

    def handle(self, *app_labels, **options):
        data = {
            "mappings": {
                "product": {
                    "properties": {
                        "type": {"type": "keyword"},
                        "categories": {"type": "nested"},
                        "attribute_values": {"type": "nested", "properties": {"slug": {"type": "keyword"}}
                                            },
                        "query_suggest": {
                           "type": "completion",
                           "analyzer": "simple",
                           "search_analyzer": "simple",
                        }
                    }
                }
        }}
        requests.delete(settings.ELASTIC_URL)
        res = requests.put(settings.ELASTIC_URL, data=json.dumps(data))
        if res.status_code != 200:
            print res.content