"""

Copyright 2014 Sotera Defense Solutions, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

import sys

import mysql.connector
from mysql.connector import errorcode
import tangelo

from datawake.conf import datawakeconfig as dbconfig


"""

Interface to datawake relational database tables (mysql)

"""




#

# ##  GENERIC DB FUNCTIONS ###


#
# Returns a connection to the datawake database
#
def get_cnx():
    user = dbconfig.DATAWAKE_CORE_DB['user']
    db = dbconfig.DATAWAKE_CORE_DB['database']
    pw = dbconfig.DATAWAKE_CORE_DB['password']
    host = dbconfig.DATAWAKE_CORE_DB['host']
    port = dbconfig.DATAWAKE_CORE_DB['port']
    return mysql.connector.connect(user=user, password=pw, host=host, database=db, port=port)


#
# Executes a sql statement and commits it.
# returns the cursor last row id, which may be null
#
def dbCommitSQL(sql, params):
    cnx = get_cnx()
    cursor = cnx.cursor()
    try:
        cursor.execute(sql, params)
        cnx.commit()
        return cursor.lastrowid
    finally:
        cnx.close()
        cursor.close()


#
# Return all rows from a select query
#
def dbGetRows(sql, params):
    cnx = get_cnx()
    cursor = cnx.cursor()
    try:
        cursor.execute(sql, params)
        return cursor.fetchall()
    finally:
        cnx.close()
        cursor.close()


# ###   BROWSE PATH SCRAPE  ###


#
# Add a post to the posts table (datawake_data)
#
def addBrowsePathData(org, url, userId, userName, trail=None, domain='default'):
    org = org.upper()
    sql = " INSERT INTO datawake_data (url,userId,userName,trail,org,domain) VALUES (%s,%s,%s,%s,%s,%s) "
    params = [url, userId, userName, trail, org, domain]
    lastId = dbCommitSQL(sql, params)
    return lastId


def get_post_id(url):
    sql = "select id from datawake_data where url=%s limit 1;"
    params = [url]
    rows = dbGetRows(sql, params)
    if len(rows) == 0:
        return -1
    return rows[0][0]


#
# Get a post from the posts table (datwake_data)
#

def getBrowsePathData(org, id, domain='default'):
    org = org.upper()
    sql = "SELECT id,ts,url,trail,org FROM datawake_data where org = %s AND id = %s AND domain = %s"
    params = [org, id, domain]
    row = dbGetRows(sql, params)[0]
    return {
        'id': row[0],
        'ts': row[1],
        'url': row[2].encode(),
        'trail': row[3],
        'org': row[4]
    }


#
# Get all time stamps from the selected trail,users,org
# returns a dictionary of the form  {'min':0,'max':0,'data':[]}
#
def getTimeWindow(org, users, trail='*', domain='default'):
    sql = 'SELECT unix_timestamp(ts) as ts from datawake_data WHERE org = %s AND domain = %s '
    params = [org.upper(), domain]

    # add where clause for trail and users
    if trail != '*':
        sql = sql + ' AND trail = %s '
        params.append(trail)
    if len(users) > 0:
        param_string = ','.join(['%s' for i in range(len(users))])
        sql = sql + ' AND userName in (' + param_string + ') '
        params.extend(users)

    sql = sql + ' order by ts asc'
    rows = dbGetRows(sql, params)
    data = map(lambda x: x[0], rows)
    if len(data) == 0:
        return {'min': 0, 'max': 0, 'data': []}
    else:
        return {'min': data[0], 'max': data[-1], 'data': data}


#
# Return a list of hourly counts in the form {ts:_,count:_}
#
def getHourlyBrowsePathCounts(org, users, trail, domain='default'):
    sql = 'SELECT (unix_timestamp(ts) DIV 3600)*3600  as group_hour, count(1) from datawake_data where org = %s AND domain = %s '
    params = [org.upper(), domain]
    if trail != '*' and trail != '':
        sql = sql + ' AND trail = %s '
        params.append(trail)
    if len(users) > 0:
        param_string = ','.join(['%s' for i in range(len(users))])
        sql = sql + ' AND userId in (' + param_string + ') '
        params.extend(users)
    sql = sql + " GROUP BY group_hour"


    rows = dbGetRows(sql, params)
    result = []
    delta = 3600
    if len(rows) > 0: curr = rows[0][0]
    for row in rows:
        if row[0] is None: continue
        print 'row ', row
        dt = row[0]
        while (dt - curr > 3600):
            curr = curr + delta
            result.append({'ts': curr, 'count': 0})
        result.append({'ts': dt, 'count': row[1]})
        curr = dt

    # add one hour
    if len(result) > 0:
        curr = curr + 3600
        result.append({'ts': curr, 'count': 0})

    return result


#
# Delete all user activity for a selected user within a time frame and org
#
def deleteUserData(org, user, startdate, enddate, domain='default'):
    sql = """DELETE from datawake_data
              where org = %s AND
              domain = %s AND
              userName = %s AND
              unix_timestamp(ts) >=%s AND
              unix_timestamp(ts) <= %s
           """
    params = [org.upper(), domain, user, startdate, enddate]
    return dbCommitSQL(sql, params)


#
# Associate a text selection with a post Id
# by adding it to the selections table
#
def addSelection(postId, selection):
    sql = " INSERT INTO datawake_selections (postId,selection) VALUES (%s,%s) "
    return dbCommitSQL(sql, [postId, selection])


def getSelections(domain, trail, url, org):
    sql = """SELECT datawake_selections.selection
              FROM datawake_selections
              INNER JOIN datawake_data
              ON datawake_selections.postId=datawake_data.id
              WHERE datawake_data.url = %s
              AND datawake_data.domain = %s
              AND datawake_data.trail = %s
              AND datawake_data.org = %s"""
    params = [url, domain, trail, org]
    rows = dbGetRows(sql, params)
    return map(lambda x: x[0], rows)


# ##  ORGANIZATIONS  ###





#
# Return a list or (team_id,team_name)
#
def getTeams(email):

    sql = """
        SELECT t1.id,t1.name
        FROM datawake_teams as t1
        INNER JOIN datawake_team_users as t2 ON t1.id = t2.team_id
        WHERE  t2.email = %s
    """
    rows = dbGetRows(sql, [email])
    return map(lambda x: dict(id= x[0], name =x[1]),rows)


def hasTeamAccess(email,team_id):
    teams = getTeams(email)
    sql = """
        SELECT t1.id,t1.name
        FROM datawake_teams as t1
        INNER JOIN datawake_team_users as t2 ON t1.id = t2.team_id
        WHERE  t2.email = %s AND t1.id = %s
    """
    rows = dbGetRows(sql,[email,team_id])
    return len(rows) > 0




#
# Create a new team
#
def createTeam(name,description,emails=[]):
    team_id = dbCommitSQL("INSERT INTO datawake_teams (name,description) VALUES (%s,%s)",[name,description])
    inserts = []
    params = []
    for email in emails:
        inserts.append("INSERT INTO datawake_team_users (team_id,email) VALUES (%s,%s)")
        params.append(team_id)
        params.append(email)
    dbCommitSQL(';'.join(inserts),params)
    return (team_id,name)



#
# Return users within an org who have been active on at least one trail
# returns a list of dicts, {name:_, id:_}
#
def getActiveUsers(org):
    sql = """select distinct(userId), username from datawake_data where org = %s """
    rows = dbGetRows(sql, [org.upper()])
    result = map(lambda x: {'name': x[1].encode(), 'id': x[0]}, rows)
    return result


### TRAILS ###


#
# Ad a new trail to the trails table
#
def addTrail(org, name, description, userId, domain='default'):
    org = org.upper()
    sql = "INSERT INTO datawake_trails (name,description,created_by,org,domain) values (%s,%s,%s,%s,%s)"
    return dbCommitSQL(sql, [name, description, userId, org, domain])


#
# Get a list of all trails name and description
#
def listTrails(org, domain='default'):
    org = org.upper()
    sql = "select name,description,unix_timestamp(created) from datawake_trails where org = %s AND domain = %s ORDER BY created DESC"
    rows = dbGetRows(sql, [org, domain])
    return map(lambda x: {'name': x[0], 'description': x[1], 'created': x[2]}, rows)


#
# Return a list of trail names found in the datawake_data table
#
def get_active_trail_names(org, domain='default'):
    sql = "Select distinct(trail) from datawake_data where org = %s AND domain = %s "
    params = [org.upper(), domain]
    trails = dbGetRows(sql, params)
    trails = map(lambda x: x[0], trails)
    trails = filter(lambda x: x is not None and x != '', trails)
    return trails


#
# Return a mapping of org name to list of active trails
#
def get_all_active_trails(domain='default'):
    sql = "select distinct trail,org from datawake_data where domain = %s "
    rows = dbGetRows(sql, [domain])
    org_trails = {}
    for row in rows:
        (trail, org) = row
        if org not in org_trails:
            org_trails[org] = []
        org_trails[org].append(trail)
    return org_trails


#
# Return list of trails within an org  with counts of user and sze of trail
#
def getTrailsWithUserCounts(org):
    org = org.upper()
    sql = """
        select domain,trail, count(distinct(userId)) as users, count(distinct(id)) as records
        from datawake_data
        where trail is not NULL AND org = %s
        group by domain,trail
       """
    rows = dbGetRows(sql, [org])
    return map(lambda x: {'domain': x[0], 'trail': x[1], 'userCount': x[2], 'records': x[3]}, rows)



####   URL RANKS   ####


#
# Rank a url
#
def rankUrl(org, userId, trailname, url, rank, domain='default'):
    org = org.upper()
    sql = """SELECT id
            FROM datawake_url_rank
            WHERE org = %s AND
            domain = %s AND
            userId = %s AND
            trailname = %s AND
            url = %s"""
    params = [org, domain, userId, trailname, url]
    rows = dbGetRows(sql, params)

    # update existing row
    if len(rows) > 0:
        id = rows[0][0]
        sql = """UPDATE datawake_url_rank
                 SET rank = %s
                 WHERE id = %s
               """
        dbCommitSQL(sql, [rank, id])

    # insert a new row
    else:
        sql = """ INSERT INTO datawake_url_rank (userId,trailname,url,rank,org,domain)
                  VALUES (%s,%s,%s,%s,%s,%s)
              """
        params = [userId, trailname, url, rank, org, domain]
        dbCommitSQL(sql, params)


#
# Get url rank for a user and trail
# Always returns a rank, defaults to 0
#
def getUrlRank(org, userId, trailname, url, domain='default'):
    org = org.upper()
    sql = """ SELECT rank
              FROM datawake_url_rank
              WHERE org = %s AND domain = %s AND userId = %s AND trailname = %s AND url = %s
          """
    params = [org, domain, userId, trailname, url]
    rows = dbGetRows(sql, params)
    if len(rows) == 0:
        return 0
    else:
        return rows[0][0]


#
# return a dict of url->rank for a single user within a trail and org
#
def getUserUrlRanks(org, userId, trail, domain='default'):
    sql = "SELECT url,rank from datawake_url_rank where org = %s AND domain =%s AND userId = %s AND trailname= %s"
    params = [org.upper(), domain, userId, trail]
    rows = dbGetRows(sql, params)
    ranks = {}
    for row in rows:
        ranks[row[0]] = row[1]
    return ranks



#
# return a dict of url->rank for a single user within a trail and org
#
def getRankedUrls(org, trail, domain='default'):
    sql = "SELECT url,rank from datawake_url_rank where org = %s AND domain =%s AND trailname= %s AND rank > 0"
    params = [org.upper(), domain, trail]
    rows = dbGetRows(sql, params)
    return rows


####  URL Counts ####


#
# Get the number of times a url has been recorded
# by the data wake
#
def getUrlCount(org, url, domain='default'):
    org = org.upper()
    sql = "SELECT count(1) from datawake_data where url = %s AND org = %s AND domain = %s "
    params = [url, org, domain]
    rows = dbGetRows(sql, params)
    if len(rows) == 0:
        return 0
    else:
        return rows[0][0]


#### Datawake Domains ####



def get_domains(team_id):
    sql = "SELECT id,name,description from datawake_domains where team_id = %s"
    rows = dbGetRows(sql, [team_id])
    return map(lambda x: dict(id=x[0],name=x[1],description=x[2]),rows)


def add_new_domain(team_id,name, description):
    sql = "INSERT INTO datawake_domains (name,description,team_id) values (%s,%s,%s)"
    params = [name, description, team_id]
    dbCommitSQL(sql, params)


def remove_domain(domain_id):
    dbCommitSQL("DELETE FROM datawake_domains WHERE id = %s", [domain_id])







def add_extractor_feedback(org, domain, raw_text, entity_type, entity_value, url):
    sql = "insert into scraping_feedback(org, domain, raw_text, entity_type, entity_value, url) value (%s,%s,%s,%s,%s,%s)"
    return dbCommitSQL(sql, [org, domain, raw_text, entity_type, entity_value, url])


def get_feedback_entities(org, domain, url):
    sql = "select entity_type, entity_value from scraping_feedback where url=%s and domain=%s and org=%s"
    params = [url, domain, org]
    rows = dbGetRows(sql, params)
    return map(lambda x: dict(type=x[0], value=x[1]), rows)


def get_invalid_extracted_entity_count(user_name, entity_type, entity_value, domain, org):
    sql = "select count(*) from invalid_extracted_entity where userName=%s and entity_type=%s and entity_value=%s and domain=%s and org=%s"
    params = [user_name, entity_type, entity_value, domain, org]
    return dbGetRows(sql, params)[0][0]


def mark_invalid_extracted_entity(user_name, entity_type, entity_value, domain, org):
    count = get_invalid_extracted_entity_count(user_name, entity_type, entity_value, domain, org)
    if count == 0:
        params = [user_name, entity_type, entity_value, domain, org]
        sql = "insert into invalid_extracted_entity(userName, entity_type, entity_value, domain, org) value (%s,%s,%s,%s,%s)"
        return dbCommitSQL(sql, params)
    else:
        return -1

def get_marked_entities(org, domain, user_name):
    sql = "select entity_value from invalid_extracted_entity where org=%s and domain=%s and userName=%s"
    params = [org, domain, user_name]
    rows = dbGetRows(sql, params)
    return map(lambda x: dict(value=x[0]), rows)



def get_marked_entities_for_domain(org, domain):
    sql = "select entity_type,entity_value from invalid_extracted_entity where org=%s and domain=%s"
    params = [org, domain]
    rows = dbGetRows(sql, params)
    return rows