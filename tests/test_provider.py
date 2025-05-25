import json

from tofuref.data.providers import Provider
from tofuref.widgets.providers_option_list import ProvidersOptionList

PROVIDER_JSON = json.loads("""{
  "addr": {
    "display": "0username/rabbitmq",
    "namespace": "0username",
    "name": "rabbitmq"
  },
  "link": "",
  "canonical_addr": null,
  "reverse_aliases": [],
  "description": "",
  "popularity": 0,
  "fork_count": 0,
  "fork_of": {
    "display": "",
    "namespace": "",
    "name": ""
  },
  "upstream_popularity": 0,
  "upstream_fork_count": 0,
  "versions": [
    {
      "id": "v1.9.1",
      "published": "2023-06-05T15:03:47Z"
    },
    {
      "id": "v1.8.1",
      "published": "2022-05-06T00:10:58Z"
    },
    {
      "id": "v1.7.0",
      "published": "2022-04-27T20:42:44Z"
    }
  ],
  "is_blocked": false
}
""")


def test_provider_use():
    provider = Provider.from_json(PROVIDER_JSON)
    assert (
        provider.use_configuration
        == """    rabbitmq = {
      source  = "0username/rabbitmq"
      version = "1.9.1"
    }"""
    )


def test_provider_fallback_exists():
    p = ProvidersOptionList()
    assert p.fallback_providers_file.exists()
