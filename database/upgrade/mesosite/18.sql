-- Storage of metadata
ALTER TABLE iembot_twitter_oauth ADD created timestamptz DEFAULT now();
ALTER TABLE iembot_twitter_oauth ADD updated timestamptz DEFAULT now();
