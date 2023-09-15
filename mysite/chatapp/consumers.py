from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from .models import ChatRoom,ChatMessage


class ChatConsumer(AsyncWebsocketConsumer):
    # make connection to a particular room
    # get group names, room names 
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' %self.room_name

        # this is a function call
        # takes the channel layer and adds the room, group name to it
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # this is a function call to accept incoming connection
        await self.accept()


    async def disconnect(self):
        await self.channel_layer.group_discard(
            self.channel_layer,
            self.room_group_name
        )


    # Receiving message
    async def receive(self,text_data):
        # loads message data in jason format
        data = json.loads(text_data)
        message = data['message']
        username = data['username']
        room = data['room']


        await self.channel_layer.group_send(
            self.room_group_name,{
                'type':'chat_message',
                'message': message,
                'username': username ,
                'room': room,
            }
        )

        await self.save_message(username,room,message)



    async def chat_message(self,event):
        message = event['message']
        username = event['username']
        room = event['room']

        await self.send(text_data=json.dumps({
            'message' : message,
            'username': username,
            'room': room,
        }))

    # To save messages in db once they are received
    @sync_to_async
    def save_message(self,username,room,message):
        user = User.objects.get(username=username)
        room = ChatRoom.objects.get(slug=room)
        ChatMessage.objects.create(user=user, room=room, message_content= message)

