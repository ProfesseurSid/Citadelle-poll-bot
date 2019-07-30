# Citadelle-poll-bot
Attempt for a Citadelle bot managing polls

# Documentation source
https://matrix.org/docs/spec/client_server/latest

# Basics
## Variables
In the next examples, here are the needed env variables :
- **$CITADELLE**: the Citadelle server's name or IP.
- **$EMAIL**: the e-mail address for the account to be used by the bot.
- **$PASSWORD**: the password for the account to be used by the bot.
- **$DEVICE_ID**: the device ID for the device to be used by the bot.
- **$ROOM_ID**: the ID of the room the action must be taken on. Starts with *!*.
- **$TRANSACTION_ID**: a number used to ensure unicity of the events.
- **$TKN**: the access token granted after the request. Lasts one hour.
- **$USER_UNIC**: the unique identifier of the user. Starts with *@*.
- **$FILTER**: the filter ID returned at filter's creation.
- **$BATCH**: the batch from which to receive the events.

## Requesting the tokens
**POST** https://$CITADELLE/_matrix/client/r0/login
```JSON
{
  "type": "m.login.password",
  "identifier": {
    "type": "m.id.thirdparty",
    "medium": "email",
    "address": "$EMAIL"
  },
  "password": "$PASSWORD",
  "device_id": "$DEVICE_ID",
  "initial_device_display_name": "Poll's bot"
}
```
```SHELL
curl.exe --request POST --url https://$CITADELLE/_matrix/client/r0/login --header 'cache-control: no-cache' --header 'content-type: application/json' --data "{\"type\":\"m.login.password\",\"identifier\":{\"type\":\"m.id.thirdparty\",\"medium\":\"email\",\"address\":\"$EMAIL\"},\"password\":\"$PASSWORD\",\"device_id\":\"$DEVICE_ID\",\"initial_device_display_name\":\"Poll's bot\"}"
```

## Sending a message
**PUT** https://$CITADELLE/_matrix/client/r0/rooms/$ROOM_ID:$CITADELLE/send/m.room.message/$TRANSACTION_ID
```JSON
{
  "msgtype": "m.text",
  "body": "Test bot"
}
```
```SHELL
curl --request PUT --url "https://$CITADELLE/_matrix/client/r0/rooms/$ROOM_ID:$CITADELLE/send/m.room.message/$TRANSACTION_ID" --header 'content-type: application/json' --header "authorization: Bearer $TKN" --data "{\"msgtype\": \"m.text\", \"body\": \"Test bot\"}"
```

## Creating a filter
*To get almost only $ROOM_ID room's messages*

**POST** https://$CITADELLE/_matrix/client/r0/user/$USER_UNIC:$CITADELLE/filter
```JSON
{
  "presence": {
    "limit": 0,
    "not_types": ["*"]
  },
  "account_data": {
    "limit": 0,
    "not_types": ["*"]
  },
  "room": {
    "state": {
      "types": ["m.room.message"]
    },
    "rooms": ["$ROOM_ID:$CITADELLE"]
  }
}
```
```SHELL
curl.exe --request POST --url "https://$CITADELLE/_matrix/client/r0/user/$USER_UNIC:$CITADELLE/filter" --header 'content-type: application/json' --header "authorization: Bearer $TKN" --data "{\"presence\":{\"limit\":0,\"not_types\":[\"*\"]},\"account_data\":{\"limit\":0,\"not_types\":[\"*\"]},\"room\":{\"state\":{\"types\":[\"m.room.message\"]},\"rooms\":[\"$ROOM_ID:$CITADELLE\"]}}"
```

## Synchronizing
*After each call, $BATCH should take next_batch's value from the response*

**GET** https://$CITADELLE/_matrix/client/r0/sync?filter=$FILTER&since=$BATCH&full_state=false&set_presence=offline&timeout=30000&access_token=$TKN
```SHELL
curl.exe --request GET --url "https://$CITADELLE/_matrix/client/r0/sync?filter=$FILTER&since=$BATCH&full_state=false&set_presence=offline&timeout=30000&access_token=$TKN"
```