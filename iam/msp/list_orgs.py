import logging
import requests
import sys
import click
import jellyfish
from click_option_group import optgroup, MutuallyExclusiveOptionGroup
import pprint
import json

@click.command(no_args_is_help=True)
@optgroup.group('Connection configuration',
                help='The configuration of some server connection')
@optgroup.option('--refresh-token', prompt="Refresh Token", help='Refresh Token from FlexeraOne', required=True)
@optgroup.option('--host', '-h', prompt="IAM API Endpoint", default="api.flexeratest.com", show_default=True)
@optgroup.option('--msp-org-id', '-m', prompt="MSP Org ID", help="MSP Org ID", required=True)
@optgroup.option('--filename', '-f', help="Filename to save results to.")
@optgroup.group('Org Options', cls=MutuallyExclusiveOptionGroup,
                help='Org Options, either id or name')
@optgroup.option('--org-id', '-o', help='Org ID to Get')
@optgroup.option('--org-name', '-n', help="Organization Name to find. Using the name will only print close orgs")
def list_iam_msp_orgs(**params):
    """
    Lists Organizations and allows search by name
    """
    # Tweak the destination (e.g. sys.stdout instead) and level (e.g. logging.DEBUG instead) to taste!
    click.echo(params)
    logging.basicConfig(format='%(levelname)s:%(asctime)s:%(message)s', stream=sys.stderr, level=logging.INFO)
    # click.echo(orgs[['id', 'name', 'match_score']])
    access_token = generate_access_token(params['refresh_token'], params['host'])
    if params['org_id']:
        orgs = get_org(params['host'], access_token, params['msp_org_id'], params['org_id'])
    else:
        org_list = list_orgs(params['host'], access_token, params['msp_org_id'])
        if params['org_name']:
            orgs = get_closest_match(params['org_name'], org_list)
        else:
            orgs = org_list
    if params['filename']:
        with open(params['filename'], 'w+') as f:
            f.write(json.dumps(orgs, indent=4, sort_keys=False))
    else:
        pprint.pprint(orgs)

def generate_access_token(refresh_token, host):
    domain = '.'.join(host.split('.')[-2:])
    token_url = "https://login.{}/oidc/token".format(domain)

    logging.info("OAuth2: Getting Access Token via Refresh Token for {} ...".format(token_url))
    token_post_request = requests.post(token_url, data={"grant_type": "refresh_token", "refresh_token": refresh_token})
    token_post_request.raise_for_status()
    access_token = token_post_request.json()["access_token"]
    return access_token

def get_org(host, access_token, msp_org_id, org_id):
    headers = {"Authorization": "Bearer " + access_token, "Content-Type": "application/json"}
    kwargs = {"headers": headers, "allow_redirects": False}
    managed_service_provider_customer_url = "https://{}/msp/v1/orgs/{}/customers/{}".format(host, msp_org_id, org_id)
    get_response = requests.get(managed_service_provider_customer_url, **kwargs)
    get_response.raise_for_status()
    return get_response.json()

def list_orgs(host, access_token, msp_org_id):
    headers = {"Authorization": "Bearer " + access_token, "Content-Type": "application/json"}
    kwargs = {"headers": headers, "allow_redirects": False}
    managed_service_provider_customers_url = "https://{}/msp/v1/orgs/{}/customers".format(host, msp_org_id)
    get_response = requests.get(managed_service_provider_customers_url, **kwargs)
    get_response.raise_for_status()
    return get_response.json()

def get_closest_match(x, org_list):
    number_of_changes_needed = 0
    for org in org_list:
        match_score = jellyfish.damerau_levenshtein_distance(org['name'], x)
        org['match_score'] = match_score
        if number_of_changes_needed < match_score:
            number_of_changes_needed = match_score
    best_match = list(filter(lambda x: x['match_score'] < number_of_changes_needed/2, org_list))
    top_ten = sorted(best_match, key=lambda i: i['match_score'])[:10]
    return top_ten
