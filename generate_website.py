#!/usr/bin/env python3
"""
Generate a complete interactive HTML website from README.md
"""

import re
import json

def parse_readme():
    """Parse README.md and extract all artifacts"""
    with open('README.md', 'r', encoding='utf-8') as f:
        content = f.read()

    sections = []
    current_section = None
    current_artifact = None
    capturing_section_n_content = False
    section_n_content = []
    artifact_counter = 1  # Track artifact numbers globally

    # Split by major sections (A-N)
    section_pattern = r'^## ([A-N])\. (.+)$'
    artifact_pattern = r'^### (\d+)\. (.+)$'
    # Pattern for bold artifact names (used in Section L)
    bold_artifact_pattern = r'^\*\*([^*]+)\*\*\s*$'

    lines = content.split('\n')

    for i, line in enumerate(lines):
        # Check for section headers
        section_match = re.match(section_pattern, line)
        if section_match:
            if current_section:
                # Add the last artifact before closing the section
                if current_artifact:
                    current_section['artifacts'].append(current_artifact)
                # Special handling for Section N - add captured content
                if capturing_section_n_content and section_n_content:
                    current_section['content'] = '\n'.join(section_n_content)
                    capturing_section_n_content = False
                    section_n_content = []
                sections.append(current_section)

            current_section = {
                'letter': section_match.group(1),
                'title': section_match.group(2),
                'artifacts': []
            }
            current_artifact = None

            # Section L has non-numbered artifacts, so assign them numbers starting at 154
            # (after all the numbered artifacts 1-153 from sections A-K and M)
            if section_match.group(1) == 'L':
                artifact_counter = 154

            # Start capturing content for Section N
            if section_match.group(1) == 'N':
                capturing_section_n_content = True

            continue

        # If we're capturing Section N content
        if capturing_section_n_content and line.strip():
            # Skip the separator line and total artifacts line
            if not line.startswith('---') and not line.startswith('**Total Artifacts'):
                section_n_content.append(line)
            continue

        # Check for numbered artifacts
        artifact_match = re.match(artifact_pattern, line)
        if artifact_match and current_section and not capturing_section_n_content:
            if current_artifact:
                current_section['artifacts'].append(current_artifact)

            current_artifact = {
                'number': artifact_match.group(1),
                'name': artifact_match.group(2),
                'purpose': '',
                'example': '',
                'sectors': [],
                'note': ''
            }
            artifact_counter = int(artifact_match.group(1)) + 1
            continue

        # Check for bold artifact names (Section L format)
        bold_match = re.match(bold_artifact_pattern, line)
        if bold_match and current_section and not capturing_section_n_content:
            # Skip subsection headers like "PUBLIC ADMINISTRATION SPECIFIC"
            if not line.isupper() or '/' in line:
                if current_artifact:
                    current_section['artifacts'].append(current_artifact)

                current_artifact = {
                    'number': str(artifact_counter),
                    'name': bold_match.group(1),
                    'purpose': '',
                    'example': '',
                    'sectors': [],
                    'note': ''
                }
                artifact_counter += 1
                continue

        # Parse artifact details
        if current_artifact:
            if line.startswith('**Purpose:**'):
                current_artifact['purpose'] = line.replace('**Purpose:**', '').strip()
            elif line.startswith('**Example:**'):
                current_artifact['example'] = line.replace('**Example:**', '').strip()
            elif line.startswith('**Sectors:**'):
                sectors_text = line.replace('**Sectors:**', '').strip()
                current_artifact['sectors'] = [s.strip() for s in sectors_text.split(',')]
            elif line.startswith('**Note:**'):
                current_artifact['note'] = line.replace('**Note:**', '').strip()

    # Add last artifact and section
    if current_artifact and current_section:
        current_section['artifacts'].append(current_artifact)
    if current_section:
        # Handle Section N content if we're still capturing
        if capturing_section_n_content and section_n_content:
            current_section['content'] = '\n'.join(section_n_content)
        sections.append(current_section)

    return sections

