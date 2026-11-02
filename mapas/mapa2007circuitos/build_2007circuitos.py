"""Presidenciales 2007 por circuito, reutilizando el constructor nacional del proyecto."""
from pathlib import Path
from collections import Counter
from types import SimpleNamespace
import json, sys, pickle, re
import shapely
from shapely.geometry import shape
from shapely.ops import unary_union

TASK = Path(__file__).resolve().parent
PROJECT = TASK.parents[1]
AMBA='--amba' in sys.argv
sys.path.insert(0,str(PROJECT/'comun'))
SOURCE_BUILDER=(PROJECT/'comun/atlas_leg2003_2025.py').read_text(encoding='utf8')
# Las funciones de proyección y SVG son las mismas que en los atlas nacionales existentes.
sys.argv=[sys.argv[0],'2007circuitos']
__file__=str(PROJECT/'comun/atlas_leg2003_2025.py')
exec(compile(SOURCE_BUILDER.split('# ---------------------------------------------------------------- geometria')[0],
             str(PROJECT/'comun/atlas_leg2003_2025.py'),'exec'))
HERE=str(TASK)
data=json.loads((TASK/'datos_preparados.json').read_text(encoding='utf8'))
report=json.loads((TASK/'control_cobertura.json').read_text(encoding='utf8'))
if AMBA:
    all_source=data
    old=json.loads((PROJECT/'mapas/mapaAMBA2025/dataset_amba2025.json').read_text(encoding='utf8'))
    import unicodedata
    def normpart(s):
        return re.sub('[^a-z]','',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower())
    wanted={normpart(t['p']) for t in old['territories']}
    # La tabla de nombres 2007 contiene formas abreviadas de algunos partidos.
    aliases={'matanza':'lamatanza','lasheras':'generallasheras','generalmadariaga':'generaljuanmadariaga',
             'jc paz':'josecpaz','jcpaz':'josecpaz','sanmartin':'generalsanmartin'}
    def in_amba(d,name):
        n=normpart(name);n=aliases.get(n,n)
        return d=='01' or (d=='02' and n in wanted)
    sections={tuple(r['key'][:2]) for r in data['votes'] if in_amba(r['key'][0],r['name'])}
    data=dict(units=[u for u in data['units'] if u['d']=='01' or (u['d']=='02' and
        ((u['d'],str(u['source']['codigo_seccion_fuente']).zfill(3)) in sections))],
        votes=[r for r in data['votes'] if tuple(r['key'][:2]) in sections])
    TASK=PROJECT/'mapas/mapaAMBA2007';TASK.mkdir(exist_ok=True);HERE=str(TASK);KEY='amba2007'
    S,X0,Y0=975.0,548.0,140.0;LON0,LAT1=-59.3775,-33.9233
    geom.KX=__import__('math').cos(__import__('math').radians(34.7))
PROVINCES=['Capital Federal','Buenos Aires','Catamarca','Córdoba','Corrientes','Chaco','Chubut','Entre Ríos',
           'Formosa','Jujuy','La Pampa','La Rioja','Mendoza','Misiones','Neuquén','Río Negro','Salta','San Juan',
           'San Luis','Santa Cruz','Santa Fe','Santiago del Estero','Tucumán','Tierra del Fuego']
NAME={'FPV':('Cristina Fernández','Frente para la Victoria','#75aadb','FPV'),
      'CC':('Elisa Carrió','Coalición Cívica','#6fb53e','CC'),
      'UNA':('Roberto Lavagna','Concertación UNA','#e10019','UNA'),
      'FREJULI':('Alberto Rodríguez Saá','Justicia, Unión y Libertad','#66ffcc','JUL'),
      'SOB':('Jorge Sobisch','MPU y aliados','#14306e','MPU'),
      'PSA':('Fernando Solanas','Socialista Auténtico','#dd2c1a','PSA'),
      'REC':('Ricardo López Murphy','Recrear','#35649c','REC'),
      'MST':('Vilma Ripoll','MST','#cc0000','MST'), 'PO':('Néstor Pitrola','Partido Obrero','#f4022e','PO'),
      'FITS':('José Montes','FIT por el Socialismo','#f65058','FITS'),
      'FRAL':('Luis Ammann','Frente Amplio','#ff4500','FRAL'),
      'MIJD':('Raúl Castells','MIJD','#b0c236','MIJD'),
      'PPR':('Gustavo Breide Obeid','PPR','#2b2361','PPR'),
      'MUS':('Juan Ricardo Mussa','Lealtad Popular','#ee82ee','CLP')}
