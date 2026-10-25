import random
import string
import re
import sys
import json
import os
from colorama import Fore, Style, init
from models import VaultItem
from file_manager import save_vault, load_vault
from cryptography.fernet import Fernet


MASTER_CONFIG_FILE = "master_auth.json"
KEY_FILENAME = "secret.key"

def get_cipher():
    
    if os.path.exists(KEY_FILENAME):
        with open(KEY_FILENAME, "rb") as key_file:
            key = key_file.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_FILENAME, "wb") as key_file:
            key_file.write(key)
    return Fernet(key)

def authenticate_user():
    
    cipher = get_cipher()
    
   
    if not os.path.exists(MASTER_CONFIG_FILE):
        print(Fore.CYAN + "\n" + "="*50)
        print(Fore.CYAN + "       🛡️ SECURE SETUP: CREATE MASTER ACCOUNT       ")
        print(Fore.CYAN + "="*50)
        
        while True:
            username = input(Fore.WHITE + "👤 Enter a new Master Username: ").strip()
            if username:
                break
            print(Fore.RED + "❌ Username cannot be empty. Please try again.")
            
        while True:
            password = input(Fore.WHITE + "🔑 Enter a strong Master Password (min 4 chars): ").strip()
            if len(password) >= 4:
                break
            print(Fore.RED + "❌ Password is too short. Must be at least 4 characters.")
            
        
        auth_data = {"username": username, "password": password}
        json_data = json.dumps(auth_data, ensure_ascii=False, indent=4)
        encrypted_data = cipher.encrypt(json_data.encode('utf-8'))
        
        with open(MASTER_CONFIG_FILE, "wb") as f:
            f.write(encrypted_data)
            
        print(Fore.GREEN + "\n✨ Encrypted Master account created successfully! Let's log in now.\n")

    
    try:
        with open(MASTER_CONFIG_FILE, "rb") as f:
            encrypted_data = f.read()
            decrypted_data = cipher.decrypt(encrypted_data)
            auth_data = json.loads(decrypted_data.decode('utf-8'))
    except Exception as e:
        print(Fore.RED + f"❌ Error loading authentication data: {e}")
        sys.exit()
        
    print(Fore.CYAN + "\n" + "="*50)
    print(Fore.CYAN + "               🔒 SECURE MASTER LOGIN               ")
    print(Fore.CYAN + "="*50)
    
    attempts = 3
    while attempts > 0:
        username_input = input(Fore.WHITE + "👤 Master Username: ").strip()
        password_input = input(Fore.WHITE + "🔑 Master Password: ").strip()
        
        if username_input == auth_data["username"] and password_input == auth_data["password"]:
            print(Fore.GREEN + "\n" + "—"*50)
            print(Fore.GREEN + "  ✅ Access Granted! Welcome to your Secure Vault.")
            print(Fore.GREEN + "—"*50 + "\n")
            return True
        else:
            attempts -= 1
            print(Fore.RED + f"❌ Incorrect username or password! Attempts left: {attempts}\n")
            
    print(Fore.RED + "⛔ Too many failed login attempts. Exiting program for security.")
    sys.exit()

def generate_strong_password(length=12):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(random.choice(chars) for _ in range(length))
def check_password_strength(password):
    if len(password) < 6:
        return Fore.RED + "Weak 🔴 (Too short)"
    
    score = 0
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if any(c.islower() for c in password) and any(c.isupper() for c in password):
        score += 1
    if any(c.isdigit() for c in password):
        score += 1
    if any(c in "!@#$%^&*()" for c in password):
        score += 1

    if score <= 2:
        return Fore.RED + "Weak 🔴"
    elif score <= 4:
        return Fore.YELLOW + "Medium 🟡"
    else:
        return Fore.GREEN + "Strong 🟢"

def print_header(title):
    print(Fore.CYAN + Style.BRIGHT + "\n" + "=" * 50)
    print(Fore.CYAN + Style.BRIGHT + f"   {title}")
    print(Fore.CYAN + Style.BRIGHT + "=" * 50)

