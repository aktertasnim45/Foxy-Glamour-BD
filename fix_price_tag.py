path = r'i:\FGBDgithub\Foxy-Glamour-BD\store\templates\store\product_detail.html'

with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = 0
for i, line in enumerate(lines):
    if skip > 0:
        skip -= 1
        continue
        
    # Detect the messy start
    if '<p class="pdp-original-price"' in line and 'TK. {{' in line:
        # Check if next line continues it
        if i+2 < len(lines):
            # This looks like the split block
            # Construct the clean line
            new_lines.append(
                '            <p class="pdp-original-price" style="text-decoration: line-through; color: #999; font-size: 0.9rem; margin: 0;">TK. {{ product.price|floatformat:0 }}</p>\n'
            )
            skip = 2 # Skip the next 2 messy lines
            print("Found and fixed split price tag block.")
        else:
            new_lines.append(line)
    else:
        new_lines.append(line)

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
