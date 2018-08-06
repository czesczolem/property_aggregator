#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Flask
from flask import request
import os
import logging
import elasticsearch

from otodom.category import get_category
from otodom.offer import get_offer_information

app = Flask(__name__)

log = logging.getLogger(__file__)

es = elasticsearch.Elasticsearch([{'host': '172.18.0.1', 'port': 8888}])

SCRAPE_LIMIT = os.environ.get('SCRAPE_LIMIT', None)


@app.route('/scrap')
def start_scraping():
    main = request.args.get("main_category")
    detail = request.args.get('detail_category')
    region = request.args.get('region')
    filters = request.args.get('filters')
    if not filters:
        filters = {}
    command = ''
    os.system(command)
    info = "scraping {} {} {} {}".format(main, detail, region, filters)

    parsed_category = get_category(main, detail, region, **filters)

    log.info("Offers in that category - {0}".format(len(parsed_category)))

    if SCRAPE_LIMIT:
        parsed_category = parsed_category[:int(SCRAPE_LIMIT)]
        log.info("Scarping limit - {0}".format(len(parsed_category)))

    for id, offer in enumerate(parsed_category):
        log.info("Scarping offer - {0}".format(offer['detail_url']))
        offer_detail = get_offer_information(offer['detail_url'], context=offer)
        print("id: ", id)
        offer_detail_enc = {k: unicode(v).encode("utf-8") for k,v in offer_detail.iteritems()}
        es.index(index='otodom', doc_type='offers', id=id, body=offer_detail_enc)
        log.info("Scraped offer - {0}".format(offer_detail))

    return info


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=5000)