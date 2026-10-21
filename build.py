"""Builds the static ePortfolio site.

The narratives and self-assessment live as Markdown in content/ (copied from
the TrakCode repo's capstone/narratives). This script renders them, plus the
hand-written pages below, into plain HTML files at the repo root, which is
what GitHub Pages serves. No dependencies beyond the Python standard library.

    python build.py
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).parent
REPO = 'https://github.com/CountryCoder44/trakcode-cs499'
TREE = REPO + '/tree/main/'
BLOB = REPO + '/blob/main/'
SITE = 'https://countrycoder44.github.io/'
GITHUB = 'https://github.com/CountryCoder44'
LINKEDIN = 'https://www.linkedin.com/in/rycartwrightfromjersey'


# ---------------------------------------------------------------- markdown --

INLINE = re.compile(r'(\*\*[^*]+\*\*|`[^`]+`|\[[^\]]+\]\([^)]+\))')


def inline(text):
    out = []
    for part in INLINE.split(text):
        if not part:
            continue
        if part.startswith('**') and part.endswith('**'):
            out.append('<strong>' + inline(part[2:-2]) + '</strong>')
        elif part.startswith('`') and part.endswith('`'):
            out.append('<code>' + html.escape(part[1:-1]) + '</code>')
        elif part.startswith('['):
            m = re.match(r'\[([^\]]+)\]\(([^)]+)\)', part)
            out.append('<a href="%s">%s</a>' % (html.escape(m.group(2)), html.escape(m.group(1))))
        else:
            out.append(html.escape(part))
    return ''.join(out)


def render_markdown(md, shift=0, skip_title=True):
    """A small Markdown subset: #-### headings, paragraphs, - and 1. lists,
    **bold**, `code`, [links]. `shift` demotes headings (## -> h3 when 1)."""
    lines = md.replace('\r\n', '\n').split('\n')
    if skip_title:
        # Drop the document title and the byline under it; pages have their own header.
        while lines and not lines[0].startswith('# '):
            lines.pop(0)
        if lines:
            lines.pop(0)
        while lines and (not lines[0].strip() or '·' in lines[0]):
            lines.pop(0)
    out, para, list_kind = [], [], None

    def flush_para():
        if para:
            out.append('<p>' + inline(' '.join(para)) + '</p>')
            para.clear()

    def close_list():
        nonlocal list_kind
        if list_kind:
            out.append('</%s>' % list_kind)
            list_kind = None

    for raw in lines:
        s = raw.strip()
        if not s:
            flush_para(); close_list(); continue
        m = re.match(r'^(#{1,3}) (.*)$', s)
        if m:
            flush_para(); close_list()
            level = min(len(m.group(1)) + shift, 4)
            out.append('<h%d>%s</h%d>' % (level, inline(m.group(2)), level))
            continue
        m = re.match(r'^(?:- |(\d+)\. )(.*)$', s)
        if m:
            flush_para()
            kind = 'ol' if m.group(1) else 'ul'
            if list_kind != kind:
                close_list(); out.append('<%s>' % kind); list_kind = kind
            out.append('<li>' + inline(m.group(2)) + '</li>')
            continue
        close_list()
        para.append(s)
    flush_para(); close_list()
    return '\n'.join(out)


def content(name):
    return (ROOT / 'content' / name).read_text(encoding='utf-8')


# ------------------------------------------------------------------ layout --

NAV = [('index.html', 'Home'), ('about.html', 'About'), ('projects.html', 'Projects')]


def page(filename, title, description, body, section):
    nav = '\n'.join(
        '<li><a href="%s"%s>%s</a></li>' % (href, ' aria-current="page"' if label == section else '', label)
        for href, label in NAV
    )
    full_title = title if title.startswith('Ryan Cartwright') else title + ' | Ryan Cartwright'
    doc = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(full_title)}</title>
