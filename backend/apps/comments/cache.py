from django.core.cache import cache

GEN_KEY = 'comments:gen'
TTL = 300


# every cached list carries the generation in its key, so one incr drops them all at once
def generation():
    gen = cache.get(GEN_KEY)
    if gen is None:
        cache.set(GEN_KEY, 1, None)
        gen = 1
    return gen


def bump():
    try:
        cache.incr(GEN_KEY)
    except ValueError:
        cache.set(GEN_KEY, 1, None)