def generate_html(sections):
    """Generate complete HTML with all artifacts"""

    # Convert sections to JavaScript format
    artifacts_js = json.dumps(sections, indent=4)

    html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Master List of Organizational and Leadership Artifacts</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --primary: #2c3e50;
            --secondary: #3498db;
            --accent: #e74c3c;
            --light-bg: #ecf0f1;
            --dark-text: #2c3e50;
            --light-text: #7f8c8d;
            --card-bg: #ffffff;
            --border: #bdc3c7;
            --success: #27ae60;
            --warning: #f39c12;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: var(--dark-text);
            background: var(--light-bg);
        }

        .header {
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
            padding: 2rem 2rem 3rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            font-weight: 700;
        }

        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
            max-width: 800px;
        }

        .stats {
            display: flex;
            gap: 2rem;
            margin-top: 1.5rem;
            flex-wrap: wrap;
        }

        .stat-item {
            background: rgba(255,255,255,0.1);
            padding: 1rem 1.5rem;
            border-radius: 8px;
            backdrop-filter: blur(10px);
        }

        .stat-number {
            font-size: 2rem;
            font-weight: 700;
            display: block;
        }

        .stat-label {
            font-size: 0.9rem;
            opacity: 0.8;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 1rem;
        }

        .main-layout {
            display: grid;
            grid-template-columns: 280px 1fr;
            gap: 2rem;
            margin-top: -2rem;
            position: relative;
        }

        .sidebar {
            position: sticky;
            top: -3rem;
            height: fit-content;
            background: var(--card-bg);
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            max-height: calc(100vh - 2rem);
            overflow-y: auto;
        }

        .search-box {
            width: 100%;
            padding: 0.75rem 1rem;
            border: 2px solid var(--border);
            border-radius: 8px;
            font-size: 0.95rem;
            margin-bottom: 1.5rem;
            transition: border-color 0.3s;
        }

        .search-box:focus {
            outline: none;
            border-color: var(--secondary);
        }

        .filter-section {
            margin-bottom: 1.5rem;
        }

        .filter-title {
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--light-text);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.75rem;
        }

        .filter-buttons {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }

        .filter-btn {
            padding: 0.4rem 0.75rem;
            background: var(--light-bg);
            border: 1px solid var(--border);
            border-radius: 6px;
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.2s;
        }

        .filter-btn:hover {
            background: var(--secondary);
            color: white;
            border-color: var(--secondary);
        }

        .filter-btn.active {
            background: var(--secondary);
            color: white;
            border-color: var(--secondary);
        }

        .nav-sections {
            list-style: none;
        }

        .nav-sections li {
            margin-bottom: 0.5rem;
        }

        .nav-sections a {
            display: block;
            padding: 0.5rem 0.75rem;
            color: var(--dark-text);
            text-decoration: none;
            border-radius: 6px;
            transition: all 0.2s;
            font-size: 0.9rem;
        }

        .nav-sections a:hover {
            background: var(--light-bg);
            padding-left: 1rem;
        }

        .content {
            background: var(--card-bg);
            border-radius: 12px;
            padding: 2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            margin-bottom: 2rem;
        }

        .section {
            margin-bottom: 3rem;
            scroll-margin-top: 2rem;
        }

        .section-header {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1.5rem;
            padding-bottom: 0.75rem;
            border-bottom: 3px solid var(--secondary);
        }

        .section-letter {
            width: 50px;
            height: 50px;
            background: var(--secondary);
            color: white;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            font-weight: 700;
            flex-shrink: 0;
        }

        .section-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--primary);
        }

        .artifacts-grid {
            display: grid;
            gap: 1rem;
        }

        .artifact-card {
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1.25rem;
            transition: all 0.3s;
            background: white;
            position: relative;
        }

        .artifact-card:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border-color: var(--secondary);
            transform: translateY(-2px);
        }

        .bookmark-btn {
            position: absolute;
            top: 1rem;
            right: 1rem;
            background: transparent;
            border: none;
            cursor: pointer;
            font-size: 1.5rem;
            padding: 0.25rem;
            transition: all 0.2s;
            opacity: 0.5;
        }

        .bookmark-btn:hover {
            opacity: 1;
            transform: scale(1.1);
        }

        .bookmark-btn.bookmarked {
            opacity: 1;
        }

        .header-bottom {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 2rem;
            margin-top: 1.5rem;
        }

        .methodology-header {
            background: var(--card-bg);
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            flex: 2;
        }

        .methodology-header h3 {
            margin: 0 0 0.75rem 0;
            color: var(--primary);
            font-size: 1.1rem;
        }

        .framework-box-full {
            background: linear-gradient(135deg, rgba(52, 73, 94, 0.08) 0%, rgba(155, 89, 182, 0.12) 100%);
            border-left: 4px solid var(--secondary);
            padding: 1.5rem;
            border-radius: 8px;
            margin: 0.5rem 0;
        }

        .priority-modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.3);
        }

        .priority-modal-content-compact {
            background-color: white;
            margin: 20% auto;
            padding: 1rem;
            border-radius: 12px;
            width: fit-content;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }

        .priority-options-compact {
            display: flex;
            gap: 1rem;
        }

        .priority-icon {
            font-size: 2rem;
            cursor: pointer;
            transition: all 0.2s;
            padding: 0.5rem;
            border-radius: 50%;
        }

        .priority-icon:hover {
            transform: scale(1.2);
            background: var(--light-bg);
        }

        .priority-icon[data-priority="none"] {
            opacity: 0.5;
        }

        .export-section {
            margin-top: 1rem;
            padding-top: 1rem;
            border-top: 1px solid var(--border);
        }

        .artifact-number {
            display: inline-block;
            background: var(--secondary);
            color: white;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }

        .artifact-name {
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--primary);
            margin-bottom: 0.75rem;
        }

        .artifact-purpose {
            color: var(--dark-text);
            margin-bottom: 0.75rem;
            line-height: 1.5;
        }

        .artifact-example {
            background: var(--light-bg);
            padding: 0.75rem;
            border-radius: 6px;
            font-size: 0.9rem;
            margin-bottom: 0.75rem;
            color: var(--light-text);
        }

        .artifact-example strong {
            color: var(--dark-text);
        }

        .artifact-note {
            background: #fff3cd;
            border-left: 3px solid var(--warning);
            padding: 0.75rem;
            border-radius: 6px;
            font-size: 0.9rem;
            margin-top: 0.75rem;
            color: #856404;
        }

        .sectors {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }

        .sector-tag {
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 500;
        }

        .sector-tag.public {
            background: #e3f2fd;
            color: #1976d2;
        }

        .sector-tag.nonprofit {
            background: #f3e5f5;
            color: #7b1fa2;
        }

        .sector-tag.general {
            background: #e8f5e9;
            color: #388e3c;
        }

        .methodology {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
        }

        .methodology h2 {
            margin-bottom: 1rem;
        }

        .methodology p {
            opacity: 0.95;
            line-height: 1.7;
        }

        .framework-box {
            background: rgba(255,255,255,0.1);
            padding: 1.5rem;
            border-radius: 8px;
            margin: 1rem 0;
            backdrop-filter: blur(10px);
        }

        @media (max-width: 968px) {
            .main-layout {
                grid-template-columns: 1fr;
            }

            .sidebar {
                position: relative;
                top: 0;
                max-height: none;
            }

            .header h1 {
                font-size: 1.75rem;
            }

            .stats {
                gap: 1rem;
            }

            .section-title {
                font-size: 1.25rem;
            }
        }

        .reset-btn {
            width: 100%;
            padding: 0.75rem;
            background: var(--accent);
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            margin-bottom: 1rem;
            font-weight: 600;
            transition: all 0.2s;
        }

        .reset-btn:hover {
            background: #c0392b;
        }

        /* Comparison table styles */
        .comparison-content {
            margin-top: 1.5rem;
        }

        .comparison-content p {
            margin-bottom: 1rem;
            line-height: 1.7;
        }

        .comparison-content h3 {
            color: var(--primary);
            margin: 1.5rem 0 1rem;
            font-size: 1.25rem;
        }

        .comparison-content strong {
            color: var(--primary);
        }

        .comparison-table {
            width: 100%;
            border-collapse: collapse;
            margin: 1.5rem 0;
            background: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border-radius: 8px;
            overflow: hidden;
        }

        .comparison-table thead {
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
        }

        .comparison-table th {
            padding: 1rem;
            text-align: left;
            font-weight: 600;
            font-size: 0.95rem;
        }

        .comparison-table td {
            padding: 1rem;
            border-bottom: 1px solid var(--border);
            line-height: 1.6;
        }

        .comparison-table tbody tr:hover {
            background: var(--light-bg);
        }

        .comparison-table tbody tr:last-child td {
            border-bottom: none;
        }

        .comparison-content ol {
            margin: 1rem 0 1rem 2rem;
            line-height: 1.8;
        }

        .comparison-content ol li {
            margin-bottom: 0.75rem;
        }

        .key-insights {
            background: #f8f9fa;
            border-left: 4px solid var(--secondary);
            padding: 1.5rem;
            border-radius: 8px;
            margin: 1.5rem 0;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <h1>Master List of Organizational and Leadership Artifacts</h1>
            <p>A comprehensive compilation of organizational, leadership, strategic, operational, and governance artifacts used across public administration, nonprofit leadership, and general organizational management</p>
            <div class="header-bottom">
                <div class="stats">
                    <div class="stat-item">
                        <span class="stat-number" id="totalArtifacts">153</span>
                        <span class="stat-label">Artifacts</span>
                    </div>
                </div>
                <div class="methodology-header">
                    <h3>The Strategic Foundation (Identity Layer)</h3>
                    <div class="framework-box-full">
                        <span style="font-size: 1.1rem; display: block; margin: 0.75rem 0;">
                            <strong>Purpose</strong> (most stable) → <strong>Vision</strong> (aspirational) → <strong>Mission</strong> (operational) → <strong>Values</strong> (behavioral)
                        </span>
                        <ul style="margin-top: 0.75rem; list-style: none; padding-left: 0;">
                            <li>• Purpose answers "Why do we exist?" and remains highly stable over time</li>
                            <li>• Vision answers "Where are we going?" and provides the aspirational future state</li>
                            <li>• Mission answers "What do we do and for whom?" and describes current operations</li>
                            <li>• Values answer "How do we behave?" and guide daily decision-making</li>
                        </ul>
                    </div>
                    <h3 style="margin-top: 1.5rem;">The Universal Artifact Stack</h3>
                    <div class="framework-box-full">
                        <span style="font-size: 1.1rem; display: block; margin: 0.75rem 0;">
                            <strong>Identity</strong> → <strong>Direction</strong> → <strong>Priorities</strong> → <strong>Action</strong> → <strong>Accountability</strong>
                        </span>
                        <span style="font-size: 1.05rem; display: block; margin: 0.75rem 0; opacity: 0.9;">
                            Vision & Mission → Guiding Principles/Values → Strategic Goals → Initiatives/Plans → Performance Metrics
                        </span>
                        <ul style="margin-top: 0.75rem; list-style: none; padding-left: 0;">
                            <li>• <strong>Vision Statement</strong> - Aspirational future state (Identity)</li>
                            <li>• <strong>Mission Statement</strong> - Current purpose and operations (Identity)</li>
                            <li>• <strong>Core Values</strong> - Behavioral expectations and culture (Direction)</li>
                            <li>• <strong>Guiding Principles</strong> - Decision-making frameworks (Direction)</li>
                            <li>• <strong>Strategic Goals</strong> - Major 3-5 year objectives (Priorities)</li>
                            <li>• <strong>Strategic Priorities</strong> - Current focus areas for resource allocation (Priorities)</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="container">
        <div class="main-layout">
            <aside class="sidebar">
                <button class="reset-btn" onclick="resetFilters()">Reset All Filters</button>
                <input type="text" class="search-box" id="searchBox" placeholder="Search artifacts...">

                <div class="filter-section">
                    <div class="filter-title">Filter by Sector</div>
                    <div class="filter-buttons">
                        <button class="filter-btn active" data-sector="all">All</button>
                        <button class="filter-btn" data-sector="public">Public</button>
                        <button class="filter-btn" data-sector="nonprofit">Nonprofit</button>
                        <button class="filter-btn" data-sector="general">General</button>
                    </div>
                </div>

                <div class="filter-section">
                    <div class="filter-title">Bookmarked <span id="bookmarkCount">(0)</span></div>
                    <button class="filter-btn" id="showBookmarked" data-filter="bookmarked">View Saved</button>
                    <div class="export-section">
                        <button class="filter-btn" id="exportBookmarks" style="background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%); color: white;">Export Saved</button>
                    </div>
                    <button class="filter-btn" id="clearBookmarks" style="margin-top: 0.5rem;">Clear All</button>
                </div>

                <div class="filter-title">Sections</div>
                <ul class="nav-sections" id="navList">
                    <!-- Will be populated dynamically -->
                </ul>
            </aside>

            <main>
                <div class="content">
                    <div id="artifactContainer">
                        <!-- Artifacts will be dynamically loaded here -->
                    </div>
                </div>
            </main>
        </div>
    </div>

    <!-- Priority Selection Modal -->
    <div id="priorityModal" class="priority-modal">
        <div class="priority-modal-content-compact">
            <div class="priority-options-compact">
                <div class="priority-icon" data-priority="none" title="No priority">⚪</div>
                <div class="priority-icon" data-priority="immediate" title="Immediate">🔴</div>
                <div class="priority-icon" data-priority="mid-term" title="Mid-term">🟡</div>
                <div class="priority-icon" data-priority="long-term" title="Long-term">🟢</div>
            </div>
        </div>
    </div>

    <script>
        // Artifact data
        const artifactsData = ''' + artifacts_js + ''';

        // Render navigation
        function renderNavigation() {
            const navList = document.getElementById('navList');
            navList.innerHTML = artifactsData.map(section => `
                <li><a href="#section-${section.letter.toLowerCase()}">${section.letter}. ${section.title.split(' ').slice(0, 3).join(' ')}...</a></li>
            `).join('');
        }

        // Convert markdown content to HTML (for Section N)
        function markdownToHtml(markdown) {
            if (!markdown) return '';

            let html = markdown;

            // Convert markdown table to HTML
            const tableRegex = /\\|(.+)\\|\\n\\|[-:\\s|]+\\|\\n((?:\\|.+\\|\\n?)+)/g;
            html = html.replace(tableRegex, (match, header, rows) => {
                const headers = header.split('|').map(h => h.trim()).filter(h => h);
                const rowsArray = rows.trim().split('\\n').map(row =>
                    row.split('|').map(cell => cell.trim()).filter(cell => cell)
                );

                let tableHtml = '<table class="comparison-table"><thead><tr>';
                headers.forEach(h => tableHtml += `<th>${h}</th>`);
                tableHtml += '</tr></thead><tbody>';

                rowsArray.forEach(row => {
                    tableHtml += '<tr>';
                    row.forEach(cell => tableHtml += `<td>${cell}</td>`);
                    tableHtml += '</tr>';
                });

                tableHtml += '</tbody></table>';
                return tableHtml;
            });

            // Convert headings
            html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');

            // Convert bold
            html = html.replace(/\\*\\*(.+?)\\*\\*/g, '<strong>$1</strong>');

            // Convert numbered lists
            html = html.replace(/^(\\d+\\.\\s+.+?)(?=\\n\\d+\\.| \\n\\n|$)/gms, (match) => {
                const items = match.split(/\\n(?=\\d+\\.\\s)/).map(item => {
                    const text = item.replace(/^\\d+\\.\\s+/, '');
                    return `<li>${text}</li>`;
                }).join('');
                return `<ol>${items}</ol>`;
            });

            // Convert paragraphs
            html = html.replace(/^(?!<[holt]|<table)(.+)$/gm, '<p>$1</p>');

            // Wrap key insights
            html = html.replace(/<h3>Key Insights from Comparative Analysis:<\\/h3>(.*?)(?=<h3>|$)/s,
                '<div class="key-insights"><h3>Key Insights from Comparative Analysis:</h3>$1</div>');

            return html;
        }

        // Render artifacts
        function renderArtifacts() {
            const container = document.getElementById('artifactContainer');
            container.innerHTML = '';

            artifactsData.forEach(section => {
                const sectionDiv = document.createElement('div');
                sectionDiv.className = 'section';
                sectionDiv.id = `section-${section.letter.toLowerCase()}`;

                // Check if section has special content (like Section N)
                if (section.content) {
                    sectionDiv.innerHTML = `
                        <div class="section-header">
                            <div class="section-letter">${section.letter}</div>
                            <h2 class="section-title">${section.title}</h2>
                        </div>
                        <div class="comparison-content">
                            ${markdownToHtml(section.content)}
                        </div>
                    `;
                } else {
                    // Regular artifact cards
                    sectionDiv.innerHTML = `
                        <div class="section-header">
                            <div class="section-letter">${section.letter}</div>
                            <h2 class="section-title">${section.title}</h2>
                        </div>
                        <div class="artifacts-grid">
                            ${section.artifacts.map(artifact => `
                                <div class="artifact-card" data-sectors="${artifact.sectors.join(',').toLowerCase()}" data-name="${artifact.name.toLowerCase()}" data-number="${artifact.number}">
                                    <button class="bookmark-btn" onclick="toggleBookmark(${artifact.number})" title="Bookmark this artifact">
                                        📚
                                    </button>
                                    <div class="artifact-number">#${artifact.number}</div>
                                    <div class="artifact-name">${artifact.name}</div>
                                    <div class="artifact-purpose">${artifact.purpose}</div>
                                    ${artifact.example ? `<div class="artifact-example"><strong>Example:</strong> ${artifact.example}</div>` : ''}
                                    ${artifact.note ? `<div class="artifact-note"><strong>Note:</strong> ${artifact.note}</div>` : ''}
                                    <div class="sectors">
                                        ${artifact.sectors.map(sector => `
                                            <span class="sector-tag ${sector.toLowerCase()}">${sector}</span>
                                        `).join('')}
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    `;
                }

                container.appendChild(sectionDiv);
            });

            updateVisibleCount();
        }

        // Update visible artifact count
        function updateVisibleCount() {
            const visibleCards = document.querySelectorAll('.artifact-card:not([style*="display: none"])');
            document.getElementById('totalArtifacts').textContent = visibleCards.length;
        }

        // Bookmark functionality with priorities
        let currentBookmarkNumber = null;

        function getBookmarks() {
            const saved = localStorage.getItem('artifactBookmarks');
            return saved ? JSON.parse(saved) : [];
        }

        function saveBookmarks(bookmarks) {
            localStorage.setItem('artifactBookmarks', JSON.stringify(bookmarks));
            updateBookmarkCount();
            updateBookmarkButtons();
        }

        function toggleBookmark(artifactNumber) {
            let bookmarks = getBookmarks();
            const existingIndex = bookmarks.findIndex(b => b.number === artifactNumber);

            if (existingIndex > -1) {
                // Remove bookmark
                bookmarks.splice(existingIndex, 1);
                saveBookmarks(bookmarks);
            } else {
                // Show priority modal
                currentBookmarkNumber = artifactNumber;
                document.getElementById('priorityModal').style.display = 'block';
            }
        }

        function addBookmarkWithPriority(artifactNumber, priority) {
            let bookmarks = getBookmarks();
            bookmarks.push({ number: artifactNumber, priority: priority });
            saveBookmarks(bookmarks);
        }

        function updateBookmarkCount() {
            const count = getBookmarks().length;
            document.getElementById('bookmarkCount').textContent = `(${count})`;
        }

        function updateBookmarkButtons() {
            const bookmarks = getBookmarks();
            document.querySelectorAll('.bookmark-btn').forEach(btn => {
                const card = btn.closest('.artifact-card');
                const number = parseInt(card.dataset.number);
                const isBookmarked = bookmarks.some(b => b.number === number);
                if (isBookmarked) {
                    btn.classList.add('bookmarked');
                } else {
                    btn.classList.remove('bookmarked');
                }
            });
        }

        function showBookmarkedOnly() {
            const bookmarks = getBookmarks();
            const cards = document.querySelectorAll('.artifact-card');

            cards.forEach(card => {
                const number = parseInt(card.dataset.number);
                const isBookmarked = bookmarks.some(b => b.number === number);
                card.style.display = isBookmarked ? 'block' : 'none';
            });

            updateVisibleCount();
        }

        function clearAllBookmarks() {
            if (confirm('Are you sure you want to clear all bookmarked artifacts?')) {
                saveBookmarks([]);
                resetFilters();
            }
        }

        function exportBookmarks() {
            const bookmarks = getBookmarks();
            if (bookmarks.length === 0) {
                alert('No bookmarked artifacts to export!');
                return;
            }

            // Group by priority
            const grouped = {
                immediate: [],
                'mid-term': [],
                'long-term': [],
                none: []
            };

            bookmarks.forEach(bookmark => {
                const artifact = findArtifactByNumber(bookmark.number);
                if (artifact) {
                    grouped[bookmark.priority].push({
                        number: bookmark.number,
                        name: artifact.name,
                        purpose: artifact.purpose,
                        example: artifact.example,
                        sectors: artifact.sectors.join(', ')
                    });
                }
            });

            // Create CSV content
            let csv = 'Priority,Number,Name,Purpose,Example,Sectors\\n';

            ['immediate', 'mid-term', 'long-term', 'none'].forEach(priority => {
                const priorityLabel = priority === 'none' ? 'Unprioritized' :
                                     priority === 'mid-term' ? 'Mid-term' :
                                     priority.charAt(0).toUpperCase() + priority.slice(1);
                grouped[priority].forEach(artifact => {
                    csv += `"${priorityLabel}","${artifact.number}","${artifact.name.replace(/"/g, '""')}","${artifact.purpose.replace(/"/g, '""')}","${artifact.example.replace(/"/g, '""')}","${artifact.sectors}"\\n`;
                });
            });

            // Download CSV
            const blob = new Blob([csv], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `leadership-artifacts-${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        }

        function findArtifactByNumber(number) {
            for (const section of artifactsData) {
                const artifact = section.artifacts.find(a => parseInt(a.number) === number);
                if (artifact) return artifact;
            }
            return null;
        }

        // Priority modal event listeners
        document.querySelectorAll('.priority-icon').forEach(icon => {
            icon.addEventListener('click', function() {
                const priority = this.dataset.priority;
                addBookmarkWithPriority(currentBookmarkNumber, priority);
                document.getElementById('priorityModal').style.display = 'none';
                currentBookmarkNumber = null;
            });
        });

        // Close modal when clicking outside - auto-save with "none" priority
        document.getElementById('priorityModal').addEventListener('click', function(e) {
            if (e.target === this) {
                addBookmarkWithPriority(currentBookmarkNumber, 'none');
                this.style.display = 'none';
                currentBookmarkNumber = null;
            }
        });

        // Search functionality
        document.getElementById('searchBox').addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase();
            const cards = document.querySelectorAll('.artifact-card');

            cards.forEach(card => {
                const text = card.textContent.toLowerCase();
                card.style.display = text.includes(searchTerm) ? 'block' : 'none';
            });

            updateVisibleCount();
        });

        // Filter functionality
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');

                const sector = e.target.dataset.sector;
                const cards = document.querySelectorAll('.artifact-card');

                cards.forEach(card => {
                    if (sector === 'all') {
                        card.style.display = 'block';
                    } else {
                        const cardSectors = card.dataset.sectors;
                        card.style.display = cardSectors.includes(sector) ? 'block' : 'none';
                    }
                });

                updateVisibleCount();
            });
        });

        // Reset filters
        function resetFilters() {
            document.getElementById('searchBox').value = '';
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            document.querySelector('.filter-btn[data-sector="all"]').classList.add('active');
            document.querySelectorAll('.artifact-card').forEach(card => {
                card.style.display = 'block';
            });
            updateVisibleCount();
        }

        // Smooth scroll
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Bookmark button event listeners
        document.getElementById('showBookmarked').addEventListener('click', showBookmarkedOnly);
        document.getElementById('exportBookmarks').addEventListener('click', exportBookmarks);
        document.getElementById('clearBookmarks').addEventListener('click', clearAllBookmarks);

        // Initialize
        renderNavigation();
        renderArtifacts();
        updateBookmarkCount();
        updateBookmarkButtons();
    </script>
</body>
</html>'''

    return html_template

def main():
    print("Parsing README.md...")
    sections = parse_readme()

    print(f"Found {len(sections)} sections")
    total_artifacts = sum(len(s['artifacts']) for s in sections)
    print(f"Found {total_artifacts} artifacts")

    print("Generating HTML...")
    html = generate_html(sections)

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)

    print("✓ Generated index.html successfully!")
    print(f"✓ Includes all {total_artifacts} artifacts across {len(sections)} sections")

if __name__ == '__main__':
    main()
