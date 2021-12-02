from main import flexera_cli
import click
from .msp.add_org import add_iam_msp_org
from .msp.del_org import del_iam_msp_org
from .msp.list_orgs import list_iam_msp_orgs
from .msp.update_org import update_iam_msp_org


@flexera_cli.group("iam")
@click.pass_obj
def iam_cli():
    pass

@iam_cli.group("msp")
@click.pass_obj
def msp_cli():
    pass


msp_cli.add_command(add_iam_msp_org(), "add")
msp_cli.add_command(del_iam_msp_org(), "delete")
msp_cli.add_command(list_iam_msp_orgs(), "list")
msp_cli.add_command(update_iam_msp_org(), "update")