CAND={c:dict(n=n,sub=sub,base=col,logo=logo) for c,(n,sub,col,logo) in NAME.items()}
CAND['OTR']=dict(n='Otros',sub='Resto de candidaturas',base='#999999',logo='···')
BEIGE='#e6dcc3'
NOTE=('Votos locales: planilla aportada «Query resultsee1 (2).xlsx», hoja Sheet1; presidenciales del 28 de octubre de 2007. '
      'La planilla contiene votos positivos, sin padrón, blancos ni nulos; no permite calcular participación por circuito. '
      'Torta y barras nacionales: tabla de Wikipedia, separada de la base local. '
      'Geometría: serie aproximada 2007 de geometria/circuitos_serie; combina capas de otras fechas, algunas con CRS supuesto. '
      'No acredita los límites vigentes en 2007. Beige: polígonos sin dato o áreas sin circuitos cartografiados. '
      f'Correspondencia: {report["mapped_circuits"]} de {report["circuits"]} circuitos de la planilla; '
      f'{report["coverage_pct"]:.2f}% de sus votos positivos. No se imputan los faltantes.')
if AMBA:
    NOTE=('AMBA: Capital Federal y 40 partidos, mismo recorte del atlas AMBA 2025. Votos de las presidenciales de 2007, '
          'planilla aportada, hoja Sheet1. Torta y barras: suma regional de la planilla; no es el resultado nacional. '
          'Cartografía aproximada de geometria/circuitos_serie/por_anio/2007: CABA referencia 2006 y Buenos Aires 2003, '
          'con la incertidumbre de fecha y CRS indicada en las fichas. No se imputan votos. No hay padrón, blancos ni nulos; '
          'no se calcula participación por circuito.')

def rec(P,note=''):
    total=sum(P.values())
    r=dict(lines=[[c,int(v),round(100*v/total,2)] for c,v in sorted(P.items(),key=lambda x:-x[1]) if v>0] if total else [],
           metrics=[['Votos positivos',format(total,',').replace(',','.')]],note=note)
    if total:
        leaders=[c for c,v in P.items() if v==max(P.values())]
        if len(leaders)>1:r.update(fill='#757575',note=note+' Empate en primer lugar: '+', '.join(NAME[c][0] for c in leaders)+'.')
        else:
            win=leaders[0];r.update(w=win,q=round(100*P[win]/total,2))
    else:r.update(fill=BEIGE,note=note+' Sin correspondencia con datos de la planilla.')
    return r

U=[];unit_rec=[]
for u in data['units']:
    p=u['source']; name='Circuito '+u['c']
    if u['name']: name+=' · '+u['name']
    note=(f'Cartografía aproximada: {p["id_fuente"]}, referencia {p["anio_fuente_desde"]}. '+p['nota_fuente'])
    if len(u['keys'])>1:note+=' Se suman subdivisiones de la planilla en el polígono padre: '+', '.join(k[2] for k in u['keys'])+'.'
    U.append(dict(prov=PROVINCES[int(u['d'])-1],name=name,kind='circuito',geom=shape(u['geometry'])))
    unit_rec.append(rec(u['P'],note))
G_raw=[shapely.transform(u['geom'],proj) for u in U]
G=[g.simplify(.025,preserve_topology=True) for g in G_raw]
REF_U=pickle.load(open(PROJECT/'mapas/mapa2007/units_leg2003_2025.pkl','rb'))
REF_G=[shapely.transform(u['geom'],proj) for u in REF_U]
MALV=set()
for i,u in enumerate(REF_U):
    if AMBA:break
    if u['name']=='Islas Malvinas':
        MALV.add(len(U));U.append(u);G_raw.append(REF_G[i]);G.append(REF_G[i])
        unit_rec.append(dict(lines=[],metrics=[],fill='#a9a9a9',note='Sin votación argentina en estas islas.'))
