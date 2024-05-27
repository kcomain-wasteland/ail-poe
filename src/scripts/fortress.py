import json
import logging
from enum import Enum, StrEnum

import requests

BASE_URL = "https://api.fortress.com.hk/api/v2/ftrhk/products/search"

class Categories(Enum):
    vacuum = 56
    aircon = 51
    refrigerator = 61

class Sorting(StrEnum):
    bestseller = "bestSeller"

def params(category: Categories, sort: Sorting = Sorting.bestseller, count: int = 100):
    return {
        "fields": "FTR_FULL",
        "curr": "HKD",
        "lang": "en",
        "pageSize": count,
        "sort": sort.value,
        "ignoreSort": False,
        "query": f":${sort.value}:category:{category}"
    }

if __name__ == "__main__":
    logging.basicConfig() # you need to initialize logging, otherwise you will not see anything from requests
    logging.getLogger().setLevel(1)
    logger = logging.getLogger("app")

    things = [
        Categories.aircon,
        Categories.refrigerator,
        Categories.vacuum,
    ]
    
    for thing in things:
        _params = params(thing.value)
        logger.debug(_params)
        
        logger.debug(f"getting {thing.name}")
        res = requests.get(
            BASE_URL,
            _params,
            headers = {
                "accept": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/125.0",
            }
        )
        
        logger.info("writing %s", thing.name)
        with open(f"src/kb/fortress_{thing.name}.txt", "wb+") as f:
            f.write(res.content)
