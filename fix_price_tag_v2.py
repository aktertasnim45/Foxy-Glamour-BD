path = r'i:\FGBDgithub\Foxy-Glamour-BD\store\templates\store\product_detail.html'

with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
i = 0
found = False
while i < len(lines):
    line = lines[i]
    # Check for the start of the bad block (loose check)
    if 'pdp-original-price' in line and (i + 2 < len(lines)):
        # Look ahead 2 lines
        l1 = line
        l2 = lines[i+1]
        l3 = lines[i+2]
        
        # Heuristic: if it spans 3 lines and has {{ in the middle one
        if 'pdp-original-price' in l1 and 'TK. {{' in l2 and '}}</p>' in l3:
            # Replace with single line
            new_lines.append('            <p class="pdp-original-price" style="text-decoration: line-through; color: #999; font-size: 0.9rem; margin: 0;">TK. {{ product.price|floatformat:0 }}</p>\n')
            i += 3
            found = True
            continue
    
    new_lines.append(line)
    i += 1

if found:
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("FIXED: Replaced multi-line price tag.")
else:
    print("FAILED: Could not find pattern.")
