 # tor_spider

Spider for **.onion** sites.
To run it you need to:
- pip3 install scrapy
- sudo pacman -S tor
- sudo pacman -S privoxy
- sudo pacman -S python-ssdeep
- in privoxy config *( /etc/privoxy/config )* you need to delete # from  
**forward-socks5t   /               127.0.0.1:9050 .**  
line.
- scrapy crawl tor_spider