<meta name="description" content="{html.escape(description)}">
<meta property="og:title" content="{html.escape(full_title)}">
<meta property="og:description" content="{html.escape(description)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{SITE}{filename.replace("index.html", "")}">
<meta property="og:image" content="{SITE}assets/img/trakcode.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="{SITE}{filename.replace("index.html", "")}">
<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="assets/css/site.css">
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
  <nav class="container nav" aria-label="Main">
    <a class="brand" href="index.html"><span class="brand-mark" aria-hidden="true">RC</span><span class="brand-name">Ryan Cartwright</span></a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="nav-links">Menu</button>
    <ul class="nav-links" id="nav-links">
{nav}
    </ul>
  </nav>
</header>
<main id="main">
{body}
</main>
<footer class="site-footer">
  <div class="container">
    <span>&copy; 2026 Ryan Cartwright. CS 499 Computer Science Capstone, Southern New Hampshire University.</span>
    <span><a href="{GITHUB}">GitHub</a> &middot; <a href="{LINKEDIN}">LinkedIn</a> &middot; <a href="{REPO}">Capstone source</a></span>
  </div>
</footer>
<script src="assets/js/site.js"></script>
</body>
</html>
'''
    (ROOT / filename).write_text(doc, encoding='utf-8', newline='\n')
    print('wrote', filename)


def file_link(path, label=None):
    if path is None:
        return '<span class="none">None (added in this enhancement)</span>'
    url = (TREE if path.endswith('/') else BLOB) + path.rstrip('/')
    name = path.rstrip('/').rsplit('/', 1)[-1] + ('/' if path.endswith('/') else '')
    return '<a href="%s" title="%s">%s</a>' % (url, html.escape(path), html.escape(label or name))


# -------------------------------------------------------------- enhancements --

ENHANCEMENTS = [
    {
        'n': 1, 'slug': 'enhancement-1', 'md': 'enhancement-1-software-design.md',
        'docx': 'enhancement-1-software-design.docx', 'folder': 'capstone/enhancement-1-software-design/',
        'word': 'One', 'title': 'Software Design and Engineering', 'milestone': 'Milestone Two',
        'summary': ('I restructured the backend layer every TrakCode feature runs through: I split a '
                    '660-line AI tutor service into independently testable modules, replaced ten copies '
                    'of guesswork error handling with a typed error hierarchy, and added the project\'s '
                    'first automated tests and continuous integration. Along the way I fixed a safety '
                    'check that failed open instead of closed.'),
        'card': 'A testable tutor service, typed errors, the first test suite and CI, and a guardrail that fails closed.',
        'highlights': [
            ('55 tests', 'written where none existed, now run on every push and pull request'),
            ('~150 lines', 'of duplicated error handling removed from ten controllers'),
            ('Fail closed', 'an AI safety check that silently switched off on an outage now defaults to safe'),
        ],
        'before_label': 'Original artifact',
        'files': [
            ('AI tutor service', 'capstone/original/server/src/services/tutor.service.ts',
             'capstone/enhancement-1-software-design/server/src/services/tutor/'),
            ('Error handling', 'capstone/original/server/src/controllers/',
             'capstone/enhancement-1-software-design/server/src/middleware/errorHandler.ts'),
            ('Typed errors', None, 'capstone/enhancement-1-software-design/server/src/errors/AppError.ts'),
            ('Continuous integration', None, 'capstone/enhancement-1-software-design/.github/workflows/ci.yml'),
            ('API documentation', None, 'capstone/enhancement-1-software-design/server/openapi.yaml'),
        ],
    },
    {
        'n': 2, 'slug': 'enhancement-2', 'md': 'enhancement-2-algorithms.md',
        'docx': 'enhancement-2-algorithms.docx', 'folder': 'capstone/enhancement-2-algorithms/',
        'word': 'Two', 'title': 'Algorithms and Data Structures', 'milestone': 'Milestone Three',
        'summary': ('I improved the parts of TrakCode that make decisions. Problem selection is now fair '
                    'and backed by compound indexes, a repeated lesson walk is cached so it runs once per '
                    'request, and the hint system is a language-aware rule table instead of a Python-only '
                    'chain of checks. Each change is supported by complexity analysis and measured results.'),
        'card': 'Fair, indexed problem selection, a cached lesson walk, and a language-aware hint rule table.',
        'highlights': [
            ('O(log n + k)', 'indexed problem lookup, down from an in-memory sort of every match'),
            ('172 ms to 0.6 ms', 'for 10,000 lesson walks once the result is cached'),
            ('51 tests', 'added, which found a bug hiding hints for two of three languages'),
        ],
        'before_label': 'Milestone Two snapshot',
        'files': [
            ('Problem selection', 'capstone/enhancement-1-software-design/server/src/services/problemBank.service.ts',
             'capstone/enhancement-2-algorithms/server/src/services/problemBank.service.ts'),
            ('Selection indexes', None, 'capstone/enhancement-2-algorithms/server/src/models/Problem.ts'),
            ('Lesson walk cache', 'capstone/enhancement-1-software-design/server/src/models/SeqTopic.ts',
             'capstone/enhancement-2-algorithms/server/src/models/SeqTopic.ts'),
            ('Hint rules', 'capstone/enhancement-1-software-design/server/src/services/seqGrader.ts',
             'capstone/enhancement-2-algorithms/server/src/services/nearMissHint.ts'),
        ],
    },
    {
        'n': 3, 'slug': 'enhancement-3', 'md': 'enhancement-3-databases.md',
        'docx': 'enhancement-3-databases.docx', 'folder': 'capstone/enhancement-3-databases/',
        'word': 'Three', 'title': 'Databases', 'milestone': 'Milestone Four',
        'summary': ('I improved how TrakCode stores, validates, and retrieves learner data in MongoDB. Nine '
                    'duplicated progress queries now go through one data access layer, a referential '
                    'integrity check finds records stranded by content changes, and the "already seen" '
                    'check for practice problems now runs inside the database, verified with the query planner.'),
        'card': 'One data access layer, a referential integrity check, and an "already seen" check moved into the database.',
        'highlights': [
            ('9 to 1', 'duplicated progress queries consolidated into one repository layer'),
            ('36 orphans', 'found in real development data by the new integrity check'),
            ('0 scans', 'collection scans in the new lookup, confirmed by the query planner'),
        ],
        'before_label': 'Milestone Three snapshot',
        'files': [
            ('Progress data access', 'capstone/enhancement-2-algorithms/server/src/controllers/seq.controller.ts',
             'capstone/enhancement-3-databases/server/src/repositories/seqProgress.repository.ts'),
            ('Integrity check', None, 'capstone/enhancement-3-databases/server/src/services/seqProgressIntegrity.service.ts'),
            ('Integrity command', None, 'capstone/enhancement-3-databases/server/src/scripts/checkSeqProgressIntegrity.ts'),
            ('"Already seen" check', 'capstone/enhancement-2-algorithms/server/src/services/problemBank.service.ts',
             'capstone/enhancement-3-databases/server/src/services/problemBank.service.ts'),
        ],
    },
]


def enhancement_page(e):
    rows = '\n'.join(
        f'<tr><th scope="row">{html.escape(label)}</th><td>{file_link(before)}</td><td>{file_link(after)}</td></tr>'
        for label, before, after in e['files']
    )
    highlights = '\n'.join(f'<li><strong>{html.escape(a)}</strong>{html.escape(b)}</li>' for a, b in e['highlights'])
    prev_e = ENHANCEMENTS[e['n'] - 2] if e['n'] > 1 else None
    next_e = ENHANCEMENTS[e['n']] if e['n'] < len(ENHANCEMENTS) else None
    prev_link = (f'<a href="{prev_e["slug"]}.html"><span>Previous</span>Enhancement {prev_e["word"]}: {prev_e["title"]}</a>'
                 if prev_e else '<a href="trakcode.html"><span>Back to</span>TrakCode capstone overview</a>')
    next_link = (f'<a class="next" href="{next_e["slug"]}.html"><span>Next</span>Enhancement {next_e["word"]}: {next_e["title"]}</a>'
                 if next_e else '<a class="next" href="trakcode.html"><span>Back to</span>TrakCode capstone overview</a>')
    body = f'''
