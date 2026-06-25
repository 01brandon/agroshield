import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Listing, Bid

class AuctionConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.listing_id      = self.scope['url_route']['kwargs']['listing_id']
        self.room_group_name = f'auction_{self.listing_id}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)

        if data.get('action') == 'place_bid':
            bid = await self.save_bid(data['amount'])
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type':    'bid_update',
                    'bidder':  self.scope['user'].email,
                    'amount':  str(bid.amount),
                    'bid_id':  bid.id,
                }
            )

    async def bid_update(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_bid(self, amount):
        listing = Listing.objects.get(id=self.listing_id)
        return Bid.objects.create(
            listing = listing,
            buyer   = self.scope['user'],
            amount  = amount,
        )
