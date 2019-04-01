# -*- coding: utf-8 -*-

# Scrapy settings for autohomebot project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'autohomebot'
FEED_EXPORT_ENCODING = 'utf-8'  # 设置返回文本编码

SPIDER_MODULES = ['autohomebot.spiders']
NEWSPIDER_MODULE = 'autohomebot.spiders'

# 获取代理的URL
PROXY_POOL_URL = 'http://127.0.0.1:5555/random'

# 数据库连接地址
MONGODB_URL = 'absit1309'
# 数据库名称
MONGODB_NAME = 'autohome'

# RETRY_TIMES=10
# RETRY_ENABLED=False

DUPEFILTER_DEBUG = True
# DUPEFILTER_CLASS='scrapy.dupefilters.RFPDupeFilter' #禁止过滤重置请求，一个请求可以发送多次,直至成功

# 下载器超时时间(单位: 秒)
# DOWNLOAD_TIMEOUT=180
DOWNLOAD_TIMEOUT = 15

# logging输出的文件名。如果为None，则使用标准错误输出(standard error)。
LOG_FILE = 'spider.log'
# log的最低级别。可选的级别有: CRITICAL、 ERROR、WARNING、INFO、DEBUG。更多内容请查看 Logging 。
LOG_LEVEL = 'INFO'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'autohomebot (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 16

# 下载器在下载同一个网站下一个页面前需要等待的时间。该选项可以用来限制爬取速度， 减轻服务器压力。同时也支持小数
# 该设定影响(默认启用的) RANDOMIZE_DOWNLOAD_DELAY 设定。 默认情况下，Scrapy在两个请求间不等待一个固定的值，
# 而是使用0.5到1.5之间的一个随机值 * DOWNLOAD_DELAY 的结果作为等待间隔。
# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False  # 关闭COOKIES防反爬

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Scrapy HTTP Request使用的默认header。
# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'autohomebot.middlewares.AutohomebotSpiderMiddleware': 543,
# }

# 保存项目中启用的下载中间件及其顺序的字典
# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'autohomebot.middlewares.AutohomebotDownloaderMiddleware': 543,
    # 'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': None,  # 禁用重定向
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': None  # 禁止重试
}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'autohomebot.pipelines.AutohomebotPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# # 广度优先
# DEPTH_PRIORITY = 1
# SCHEDULER_DISK_QUEUE = 'scrapy.squeues.PickleFifoDiskQueue'
# SCHEDULER_MEMORY_QUEUE = 'scrapy.squeues.FifoMemoryQueue'

# 禁止重定向
# REDIRECT_ENABLED = False  # 关掉重定向, 不会重定向到新的地址
# HTTPERROR_ALLOWED_CODES = [301, 302]  # 返回301, 302时, 按正常返回对待, 可以正常写入cookie