<section class="section">
  <div class="container">
    <p class="crumbs"><a href="projects.html">Projects</a> / <a href="trakcode.html">TrakCode capstone</a> / Enhancement {e["word"]}</p>
    <span class="eyebrow">Enhancement {e["word"]} &middot; {e["milestone"]}</span>
    <h1>{e["title"]}</h1>
    <p class="lede">{html.escape(e["summary"])}</p>
    <div class="btn-row" style="margin:24px 0 36px">
      <a class="btn" href="{TREE + e["folder"].rstrip("/")}">Enhanced code</a>
      <a class="btn btn-outline" href="{TREE}capstone/original">Original code</a>
      <a class="btn btn-outline" href="downloads/{e["docx"]}" download>Narrative (.docx)</a>
    </div>
    <ul class="highlights">
{highlights}
    </ul>
  </div>
</section>
<section class="section section-alt">
  <div class="container">
    <div class="section-head">
      <h2>Before and after</h2>
      <p>The key files for this enhancement. "Before" is the {html.escape(e["before_label"])}, the code as it stood when this enhancement began.</p>
    </div>
    <div class="table-wrap">
      <table>
        <thead><tr><th scope="col">Area</th><th scope="col">Before</th><th scope="col">After</th></tr></thead>
        <tbody>
{rows}
        </tbody>
      </table>
    </div>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="section-head"><h2>Narrative</h2></div>
    <article class="prose">
{render_markdown(content(e["md"]), shift=1)}
    </article>
    <nav class="pager" aria-label="Enhancements">{prev_link}{next_link}</nav>
  </div>
