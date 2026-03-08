import redis

r = redis.Redis(
    host='redis-10391.c93.us-east-1-3.ec2.redns.redis-cloud.com',
    port=10391,
    decode_responses=True,
    username="default",
    password="GkGBy5K5q7Dy8gmAU1ku7fv0B8yDvgTp",
)


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

# work hours

key = 'time:15'
val = {103: 23.8, 101: 19.4}

r.hset(key, mapping=val) # for project 15

#payment

key = 'payment:103'
val = {15: 2000}
r.hset(key, mapping=val) # for payments of employee 103

key = 'payment:105'
val = {15: 3700, 22: 6800}
r.hset(key, mapping=val) # for payments of employee 105

key = 'payrates'
r.zadd(key, {1: 84.5})
r.zadd(key, {2: 105.0})
r.zadd(key, {3: 35.75})

print(r.zrevrange('payrates',0,0))

def findProjectCost(name):
    id = r.hget("ProjectNames", name)
    key = f'project:{id}'
    cost = r.hget(key, 'total')
    return cost

def findProjectTeamSize(name):
    id = r.hget("ProjectNames", name)
    key = f'time:{id}'
    val = r.hgetall(key)
    return len(val)

def findTotalPayment(id):
    key = f'payment:{id}'
    val = r.hgetall(key)
    s = 0
    for f, v in val.items():
        s += float(v)
    return s


# main

cost = findProjectCost('Evergreen')
print(cost)

size = findProjectTeamSize('Evergreen')
print(size)

pay = findTotalPayment(105)
print(pay)