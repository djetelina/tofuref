"""
Used for generating fallback/providers.json

Fetches full registry index, gets the 50 most popular providers and their 5 most recent versions
and saves that as a fallback response to the API call.

The fallback is also used for testing purposes.
"""

import json

import httpx

NUMBER_OF_PROVIDERS = 50
NUMBER_OF_VERSIONS = 5


def main():
    data = httpx.get("https://api.opentofu.org/registry/docs/providers/index.json").json()

    providers = [x for x in data["providers"] if x["addr"]["namespace"] != "terraform-providers"]

    top_providers = sorted(providers, key=lambda p: p["popularity"], reverse=True)[:NUMBER_OF_PROVIDERS]

    for provider in top_providers:
        provider["versions"] = provider["versions"][:NUMBER_OF_VERSIONS]
    with open("providers.json", "w") as f:  # noqa: PTH123
        json.dump({"providers": top_providers}, f, indent=2)


if __name__ == "__main__":
    main()
