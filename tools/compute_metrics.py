#!/usr/bin/env python3
"""
PayFlow : calcule les métriques du dossier à partir du code et des données.
Usage : python3 tools/compute_metrics.py [racine_du_dossier]   (Python 3, aucune dépendance)
Si votre PaymentService.java local diffère du nôtre, remplacez le fichier puis relancez.

Conventions (à annoncer dans la présentation, elles changent les valeurs) :
- LOC : lignes non vides hors commentaires (les accolades seules comptent).
- V(G) = nombre de if / for / while / case / catch / ?: / && / || + 1.
- Halstead : opérateurs = mots-clés (dont types primitifs, void, new, return...) et symboles ;
  les paires () et {} comptent pour 1 opérateur ; ; , . sont des opérateurs ;
  opérandes = identifiants (noms de classes, méthodes, variables) et littéraux.
  Les lignes package/import et les paramètres génériques <...> ne sont pas comptés.
- MI = max(0, (171 - 5.2 ln V - 0.23 G - 16.2 ln LOC) * 100 / 171), G = plus grand V(G) d'une méthode.
"""
import csv, math, re, sys, glob, os
from datetime import datetime

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..')
KW = set('''abstract boolean break case catch char class continue default do double else extends final finally float
for if implements import instanceof int long new package private protected public return static super switch
this throw throws try void while'''.split())
LIT_KW = {'true', 'false', 'null'}

def strip_comments(t):
    t = re.sub(r'/\*.*?\*/', '', t, flags=re.S)
    return re.sub(r'//[^\n]*', '', t)

def code_lines(t):
    return [l for l in strip_comments(t).split('\n') if l.strip()]

def halstead(text):
    t = strip_comments(text)
    t = '\n'.join(l for l in t.split('\n') if not l.strip().startswith(('package ', 'import ')))
    t = re.sub(r'"(?:\\.|[^"\\])*"', lambda m: ' STR_%d ' % (abs(hash(m.group())) % 10**8), t)
    t = re.sub(r'\b([A-Z]\w*)<[^<>()=;]*>', r'\1', t)
    toks = re.findall(r'STR_\d+|\d+\.\d+|\d+|[A-Za-z_]\w*|&&|\|\||<=|>=|==|!=|\+\+|--|[-+*/%=<>!&|?:;,.(){}\[\]]', t)
    ops, opd = [], []
    for k in toks:
        if k in (')', '}', ']'):
            continue
        if k in KW or not (re.match(r'[A-Za-z_]', k) or re.match(r'\d', k) or k.startswith('STR_')):
            ops.append({'(': '()', '{': '{}', '[': '[]'}.get(k, k))
        else:
            opd.append(k)
    n1, n2, N1, N2 = len(set(ops)), len(set(opd)), len(ops), len(opd)
    N, n = N1 + N2, n1 + n2
    V = N * math.log2(n) if n > 1 else 0
    D = (n1 / 2) * (N2 / n2) if n2 else 0
    return dict(n1=n1, n2=n2, N1=N1, N2=N2, N=N, n=n, V=V, D=D, E=D * V)

def vg(body):
    b = strip_comments(re.sub(r'"(?:\\.|[^"\\])*"', '""', body))
    return 1 + len(re.findall(r'\b(?:if|for|while|case|catch)\b|&&|\|\||\?', b))

def parse_class(path):
    text = open(path, encoding='utf-8').read()
    lines = text.split('\n')
    name = re.search(r'public class (\w+)', text).group(1)
    attrs, methods, i = [], [], 0
    while i < len(lines):
        l = lines[i]
        m = re.match(r'^ {4}(public|private)\s+(?:final\s+)?[\w<>, \[\]]+?\s+(\w+)\s*(=[^;]*)?;\s*$', l)
        if m and '(' not in l.split('=')[0]:
            attrs.append((m.group(2), m.group(1)))
        m = re.match(r'^ {4}(public|private)\s+[\w<>, \[\]]+?\s+(\w+)\(', l)
        if m:
            depth, body, j = 0, [], i
            while True:
                body.append(lines[j])
                depth += lines[j].count('{') - lines[j].count('}')
                if depth == 0 and '{' in ''.join(body):
                    break
                j += 1
            methods.append(dict(name=m.group(2), vis=m.group(1), text='\n'.join(body)))
            i = j
        i += 1
    return dict(name=name, text=text, attrs=attrs, methods=methods)

