# api security configuration for agroshield
# applied globally through settings.py

from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

class AnonBurstRateThrottle(AnonRateThrottle):
    # unauthenticated users: 30 requests per minute max
    scope = 'anon_burst'
    THROTTLE_RATES = {'anon_burst': '30/min'}

class UserBurstRateThrottle(UserRateThrottle):
    # authenticated users: 200 requests per minute max
    scope = 'user_burst'
    THROTTLE_RATES = {'user_burst': '200/min'}
