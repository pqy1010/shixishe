DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS video;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
);




/*moviename,updatetime,movieimg,moviedescrib,othername,moviestatus,movieborntime,actor,director,movieclass,classextant,country,year,lang,episodr,movielen,click,links*/
CREATE TABLE video (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  img TEXT,
  jishu TEXT,
  othername TEXT,
  director TEXT,
  actor TEXT,
  genre TEXT,
  region TEXT,
  language TEXT,
  screen TEXT,
  mlen TEXT,
  updatet TEXT,
  clicknum TEXT,
  todayclicknum TEXT,
  score TEXT,
  scorenum TEXT,
  introduction TEXT,
  yun1 TEXT,
  m3u8 TEXT,
  download TEXT,
  platform TEXT,
  other TEXT,
  other1 TEXT,
  other2 TEXT,
  other3 TEXT,
  permituid TEXT,
  FOREIGN KEY (author_id) REFERENCES user (id)
);