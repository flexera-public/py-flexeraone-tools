import json
import logging
import requests
import sys
import click
import pprint

# Flexera Organization Capability List for command line validation
flexera_capabilities = [
    "fss",
    "fcm",
    "policy",
    "optima"
]

@click.command()
@click.option('--refresh-token', prompt="Refresh Token", help='Refresh Token from FlexeraOne', required=True)
@click.option('--host', '-h', prompt="IAM API Endpoint", default="api.flexeratest.com", show_default=True)
@click.option('--org-name', '-n', prompt="Organization Name", help="Organization Name", required=True)
@click.option('--first-name', '-f', prompt="Owner First Name", help="Owner First Name", required=True)
@click.option('--last-name', '-l', prompt="Owner Last Name", help="Owner Last Name", required=True)
@click.option('--email', '-e', prompt="Owner Email", help="Owner Email", required=True)
@click.option('--msp-org-id', '-m', prompt="MSP Org ID", help="MSP Org ID", required=True)
@click.option('--capabilities', '-o', prompt="Capability to Enable", required=True, multiple=True, type=click.Choice(flexera_capabilities))
def add_iam_msp_org(refresh_token, host, org_name, first_name, last_name, email, msp_org_id, capabilities):
    """
    Organization Add Tool for MSP's
    """
    # Tweak the destination (e.g. sys.stdout instead) and level (e.g. logging.DEBUG instead) to taste!
    logging.basicConfig(format='%(levelname)s:%(asctime)s:%(message)s', stream=sys.stderr, level=logging.INFO)
    access_token = generate_access_token(refresh_token, host)
    org_data = generate_org_data(org_name, first_name, last_name, email, set(capabilities))
    click.echo(org_data)
    create_org(host, access_token, msp_org_id, org_data)

def generate_access_token(refresh_token, host):
    domain = '.'.join(host.split('.')[-2:])
    token_url = "https://login.{}/oidc/token".format(domain)

    logging.info("OAuth2: Getting Access Token via Refresh Token for {} ...".format(token_url))
    token_post_request = requests.post(token_url, data={"grant_type": "refresh_token", "refresh_token": refresh_token})
    token_post_request.raise_for_status()
    access_token = token_post_request.json()["access_token"]
    return access_token

def generate_org_data(org_name, first_name, last_name, email, capabilities):
    """
    generate_org_data(org_name, first_name, last_name, email, capabilities)
    Generates org create data from inputs and returns org data object.
    """
    capability_name_list = []
    for capability in capabilities:
        capability_name_list.append({"Name": capability})

    org_data = {
        "name": org_name,
        "owners": [{"firstName": first_name, "lastName": last_name, "email": email}],
        "capabilities": capability_name_list
    }
    return org_data

def create_org(host, access_token, msp_org_id, org_data):
    """
    create_org(host, access_token, msp_org_id, org_data)
    Creates the org and logs the response.
    """
    headers = {"Authorization": "Bearer " + access_token, "Content-Type": "application/json"}
    kwargs = {"headers": headers, "allow_redirects": False}
    managed_service_provider_customer_url = "https://{}/msp/v1/orgs/{}/customers".format(host, msp_org_id)
    create_org_request = requests.post(managed_service_provider_customer_url, json.dumps(org_data), **kwargs, stream=True)
    create_org_request.raise_for_status()
    logging.info("Response: {}\nHeaders: {}\n".format(create_org_request.status_code, create_org_request.headers))
    new_org_url = "https://{}{}".format(host, create_org_request.headers['location'])
    get_response = requests.get(new_org_url, **kwargs)
    get_response.raise_for_status()
    logging.info("Response: {}\nHeaders: {}\n".format(get_response.status_code, get_response.headers))
    pprint.pprint(get_response.json())
