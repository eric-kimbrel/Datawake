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

import re
import json

import tangelo

import datawake.util.db.datawake_mysql as db
from datawake.util.session.helper import is_in_session
from datawake.util.session import helper
from datawake.util.validate.parameters import required_parameters


"""
 List / Create Trails

    primarily used on the plugin newTab.

"""

#
# Perform a starts-with search for trails
#
@tangelo.restful
@is_in_session
@required_parameters(['domain_id','team_id'])
@tangelo.types(domain_id=int,team_id=int)
def get(team_id,domain_id):
    """
    Verifies the current signed in user has access to the domain and team,
    then returns trails
    :param team_id:
    :param domain_id:
    :return: Trails for the team and domain.
      [{id:trailid,name:trailname,description:traildescriptin},..]
    """

    user = helper.get_user()

    # verify the user can access the team
    if not db.hasTeamAccess(user.get_email(),team_id):
        tangelo.content_type()
        tangelo.http_status(401)
        tangelo.log("401 Unauthorized")
        return "401 Unauthorized"

    # verify the team can access the domain
    domains = db.get_domains(team_id)
    valid = False
    for domain in domains:
        if domain['id'] == domain_id:
            valid = True
            break
    if not valid:
        tangelo.content_type()
        tangelo.http_status(401)
        tangelo.log("401 Unauthorized ")
        return "401 Unauthorized"


    # get and return the trails
    trails = db.listTrails(team_id, domain_id)
    return json.dumps(trails)



@is_in_session
@required_parameters(['team_id','domain_id', 'name'])
@tangelo.types(domain_id=int,team_id=int)
def add_trail(team_id,domain_id,name,description=''):

    tangelo.log('datawake_trails POST name=%s description=%s domain=%s team=%s' % (name, description, domain_id,team_id))

    #check the trail name
    if name is None or len(name) < 1:
        raise ValueError("Trail names must have at least one character")

    user = helper.get_user()

    # verify the user can access the team
    if not db.hasTeamAccess(user.get_email(),team_id):
        tangelo.content_type()
        tangelo.http_status(401)
        tangelo.log("401 Unauthorized")
        return "401 Unauthorized"

    # verify the team can access the domain
    domains = db.get_domains(team_id)
    valid = False
    for domain in domains:
        if domain['id'] == domain_id:
            valid = True
            break
    if not valid:
        tangelo.content_type()
        tangelo.http_status(401)
        tangelo.log("401 Unauthorized ")
        return "401 Unauthorized"

    # create and then return the new trail
    try:
        newTrailId = db.addTrail(team_id,domain_id,name, description, user.get_email())
        newTrail = dict(id=newTrailId,name=name,description=description)
        tangelo.log(newTrail)
        return json.dumps(newTrail)
    except Exception as e:
        tangelo.log(e)
        tangelo.http_status(501)
        return "Failed to create trail. This trail name may already be used."



post_actions = {
    'create': add_trail
}


@tangelo.restful
def post(action, *args, **kwargs):
    body = tangelo.request_body().read()
    post_data = json.loads(body, strict=False)

    def unknown(**kwargs):
        return tangelo.HTTPStatusCode(404, "unknown service call")

    return post_actions.get(action, unknown)(**post_data)