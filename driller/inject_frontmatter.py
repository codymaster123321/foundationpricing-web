import os
import re

frontmatter_path = r'g:\0_RAFAL\Antigravity\subterra-project\deep_research_knowledge_base_reports\frontmatter.md'
kb_dir = r'g:\0_RAFAL\Antigravity\subterra-project\injector\src\data\knowledge-base'

with open(frontmatter_path, 'r', encoding='utf-8') as f:
    fm_content = f.read()

blocks = re.findall(r'(---.*?title:\s*\"(.*?)\".*?---)', fm_content, re.DOTALL)

def normalize(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())

matched_count = 0

for filename in os.listdir(kb_dir):
    if not filename.endswith('.md'):
        continue
    file_path = os.path.join(kb_dir, filename)
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    file_title = None
    # 1. Try to extract title from existing frontmatter if any
    m_fm_title = re.search(r'^title:\s*\"(.*?)\"', content, re.MULTILINE)
    if m_fm_title:
        file_title = m_fm_title.group(1).strip()
        
    # 2. Try to extract from the first H1
    if not file_title:
        m_h1 = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if m_h1:
            file_title = m_h1.group(1).strip()
            # remove formatting if any
            file_title = file_title.replace('*', '')

    if not file_title:
        print(f'NO TITLE: {filename}')
        continue
        
    norm_file_title = normalize(file_title)
    
    matched_fm = None
    for fm_text, title_string in blocks:
        if normalize(title_string) == norm_file_title:
            matched_fm = fm_text
            break
            
    if not matched_fm:
        print(f'NO MATCH: {filename} -> {file_title}')
        continue
        
    # Check if starts with ---
    if content.startswith('---'):
        end_idx = content.find('---', 3)
        if end_idx != -1:
             content = content[end_idx+3:].lstrip()
             
    new_content = matched_fm.strip() + '\n\n' + content.lstrip()
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f'OK: {filename}')
    matched_count += 1

print(f'\nTotal matched and updated: {matched_count}')