</section>'''
    page(e['slug'] + '.html', f'Enhancement {e["word"]}: {e["title"]}',
         f'CS 499 Enhancement {e["word"]} ({e["title"]}) for TrakCode: the narrative, key changes, and code.', body, 'Projects')


# ------------------------------------------------------------------- pages --

SKILLS = [('TypeScript', 'typescript'), ('JavaScript', 'javascript'), ('React', 'react'), ('Node.js', 'nodejs'),
          ('Python', 'python'), ('Java', 'java'), ('C++', 'cpp'), ('MongoDB', 'mongodb'),
          ('PostgreSQL', 'postgresql'), ('AWS', 'aws'), ('Linux', 'linux'), ('GitHub', 'github')]


def home():
    glance = '\n'.join([
        '<li><a href="#self-assessment"><b>Professional self-assessment</b><span>Start here</span></a></li>',
    ] + [f'<li><a href="{e["slug"]}.html"><b>Enhancement {e["word"]}</b><span>{e["title"]}</span></a></li>' for e in ENHANCEMENTS])
    skills = '\n'.join(f'<div class="skill"><img src="assets/img/icons/{f}.png" alt="" width="44" height="44">{n}</div>' for n, f in SKILLS)
    body = f'''
<section class="hero">
  <div class="container hero-grid">
    <div>
      <span class="eyebrow">CS 499 Computer Science Capstone ePortfolio</span>
      <h1>Hi, I&rsquo;m <span class="accent">Ryan Cartwright</span></h1>
      <p class="lede">Full-stack software engineer and founder of Fireback Software LLC. I build complete products, from the first idea to the people using them, and I care most about software that keeps working when nobody is watching it.</p>
      <div class="btn-row">
        <a class="btn" href="trakcode.html">Explore the capstone</a>
        <a class="btn btn-outline" href="about.html">About me</a>
      </div>
    </div>
    <aside class="card glance" aria-labelledby="glance-title">
      <h2 id="glance-title">This ePortfolio at a glance</h2>
      <ol>
{glance}
      </ol>
    </aside>
  </div>