PROVS=sorted({u['prov'] for u in REF_U})
prov_geom={p:unary_union([REF_G[i] for i,u in enumerate(REF_U) if u['prov']==p]) for p in PROVS}
from outline_clean import clean_outline,clean_holes
prov_geom={p:clean_holes(g) for p,g in prov_geom.items()}
country=clean_outline(unary_union(list(prov_geom.values())).simplify(.12))
if AMBA:country=unary_union(G_raw).simplify(.03)
prov_mini={p:g.simplify(1.2) for p,g in prov_geom.items()}
prov_votes={p:Counter() for p in PROVS}
ant=Counter()
for row in data['votes']:
    d,s,c=row['key'];prov_votes[PROVINCES[int(d)-1]].update(row['P'])
    if d=='24' and s=='003':ant.update(row['P'])
ANT_I=len(U)
ant_rec=rec(ant,'Suma de los circuitos de Antártida de la planilla; el recuadro representa el sector, no sus límites de circuito.')
all_rec=unit_rec+[ant_rec]
wins=Counter(r['w'] for r in all_rec if 'w' in r)
WIKI_TOTALS={'FPV':8652293,'CC':4403642,'UNA':3230236,'FREJULI':1459174,'PSA':301543,'REC':273406,
             'SOB':268401,'MST':142528,'PO':116688,'FITS':84694,'FRAL':69787,'MIJD':48878,'PPR':45318,'MUS':10558}
WP=19107140
assert sum(WIKI_TOTALS.values())-WP==6  # La fila de Solanas genera una discrepancia interna de seis votos en Wikipedia.
wiki=dict(art='Elecciones presidenciales de Argentina de 2007',blocs={c:WIKI_TOTALS[c] for c in wins},
          otros=WP-sum(WIKI_TOTALS[c] for c in wins),positivos=WP,blancos=1331011,dif=241175,total=20679327,
          inscriptos=27137536,lab_pos='Votos positivos',lab_bla='Votos en blanco',lab_nul='Votos anulados',extra=[['Diferencia de actas','1']])
wikitop.WIKI[KEY]=wiki
cands,slices,partp,metrics=wikitop.national(KEY)
national=dict(cands=cands,slices=slices,partp=partp,metrics=metrics)
if AMBA:
    regional=Counter()
    for row in data['votes']:regional.update(row['P'])
    total=sum(regional.values())
    cands=sorted([dict(code=c,votes=regional[c],pct=round(100*regional[c]/total,2)) for c in wins],key=lambda c:-c['votes'])
    slices=[dict(code=c['code'],v=c['votes']) for c in cands]+[dict(fill='#717274',v=total-sum(c['votes'] for c in cands))]
    national=dict(cands=cands,slices=slices,partp=None,metrics=[['Votos positivos del AMBA',format(total,',').replace(',','.')],
        ['Circuitos en la planilla',str(len(data['votes']))],['Participación','Sin padrón en la planilla']])
    all_rec=unit_rec
prov_rec={p:rec(P,'Suma provincial de los votos de la planilla, incluidos los circuitos sin polígono.') for p,P in prov_votes.items()}
MODES=[dict(id='gan',tile='GANÓ',note=NOTE,units=all_rec,prov=prov_rec,national=national,legend=dict(keys=[[BEIGE,'Sin dato o cartografía de circuito'],['#757575','Empate en primer lugar']]))]
def mix(h,t):
    return '#'+''.join(f'{round(255+(int(h[i:i+2],16)-255)*t):02x}' for i in (1,3,5))
for code in ['FPV','CC','UNA','FREJULI','SOB']:
    edges=[0,20,30,40,50,60,70];colors=[mix(NAME[code][2],.12+.88*i/6) for i in range(7)]
    def chor(r):
        o={k:v for k,v in r.items() if k not in ('w','q','fill')}
        total=sum(x[1] for x in r['lines']); val=next((x[2] for x in r['lines'] if x[0]==code),0)
        o['fill']=colors[max(i for i,e in enumerate(edges) if val>=e)] if total else BEIGE
        return o
    MODES.append(dict(id=code.lower(),tile=NAME[code][3],note=NOTE,units=[chor(r) for r in all_rec],
                      prov={p:chor(r) for p,r in prov_rec.items()},national=national,
                      legend=dict(title='% '+NAME[code][0],stops=[[col,str(e)+'%'] for col,e in zip(colors,edges)],bars=False)))
