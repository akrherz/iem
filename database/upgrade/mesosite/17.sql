-- GH Issue 169 the proper storage of twitter accounts
ALTER TABLE iembot_twitter_oauth add user_id bigint;
CREATE UNIQUE INDEX iembot_twitter_oauth_idx on iembot_twitter_oauth(user_id);

ALTER TABLE iembot_twitter_subs
  add user_id bigint REFERENCES iembot_twitter_oauth(user_id);