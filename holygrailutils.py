import redis
import os

running_env = os.getenv("FLASK_ENV", "development") 

REDIS_HOST='40.76.248.225'
REDIS_PASS='Corestrat@1234'
""" lines to be added in other py files
import holygrailutils
# redis_client = redis.Redis(host='localhost', port=6379, db=0)
redis_client = holygrailutils.get_redis_client()
"""
# def get_redis_client():
#     return redis.Redis(
#         host=REDIS_HOST,
#         port=6379, 
#         password=REDIS_PASS
#     )
    
    
"""

if ssl enabled include this line
client = redis.Redis(
    host='holtgrail-azure-cache.redis.cache.windows.net',
    port=6380,  # Port for TLS connections
    password='0Q3DySfnjbh0ETj8RjZhJoKWn4kPQwxAFAzCaOP793w=',
    ssl=True
)

if running_env == 'testing':

            return redis.Redis(
            host=REDIS_HOST,
            port=6380,  # Port for TLS connections
            password=REDIS_PASS
            ssl=True
          
        )
    else:
          return redis.Redis(
            host='localhost',
            port=6379,
          )
"""



