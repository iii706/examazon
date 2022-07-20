# import cloudscraper
#
# cat_urls = [
#     'https://www.amazon.com/ref=nav_logo',
# ]
#
# scraper1 = cloudscraper.create_scraper(
#         browser={
#             'browser': 'chrome',
#             'platform': 'ios',
#             'desktop': True,
#             #'mobile': True,
#         },
#         interpreter='nodejs'
#     )
#
# res = scraper1.get(cat_urls[0])
# print(res.text)
# print(res.status_code)

from datetime import datetime

import time

# time='April 26, 2019'
# time_format=datetime.strptime(time,'%B %d, %Y')  #datetime.datetime(2016, 11, 18, 0, 0)
# print(time_format)
# time_format = datetime.datetime.strftime(time_format, '%Y-%m-%d %H:%M:%S')   #'2016-11-18 00:00:00'
# print(time_format)
#
# datetime.datetime.utcnow()
# datetime.datetime.utcnow() + datetime.timedelta(days=7)
# (datetime.datetime.utcnow() + datetime.timedelta(days=7)).isoformat()
# datetime.datetime.utcnow().isoformat()
title = ' 8.31x4.06x3.98 inches; 8.                        ‏'
print(title.strip())