def calls(body):
    b = re.sub(r'"(?:\\.|[^"\\])*"', '""', strip_comments(body))
    b = b.split('{', 1)[1]
    b = re.sub(r'\bnew\s+\w+', '', b)
    return {c for c in re.findall(r'(\w+)\s*\(', b) if c not in KW}

def analyse(folder):
    classes = [parse_class(p) for p in sorted(glob.glob(os.path.join(folder, '*.java')))]
    names = [c['name'] for c in classes]
    res = []
    for c in classes:
        for m in c['methods']:
            m['vg'] = vg(m['text'])
        wmc = sum(m['vg'] for m in c['methods'])
        cond = wmc - len(c['methods'])
        body_all = c['text']
        coupled = {o for o in names if o != c['name'] and re.search(r'\b%s\b' % o, body_all)}
        coupled |= {o['name'] for o in classes if o['name'] != c['name'] and re.search(r'\b%s\b' % c['name'], o['text'])}
        rs = {m['name'] for m in c['methods']}
        for m in c['methods']:
            rs |= calls(m['text'])
        use = [{a for a, _ in c['attrs'] if re.search(r'\b%s\b' % a, m['text'].split('{', 1)[1])} for m in c['methods']]
        P = Q = 0
        for x in range(len(use)):
            for y in range(x + 1, len(use)):
                if use[x] & use[y]: Q += 1
                else: P += 1
        loc = len(code_lines(c['text']))
        h = halstead(c['text'])
        G = max(m['vg'] for m in c['methods'])
        mi = max(0, (171 - 5.2 * math.log(h['V']) - 0.23 * G - 16.2 * math.log(loc)) * 100 / 171)
        res.append(dict(name=c['name'], loc=loc, methods=len(c['methods']), attrs=len(c['attrs']), cond=cond,
                        wmc=wmc, vgmax=G, dit=1, noc=0, cbo=len(coupled), rfc=len(rs), lcom=max(0, P - Q),
                        P=P, Q=Q, halstead=h, mi=mi, details={m['name']: m['vg'] for m in c['methods']},
                        hidden_m=sum(m['vis'] == 'private' for m in c['methods']),
                        hidden_a=sum(v == 'private' for _, v in c['attrs']), raw=c))
    return res

def mood(res):
    tm = sum(r['methods'] for r in res); ta = sum(r['attrs'] for r in res); tc = len(res)
    pairs = sum(r['cbo'] for r in res) / 2 if False else sum(
        1 for r in res for o in res if o is not r and re.search(r'\b%s\b' % o['name'], r['raw']['text']))
    return dict(MHF=sum(r['hidden_m'] for r in res) / tm, AHF=sum(r['hidden_a'] for r in res) / ta if ta else None,
                MIF=0.0, AIF=0.0, PF=None, CF=(pairs / (tc * tc - tc)) if tc > 1 else None, couples=pairs, TC=tc)

def show(title, folder):
    res = analyse(folder)
    print('=' * 70, '\n', title, '\n' + '=' * 70)
    for r in res:
        h = r['halstead']
        print(f"{r['name']:<16} LOC={r['loc']:<3} méthodes={r['methods']} attr={r['attrs']} conditions={r['cond']} "
              f"WMC={r['wmc']} V(G)max={r['vgmax']} DIT={r['dit']} NOC={r['noc']} CBO={r['cbo']} RFC={r['rfc']} "
              f"LCOM={r['lcom']} (P={r['P']},Q={r['Q']})")
        print(f"{'':<16} V(G) par méthode={r['details']}")
        print(f"{'':<16} Halstead n1={h['n1']} n2={h['n2']} N1={h['N1']} N2={h['N2']} N={h['N']} n={h['n']} "
              f"V={h['V']:.1f} D={h['D']:.1f} E={h['E']:.0f}  MI={r['mi']:.1f}")
    print('MOOD', {k: (round(v, 3) if isinstance(v, float) else v) for k, v in mood(res).items()})
    return res

