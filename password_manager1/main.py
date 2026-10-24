import random
import string
from colorama import Fore, Style, init
from models import VaultItem
from file_manager import save_vault, load_vault

init(autoreset=True)
def generate_strong_password(length=12):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(random.choice(chars) for _ in range(length))
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
    print(Fore.YELLOW + " 5. " + Fore.WHITE + "Delete Account")
    print(Fore.YELLOW + " 6. " + Fore.RED + "Exit")
    print(Fore.CYAN + "-" * 50)
def main():
    vault_items = load_vault()

    while True:
        show_menu()
        
        try:
            choice = int(input(Fore.GREEN + "Choose an option (1-6): " + Style.RESET_ALL))
        except ValueError:
            print(Fore.RED + "❌ Invalid input! Please enter a number between 1 and 6.")
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
                    user_input = input(Fore.WHITE + "Enter username or email (type 'b' to go back): ").strip()
                    if user_input.lower() == 'b':
                        step = 1
                        continue
                    if user_input:
                        username = user_input
                        step = 3

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
            sites = list(set([item.site_name.capitalize() for item in vault_items]))
            
            print(Fore.YELLOW + f"📌 Total Saved Accounts : {Fore.WHITE}{total_accounts}")
            if total_accounts > 0:
                print(Fore.YELLOW + f"🌐 Unique Sites Managed : {Fore.WHITE}{', '.join(sites)}")
                print(Fore.GREEN + f"🛡️  Security Status     : ACTIVE (Masked & Protected)")
            else:
                print(Fore.LIGHTBLACK_EX + "💡 Tip: Add some accounts to view active analytics.")

        elif choice == 5:
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

        elif choice == 6:
            print(Fore.CYAN + Style.BRIGHT + "\n👋 Exiting Password Manager. Stay secure!")
            break
if __name__ == "__main__":
    main()