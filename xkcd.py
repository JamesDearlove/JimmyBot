import feedparser

xkcd_feed =  "https://xkcd.com/rss.xml"
d = feedparser.parse(xkcd_feed)

latest = d["entries"][0]
print(latest["link"])