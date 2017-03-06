-- Ensure some uniqueness in iembot config
CREATE UNIQUE index iembot_room_subscriptions_idx on
  iembot_room_subscriptions(roomname, channel);

