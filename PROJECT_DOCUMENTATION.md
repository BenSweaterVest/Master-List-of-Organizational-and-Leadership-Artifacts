# Master List of Organizational and Leadership Artifacts - Project Documentation

## Project Overview

A comprehensive, interactive web catalog of 188 organizational and leadership artifacts used across public administration, nonprofit leadership, and general organizational management. Each artifact is fully researched with academic/authoritative explanations and real-world examples.

**Live Site:** https://leadership-artifacts.pages.dev/

## Features

### Core Functionality
- **188 Artifacts** organized by domain and category
- **376 Research Links** - 2 curated links per artifact (explanation + example)
- **Interactive Filtering** by sector (Public, Nonprofit, General)
- **Search Functionality** for finding specific artifacts
- **Bookmark System** with priority indicators (no priority, immediate, mid-term, long-term)
- **Responsive Design** with mobile-friendly interface

### Research Quality Standards
All research sources prioritize academic rigor:
- **.edu domains** - Universities and academic institutions
- **.gov domains** - Government agencies and official resources
- **Professional organizations** - PMI, SHRM, NASW, OECD, BoardSource, etc.
- **Standards bodies** - ISO, NIST, COSO, etc.

## Repository Structure

```
/
├── index.html                      # Main application (188 artifacts with full UI)
├── README.md                       # Original project README
├── PROJECT_DOCUMENTATION.md        # This file - comprehensive project docs
├── org-documents-reference.md      # Reference material
├── generate_website.py             # Website generation script
├── integrate_research.py           # Script to merge research JSON into index.html
└── research-data/                  # Curated research for artifacts 11-188
    ├── README.md                   # Research data documentation
    ├── artifacts-11-20.json        # Strategic Direction & Identity
    ├── artifacts-21-30.json        # Governance & Oversight
    ├── artifacts-31-40.json        # Operational Management
    ├── artifacts-41-50.json        # Operations & HR
    ├── artifacts-51-60.json        # Workforce Development
    ├── artifacts-61-70.json        # HR/Workforce & Finance
    ├── artifacts-71-80.json        # Technology & Data
    ├── artifacts-81-90.json        # Risk & Continuity
    ├── artifacts-91-100.json       # Communications & Engagement
    ├── artifacts-101-120.json      # Evaluation & Project Management
    ├── artifacts-121-130.json      # Change Management
    ├── artifacts-131-153.json      # Advanced & Specialized Tools
    ├── artifacts-154-186.json      # Specialized & Sector-Specific
    └── artifacts-187-188.json      # Consulting Artifacts
```

## Artifact Categories

### A. Strategic Direction & Organizational Identity (1-10)
Mission, Vision, Values, Purpose, Strategic Goals & Priorities

### B. Governance & Oversight (11-30)
Board governance, bylaws, ethics, conflict of interest, audit frameworks

### C. Operational Management (31-50)
Operating models, capabilities, service delivery, SOPs, SLAs

### D. Workforce Development & People (51-70)
Workforce planning, succession, skills, onboarding, performance, DEI, benefits

### E. Financial Planning & Resource Management (65-80)
Budgets, financial controls, grants, capital planning

### F. Technology, Data & Information (71-80)
Data governance, IT strategy, cybersecurity, architecture

### G. Risk, Continuity & Resilience (81-90)
Risk management, business continuity, COOP, threat assessment

### H. Communications & Public Engagement (91-100)
Communications plans, brand guidelines, stakeholder engagement, transparency

### I. Evaluation, Learning & Improvement (101-120)
Performance measurement, balanced scorecard, OKRs, logic models, M&E, audits

### J. Change, Transformation & Culture (121-130)
Change management, readiness, adoption, culture frameworks, symbolic actions

### K. Program, Project & Portfolio Management (114-120)
Project charters, governance, portfolio prioritization, benefits realization

### L. Sector-Specific & Regulatory (154-166)
Briefing books, legislative reports, rulemaking, interagency agreements

### M. Advanced & Specialized Tools (131-153)
Design principles, personas, PESTLE, SWOT, scenario planning, systems mapping

### N. Specialized Consulting & Nonprofit (167-188)
Impact frameworks, fundraising, volunteer management, consulting deliverables

## Technical Implementation

### Frontend Stack
- **HTML5** with semantic markup
- **CSS3** with custom properties (CSS variables)
- **Vanilla JavaScript** - no framework dependencies
- **localStorage** for bookmark persistence
- **Responsive Grid Layout** for desktop/mobile

### Key UI Features
1. **Priority System**:
   - One-click bookmarking
   - Inline priority indicators (⚪🔴🟡🟢)
   - Visual feedback with opacity/transforms
   - Default: No priority

