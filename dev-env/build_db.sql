
CREATE DATABASE IF NOT EXISTS memex_sotera;
USE memex_sotera;

DROP TABLE IF EXISTS datawake_team_users;
DROP TABLE IF EXISTS datawake_domains;
DROP TABLE IF EXISTS datawake_domain_entities;
DROP TABLE IF EXISTS datawake_trails;
DROP TABLE IF EXISTS datawake_selections;
DROP TABLE IF EXISTS datawake_data;
DROP TABLE IF EXISTS datawake_url_rank;
DROP TABLE IF EXISTS general_extractor_web_index;
DROP TABLE IF EXISTS domain_extractor_web_index;
DROP TABLE IF EXISTS scraping_feedback;
DROP TABLE IF EXISTS invalid_extracted_entity;
DROP TABLE IF EXISTS datawake_teams;

CREATE TABLE datawake_teams (
  id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(100),
  description TEXT,
  PRIMARY KEY(id),
  UNIQUE (name)
);


CREATE TABLE datawake_team_users (
  team_id INT,
  email VARCHAR(245),
  FOREIGN KEY (team_id) REFERENCES datawake_teams(id) ON DELETE CASCADE
);


CREATE TABLE datawake_domains (
  id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(300),
  description TEXT,
  team_id INT,
  FOREIGN KEY (team_id) REFERENCES datawake_teams(id) ON DELETE CASCADE,
  PRIMARY KEY(id),
  UNIQUE (name,team_id)
);


CREATE TABLE datawake_domain_entities (
  domain_id INT,
  feature_type varchar(100),
  feature_value varchar(1024),
  INDEX(domain_id,feature_type(100),feature_value(100))
);


CREATE TABLE datawake_trails (
  name VARCHAR(100) NOT NULL,
  created TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  created_by TEXT,
  description TEXT,
  org VARCHAR(300),
  domain VARCHAR(300),
  PRIMARY KEY(name,org,domain)
);


CREATE TABLE datawake_selections (
  id INT NOT NULL AUTO_INCREMENT,
  postId INT NOT NULL,
  selection TEXT,
  PRIMARY KEY(id),
  INDEX(postId)
);


CREATE TABLE datawake_data (
  id INT NOT NULL AUTO_INCREMENT,
  ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  url TEXT,
  userId TEXT,
  userName TEXT,
  trail VARCHAR(100),
  org VARCHAR(300),
  domain VARCHAR(300),
  PRIMARY KEY(id),
  INDEX(url(30))
);


CREATE TABLE datawake_url_rank (
  id INT NOT NULL AUTO_INCREMENT,
  url TEXT,
  userId TEXT,
  trailname VARCHAR(100),
  rank INT,
  org VARCHAR(300),
  domain VARCHAR(300),
  PRIMARY KEY(id),
  INDEX(url(30),userId(20),trailname)
);


CREATE TABLE general_extractor_web_index (
  url varchar(1024),
  entity_type varchar(100),
  entity_value varchar(1024),
  ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  index(url(300))
);


CREATE TABLE domain_extractor_web_index (
  domain VARCHAR(300),
  url varchar(1024),
  entity_type varchar(100),
  entity_value varchar(1024),
  ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  index(domain(300),url(300))
);


CREATE TABLE scraping_feedback (
  entity_type varchar(100),
  entity_value varchar(1024),
  raw_text varchar (100),
  url TEXT,
  domain varchar (300),
  org VARCHAR(300),
  index(org(300),domain(300))
);


CREATE TABLE invalid_extracted_entity (
  entity_value varchar (1024),
  entity_type varchar (100),
  domain varchar (300),
  org VARCHAR(300),
  userName TEXT,
  ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  index(org(300),domain(300), entity_type(100), entity_value(100))
);

\q
