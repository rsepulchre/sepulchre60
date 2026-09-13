<<<<<<< HEAD
# Sepulchre 60 — Rodolphe Sepulchre at sixty

A plain static website for two proposed birthday workshops and two commemorative collections. The design follows the restrained academic structure of Anders Rantzer’s 60th-birthday workshop: centred headings, a short introduction, circular portraits, and a chronological programme.

## View and host

Open `dist/index.html` locally, or copy the contents of `dist/` to any static web host or GitHub Pages publishing directory. All internal links use relative paths and explicit filenames. Fonts use the system stack; all images and styles are local. The workshop themes are **ICE: Interactions, Control and Events** and **FIRE: Feedback, Interaction, Robustness and Events**. No browser JavaScript, framework, database or external font service is required. `.nojekyll` is included. Existing older workshop URLs continue to work through static forwarding pages.

## Navigation

The site has five main buttons: Home, ECC, CDC, Festschrift and Liber amicorum. Each workshop has three buttons: Home, Academic tree and Programme.

The ECC home combines logistics and 20 linked portraits: 19 alumni plus Rodolphe, arranged in five columns and four rows on desktop. The grid adapts to smaller screens. The CDC home uses the same template with its 13 collaborators plus Rodolphe. Participant lists are provisional until confirmations are supplied.

## Programme

ECC runs 09:00–17:20 with twenty 20-minute contributions (15-minute talk and 5-minute questions), two 20-minute coffee breaks and one 60-minute lunch. The alumni are ordered by documented joining year; same-year cohorts use alphabetical surname order. Rodolphe closes. Franci uses 2012 and Miranda-Villatoro 2018 from their personal biographies; the conflicting roster dates are disclosed in the programme notes.

CDC runs 09:00–17:40 with fourteen 30-minute contributions (25-minute talk and 5-minute questions), two 20-minute coffee breaks and one 60-minute lunch. Its four sessions contain three, four, three and four talks respectively. ECC uses four balanced sessions of five talks. Its collaborator order remains provisional and is not presented as an alumni chronology.

## Genealogy

The ECC tree continues downward into the full official roster: 9 current and 25 former PhD entries, and 3 current and 30 former postdoc entries. These 67 roles represent 61 distinct people; six appear in both branches. Dates reproduce the listed periods, not degree-award dates. `content/descendants.json` preserves each entry and its provenance.

The Academic tree places the mathematical PhD branch on the left and the postdoctoral mentor’s medical and intellectual ancestry on the right. Long sequences can be expanded without JavaScript. Each name links to a source record. Historical teacher/correspondence relationships are distinguished from doctoral supervision, and uncertain medieval associations are disclosed. The right branch belongs to Rodolphe’s postdoctoral mentor, not to a second doctoral degree for Rodolphe.

## Collections

Festschrift provides an editorial introduction, background bibliography and manuscript outline. No submitted papers are invented. Liber amicorum includes two identified public archive photographs with source captions and credits; it awaits friends’ own recollections. Contribution outlines are downloadable Markdown files. There are no upload forms or external messages. To publish a contributed item, add its approved text and assets locally and regenerate the pages.

## Edit and regenerate

`content/workshops.json` contains event facts, profiles and schedules. `content/genealogy.json` contains the displayed trees and source notes. `content/memories.json` contains archive photographs. `content/research.json` supplies the background bibliography. Edit these and run `node scripts/render.mjs`. Node is an optional authoring dependency only. Every generated HTML page can also be edited directly, though regeneration overwrites such edits. `dist/assets/style.css` controls the design.

For schedule entries use `time`, `kind` (`talk` or `break`), `person` (profile slug), `title`, and optional `breakType` (`coffee` or `lunch`). Speaker profiles include `joinYear` and `joinRole` for chronology. New portrait assets should have real public or supplied provenance and accompanying credits.

## Banner

The recurring banner is a simulated classical Hodgkin–Huxley action potential on five musical staff lines. `dist/assets/hh-model.json` records equations, units, parameters, stimulus, numerical checks and primary sources; `hh-trace.csv` contains the data. `scripts/generate_hh_staff.py` preserves the computation. It is a simulated illustration, not experimental data. The homepage pairs Rodolphe’s portrait with his verified line “Music is rhythmic. So is life.”, linked to *Clocks and Rhythms* (2022). An original generated ICE/FIRE brush circle sits to the right of the workshop list on desktop, with separate ice-blue and fire-orange brushstrokes. Original public portrait and archive photos are preserved without bitmap editing.

## Planning facts

ECC’s announced workshop day is 13 July 2027, Brussels; workshop acceptance is pending. CDC’s overall event is announced for 13–17 December 2027, Lisbon; the exact birthday workshop day remains unconfirmed. Workshop room, registration, organisers and contact details need confirmed information. The current hosted site retains its existing audience and stable URL.

Source dossiers in `docs/` retain research provenance, genealogy records, chronological caveats and archive-photo captions. Key references:

- https://people.kth.se/~mikaelj/rantzer_fest/index.html
- https://www.mathgenealogy.org/id.php?id=103842
- https://sites.google.com/site/rsepulchre/phds-postdocs
- https://ecc27.euca-ecc.org/call-for-papers/
- https://www.abreuevents.com/CDC_2027-42175.aspx
=======
# sepulchre60
>>>>>>> 455db6073c2b9c4085c33ef22e1b9cc06f9ea436
