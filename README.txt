README.md

========================
1. Where to edit
========================

Report metadata
  Setup/Statics.tex
  (title, subtitle, authors, student numbers, department)

Document entry point
  main.tex
  (controls chapter order)

Project schedule
  schedule.tex
  (5-week project plan)

Chapters
  Chapters/
    01_Theoretical_introduction/
    02_CORAS_analysis/
    03_Discussion/
    04_Conclusion/

Front/back pages
  Frontmatter/
  Backmatter/
  (front page, appendix, back page)


========================
2. References and citations
========================

Each major chapter has its own bibliography file.

Examples:

  Chapters/01_Theoretical_introduction/bibliography.bib
  Chapters/02_CORAS_analysis/bibliography.bib

Add new entries to the relevant .bib file.

Citations in LaTeX use the standard commands, for example:

  \citep{key}


========================
3. Figures and assets
========================

Chapter figures
  Place figures inside the chapter's "figures/" folder.

Graphics in LaTeX
  Use relative paths when including images.

Shared template assets
  Resources/