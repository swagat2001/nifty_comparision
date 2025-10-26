"""
FIX SYNTAX ERRORS IN validated_tickers.py
Fixes apostrophe issues in company names
"""
import re


def fix_syntax_errors():
    """Fix syntax errors in validated_tickers.py"""
    
    print("\n" + "="*80)
    print("FIXING SYNTAX ERRORS IN validated_tickers.py")
    print("="*80 + "\n")
    
    try:
        with open('validated_tickers.py', 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        print("❌ Could not read validated_tickers.py")
        return
    
    # Backup first
    try:
        with open('validated_tickers_BEFORE_FIX.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("✓ Backup created: validated_tickers_BEFORE_FIX.py")
    except:
        pass
    
    # Count initial errors
    initial_errors = content.count("'") - content.count("\\'")
    
    # Fix apostrophes in company names
    # Pattern: 'COMPANY'S NAME': 'TICKER',
    # Should be: 'COMPANY\'S NAME': 'TICKER',
    
    fixes_made = 0
    
    # Find all lines with dictionary entries
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        original_line = line
        
        # Check if it's a dictionary entry line
        if "': '" in line and line.strip().startswith("'"):
            # Count apostrophes
            parts = line.split("': '")
            
            if len(parts) >= 2:
                # First part is the key (company name)
                key_part = parts[0]
                
                # If key has unescaped apostrophes (other than the opening one)
                # We need to escape them
                if key_part.count("'") > 1:  # More than just the opening quote
                    # Find apostrophes that aren't at the start
                    # and aren't already escaped
                    fixed_key = key_part[0]  # Keep first quote
                    
                    for i in range(1, len(key_part)):
                        char = key_part[i]
                        if char == "'" and key_part[i-1] != "\\":
                            # This is an unescaped apostrophe - escape it
                            fixed_key += "\\'"
                            fixes_made += 1
                        else:
                            fixed_key += char
                    
                    # Reconstruct line
                    line = fixed_key + "': '" + "': '".join(parts[1:])
        
        fixed_lines.append(line)
    
    fixed_content = '\n'.join(fixed_lines)
    
    # Write fixed content
    try:
        with open('validated_tickers.py', 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        print(f"✓ Fixed {fixes_made} syntax errors")
    except Exception as e:
        print(f"❌ Error writing file: {e}")
        return
    
    # Verify the fix by trying to import
    print("\nVerifying fix...")
    try:
        # Try to compile it
        compile(fixed_content, 'validated_tickers.py', 'exec')
        print("✓ File syntax is now valid!")
    except SyntaxError as e:
        print(f"⚠️  Still has syntax error: {e}")
        print("   Manual fix required")
        return
    
    print("\n" + "="*80)
    print("✅ FIX COMPLETE!")
    print("="*80)
    print("\nvalidated_tickers.py has been fixed")
    print("You can now run: python main.py")
    print("="*80 + "\n")


if __name__ == "__main__":
    fix_syntax_errors()