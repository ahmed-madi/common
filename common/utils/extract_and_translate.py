#!/usr/bin/env python3
"""
Extract field labels from Frappe DocType JSON files and generate Arabic translations.
"""

import json
import re
from pathlib import Path
from typing import Dict, Set
from deep_translator import GoogleTranslator

# Base directory to search for JSON files
BASE_DIR = Path(__file__).parent

def extract_labels_from_json(json_path: Path) -> tuple[Set[str], Dict[str, str], str]:
    """Extract all label values, Select field options, and DocType name from a JSON file.
    
    Returns:
        tuple: (set of labels, dict mapping field labels to their options string, doctype name)
    """
    labels = set()
    select_options = {}
    doctype_name = ""
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract DocType name
        if 'name' in data and isinstance(data['name'], str):
            doctype_name = data['name']
        
        # Extract labels and options from fields array
        if 'fields' in data and isinstance(data['fields'], list):
            for field in data['fields']:
                if isinstance(field, dict):
                    # Extract label
                    if 'label' in field:
                        label = field['label']
                        if label and isinstance(label, str):
                            labels.add(label)
                    
                    # Extract Select field options
                    if field.get('fieldtype') == 'Select' and 'options' in field:
                        options = field['options']
                        if options and isinstance(options, str) and '\n' in options:
                            field_label = field.get('label', field.get('fieldname', ''))
                            select_options[field_label] = options
    
    except Exception as e:
        print(f"Error processing {json_path}: {e}")
    
    return labels, select_options, doctype_name

def extract_workspace_labels(json_path: Path) -> tuple[Set[str], str]:
    """Extract labels from Workspace JSON files.
    
    Extracts:
    - label (workspace label)
    - shortcuts[].label (shortcut labels)
    - quick_lists[].label (quick list labels)
    
    Returns:
        tuple: (set of labels, workspace name)
    """
    labels = set()
    workspace_name = ""
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract workspace name
        if 'name' in data and isinstance(data['name'], str):
            workspace_name = data['name']
        
        # Extract workspace label
        if 'label' in data and isinstance(data['label'], str) and data['label']:
            labels.add(data['label'])
        
        # Extract shortcut labels
        if 'shortcuts' in data and isinstance(data['shortcuts'], list):
            for shortcut in data['shortcuts']:
                if isinstance(shortcut, dict) and 'label' in shortcut:
                    label = shortcut['label']
                    if label and isinstance(label, str):
                        labels.add(label)
        
        # Extract quick_list labels
        if 'quick_lists' in data and isinstance(data['quick_lists'], list):
            for quick_list in data['quick_lists']:
                if isinstance(quick_list, dict) and 'label' in quick_list:
                    label = quick_list['label']
                    if label and isinstance(label, str):
                        labels.add(label)
    
    except Exception as e:
        print(f"Error processing workspace {json_path}: {e}")
    
    return labels, workspace_name