</section>
<section class="section section-alt" id="self-assessment">
  <div class="container">
    <span class="eyebrow">Start here</span>
    <h2>Professional Self-Assessment</h2>
    <div class="doc-meta">
      <span>An introduction to my skills and to the capstone work that follows.</span>
      <a href="downloads/professional-self-assessment.docx" download>Download as Word (.docx)</a>
    </div>
    <article class="prose">
{render_markdown(content("professional-self-assessment.md"), shift=1)}
    </article>
    <div class="btn-row" style="margin-top:32px">
      <a class="btn" href="trakcode.html">Continue to the capstone artifacts</a>
    </div>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="section-head">
      <h2>Skills and tools</h2>
      <p>The languages, frameworks, and platforms I use most across client work, coursework, and my own products.</p>
    </div>
    <div class="skills">
{skills}
    </div>
  </div>
</section>'''
    page('index.html', 'Ryan Cartwright | CS 499 ePortfolio',
         'The CS 499 Computer Science Capstone ePortfolio of Ryan Cartwright, full-stack software engineer: '
         'professional self-assessment and three enhancements to TrakCode.', body, 'Home')


TIMELINE = [
    ('2019', 'Electrical engineering studies', 'Began studying electrical engineering at a community college.'),
    ('2020 to 2024', 'Agricultural Automation Engineer, Microgreens & Micromachines',
     'Self-taught. Automated an aeroponic growing operation with Arduino controllers in C++ and built the web app that monitored it.'),
    ('February 2024 to present', 'Founder and Principal Software Engineer, Fireback Software LLC',
     'Full-stack and AI-powered applications for clients, built with distributed developers and QA teams.'),
    ('September 2024', 'Back to school for computer science', 'Studied computer science at Middlesex County College.'),
    ('2025 to 2026', 'B.S. Computer Science, Southern New Hampshire University', 'All coursework completed. Degree conferral expected October 2026.'),
    ('September 2025 to May 2026', 'Full-Stack Software Engineering Bootcamp, Metana', 'Completed alongside my degree.'),
    ('December 2026', 'M.S. Artificial Intelligence, Southern New Hampshire University', 'Beginning my graduate studies.'),
]

VALUES = [
    ('Verify, don\'t assume', 'A change is not done until I can show it works: tests, measurements, and real data, not a feeling that it should be fine.'),
    ('Design for failure', 'My first automation job meant a failure could cost a whole crop. I still ask how a system will fail and what that does to the people using it.'),
    ('Talk at the right level', 'Leadership wants the outcome and the risk; a teammate needs the mechanism. I try to give each the version they need.'),
]


def about():
    timeline = '\n'.join(f'<li><span class="when">{html.escape(w)}</span><h3>{html.escape(t)}</h3><p>{html.escape(d)}</p></li>' for w, t, d in TIMELINE)
    values = '\n'.join(f'<div class="card"><h3>{html.escape(t)}</h3><p style="margin:0;color:var(--text-dim)">{html.escape(d)}</p></div>' for t, d in VALUES)
    body = f'''
<section class="section">
  <div class="container about-grid">
    <img class="portrait" src="assets/img/portrait.jpg" alt="Portrait of Ryan Cartwright" width="576" height="720">
    <div>
      <span class="eyebrow">About me</span>
      <h1>Ryan Cartwright</h1>
      <p class="lede">Full-stack software engineer, AI product engineer, and founder of Fireback Software LLC.</p>
      <p>I like owning a product from the first idea to the people using it. I founded Fireback Software LLC in February 2024, where I build full-stack web applications, AI-powered features, and cloud infrastructure for clients, usually alongside distributed developers and QA teams.</p>
      <p>I didn&rsquo;t start out in a computer science classroom. I taught myself embedded programming and web development at an agricultural company, where I automated an aeroponic growing operation and built the web app that monitored it. That hands-on start is why I care so much about software that keeps working when nobody is watching.</p>
      <p>I&rsquo;ve completed my Bachelor of Science in Computer Science at Southern New Hampshire University (conferral expected October 2026), and I begin a Master of Science in Artificial Intelligence in December 2026. Outside of client work I&rsquo;m building TrakCode, an AI-native coding education platform, and ChromiTap, a digital art and color management application.</p>
      <div class="social" style="margin-top:24px">
        <a href="{GITHUB}"><img src="assets/img/icons/github.png" alt="" width="20" height="20">GitHub</a>
        <a href="{LINKEDIN}"><img src="assets/img/icons/linkedin.png" alt="" width="20" height="20">LinkedIn</a>
      </div>
    </div>
  </div>
