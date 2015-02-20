USE memex_sotera;

INSERT INTO datawake_teams (name,description) VALUES ("team1","test team 1");
INSERT INTO datawake_teams (name,description) VALUES ("team2","test team 2");

INSERT INTO datawake_team_users (team_id,email) VALUES (1,"john.doe@nomail.none");
INSERT INTO datawake_team_users (team_id,email) VALUES (2,"john.doe@nomail.none");


INSERT INTO datawake_domains (name,description,team_id) VALUES ("domain1","first domain",1);
INSERT INTO datawake_domains (name,description,team_id) VALUES ("domain2","second domain",2);
INSERT INTO datawake_domains (name,description,team_id) VALUES ("domain3","another domain",1);
INSERT INTO datawake_domains (name,description,team_id) VALUES ("domain4","yet another domain",2);


INSERT INTO datawake_trails (name,team_id,domain_id) VALUES ("trail1",1,1);
INSERT INTO datawake_trails (name,team_id,domain_id) VALUES ("trail2",1,3);
INSERT INTO datawake_trails (name,team_id,domain_id) VALUES ("trail3",1,3);


\q
