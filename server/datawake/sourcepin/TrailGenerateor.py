import sys
import json
import argparse
import datawake.util.db.datawake_mysql as db
from datawake.util.dataconnector import factory
from datawake.extractor import master_extractor as extractors


"""
Auto generate a trail based a dump from source pin.


"""

USER_ID = 'auto'
USER_NAME = 'auto'

def addTrail(org,domain,name):
    exists = False
    for result in db.listTrails(org,domain):
        if result['name'] == 'name':
            exists = True
            break

    if not exists:
        db.addTrail(org, name, "auto generated trail", USER_ID, domain=domain)





def generate_trail(org,trail,domain,filename):


    file = open(filename,'r')
    addTrail(org,domain,trail)
    connector = factory.get_entity_data_connector()
    i = 0
    for line in file:
        i = i + 1
        print 'processing line: ',i

        jsonObj = json.loads(line, strict=False)

        url = jsonObj['url']
        html = ''
        if 'html_rendered' in jsonObj:
            html = jsonObj['html_rendered']
        elif 'html' in jsonObj:
            html = jsonObj['html']
        else:
            print 'no html on line ',i
            continue

        (features,errors) = extractors.extractAll(html)

        for type,values in features.iteritems():
            connector.insert_entities(url,type,values)

            if len(values) > 0:
                features_in_domain = connector.get_domain_entity_matches(domain,type,values)
                if len(features_in_domain) > 0:
                    connector.insert_domain_entities(domain,url, type, features_in_domain)



        for error in errors:
            print "FEATURE EXTRACTION ERROR: ",error


        db.addBrowsePathData(org, url, 'auto', 'auto', trail, domain=domain)



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process json to populate a trail.')
    parser.add_argument('org')
    parser.add_argument('trail')
    parser.add_argument('domain')
    parser.add_argument('jsonFile', help='Input file name.')
    args = parser.parse_args()


    generate_trail(args.org,args.trail,args.domain,args.jsonFile)