</section>
<section class="section section-alt">
  <div class="container">
    <div class="section-head"><h2>My path</h2></div>
    <ol class="timeline">
{timeline}
    </ol>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="section-head"><h2>How I work</h2></div>
    <div class="grid-3">
{values}
    </div>
  </div>
</section>'''
    page('about.html', 'About', 'About Ryan Cartwright: background, path into computer science, and how I work.', body, 'About')


def project_card(img, alt, title, tags, text, links, note=None, icons=None):
    """`icons` (skill icon names) stands in for `img` on projects with no screenshot."""
    tag_html = ''.join(f'<li>{html.escape(t)}</li>' for t in tags)
    link_html = ''.join(links)
    note_html = f'<p class="note">{html.escape(note)}</p>' if note else ''
    if icons:
        media = '<div class="project-media project-icons">' + ''.join(
            f'<img src="assets/img/icons/{i}.png" alt="" height="56">' for i in icons) + '</div>'
    else:
        media = f'<div class="project-media"><img src="assets/img/{img}" alt="{html.escape(alt)}" loading="lazy"></div>'
    return f'''<article class="card project">
  {media}
  <div class="project-body">
    <h3>{html.escape(title)}</h3>
    <ul class="tags">{tag_html}</ul>
    <p>{html.escape(text)}</p>
    {note_html}
    {'<div class="btn-row">' + link_html + '</div>' if link_html else ''}
  </div>
</article>'''


def projects():
    cards = '\n'.join([
        project_card('chromitap.png', 'ChromiTap color palette interface', 'ChromiTap',
                     ['Desktop app', 'Color management', 'Animation'],
                     'A long-term personal project that started as a palette tool for grabbing colors from anywhere on the screen. '
                     'It has grown well beyond that original scope into a rasterized digital art application with an advanced color '
                     'management suite, animation, and broader creative and productivity tooling that I use in my own UI and UX design work.',
                     [], 'Source is private. Demos available on request.'),
        project_card('aeroponics.jpg', 'Aeroponic growing system', 'Automated Aeroponics',
                     ['C++', 'Arduino', 'Embedded systems', 'Web app'],
                     'Built while I was self-taught at Microgreens & Micromachines. Arduino controllers in C++ run nutrient delivery, '
                     'misting, and environmental controls from sensor-driven logic, making the operation about 80% automated. '
                     'A web app I built monitors it remotely with real-time telemetry and email and text alerts. '
                     'The system reached roughly six times the crop yield in the same footprint.',
                     []),
        project_card('logistics.jpg', 'Delivery truck on a highway', 'Mobile Reporting App',
                     ['Mobile', 'Workflow automation', 'Client project'],
                     'For a logistics and operations client, I designed and deployed a mobile app that tracks employee locations during '
                     'work hours to fill in Interstate Fuel Tax Agreement (IFTA) reports automatically. It improved reporting accuracy by 27%, '
                     'and together with related workflow automation it removed more than 30 hours of manual work per week.',
                     [], 'Client work. Source is not public.'),
        project_card(None, None, 'API Watchtower',
                     ['TypeScript', 'React', 'Express', 'PostgreSQL', 'Docker'],
                     'A self-hosted dashboard that monitors REST APIs for availability, response time, and contract drift. '
                     'A built-in scheduler checks each endpoint on its own interval, a health-state machine opens and resolves '
                     'incidents automatically, and deterministic JSON-shape fingerprinting shows exactly which fields were added, '
                     'removed, or changed type. Typed end to end, tested, and runs with one Docker Compose command.',
                     [f'<a class="btn btn-outline" href="{GITHUB}/api-watchtower">Source on GitHub</a>'],
                     icons=['typescript', 'react', 'postgresql']),
        project_card(None, None, 'TMDB Explorer',
                     ['TypeScript', 'React', 'Tailwind CSS', 'Vitest'],
                     'A movie discovery app built on The Movie Database API as a take-home assignment. Combinable server-side '
                     'filters for genre, release year, and rating, client-side sorting, an animated grid and list layout, and '
                     'detail views that load cast and runtime on demand, with motion that respects reduced-motion settings.',
                     [f'<a class="btn btn-outline" href="{GITHUB}/tmdb-explorer">Source on GitHub</a>'],
                     icons=['typescript', 'react']),
        project_card(None, None, 'Travlr Getaways',
                     ['MongoDB', 'Express', 'Angular', 'Node.js', 'Coursework'],
                     'A MEAN-stack travel booking application from SNHU CS-465, Full Stack Development: a customer-facing Express '
                     'site, a REST API backed by MongoDB, and an Angular admin app with authenticated login for adding and editing trips. '
                     'Built incrementally, with each module preserved on its own branch.',
                     [f'<a class="btn btn-outline" href="{GITHUB}/cs465-fullstack">Source on GitHub</a>'],
                     icons=['mongodb', 'nodejs', 'javascript']),
    ])
    body = f'''
