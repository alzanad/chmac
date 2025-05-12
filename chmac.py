#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import re
import random
import os
import sys
from time import sleep
from colorama import init, Fore, Style

# تهيئة colorama
init(autoreset=True)

class ChMod:
    def __init__(self):
        self.check_root()
        self.clear_screen()
        self.show_header()
        self.interfaces = self.detect_interfaces()

    def clear_screen(self):
        os.system('clear' if os.name == 'posix' else 'cls')

    def check_root(self):
        if os.geteuid() != 0:
            self.print_error("يلزم تشغيل البرنامج بصلاحيات المدير (root)")
            self.print_info("يرجى تشغيل البرنامج باستخدام الأمر:\n sudo python3 chmac.py")
            sys.exit(1)

    def show_header(self):
        title = "أداة تغيير عنوان الماك المتقدم"
        line = "=" * len(title)
        print(Fore.CYAN + Style.BRIGHT + line)
        print(Fore.YELLOW + Style.BRIGHT + title)
        print(Fore.CYAN + Style.BRIGHT + line + "\n")

    def print_success(self, message):
        print(Fore.GREEN + Style.BRIGHT + "[✓] " + message)

    def print_error(self, message):
        print(Fore.RED + Style.BRIGHT + "[✗] " + message)

    def print_info(self, message):
        print(Fore.BLUE + Style.BRIGHT + "[i] " + message)

    def print_warning(self, message):
        print(Fore.YELLOW + Style.BRIGHT + "[!] " + message)

    def detect_interfaces(self):
        try:
            result = subprocess.check_output(['ip', '-o', 'link', 'show'], stderr=subprocess.PIPE).decode('utf-8')
            return [line.split(':')[1].strip() for line in result.splitlines() if 'LOOPBACK' not in line]
        except Exception as e:
            self.print_error(f"خطأ في اكتشاف واجهات الشبكة: {str(e)}")
            return []

    def get_interface_info(self, interface):
        try:
            result = subprocess.check_output(['ip', 'link', 'show', interface], stderr=subprocess.PIPE).decode('utf-8')
            mac_match = re.search(r'link/ether\s+([0-9a-fA-F:]{17})', result)
            mac = mac_match.group(1) if mac_match else "غير معروف"
            return mac
        except subprocess.CalledProcessError:
            return "غير معروف"


    def show_interfaces_menu(self):
        if not self.interfaces:
            self.print_error("لم يتم العثور على واجهات شبكية متاحة")
            sys.exit(1)

        print(Fore.MAGENTA + Style.BRIGHT + "\nواجهات الشبكة المتاحة:\n")
        for i, iface in enumerate(self.interfaces, 1):
            mac = self.get_interface_info(iface)
            print(f"{Fore.CYAN}{i}. {Fore.YELLOW}{iface} ")
            print(f"   {Fore.WHITE}عنوان MAC: {mac}\n")
        print(f"{Fore.CYAN}0. {Fore.YELLOW}كل الواجهات\n")


    def select_interface(self):
        while True:
            try:
                choice = input(f"\n{Fore.BLUE}اختر رقم الواجهة (0-{len(self.interfaces)}): {Fore.WHITE}")
                iface_index = int(choice)
                if choice == '0':
                     return self.interfaces
                elif 0 < iface_index <= len(self.interfaces):
                    return [self.interfaces[iface_index -1]] # Return as a list for consistency
                self.print_warning("الرقم خارج النطاق، يرجى المحاولة مرة أخرى")
            except ValueError:
                self.print_warning("إدخال غير صالح، يرجى إدخال رقم")



    def generate_random_mac(self):
        return "02:%02x:%02x:%02x:%02x:%02x" % (
            random.randint(0x00, 0xff),
            random.randint(0x00, 0xff),
            random.randint(0x00, 0xff),
            random.randint(0x00, 0xff),
            random.randint(0x00, 0xff)
        )

    def change_mac(self, interface, new_mac):
        try:
            subprocess.call(['ip', 'link', 'set', 'dev', interface, 'down'])
            subprocess.call(['ip', 'link', 'set', 'dev', interface, 'address', new_mac])
            subprocess.call(['ip', 'link', 'set', 'dev', interface, 'up'])
            sleep(1) # Reduced sleep time
            return True
        except Exception as e:
            self.print_error(f"خطأ في تغيير عنوان MAC: {str(e)}")
            return False


    def run(self):
        self.show_interfaces_menu()
        selected_interfaces = self.select_interface()

        for interface in selected_interfaces:
            current_mac = self.get_interface_info(interface)
            new_mac = self.generate_random_mac()

            print(f"\n{Fore.YELLOW}الواجهة: {interface}")
            print(f"{Fore.BLUE}عنوان MAC القديم: {current_mac}")

            if self.change_mac(interface, new_mac):
                print(f"{Fore.GREEN}عنوان MAC الجديد: {new_mac}\n")


if __name__ == "__main__":
    try:
        mac_changer = ChMod()
        mac_changer.run()
    except KeyboardInterrupt:
        print(Fore.RED + "\nتم إيقاف البرنامج بواسطة المستخدم")
        sys.exit(0)
    except Exception as e:
        print(Fore.RED + f"\nحدث خطأ غير متوقع: {str(e)}")
        sys.exit(1)
