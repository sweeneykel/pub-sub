import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)
# Store and retrieve a simple string.
r.set('foo', 'bar')
r.get('foo')

# Store and retrieve a dict.
r.hset('user-session:123', mapping={
    'name': 'John',
    "surname": 'Smith',
    "company": 'Redis',
    "age": 29
})
r.hgetall('user-session:123')