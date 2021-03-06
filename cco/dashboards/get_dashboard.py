import logging
import requests
import sys
import click
import json
import os

# Tweak the destination (e.g. sys.stdout instead) and level (e.g. logging.DEBUG instead) to taste!
logging.basicConfig(format='%(levelname)s:%(asctime)s:%(message)s', stream=sys.stderr, level=logging.INFO)

@click.command(no_args_is_help=True)
@click.option('--refresh-token', prompt="Refresh Token", help='Refresh Token from FlexeraOne', required=True)
@click.option('--host', '-h', prompt="IAM API Endpoint", default="api.flexeratest.com", show_default=True)
@click.option('--org-id', '-i', prompt="Organization ID", help="Organization ID", required=True)
@click.option('--dashboard-type', help="Is this a User or Org Dashboard", required=True, type=click.Choice(['org', 'user']))
@click.option('--user-id', required=False, help="User id if user option is set")
@click.option('--dashboard-id', required=True, prompt="Dashboard Id")
@click.option('--clean', required=False, default=False, type=bool)
def get_dashboard(refresh_token, host, org_id, dashboard_type, user_id, dashboard_id, clean):
    """
    list_dashboards
    """
    # Tweak the destination (e.g. sys.stdout instead) and level (e.g. logging.DEBUG instead) to taste!
    logging.basicConfig(format='%(levelname)s:%(asctime)s:%(message)s', stream=sys.stderr, level=logging.INFO)
    access_token = generate_access_token(refresh_token, host)
    # ===== Use Access Token as Bearer token from them on ===== #
    auth_headers = {"Api-Version": "1.0", "Authorization": "Bearer " + access_token}
    kwargs = {"headers": auth_headers, "allow_redirects": False}
    if host == 'api.flexera.com':
        optima_host = 'api.optima.flexeraeng.com'
    elif host == 'api.flexera.eu':
        optima_host = 'api.optima-eu.flexeraeng.com'
    dashboard_get_url = "https://{}/bill-analysis/orgs/{}".format(optima_host, org_id)
    if dashboard_type == 'user':
        dashboard_get_url = dashboard_get_url + "/users/{}/dashboards".format(user_id)
    else:
        dashboard_get_url = dashboard_get_url + "/dashboards"
    dashboard_get_url = dashboard_get_url + "/{}".format(dashboard_id)

    headers = {"Authorization": "Bearer " + access_token, "Content-Type": "application/json"}
    kwargs = {"headers": headers, "allow_redirects": False}
    get_response = requests.get(dashboard_get_url, **kwargs)
    get_response.raise_for_status()
    dashboard_json = get_response.json()
    dashboard_name = dashboard_json["name"].replace(' ', '_')
    if clean:
        for key in ["id", "href", "kind", "created_at", "updated_at"]:
            dashboard_json.pop(key)
    os.makedirs("dashboards", exist_ok=True)
    dashboard_filename = 'dashboards/{}.json'.format(dashboard_name)
    with open(dashboard_filename, 'w', encoding='utf-8') as json_file:
        jsonString = json.dumps(dashboard_json, indent=2)
        json_file.write(jsonString)
    logging.info("Dashboard File Created: {}".format(dashboard_filename))

def generate_access_token(refresh_token, host):
    domain = '.'.join(host.split('.')[-2:])
    token_url = "https://login.{}/oidc/token".format(domain)

    logging.info("OAuth2: Getting Access Token via Refresh Token for {} ...".format(token_url))
    token_post_request = requests.post(token_url, data={"grant_type": "refresh_token", "refresh_token": refresh_token})
    token_post_request.raise_for_status()
    access_token = token_post_request.json()["access_token"]
    return access_token


if __name__ == '__main__':
    # click passes no args
    # pylint: disable=no-value-for-parameter
    get_dashboard(auto_envvar_prefix='FLEXERA')
