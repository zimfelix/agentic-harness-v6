"""Independent acceptance for the frozen CRM title amendment."""
from pathlib import Path
import tempfile
from oracle import Server, deal, transition, won, audit, equal, race


def evaluate(project, artifacts):
    project, artifacts = Path(project).resolve(), Path(artifacts).resolve()
    artifacts.mkdir(parents=True, exist_ok=True)
    results = []
    def run(name, fn):
        try:
            with tempfile.TemporaryDirectory(dir=artifacts) as temp, Server(project, Path(temp) / 'db') as server:
                fn(server)
            results.append(dict(name=name, passed=True, outcome='pass'))
        except Exception as error:
            results.append(dict(name=name, passed=False, outcome='fail', error=repr(error)))
    def title(s):
        d = deal(s)
        updated = s.expect('PATCH', f'/deals/{d["id"]}', 200, {'version': 1, 'title': 'Corrected'})
        equal(updated['version'], 2); equal(updated['title'], 'Corrected'); equal(updated['status'], 'new')
        audit(s, ['deal.created', 'deal.updated'])
        updated = s.expect('PATCH', f'/deals/{d["id"]}', 200, {'version': 2, 'title': 'Combined', 'status': 'qualified'})
        equal(updated['version'], 3); equal(updated['title'], 'Combined'); equal(updated['status'], 'qualified')
        audit(s, ['deal.created', 'deal.updated', 'deal.transitioned'])
    def rejected(s):
        d = transition(s, deal(s), 'qualified')
        path = f'/deals/{d["id"]}'
        for body, code in [({'version': 1, 'title': 'Stale'}, 409),
                           ({'version': 2, 'title': 'Must not leak', 'status': 'new'}, 409),
                           ({'version': 2, 'title': ' '}, 400),
                           ({'version': 2, 'title': 'X', 'extra': 1}, 400)]:
            s.expect('PATCH', path, code, body)
            equal(s.expect('GET', path, 200), d)
        d = transition(s, d, 'won')
        s.expect('PATCH', path, 409, {'version': 3, 'title': 'Terminal'})
        equal(s.expect('GET', path, 200), d)
        audit(s, ['deal.created', 'deal.transitioned', 'deal.transitioned'])
    def rights(s):
        d = deal(s); path = f'/deals/{d["id"]}'
        s.expect('PATCH', path, 403, {'version': 1, 'title': 'X'}, token='viewer-a')
        s.expect('PATCH', path, 404, {'version': 1, 'title': 'X'}, token='editor-b')
        s.expect('PATCH', path, 400, {'version': 1, 'title': 'X', 'tenant': 'b'})
        equal(s.expect('GET', path, 200), d); audit(s, ['deal.created'])
    def competing(s):
        d = deal(s); path = f'/deals/{d["id"]}'
        outcomes = race(lambda i: s.request('PATCH', path, {'version': 1, 'title': f'Correction {i}'}))
        equal(sorted(x[0] for x in outcomes), [200,409,409,409,409,409])
        equal(s.expect('GET', path, 200)['version'], 2)
        audit(s, ['deal.created', 'deal.updated'])
    for name, fn in [('title-only-and-combined-once', title), ('failed-edit-atomic-and-terminal', rejected),
                     ('title-role-and-tenant-boundaries', rights), ('competing-title-corrections', competing)]:
        run(name, fn)
    return results
