DROP TABLE IF EXISTS config;
CREATE TABLE config (key varchar PRIMARY KEY, value varchar);
INSERT INTO config (key, value)
  VALUES ('last_time', '0000-00-00T00:00:00')
;
