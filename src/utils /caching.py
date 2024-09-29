from cashews import Cache

cache = Cache()
cache.setup('redis://localhost', client_side=True)
