-- Storage of views of the feature
ALTER TABLE feature ADD views INT default 0;
UPDATE feature SET views = 0;
