import os
import yaml
import re
from datetime import datetime, date, timedelta
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from engine.parsing.markdown_ast import parse_frontmatter, parse_date

def check_waiver_expiry():
    adr_dir = os.path.join(os.path.dirname(__file__), '..', '05-decisions')
    has_errors = False
    warning_days = 30

    print("Checking active waiver ADRs for expiration...")

    for root, _, files in os.walk(adr_dir):
        for file in files:
            if file.endswith('.md') and file.upper() != 'INDEX.md':
                file_path = os.path.join(root, file)
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                match = re.search(r'^---\s+(.*?)\s+---', content, re.DOTALL)
                if match:
                    try:
                        frontmatter = yaml.safe_load(match.group(1))
                        doc_meta = frontmatter.get('doc_meta', {})
                    except Exception:
                        continue
                        
                    adr_type = doc_meta.get('adr_type')
                    status = doc_meta.get('status')
                    
                    if adr_type == 'exception' and status == 'accepted':
                        exception_info = doc_meta.get('exception_info', {})
                        expiry_date_raw = exception_info.get('expiry_date')
                        if expiry_date_raw:
                            expiry_date = parse_date(expiry_date_raw)
                            if expiry_date:
                                today = date.today()
                                delta = (expiry_date - today).days
                                
                                rel_path = os.path.relpath(file_path, os.path.dirname(__file__)).replace('\\', '/')
                                
                                if delta < 0:
                                    print(f"[CRITICAL] Expired waiver: {rel_path} expired on {expiry_date} ({abs(delta)} days ago)")
                                    has_errors = True
                                elif delta <= warning_days:
                                    print(f"[WARNING] Expiring soon: {rel_path} expires in {delta} days on {expiry_date}")
                            else:
                                print(f"[ERROR] Invalid expiry_date format in {file}: {expiry_date_raw}")
                                has_errors = True

    if has_errors:
        print("\n[FAIL] Expiry check failed due to expired waivers.")
        sys.exit(1)
    else:
        print("\n[PASS] No expired waivers found.")
        sys.exit(0)

if __name__ == "__main__":
    check_waiver_expiry()