def external():
    print('=' * 70, '\n Données externes / usage (fictives)\n' + '=' * 70)
    inc = list(csv.DictReader(open(os.path.join(ROOT, 'data/incidents.csv'), encoding='utf-8')))
    f = '%Y-%m-%d %H:%M'
    down = sum((datetime.strptime(i['end'], f) - datetime.strptime(i['start'], f)).total_seconds() / 3600 for i in inc)
    period = 30 * 24
    n = len(inc); mttf = (period - down) / n; mttr = down / n; mtbf = mttf + mttr
    print(f'Période={period} h  pannes={n}  indisponibilité={down:.2f} h  MTTF={mttf:.2f} h  MTTR={mttr:.2f} h  '
          f'MTBF={mtbf:.2f} h  disponibilité={100 * mttf / (mttf + mttr):.2f} %')
    perf = sorted(int(r['response_ms']) for r in csv.DictReader(open(os.path.join(ROOT, 'data/perf.csv'))))
    p95 = perf[math.ceil(0.95 * len(perf)) - 1]
    print(f'Temps de réponse : moyenne={sum(perf) / len(perf):.0f} ms  médiane={(perf[9] + perf[10]) / 2:.0f} ms  p95={p95} ms  max={perf[-1]} ms')
    ux = list(csv.DictReader(open(os.path.join(ROOT, 'data/ux.csv'), encoding='utf-8')))
    g = lambda ind: next(r for r in ux if r['indicator'] == ind)['value']
    scores = [int(x) for r in ux if r['dimension'] == 'esthétique' for x in r['value'].split(';')]
    print(f"Esthétique moyenne={sum(scores) / len(scores):.2f}/5  contenu manquant={int(g('éléments attendus sur la page de paiement')) - int(g('éléments présents'))}/"
          f"{g('éléments attendus sur la page de paiement')}  liens cassés={g('liens cassés')}/{g('liens testés')} ({100 * int(g('liens cassés')) / int(g('liens testés')):.1f} %)  "
          f"abandon={100 * (1 - int(g('paiements finalisés')) / int(g('sessions arrivées sur la page de paiement'))):.0f} %")
    rel = list(csv.DictReader(open(os.path.join(ROOT, 'data/releases.csv'), encoding='utf-8')))
    for r in rel[1:]:
        Mt, Fa, Fc, Fd = (int(r[k]) for k in ('modules_total_Mt', 'modules_added_Fa', 'modules_changed_Fc', 'modules_deleted_Fd'))
        print(f"SMI {r['version']} = ({Mt} - ({Fa}+{Fc}+{Fd})) / {Mt} = {(Mt - (Fa + Fc + Fd)) / Mt:.2f}")
    d = list(csv.DictReader(open(os.path.join(ROOT, 'data/defects.csv'), encoding='utf-8')))
    prod = sum(r['detected_in'] == 'production' for r in d)
    return prod

if __name__ == '__main__':
    legacy = show('v1.2 (legacy, code fourni)', os.path.join(ROOT, 'src/main/java/payflow'))
    cible = show('Conception cible (refactorée)', os.path.join(ROOT, 'refactored/src/main/java/payflow'))
    t = open(os.path.join(ROOT, 'src/test/java/payflow/PaymentServiceTest.java'), encoding='utf-8').read()
    ht = halstead(t)
    print('Tests : LOC=%d  Halstead N=%d n=%d V=%.1f  méthodes de test=%d' % (len(code_lines(t)), ht['N'], ht['n'], ht['V'], len(re.findall(r'@Test', t))))
    prod = external()
    loc = legacy[0]['loc']
    print(f'Défauts en production={prod}  densité={prod / (loc / 1000):.0f} défauts/KLOC (LOC={loc})  soit {prod / 45:.2f} défaut/FP (FP=45)')