<section class="section">
  <div class="container">
    <span class="eyebrow">Projects</span>
    <h1>Things I&rsquo;ve built</h1>
    <p class="lede">A mix of my own products and client work. TrakCode is my CS 499 capstone artifact.</p>
  </div>
</section>
<section class="section" style="padding-top:0">
  <div class="container">
    <article class="card featured">
      <div class="project-media"><img src="assets/img/trakcode.jpg" alt="TrakCode, an AI-native coding education platform"></div>
      <div class="project-body">
        <span class="badge">CS 499 capstone artifact</span>
        <h2>TrakCode</h2>
        <ul class="tags"><li>TypeScript</li><li>React</li><li>Node.js</li><li>MongoDB</li><li>AWS</li></ul>
        <p>An AI-native, full-stack coding education platform: structured lessons, practice assignments graded by actually running the learner&rsquo;s code in a sandboxed multi-language execution service, and an AI tutor named Trak. I designed and built it, and it is the artifact for all three of my capstone enhancements.</p>
        <div class="btn-row">
          <a class="btn" href="trakcode.html">View the capstone work</a>
          <a class="btn btn-outline" href="{REPO}">Source on GitHub</a>
        </div>
      </div>
    </article>
  </div>
</section>
<section class="section section-alt">
  <div class="container">
    <div class="section-head"><h2>More projects</h2></div>
    <div class="grid-3">
{cards}
    </div>
  </div>
</section>'''
    page('projects.html', 'Projects', 'Projects by Ryan Cartwright, including TrakCode, his CS 499 capstone artifact.', body, 'Projects')


OUTCOMES = [
    ('1. Collaborative environments',
     'Enhancement One\'s CI gate on every pull request and OpenAPI contract; the repository\'s contributing guide, pull request template, and issue templates; team experience in the self-assessment.'),
    ('2. Professional communication',
     'The three narratives, the API reference and architecture README from Enhancement One, and this ePortfolio.'),
    ('3. Design and evaluate solutions, managing trade-offs',
     'Enhancement Two\'s complexity analysis of selection, caching, and hint rules; Enhancement Three\'s in-database anti-join and integrity check; dependency injection trade-offs in Enhancement One.'),
    ('4. Well-founded techniques, skills, and tools',
     'Enhancement One\'s test suite and CI; benchmarks and query-planner verification in Enhancements Two and Three; a repository layer and atomic updates.'),
    ('5. Security mindset',
     'Enhancement One\'s fail-closed AI guardrail; Enhancement Three\'s race-condition fix and reviewed deletion; sandbox isolation and secret scrubbing described in the self-assessment.'),
]


def trakcode():
    cards = '\n'.join(f'''<a class="card enh-card" href="{e["slug"]}.html">
  <span class="num">Enhancement {e["word"]} &middot; {e["milestone"]}</span>
  <h3>{e["title"]}</h3>
  <p>{html.escape(e["card"])}</p>
  <span class="more">Read the enhancement &rarr;</span>
