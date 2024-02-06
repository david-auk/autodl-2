-- Create the autodl database
CREATE DATABASE IF NOT EXISTS autodl;

-- Use the autodl database
USE autodl;

-- Create the tg_user table
CREATE TABLE IF NOT EXISTS tg_user (
  id INTEGER PRIMARY KEY,
  username VARCHAR(255),
  first_name VARCHAR(255),
  last_name VARCHAR(255),
  role VARCHAR(255) NOT NULL,
  description VARCHAR(255),
  is_authenticated SMALLINT(1) NOT NULL,
  joined_at DATETIME NOT NULL
);

-- Create the tg_user table
CREATE TABLE IF NOT EXISTS tg_login_attempt (
  id INTEGER auto_increment PRIMARY KEY,
  tg_user_id INTEGER NOT NULL,
  is_correct SMALLINT(1) NOT NULL,
  date DATETIME NOT NULL,

  CONSTRAINT fk_tg_login_attempt_tg_user
    FOREIGN KEY (tg_user_id)
    REFERENCES tg_user(id)
);

-- Create the channel table
CREATE TABLE IF NOT EXISTS yt_channel (
  id VARCHAR(255) PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  req_user_id INTEGER,
  is_pulling SMALLINT(1) NOT NULL,
  pulling_increment INTEGER NOT NULL,
  created_at DATETIME NOT NULL,

  CONSTRAINT fk_channel_tg_user
    FOREIGN KEY (req_user_id)
    REFERENCES tg_user(id)
);

-- Create the content table
CREATE TABLE IF NOT EXISTS yt_content (
  id VARCHAR(255) PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  channel_id VARCHAR(255) NOT NULL,
  req_user_id INTEGER,
  pull_type VARCHAR(255) NOT NULL,
  latest_pull SMALLINT(1) DEFAULT 1,
  upload_date DATETIME NOT NULL,
  download_date DATETIME NOT NULL,
  subtitle_path VARCHAR(255),
  description_path VARCHAR(255),
  video_path VARCHAR(255) NOT NULL,
  audio_path VARCHAR(255) NOT NULL,
  video_size INTEGER NOT NULL,
  duration INTEGER(255) NOT NULL,
  image_height INTEGER NOT NULL,
  image_width INTEGER NOT NULL,

  CONSTRAINT fk_content_channel
    FOREIGN KEY (channel_id)
    REFERENCES yt_channel(id),

  CONSTRAINT fk_content_tg_user
    FOREIGN KEY (req_user_id)
    REFERENCES tg_user(id)

);

-- Create the content_status table
CREATE TABLE IF NOT EXISTS yt_content_status (
  id INTEGER PRIMARY KEY,
  content_id VARCHAR(255) NOT NULL,
  is_available SMALLINT(1) NOT NULL,
  status VARCHAR(255) NOT NULL,
  date DATETIME NOT NULL,

  CONSTRAINT fk_content_status_content
    FOREIGN KEY (content_id)
    REFERENCES yt_content(id)
);