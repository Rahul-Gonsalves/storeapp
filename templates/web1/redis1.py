"""Basic connection example.
"""

import redis

r = redis.Redis(
    host='redis-10391.c93.us-east-1-3.ec2.redns.redis-cloud.com',
    port=10391,
    decode_responses=True,
    username="default",
    password="GkGBy5K5q7Dy8gmAU1ku7fv0B8yDvgTp",
)

success = r.set('tung', 'password!')
# True

result = r.get('nguyen')
if result is None:
    print("The user is not here!")
else:
    print(f"The password is {result}")

r.delete("foo")

key = 'project:15'
val = {"name": "Evergreen", "lead": 105, "total": 10500}

r.hset(key, mapping=val)

key = 'project:18'
val = {"name": "Amber Wave", "lead": 104, "total": 7100}

r.hset(key, mapping=val)


key = 'ProjectNames'
r.hset(key, 'Evergreen', 15)
r.hset(key, 'Amber Wave', 18)
r.hset(key, 'Rolling Tide', 22)


user_id = 'user:1001'

# HSET: sets fields in a hash. Can set multiple at once with `mapping`.
r.hset(user_id, mapping={
    'name': 'Bob',
    'email': 'bob@example.com',
    'country': 'USA'
})

# HGET: gets the value of a single field.
user_name = r.hget(user_id, 'name')
print(f"User name: {user_name}") # Output: User name: Bob

# HGETALL: gets all fields and values in the hash as a Python dictionary.
user_data = r.hgetall(user_id)
print(f"All user data: {user_data}")
# Output: All user data: {'name': 'Bob', 'email': 'bob@example.com', 'country': 'USA'}

