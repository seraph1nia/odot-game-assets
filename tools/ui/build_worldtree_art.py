"""Author original modular SVG artwork; reference boards are never runtime inputs.
Explicit authoring only. Preserve manual SVG edits before rerunning this tool.
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'sources/ui/worldtree'
RUNTIME = ROOT / 'ui/preview/UI/art/worldtree'


def svg(body, width=64, height=64):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}">{body}</svg>\n')


def save(name, text):
    for base in (SOURCE, RUNTIME):
        path = base / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)


# Thirty separately authored motifs. No socket/ring baked into any icon.
MOTIFS = {
 'world_seed': 'M30 53C14 46 12 26 30 22C47 18 51 39 35 43C25 46 21 32 31 30C39 29 40 36 34 37 M31 22V12 M31 16Q13 17 15 6Q29 5 31 16 M32 13Q47 2 51 7Q49 19 32 18',
 'shield': 'M12 12L32 5L52 12V30Q49 46 32 57Q15 46 12 30Z M22 17L32 13L42 17V29Q40 38 32 44Q24 38 22 29Z',
 'spark': 'M32 5L39 25L59 32L39 39L32 59L25 39L5 32L25 25Z',
 'leaf': 'M13 50Q3 13 53 7Q58 43 13 50Z M10 55L43 19 M22 40L20 25 M31 31L45 31',
 'flame': 'M31 5Q47 20 39 29Q47 25 48 18Q66 48 37 57Q10 62 10 40Q10 26 21 18Q16 37 27 36Q35 25 31 5Z M31 52Q19 46 30 34Q28 45 37 41Q42 52 31 52Z',
 'crossed_swords': 'M10 5L20 9L48 44L43 49L12 17Z M54 5L44 9L16 44L21 49L52 17Z M34 45L49 33 M15 33L30 45 M46 48L55 57 M18 48L9 57',
 'heart': 'M32 55C19 45 6 32 7 21C8 5 25 6 32 19C39 6 56 5 57 21C58 32 45 45 32 55Z M15 21Q16 15 22 16',
 'book': 'M7 12Q21 8 32 16Q43 8 57 12V51Q43 46 32 54Q21 46 7 51Z M32 16V54 M14 21L25 23 M14 30L25 32 M40 23L50 21 M40 32L50 30',
 'spiral': 'M20 55C-1 41 8 5 33 7C58 8 61 44 38 47C20 50 13 25 30 21C43 18 48 35 36 36C30 37 27 30 33 29',
 'bow': 'M17 7Q61 32 17 57L29 32Z M7 32H57 M48 24L57 32L48 40',
 'paw': 'M15 49Q13 39 24 33Q32 25 40 33Q51 39 49 49Q44 56 32 51Q20 56 15 49Z M10 20C1 21 7 35 13 31C18 28 16 19 10 20Z M24 8C16 8 17 24 24 24C32 24 31 8 24 8Z M42 8C34 8 34 24 41 24C49 24 50 8 42 8Z M55 20C49 18 45 29 51 32C58 35 63 22 55 20Z',
 'crystal': 'M32 4L51 24L46 46L32 59L13 42L12 24Z M32 4L24 26L32 59L40 26Z M12 24L24 26L40 26L51 24 M13 42L27 43 M37 43L46 46',
 'mushroom': 'M8 33Q7 7 32 7Q57 7 56 33Q32 41 8 33Z M26 38L23 55Q32 60 41 55L38 38 M18 25H20 M31 18H34 M43 27H46',
 'crescent_moon': 'M43 5C14 0 0 35 18 53C29 64 48 59 58 46C32 56 16 21 43 5Z M50 17L52 23L58 25L52 27L50 33L48 27L42 25L48 23Z',
 'lantern': 'M24 13V9Q32 0 40 9V13 M13 19L23 13H41L51 19Z M16 22L12 52L20 57H44L52 52L48 22Z M24 23V49 M40 23V49 M31 29Q21 40 32 47Q43 40 31 29Z',
 'water_drop': 'M32 4C29 16 9 29 11 43C14 63 50 63 53 43C55 29 35 16 32 4Z M20 38Q15 49 27 51',
 'tree_roots': 'M29 6L27 30L18 42L6 48 M35 6L37 30L47 42L59 48 M32 29V58 M20 39L20 56 M44 39L44 56 M27 48L15 60 M37 48L49 60',
 'thorn_vine': 'M9 54Q19 36 38 41Q59 43 51 22Q43 4 27 11Q15 18 26 29 M18 43L7 36L12 51 M43 41L51 53L35 45 M51 23L61 19L49 15 M28 10L25 1L39 9',
 'antlers': 'M31 56Q30 35 19 31Q6 25 9 7 M19 31L18 13 M13 23L3 18 M33 56Q34 35 45 31Q58 25 55 7 M45 31L46 13 M51 23L61 18 M24 38L22 23 M40 38L42 23',
 'eye': 'M4 32Q32 2 60 32Q32 62 4 32Z M42 32A10 13 0 1 1 22 32A10 13 0 1 1 42 32Z M32 25V39',
 'acorn': 'M16 29Q12 51 32 59Q52 51 48 29 M10 28Q11 13 31 14Q53 13 54 28Z M32 14L35 5 M18 21L23 27 M28 19L34 27 M39 19L45 27',
 'feather': 'M16 53Q13 18 42 6Q55 6 51 20L45 27L49 25L45 33L36 38L42 37L36 45L25 50Z M8 61L43 15 M22 44L20 31 M29 36L27 21 M34 29L32 17',
 'tower': 'M12 6H22V15H28V6H36V15H42V6H52V24H47L51 56H13L17 24H12Z M28 56V40Q32 34 36 40V56 M27 25H37V32H27Z',
 'rune': 'M32 5L9 49H55Z M32 5V58 M9 49L44 22 M55 49L20 22',
 'snowflake': 'M32 4V60 M8 18L56 46 M8 46L56 18 M24 10L32 18L40 10 M24 54L32 46L40 54 M9 28L20 25L18 14 M46 50L44 39L55 36 M9 36L20 39L18 50 M46 14L44 25L55 28',
 'poison_drop': 'M32 4Q14 24 11 39Q9 58 32 59Q55 58 53 39Q50 24 32 4Z M22 38A4 4 0 1 1 22 46A4 4 0 1 1 22 38 M42 38A4 4 0 1 1 42 46A4 4 0 1 1 42 38 M29 51L32 47L35 51',
 'stone': 'M6 42L15 19L37 9L54 22L59 44L43 55L19 56Z M15 19L28 32L19 56 M28 32L54 22 M28 32L43 55',
 'boot': 'M19 6H42L38 37Q39 44 54 46L57 56H10Q6 45 18 40Z M20 16H40 M19 26H39 M20 36H37 M10 50H53',
 'owl': 'M9 8L23 15Q32 10 41 15L55 8L51 29Q61 54 32 59Q3 54 13 29Z M27 27A7 7 0 1 1 13 27A7 7 0 1 1 27 27 M51 27A7 7 0 1 1 37 27A7 7 0 1 1 51 27 M28 34L32 40L36 34 M18 42L24 49 M46 42L40 49',
 'squirrel': 'M30 54C63 62 67 14 47 8C28 2 24 25 42 29C50 32 50 41 42 42L34 41Q40 25 28 21L22 10L16 22L7 29L17 34Q13 44 19 52L10 56H36 M23 27H24 M21 39L31 37',
}


def point(a, b, t):
    # Same sampled Bezier owns both the wood silhouette and runtime sap route.
    c1 = (a[0] + (b[0] - a[0]) * .30, a[1] - 68)
    c2 = (b[0], b[1] + 70)
    return tuple((1-t)**3*a[i] + 3*(1-t)**2*t*c1[i] + 3*(1-t)*t*t*c2[i] + t**3*b[i] for i in (0, 1))


def main():
    topology = json.loads((SOURCE / 'reference/canonical/worldtree_topology.json').read_text())
    save('topology.json', json.dumps(topology, indent=2) + '\n')
    for name, path in MOTIFS.items():
        save('icons/' + name + '.svg', svg('<defs><linearGradient id="ink" x2=".4" y2="1"><stop stop-color="#fff5cb"/><stop offset="1" stop-color="#cdb581"/></linearGradient></defs>' + f'<path d="{path}" fill="none" stroke="url(#ink)" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'))
    save('socket.svg', svg('<defs><radialGradient id="well"><stop stop-color="#272326"/><stop offset="1" stop-color="#0b1419"/></radialGradient><linearGradient id="bark" x2=".4" y2="1"><stop stop-color="#a48b64"/><stop offset=".4" stop-color="#534435"/><stop offset="1" stop-color="#302d2c"/></linearGradient></defs><path d="M32 3Q48 1 57 16Q66 32 56 49Q43 64 26 60Q5 57 3 36Q0 13 20 6Z" fill="url(#bark)" stroke="#172027" stroke-width="2"/><circle cx="32" cy="32" r="23" fill="url(#well)" stroke="#b19a73" stroke-width="1.4"/><path d="M10 22L6 17M52 20L57 16M17 54L14 59M44 54L48 58" stroke="#d3b38b" stroke-width="1" opacity=".4"/>'))
    save('halo.svg', svg('<defs><radialGradient id="g"><stop stop-color="#ffd98b" stop-opacity="0"/><stop offset=".59" stop-color="#ffd98b" stop-opacity="0"/><stop offset=".68" stop-color="#ffdb7d" stop-opacity=".95"/><stop offset=".74" stop-color="#f8a441" stop-opacity=".3"/><stop offset="1" stop-color="#f8a441" stop-opacity="0"/></radialGradient></defs><circle cx="32" cy="32" r="32" fill="url(#g)"/>'))
    for alive in (False, True):
        body = '<path d="M52 94Q58 60 40 34M52 70Q31 61 25 45M49 80Q74 60 78 34" fill="none" stroke="#6d6741" stroke-width="2"/>'
        leaves = ((41,35,-20),(30,49,-60),(48,59,5),(64,59,60),(75,39,30),(40,70,-50)) if alive else ((41,35,-20),(64,59,60),(40,70,-50))
        for x,y,r in leaves:
            color = '#84916e' if alive else '#514b3a'
            body += f'<g transform="translate({x} {y}) rotate({r})"><path d="M0 10Q-18-7 0-22Q16-6 0 10" fill="{color}" stroke="#272f2a"/><path d="M0 8V-18" stroke="#b3b48c" opacity=".4"/></g>'
        if alive:
            body += '<path d="M76 94L77 79M77 80Q60 80 63 72Q75 57 87 73Q91 80 77 80" fill="#6a96a0" stroke="#263b42" stroke-width="2"/><path d="M69 72L72 71M81 71L83 73" stroke="#d9e5cc" stroke-width="3"/>'
            for x,y in ((26,38),(61,51)):
                body += f'<g transform="translate({x} {y})"><path d="M0 0Q-14-12-4-14Q3-17 0 0Q15-14 14-3Q16 4 0 0Q9 16 0 14Q-9 14 0 0Q-17 7-13-2Q-12-10 0 0" fill="#e6d4ba"/><circle r="3" fill="#e0a45a"/></g>'
        save('foliage_' + ('alive' if alive else 'dead') + '.svg', svg(body,100,110))
    nodes = {n['id']: n for n in topology['nodes']}
    modules = {}
    for edge in topology['edges']:
        a = tuple(nodes[edge['from']]['position'].values()); b = tuple(nodes[edge['to']]['position'].values())
        pts = [tuple(round(v, 2) for v in point(a,b,i/20)) for i in range(21)]
        origin = (min(p[0] for p in pts)-40, min(p[1] for p in pts)-40)
        width = math.ceil(max(p[0] for p in pts)-origin[0]+40); height = math.ceil(max(p[1] for p in pts)-origin[1]+40)
        local = [(p[0]-origin[0],p[1]-origin[1]) for p in pts]
        role = nodes[edge['to']]['role']; radius = {'trunk':22,'primary':17,'secondary':12,'terminal':8}[role]
        left=[]; right=[]
        for i,p in enumerate(local):
            q=local[min(i+1,20)]; prev=local[max(i-1,0)]; dx=q[0]-prev[0]; dy=q[1]-prev[1]; length=math.hypot(dx,dy)
            r=radius*(1-.38*i/20)*(1+.08*math.sin(i*1.8))
            left.append((p[0]-dy/length*r,p[1]+dx/length*r)); right.append((p[0]+dy/length*r,p[1]-dx/length*r))
        polygon=' '.join(f'{x:.2f},{y:.2f}' for x,y in left+right[::-1])
        body='<defs><linearGradient id="wood" x2="1" y2=".6"><stop stop-color="#292d2c"/><stop offset=".35" stop-color="#625243"/><stop offset=".55" stop-color="#8a7156"/><stop offset=".7" stop-color="#463b33"/><stop offset="1" stop-color="#292c2b"/></linearGradient></defs>'
        body+=f'<polygon points="{polygon}" fill="url(#wood)" stroke="#151f24" stroke-width="3"/>'
        for offset in (-.65,-.25,.35,.65):
            d='M'+' L'.join(f'{p[0]+offset*radius:.2f},{p[1]:.2f}' for p in local)
            body+=f'<path d="{d}" fill="none" stroke="{"#b29470" if offset<0 else "#252b2b"}" stroke-width="{1.3 if offset<0 else 2.5}" opacity=".55"/>'
        # Broken, shallow bark notches, subordinate to the branching silhouette.
        for i in range(4,18,4):
            x,y=local[i]; body+=f'<path d="M{x-5:.1f} {y-8:.1f}l7 9 -4 9" fill="none" stroke="#222c2d" stroke-width="2"/>'
        save('branches/'+edge['id']+'.svg',svg(body,width,height))
        modules[edge['id']]={'origin':origin,'size':[width,height],'points':pts,'foliage':pts[15]}
    save('modules.json',json.dumps(modules,separators=(',',':'))+'\n')
    body=''
    for i in range(9):
        end=80+i*55; d=f'M320 22Q{300+(i-4)*20} 85 {end} 143Q{end-10} 154 {end-34} 160'
        body+=f'<path d="{d}" fill="none" stroke="#182429" stroke-width="{27-abs(i-4)*4}" stroke-linecap="round"/><path d="{d}" fill="none" stroke="#584b3d" stroke-width="{20-abs(i-4)*3}" stroke-linecap="round"/><path d="{d}" fill="none" stroke="#967858" stroke-width="2"/>'
    save('roots.svg',svg(body,640,180))
    living = ''
    for i in range(9):
        end=80+i*55; d=f'M320 22Q{300+(i-4)*20} 85 {end} 143Q{end-10} 154 {end-34} 160'
        living += f'<path d="{d}" fill="none" stroke="#f9b95d" stroke-width="3" opacity=".55"/><path d="{d}" fill="none" stroke="#ffe6a0" stroke-width="1" opacity=".6"/>'
    living += '<path d="M240 143Q245 98 220 85M404 148Q420 111 443 97" fill="none" stroke="#68794b" stroke-width="3"/>'
    for x,y,r in ((239,123,-40),(224,94,-30),(254,110,40),(420,128,35),(440,102,45),(405,132,-40)):
        living += f'<g transform="translate({x} {y}) rotate({r})"><path d="M0 10Q-18-7 0-22Q16-6 0 10" fill="#70815d" stroke="#314133"/><path d="M0 8V-18" stroke="#a0a780" opacity=".5"/></g>'
    living += '<path d="M175 151V131M164 130Q164 111 177 116Q192 119 191 131Z M463 149V136M453 135Q456 117 468 122Q479 125 479 136Z" fill="#6d97a4" stroke="#263c42" stroke-width="2"/><path d="M170 123H173M182 124H185M460 127H463" stroke="#cfe2d3" stroke-width="3"/>'
    save('roots_alive.svg',svg(living,640,180))
    save('twig.svg', svg('<path d="M37 89Q29 58 40 29L33 8M36 48L18 33L12 13M35 59L55 43L60 27M40 29L54 18" fill="none" stroke="#393d35" stroke-width="5" stroke-linecap="round"/><path d="M37 89Q29 58 40 29L33 8M36 48L18 33L12 13M35 59L55 43L60 27" fill="none" stroke="#85735a" stroke-width="1.3"/>',72,96))
    body = '<defs><radialGradient id="night"><stop stop-color="#263f46"/><stop offset=".65" stop-color="#122b35"/><stop offset="1" stop-color="#08151e"/></radialGradient><linearGradient id="mist" x2="0" y2="1"><stop stop-color="#5f7880" stop-opacity="0"/><stop offset="1" stop-color="#5f7880" stop-opacity=".13"/></linearGradient></defs><path d="M0 0H1600V1080H0Z" fill="url(#night)"/>'
    for i in range(16):
        x = i*111-45
        body += f'<path d="M{x-12} 970Q{x+20} 550 {x-5} 0H{x+14}Q{x+30} 550 {x+35} 970Z" fill="#07151d" opacity=".22"/><path d="M{x+7} 380L{x-80} 210M{x+14} 600L{x+105} 450" fill="none" stroke="#07151d" stroke-width="9" opacity=".22"/>'
    body += '<path d="M0 970Q240 780 470 930Q800 1020 1100 900Q1390 810 1600 980V1080H0Z" fill="#0a1c23"/><path d="M0 580H1600V1080H0Z" fill="url(#mist)"/>'
    for i in range(44):
        x=(i*239)%1600; y=(i*137)%940
        body += f'<circle cx="{x}" cy="{y}" r="{1+i%2}" fill="#739ba0" opacity=".10"/>'
    save('forest.svg',svg(body,1600,1080))
    print('Authored 30 distinct icons, 23 wooden connections, shared separate socket/glow/foliage and root illustration')


if __name__ == '__main__':
    main()
