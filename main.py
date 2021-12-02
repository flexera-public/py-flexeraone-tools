import click
from iam import iam
from click_option_group import optgroup

# https://stackoverflow.com/questions/34643620/how-can-i-split-my-click-commands-each-with-a-set-of-sub-commands-into-multipl
@click.group()
@optgroup.group('Connection configuration',
                help='The configuration of some server connection')
@optgroup.option('--refresh-token', prompt="Refresh Token", help='Refresh Token from FlexeraOne', required=True)
@optgroup.option('--host', '-h', prompt="IAM API Endpoint", default="api.flexeratest.com", show_default=True)
@click.pass_context
def flexera_cli():
    pass


if __name__ == '__main__':
    # click passes no args
    # pylint: disable=no-value-for-parameter
    flexera_cli.add_command(iam.iam.iam_cli(), "iam")
    flexera_cli(auto_envvar_prefix='FLEXERA')