2. **Filtering & Search**:
   - Real-time search across artifact names
   - Sector filtering (Public/Nonprofit/General)
   - Reset functionality

3. **Resource Links**:
   - Explanation link (📖) - Academic/authoritative
   - Example link (🔗) - Real-world implementation
   - Opens in new tabs with security attributes

### Data Structure

Each artifact follows this schema:
```json
{
  "number": "1",
  "name": "Mission Statement",
  "purpose": "Defines the organization's fundamental reason for existing...",
  "example": "\"To organize the world's information...\" (Google)",
  "sectors": ["Public", "Nonprofit", "General"],
  "note": "",
  "explanationLink": {
    "url": "https://www.hbs.edu/...",
    "title": "Harvard Business School - Mission Statement Guide"
  },
  "exampleLink": {
    "url": "https://about.google/",
    "title": "Google's Mission Statement (Official)"
  }
}
```

## Research Methodology

### Phase 1: Artifact Identification (Complete)
- Compiled 188 unique organizational artifacts
- Categorized by domain and sector applicability
- Added purpose descriptions and brief examples

### Phase 2: Research Enhancement (Complete)
- Systematic web research for each artifact
- Two links per artifact:
  - **Explanation Link**: Academic or authoritative source
  - **Example Link**: Real-world implementation or template
- Prioritized .edu, .gov, and professional organization domains

### Phase 3: Integration (Complete)
- Created JSON files for artifacts 11-188
- Developed Python integration script
- Embedded research into index.html
- Added research documentation

## Development Scripts

### `integrate_research.py`
Merges research JSON files into index.html:
```bash
python3 integrate_research.py
```

Features:
- Loads 14 JSON research files
- Parses artifact data from HTML
- Adds explanationLink and exampleLink to each artifact
- Preserves formatting and structure
- Reports statistics on integration

### `generate_website.py`
Original website generation script (legacy)

## Testing & Verification

### Artifact Coverage Check
```bash
# Verify all artifacts 11-188 are in research files
jq -r '.[].number' research-data/artifacts-*.json | sort -n | uniq | wc -l
# Should return: 178 (artifacts 11-188)

# Check for missing numbers
jq -r '.[].number' research-data/artifacts-*.json | sort -n > research_nums.txt
seq 11 188 > expected_nums.txt
diff expected_nums.txt research_nums.txt
# Should return: no output (no differences)
```

### Integration Test
```bash
python3 integrate_research.py
# Should report: "Loaded research for 168 artifacts"
# (168 = artifacts 11-20 through 187-188)
```

## Git Workflow

### Branch Structure
- `main` - Production branch
- `claude/improve-priority-ui-*` - Feature branches

### Commit Conventions
- Descriptive commit messages
- Atomic commits per feature
- All changes tested before pushing

## Future Enhancements

### Potential Features
- [ ] Export bookmarked artifacts to PDF
- [ ] Share bookmark collections via URL
- [ ] Advanced filtering by category
- [ ] Artifact comparison view
- [ ] Print-friendly layouts
- [ ] Dark mode toggle
- [ ] Artifact relationship mapping
- [ ] User-submitted examples

### Technical Improvements
- [ ] Add service worker for offline access
- [ ] Implement analytics tracking
- [ ] Add automated testing
- [ ] Create API endpoint for artifact data
- [ ] Implement versioning for artifact updates

## Maintenance

### Updating Research Links
1. Edit appropriate JSON file in `research-data/`
2. Run `python3 integrate_research.py`
3. Verify changes in `index.html`
4. Commit and push

### Adding New Artifacts
1. Add artifact to `index.html` artifactsData array
2. Create/update research JSON file
3. Update stats in header (total count)
4. Run integration script
5. Update documentation

## Credits & Sources

### Research Sources Include:
- Harvard Business School, Stanford GSB, MIT Sloan
- GAO, FEMA, NASA, IRS, Department of State
- PMI, SHRM, NASW, OECD, BoardSource
- ISO, NIST, COSO, TOGAF

### Frameworks Referenced:
- McKinsey 7S, Bain RAPID, Deloitte Greenhouse
- Balanced Scorecard (Kaplan & Norton)
- OKRs (John Doerr/Google)
- CMMI, TOGAF, FEAF, PESTLE, SWOT
- Theory of Change, Logic Models

## License

Please refer to the repository license file.

## Contact & Support

For questions, suggestions, or contributions, please open an issue in the repository.

---

**Last Updated:** November 2025
**Version:** 2.0 (Research Enhancement Complete)
**Total Artifacts:** 188
**Research Links:** 376
**Coverage:** 100%