D=SimpleNamespace(CAND=CAND,MODES=MODES,disp={i:u['name'] for i,u in enumerate(U)},ANT_I=ANT_I,report={})
disp=D.disp
# Reutilizar composición, mini provincial, siete recuadros y parches de la plantilla.
tail=SOURCE_BUILDER.split('# ---------------------------------------------------------------- SVG',1)[1]
tail=tail.replace('body = []','body = [\'<path class="circuitbg" fill="#e6dcc3" d="%s"/>\' % geom_d(country)]',1)
tail=tail.replace('X99 = insets99.build(U, G_raw, window, bbox_of, style95=True)',
                  'X99 = insets99.build(REF_U, REF_G, window, lambda idx: shapely.total_bounds([REF_G[i] for i in idx]), style95=True)')
tail=tail.replace('title="Elecciones primarias de Argentina de" if PASO else "Elecciones legislativas de Argentina de",',
                  'title="Elecciones presidenciales de",')
tail=tail.replace('"Diputados nacionales")','"Por circuito · aproximado")')
tail=tail.replace('f"<title>Elecciones legislativas {YEAR}</title>"','f"<title>Presidenciales {YEAR} por circuito</title>"')
tail=tail.replace('data-i="%d"\' % ANT_I','data-i="%d"\' % ANT_I')
if AMBA:
    start=tail.index('tuc = ');end=tail.index('ds = dict(')
    tail=tail[:start]+'''INSETS = [
    dict(id="caba",label="Capital Federal",f=[70,600,440,350],win=window(bbox_of(cap_idx),440/350,.04),show=["dc"],sd=2.2,fit="meet"),
    dict(id="core",label="Conurbano y Capital",f=[1450,140,430,420],win=window([*ll(-58.68,-34.46),*ll(-58.32,-34.82)],430/420,.0),show=["d","pb"],sd=1.5,sp=2.4),
    dict(id="lp",label="Gran La Plata",f=[1495,640,385,300],win=window([*ll(-58.02,-34.85),*ll(-57.89,-34.96)],385/300,.0),show=["d","pb"],sd=1.8,sp=2.6)]
pv=[]; KPV=.2669;pv_tx=pv_ty=0
''' +tail[end:]
    tail=tail.replace('"Elecciones presidenciales de Argentina de"','"Elecciones presidenciales de"')
    tail=tail.replace('"Por circuito · aproximado"','"AMBA · Por circuito · 2007"')
    tail=tail.replace('for i, u in enumerate(U)]+[dict(p="Tierra del Fuego",n="Antártida Argentina",k="departamento")]', 'for i, u in enumerate(U)]')
    tail=tail.replace('M570 100h840v1540h-840z','M540 100h1380v1540h-1380z')
    tail=tail.replace('M540 100h1380v1540h-1380z M570 300','M570 100h840v1540h-840z M570 300',1)
    tail=tail.replace('const R=[570,100,1410,1640]','const R=[540,100,1920,1640]')
    tail=tail.replace('"Anillo exterior: Participación"','""')
    tail=tail.replace('provinces="Provincias"','provinces=""')
    # Límites de partidos a partir de sus circuitos; Capital conserva su perímetro.
    municipal={}
    for i,u in enumerate(data['units']):
        p='Capital Federal' if u['d']=='01' else u['name']
        municipal.setdefault(p,[]).append(G_raw[i])
    extra=''.join('<path class="pb" d="%s"/>' % line_d(unary_union(gs).boundary) for p,gs in municipal.items() if p)
    tail=tail.replace('pv=[]; KPV=',f'body.append({extra!r})\npv=[]; KPV=')
tail=tail.replace('tpl = tpl.replace("{{MAIN_S}}", "1")',
                  'tpl = tpl.replace("</style>", ".circuitbg{display:var(--v-d,none);stroke:none;pointer-events:none}</style>",1)\n'
                  'tpl = tpl.replace("{{MAIN_S}}", "1")')
exec(compile(tail,str(PROJECT/'comun/atlas_leg2003_2025.py'),'exec'))
(TASK/'wiki_nacional_2007circuitos.json').write_text(json.dumps(wiki,ensure_ascii=False,indent=2),encoding='utf8')
(TASK/'control_resultados.json').write_text(json.dumps(dict(wins=dict(wins),
    comparison=[dict(code=c,base=report['totals'].get(c,0),wikipedia=v,difference=report['totals'].get(c,0)-v) for c,v in WIKI_TOTALS.items()]),ensure_ascii=False,indent=2),encoding='utf8')
print('Ganadores:',dict(wins))