</a>''' for e in ENHANCEMENTS)
    outcomes = '\n'.join(f'<tr><th scope="row">{html.escape(o)}</th><td style="font-family:inherit">{html.escape(w)}</td></tr>' for o, w in OUTCOMES)
    downloads = '\n'.join([
        '<li><a href="downloads/professional-self-assessment.docx" download>Professional Self-Assessment (.docx)</a></li>',
    ] + [f'<li><a href="downloads/{e["docx"]}" download>Enhancement {e["word"]}: {e["title"]} narrative (.docx)</a></li>' for e in ENHANCEMENTS])
    body = f'''
<section class="section">
  <div class="container">
    <p class="crumbs"><a href="projects.html">Projects</a> / TrakCode capstone</p>
    <span class="eyebrow">CS 499 capstone artifact</span>
    <h1>TrakCode</h1>
    <p class="lede">An AI-native coding education platform I designed and built. Learners work through ordered lessons, solve practice assignments graded by running their code, and can ask an AI tutor named Trak for help.</p>
    <p style="max-width:68ch;color:var(--text-dim)">It has a React and TypeScript front end, a Node.js, Express, and TypeScript API backed by MongoDB, and a separate execution service that compiles and runs learner code in Python, Java, C++, and TypeScript. I used this one real system for all three enhancement categories, so every change had to hold up in software people actually use.</p>
    <div class="btn-row" style="margin-top:24px">
      <a class="btn" href="{REPO}">Source on GitHub</a>
      <a class="btn btn-outline" href="{TREE}capstone/original">Original artifact</a>
      <a href="{REPO}/actions/workflows/ci.yml"><img src="{REPO}/actions/workflows/ci.yml/badge.svg" alt="CI status: typecheck and tests" height="20" style="margin-top:12px"></a>
    </div>
  </div>
</section>
<section class="section section-alt">
  <div class="container">
    <div class="section-head">
      <h2>Original artifact</h2>
      <p>TrakCode exactly as it stood before the enhancements. Each enhancement page links the files it changed, before and after.</p>
    </div>
    <a class="btn btn-outline" href="{TREE}capstone/original">Browse the original code on GitHub</a>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="section-head">
      <h2>Enhancements</h2>
      <p>One enhancement per category. Each page has the narrative, the key before-and-after files, and the code as submitted.</p>
    </div>
    <div class="grid-3">
{cards}
    </div>
  </div>
</section>
<section class="section section-alt">
  <div class="container">
    <div class="section-head">
      <h2>Course outcomes</h2>
      <p>Where the five CS 499 course outcomes are demonstrated across this ePortfolio.</p>
    </div>
    <div class="table-wrap">
      <table>
        <thead><tr><th scope="col">Outcome</th><th scope="col">Where it is demonstrated</th></tr></thead>
        <tbody>
{outcomes}
        </tbody>
      </table>
    </div>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="section-head"><h2>Downloads</h2><p>The written work as Word documents.</p></div>
    <ul class="prose">
{downloads}
    </ul>
  </div>
</section>'''
    page('trakcode.html', 'TrakCode: CS 499 Capstone', 'TrakCode, the CS 499 capstone artifact: the original artifact and three enhancements.', body, 'Projects')


def not_found():
    body = '''
<section class="section">
  <div class="container">
    <span class="eyebrow">404</span>
    <h1>Page not found</h1>
    <p class="lede">That page doesn&rsquo;t exist. It may have moved.</p>
    <div class="btn-row"><a class="btn" href="index.html">Go to the home page</a><a class="btn btn-outline" href="projects.html">See projects</a></div>
  </div>
</section>'''
    page('404.html', 'Page not found', 'Page not found.', body, None)


if __name__ == '__main__':
    home(); about(); projects(); trakcode()
    for e in ENHANCEMENTS:
        enhancement_page(e)
    not_found()
    (ROOT / '.nojekyll').write_text('', encoding='utf-8')
