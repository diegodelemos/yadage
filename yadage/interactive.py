import click
# import IPython

def decide_rule(rule, controller, idbased):
    click.secho('we could extend DAG with rule', fg='blue')
    if idbased:
        rule = next(x for x in controller.adageobj.rules if x.identifier == rule)

    click.secho('rule: {}/{} ({})'.format(rule.offset,
                                          rule.rule.name, rule.identifier))
    # IPython.embed()
    resp = raw_input(click.style("Shall we? (y/N) ", fg='blue'))
    shall = resp.lower() == 'y'
    if shall:
        click.secho('ok we will extend.', fg='green')
    else:
        click.secho('maybe another time... your response: {}'.format(
            resp), fg='yellow')
    return shall


def decide_step(node, controller, idbased):


    if idbased:
        node = controller.adageobj.dag.getNode(node)

    click.echo('we could submit a DAG node {}'.format(node))
    # IPython.embed()
    resp = raw_input(click.style("Shall we? (y/N) ", fg='magenta'))
    shall = resp.lower() == 'y'
    if shall:
        click.secho('ok we will submit.', fg='green')
    else:
        click.secho('will not submit for now... your response: {}'.format(
            resp), fg='yellow')
    return shall


def custom_decider(decide_func, idbased):
    # we yield until we receive some data via send()
    def decider():
        data = yield
        while True:
            data = yield decide_func(*data, idbased = idbased)
    return decider


def interactive_deciders(idbased = False):
    '''
    returns a tuple (extend,submit) of already-primed deciders for both
    extension and submission
    '''
    extend_decider = custom_decider(decide_rule, idbased)()
    extend_decider.next()  # prime decider

    submit_decider = custom_decider(decide_step, idbased)()
    submit_decider.next()  # prime decider

    return extend_decider, submit_decider
