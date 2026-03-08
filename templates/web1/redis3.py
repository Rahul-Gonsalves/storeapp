import redis
r = redis.Redis(
    host='redis-10391.c93.us-east-1-3.ec2.redns.redis-cloud.com',
    port=10391,
    decode_responses=True,
    username="default",
    password="GkGBy5K5q7Dy8gmAU1ku7fv0B8yDvgTp",
)


key = 'project:15'
val = {
    'name': 'Evergreen',
    'lead': 105,
    'cost': 10500.0
}

r.hset(key, mapping=val)

key = 'employee:105'
val = {
    'name': 'Alice Johnson',
    'jobid': 2
}

r.hset(key, mapping=val)

key = 'job:2'
val = {
    'title': 'Database Designer',
    'rate': 105.0
}

r.hset(key, mapping=val)

r.zadd('payrates', {1: 84.5})
r.zadd('payrates', {2: 105.0})
r.zadd('payrates', {3: 35.75})
r.zadd('payrates', {4: 96.75})


# time billed

key = 'time:15'
r.hset(key, 105, 23.8)
r.hset(key, 101, 19.4)
r.hset(key, 103, 35.7)

# payment billed

key = 'payment:105'
r.hset(key, 15, 3700.0)
r.hset(key, 22, 6800.0)

key = 'ProjectNames'

r.hset(key, 'Evergreen', 15)
r.hset(key, 'Amber Wave', 18)
r.hset(key, 'Rolling Tide', 22)
r.hset(key, 'Starflight', 25)

def findCostOfProject(name):
    id = r.hget('ProjectNames', name)
    key = f'project:{id}'
    cost = r.hget(key, 'cost')
    return cost

c = findCostOfProject('Evergreen')

print(f'Total cost of project Evergreen is {c}')

def findSizeOfProject(name):
    id = r.hget('ProjectNames', name)
    key = f'time:{id}'
    hour = r.hgetall(key)
    return len(hour)

s = findSizeOfProject('Evergreen')

print(f'Total size of project Evergreen is {s}')


def findPaymentOfEmployee(id):
    key = f'payment:{id}'
    val = r.hgetall(key)
    t = 0
    for p, v in val.items():
        t += float(v)
    return t

t = findPaymentOfEmployee(105)

print(f'Total payment of employee 105 is {t}')

def findHighestPayingJob():
    lj = r.zrevrange('payrates', 0, 0)
    id = lj[0]
    key = f'job:{id}'
    title = r.hget(key, 'title')
    return title

print(findHighestPayingJob())