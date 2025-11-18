#!/usr/bin/env python3
"""
Script to integrate research links into index.html
"""
import json
import re

# Load all research JSON files
research_files = [
    'artifacts-21-30.json',
    'artifacts-31-40.json',
    'artifacts-41-50.json',
    'artifacts-51-60.json',
    'artifacts-61-70.json',
    'artifacts-71-80.json',
    'artifacts-81-90.json',
    'artifacts-91-100.json',
    'artifacts-101-120.json',
    'artifacts-121-130.json',
    'artifacts-131-153.json',
    'artifacts-154-186.json'
]

# Build a dictionary of artifact number -> research data
research_data = {}
for filename in research_files:
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            artifacts = json.load(f)
            for artifact in artifacts:
                num = artifact['number']
                research_data[num] = {
                    'explanationLink': artifact.get('explanationLink'),
                    'exampleLink': artifact.get('exampleLink')
                }
    except FileNotFoundError:
        print(f"Warning: {filename} not found")

print(f"Loaded research for {len(research_data)} artifacts")

# Read the HTML file
with open('index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Find the artifactsData section
pattern = r'(const artifactsData = \[)(.*?)(\];)'
match = re.search(pattern, html_content, re.DOTALL)

if not match:
    print("Error: Could not find artifactsData in HTML")
    exit(1)

before = match.group(1)
artifacts_json_str = match.group(2)
after = match.group(3)

# Parse the artifacts data
try:
    # Add brackets to make it valid JSON
    artifacts_array = json.loads('[' + artifacts_json_str + ']')
except json.JSONDecodeError as e:
    print(f"Error parsing artifacts JSON: {e}")
    exit(1)

print(f"Parsed {len(artifacts_array)} category groups from HTML")

# Integrate research into artifacts
updates_count = 0
for category in artifacts_array:
    if 'artifacts' in category:
        for artifact in category['artifacts']:
            num = artifact.get('number')
            if num in research_data:
                # Add explanation and example links if not already present
                if 'explanationLink' not in artifact and research_data[num].get('explanationLink'):
                    artifact['explanationLink'] = research_data[num]['explanationLink']
                    updates_count += 1
                if 'exampleLink' not in artifact and research_data[num].get('exampleLink'):
                    artifact['exampleLink'] = research_data[num]['exampleLink']
                    updates_count += 1

print(f"Added {updates_count} links to artifacts")

# Convert back to JSON
updated_json_str = json.dumps(artifacts_array, indent=4, ensure_ascii=False)

# Remove the outer brackets we added
updated_json_str = updated_json_str[1:-1]

# Reconstruct the HTML
new_html = html_content[:match.start()] + before + updated_json_str + after + html_content[match.end():]

# Write the updated HTML
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(new_html)

print("Successfully updated index.html")