def extract_translatable_strings_from_python(py_path: Path) -> Set[str]:
    """Extract translatable strings from _() function calls in Python files.
    
    Extracts strings from patterns like:
    - _("text")
    - _('text')
    - frappe._("text")
    
    Returns:
        set: Set of translatable strings
    """
    strings = set()
    
    try:
        with open(py_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern to match _("...") or _('...')
        # This handles both single and double quotes
        # Pattern explanation:
        # (?:frappe\.)? - Optional "frappe." prefix
        # _ - The underscore function
        # \( - Opening parenthesis
        # (["\']) - Capture quote type (single or double)
        # ((?:(?!\1).)*) - Capture everything until the matching quote (non-greedy)
        # \1 - Match the same quote type that was captured
        # \) - Closing parenthesis
        pattern = r'(?:frappe\.)?_\((["\'])((?:(?!\1).)*)\1\)'
        
        matches = re.findall(pattern, content)
        
        for quote_type, text in matches:
            if text and text.strip():
                # Unescape common escape sequences
                text = text.replace(r'\"', '"').replace(r"\'", "'")
                text = text.replace(r'\n', '\n').replace(r'\t', '\t')
                strings.add(text.strip())
    
    except Exception as e:
        print(f"Error processing Python file {py_path}: {e}")
    
    return strings



def translate_to_arabic(text: str) -> str:
    """Translate English text to Arabic using professional translation service.
    
    Uses MyMemoryTranslator which provides more contextually accurate translations
    for professional HR terminology.
    """
    try:
        # Try MyMemoryTranslator first for better quality
        from deep_translator import MyMemoryTranslator
        translator = MyMemoryTranslator(source='en', target='ar')
        translation = translator.translate(text)
        
        # If MyMemoryTranslator fails, fallback to GoogleTranslator
        if not translation or translation == text:
            translator = GoogleTranslator(source='en', target='ar')
            translation = translator.translate(text)
            
        return translation if translation else text
    except Exception as e:
        # Final fallback to GoogleTranslator
        try:
            translator = GoogleTranslator(source='en', target='ar')
            translation = translator.translate(text)
            return translation if translation else text
        except Exception as e2:
            print(f"Translation error for '{text}': {e}, {e2}")
            return text

def process_json_files(all_translations: Dict[str, str]):
    """Process all DocType JSON files and collect translations."""
    
    # Find all JSON files recursively
    json_files = list(BASE_DIR.rglob('*.json'))
    # Exclude workspace files
    json_files = [f for f in json_files if 'workspace' not in str(f)]
    
    print(f"Found {len(json_files)} DocType JSON files")
    
    processed_count = 0
    
    for json_path in json_files:
        # Extract labels, select options, and doctype name from this file
        labels, select_options, doctype_name = extract_labels_from_json(json_path)
        
        if not labels and not select_options and not doctype_name:
            continue
        
        print(f"\nProcessing: {json_path.relative_to(BASE_DIR)}")
        print(f"  Found {len(labels)} unique labels")
        
        # Translate DocType name
        if doctype_name and doctype_name not in all_translations:
            doctype_translation = translate_to_arabic(doctype_name)
            all_translations[doctype_name] = doctype_translation
            print(f"  DocType: {doctype_name} → {doctype_translation}")
        
        # Translate labels
        for label in sorted(labels):
            if label not in all_translations:
                arabic_translation = translate_to_arabic(label)
                all_translations[label] = arabic_translation
                print(f"  {label} → {arabic_translation}")
        
        # Translate Select field options
        if select_options:
            print(f"  Found {len(select_options)} Select fields with options")
            
            for field_label, options_string in select_options.items():
                # Split options by newline
                options_list = [opt.strip() for opt in options_string.split('\n') if opt.strip()]
                
                # Translate each option and add to translations as key-value pairs
                for option in options_list:
                    if option not in all_translations:
                        translated_option = translate_to_arabic(option)
                        all_translations[option] = translated_option
                        print(f"    {field_label} option: {option} → {translated_option}")
        
        processed_count += 1
    
    print(f"\n{'='*60}")
    print("DocType processing complete!") 
    print(f"Processed {processed_count} files with field labels")
    print(f"{'='*60}")


def process_workspace_files(all_translations: Dict[str, str]):
    """Process all workspace JSON files and collect translations."""
    
    # Find all workspace JSON files
    workspace_files = list(BASE_DIR.rglob('workspace/**/*.json'))
    print(f"Found {len(workspace_files)} workspace files")
    
    processed_count = 0
    
    for json_path in workspace_files:
        # Extract labels from workspace file
        labels, workspace_name = extract_workspace_labels(json_path)
        
        if not labels and not workspace_name:
            continue
        
        print(f"\nProcessing workspace: {json_path.relative_to(BASE_DIR)}")
        print(f"  Found {len(labels)} unique labels")
        
        # Translate workspace name
        if workspace_name and workspace_name not in all_translations:
            workspace_translation = translate_to_arabic(workspace_name)
            all_translations[workspace_name] = workspace_translation
            print(f"  Workspace: {workspace_name} → {workspace_translation}")
        
        # Translate labels
        for label in sorted(labels):
            if label not in all_translations:
                arabic_translation = translate_to_arabic(label)
                all_translations[label] = arabic_translation
                print(f"  {label} → {arabic_translation}")
        
        processed_count += 1
    
    print(f"\n{'='*60}")
    print("Workspace processing complete!")
    print(f"Processed {processed_count} workspace files")
    print(f"{'='*60}")



def process_python_files(all_translations: Dict[str, str]):
    """Process all Python files and extract translatable strings from _() function calls."""
    
    # Find all Python files
    python_files = list(BASE_DIR.rglob('**/*.py'))
    # Exclude this script itself and any __pycache__ directories
    python_files = [f for f in python_files if '__pycache__' not in str(f) and f.name != 'extract_and_translate.py']
    
    print(f"Found {len(python_files)} Python files")
    
    # Collect all translatable strings from all Python files
    all_strings = set()
    files_with_strings = 0
    
    for py_path in python_files:
        strings = extract_translatable_strings_from_python(py_path)
        
        if strings:
            files_with_strings += 1
            all_strings.update(strings)
            print(f"  {py_path.relative_to(BASE_DIR)}: Found {len(strings)} translatable strings")
    
    if not all_strings:
        print("No translatable strings found in Python files")
        return
    
    print(f"Total unique translatable strings: {len(all_strings)}")
    print(f"Files with translatable strings: {files_with_strings}")
    
    # Add translations to the shared dictionary
    print("Translating strings...")
    for text in sorted(all_strings):
        if text not in all_translations:
            arabic_translation = translate_to_arabic(text)
            all_translations[text] = arabic_translation
            print(f"  {text} → {arabic_translation}")
    
    print("Python strings processing complete!")






if __name__ == '__main__':
    print("Starting Arabic translation generation...")
    print(f"Base directory: {BASE_DIR}")
    
    # Create a shared dictionary to collect all translations
    all_translations = {}
    
    # Process DocType JSON files
    print("Processing DocType JSON files...")
    process_json_files(all_translations)
    
    # Process Workspace JSON files
    print("Processing Workspace JSON files...")
    process_workspace_files(all_translations)
    
    # Process Python files for _() function calls
    print("Processing Python files for _() calls...")
    process_python_files(all_translations)
    
    # Sort translations alphabetically and write to single file
    print("Writing translations to file...")
    
    sorted_translations = dict(sorted(all_translations.items()))
    output_path = BASE_DIR / 'translations_ar.json'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sorted_translations, f, ensure_ascii=False, indent=2)
    
    print("✅ Translation generation complete!")
    print(f"Total unique translations: {len(sorted_translations)}")
    print(f"Output file: {output_path.relative_to(BASE_DIR)}")