def show_menu():
    print_header("🔐 PERSONAL PASSWORD MANAGER")
    print(Fore.YELLOW + " 1. " + Fore.WHITE + "View All Accounts (Secure View)")
    print(Fore.YELLOW + " 2. " + Fore.WHITE + "Add New Credential")
    print(Fore.YELLOW + " 3. " + Fore.WHITE + "Search Password by Site")
    print(Fore.YELLOW + " 4. " + Fore.WHITE + "Vault Statistics & Dashboard 📊")
    print(Fore.YELLOW + " 5. " + Fore.WHITE + "Update / Edit Credential ✏️") 
    print(Fore.YELLOW + " 6. " + Fore.WHITE + "Delete Account")             
    print(Fore.YELLOW + " 7. " + Fore.RED + "Exit")                       
    print(Fore.CYAN + "-" * 50)

def main():
    vault_items = load_vault()

    while True:
        show_menu()
        
        try:
            choice = int(input(Fore.GREEN + "Choose an option (1-7): " + Style.RESET_ALL))
        except ValueError:
            print(Fore.RED + "❌ Invalid input! Please enter a number between 1 and 7.")
            continue

        if choice == 1:
            print_header("📋 SAVED ACCOUNTS")
            if not vault_items:
                print(Fore.YELLOW + "📭 Your vault is empty.")
            else:
                for index, item in enumerate(vault_items, start=1):
                    print(f"{Fore.MAGENTA}{index}. {Fore.BLUE}Site: {Fore.WHITE}{item.site_name:<10} {Fore.BLUE}| User: {Fore.WHITE}{item.username:<20} {Fore.BLUE}| Password: {Fore.YELLOW}{item.get_masked_password()}")

        elif choice == 2:
            print_header("➕ ADD NEW CREDENTIAL")
            print(Fore.LIGHTBLACK_EX + "💡 Type 'b' at any step to go back one step.")
            
            POPULAR_SITES = ["Gmail", "GitHub", "Twitter", "Discord", "LinkedIn"]
            
            site = ""
            username = ""
            password = ""
            
            step = 1
            while step <= 3:
                if step == 1:
                    print(Fore.CYAN + "\nSelect a site/app:")
                    for i, site_option in enumerate(POPULAR_SITES, start=1):
                        print(f"{Fore.YELLOW} {i}. {Fore.WHITE}{site_option}")
                    print(f"{Fore.YELLOW} {len(POPULAR_SITES) + 1}. {Fore.WHITE}Other (Type manually...)")
                    print(f"{Fore.YELLOW} b. {Fore.RED}Back to Main Menu")

                    site_input = input(Fore.GREEN + "Choose option or type 'b': " + Style.RESET_ALL).strip()
                    if site_input.lower() == 'b':
                        break
                    
                    try:
                        site_choice = int(site_input)
                        if 1 <= site_choice <= len(POPULAR_SITES):
                            site = POPULAR_SITES[site_choice - 1]
                            step = 2
                        else:
                            custom_site = input(Fore.WHITE + "Enter custom site/app name (or 'b' to back): ").strip()
                            if custom_site.lower() == 'b':
                                continue
                            site = custom_site
                            step = 2
                    except ValueError:
                        if site_input.lower() == 'b':
                            break
                        site = site_input
                        step = 2

                elif step == 2:
                    user_input = input(Fore.WHITE + "Enter valid email (type 'b' to go back): ").strip()
                    if user_input.lower() == 'b':
                        step = 1
                        continue
                    
                    
                    if "@" in user_input and "." in user_input and len(user_input) > 5:
                        username = user_input
                        step = 3
                    else:
                        print(Fore.RED + "❌ Invalid email format! Please enter a valid email (e.g., name@example.com).")
                        

                elif step == 3:
                    print(Fore.CYAN + "\nPassword Options:")
                    print(" 1. Enter password manually")
                    print(" 2. Generate a strong random password automatically 🤖")
                    print(" b. Back (Change Username)")
                    
                    pwd_input = input(Fore.GREEN + "Choose option (1-2) or 'b': " + Style.RESET_ALL).strip()
                    if pwd_input.lower() == 'b':
                        step = 2
                        continue

                    try:
                        pwd_choice = int(pwd_input)
                    except ValueError:
                        pwd_choice = 1

                    if pwd_choice == 2:
                        password = generate_strong_password()
                        print(Fore.GREEN + f"🔑 Generated Strong Password: {Style.BRIGHT}{password}")
                        break
                    else:
                        pass_input = input(Fore.WHITE + "Enter password (or 'b' to back): ").strip()
                        if pass_input.lower() == 'b':
                            continue
                        strength = check_password_strength(pass_input)
                        print(Fore.CYAN + f"📊 Password Strength: {strength}")
                        password = pass_input
                        break

            if site and username and password:
                new_item = VaultItem(site, username, password)
                vault_items.append(new_item)
                save_vault(vault_items)
                print(Fore.GREEN + f"✅ Credentials for '{site}' added successfully!")

        elif choice == 3:
            print_header("🔍 ADVANCED SEARCH")
            query = input(Fore.WHITE + "Enter site name or part of it (type 'b' to go back): ").strip().lower()
            if query == 'b':
                continue
            
            found = False
            for item in vault_items:
                if query in item.site_name.lower():
                    print(Fore.GREEN + f"\n🌐 Site: {Fore.WHITE}{item.site_name}")
                    print(Fore.GREEN + f"👤 Username: {Fore.WHITE}{item.username}")
                    print(Fore.GREEN + f"🔑 Password: {Fore.YELLOW}{Style.BRIGHT}{item.password}")
                    found = True
            if not found:
                print(Fore.RED + "❌ No matching account found.")

        elif choice == 4:
            print_header("📊 VAULT DASHBOARD")
            total_accounts = len(vault_items)
            sites = sorted(list(set(item.site_name.strip().capitalize() for item in vault_items)))
            
            print(Fore.YELLOW + f"📌 Total Saved Accounts : {Fore.WHITE}{total_accounts}")
            if total_accounts > 0:
                print(Fore.YELLOW + f"🌐 Unique Sites Managed : {Fore.WHITE}{', '.join(sites)}")
                print(Fore.GREEN + f"🛡️  Security Status     : ACTIVE (Masked & Protected)")
            else:
                print(Fore.LIGHTBLACK_EX + "💡 Tip: Add some accounts to view active analytics.")

        elif choice == 5:
            print_header("✏️ UPDATE CREDENTIAL")
            if not vault_items:
                print(Fore.YELLOW + "📭 No accounts available to update.")
                continue
            
            for index, item in enumerate(vault_items, start=1):
                print(f"{Fore.MAGENTA}{index}. {Fore.WHITE}{item.site_name} ({item.username})")
            print(Fore.RED + " b. Cancel / Go Back")
            
            upd_input = input(Fore.GREEN + "Enter the number to update (or 'b' to back): " + Style.RESET_ALL).strip()
            if upd_input.lower() == 'b':
                continue

            try:
                idx = int(upd_input) - 1
                if 0 <= idx < len(vault_items):
                    item = vault_items[idx]
                    print(Fore.CYAN + f"\nEditing account for: {item.site_name}")
                    print(Fore.LIGHTBLACK_EX + "💡 Press Enter to keep the old value without changes.")
                    
                    new_user = input(Fore.WHITE + f"New username [{item.username}]: ").strip()
                    if new_user:
                        item.username = new_user
                        
                    new_pass = input(Fore.WHITE + "New password (leave blank to keep old): ").strip()
                    if new_pass:
                        item.password = new_pass
                        
                    save_vault(vault_items)
                    print(Fore.GREEN + f"✅ Account for '{item.site_name}' updated successfully!")
                else:
                    print(Fore.RED + "❌ Invalid account number.")
            except ValueError:
                print(Fore.RED + "❌ Please enter a valid number.")

        elif choice == 6:
            print_header("🗑️ DELETE ACCOUNT")
            if not vault_items:
                print(Fore.YELLOW + "📭 No accounts available to delete.")
                continue
            
            for index, item in enumerate(vault_items, start=1):
                print(f"{Fore.MAGENTA}{index}. {Fore.WHITE}{item.site_name} ({item.username})")
            print(Fore.RED + " b. Cancel / Go Back")
            
            del_input = input(Fore.RED + "Enter the number to delete (or 'b' to back): " + Style.RESET_ALL).strip()
            if del_input.lower() == 'b':
                continue

            try:
                idx = int(del_input) - 1
                if 0 <= idx < len(vault_items):
                    removed = vault_items.pop(idx)
                    save_vault(vault_items)
                    print(Fore.GREEN + f"🗑️ Account for '{removed.site_name}' deleted successfully!")
                else:
                    print(Fore.RED + "❌ Invalid account number.")
            except ValueError:
                print(Fore.RED + "❌ Please enter a valid number.")

        elif choice == 7:
            print(Fore.CYAN + Style.BRIGHT + "\n👋 Exiting Password Manager. Stay secure!")
            break

if __name__ == "__main__":
    authenticate_user()
    main()