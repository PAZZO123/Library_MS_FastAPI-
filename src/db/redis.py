import redis.asyncio as aioredis
from src.config import config

EXPIRY_OF_JTI=3600

redis_token_blocklist=aioredis.from_url(config.REDIS_URL)

async def add_jti_to_blocklist(jti:str)->None:
    await redis_token_blocklist.set(
        name=jti,
        ex=EXPIRY_OF_JTI,
        value=""
    )
    
async def token_in_blocklist(jti:str)-> bool:
    jti= await redis_token_blocklist.get(jti)
    return jti is not None
    