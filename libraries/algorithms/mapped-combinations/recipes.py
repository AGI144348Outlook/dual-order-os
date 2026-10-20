"""Explicit trusted entry points. No eval, dynamic user code or autonomous selection."""
from libraries.echo_workspace import genesis

def generalization_views(words, lexicon):
    return genesis().GeneralizationStack(lexicon).stacks_for(words)

def retrieve_generalizations(words, lexicon, vgm):
    core=genesis();stacks=generalization_views(words,lexicon)
    return {'stacks':stacks,'matches':core.VGMQuery(vgm).query_multi(stacks)}

def candidate_understandings(lobby, budget=40):
    if type(budget) is not int or not 1<=budget<=100:raise ValueError('Candidate budget 1..100')
    core=genesis();pool=core.GeneralityMatrix([lobby]);pool.populate()
    vgm=core.ValidatedGeneralizationMatrix()
    count=core.UnderstandingGenerator(pool,core.SyntacticalValidator(),vgm).generate_combinatorial(budget)
    return {'pool_size':len(pool.pool),'accepted_candidates':count,'statements':vgm.statements,
            'rejected':vgm.rejected,'status':'heuristic-candidates-not-proven-logics'}

def inspect_expression(workspace,text,surface='english'):
    return workspace.query({'operation':'language','text':text,'surface':surface})
