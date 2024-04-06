import sys
import time
from colorama import Fore, Style

def type_text(text, delay=0.01):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)

def display_logo_and_intro():
    logo = f"""
{Fore.YELLOW}
 __     __   __     __   __   ______     ______     ______   ______     __  __     ______     ______     _____    
/\\ \\   /\\ "-.\\ \\   /\\ \\ / /  /\\  ___\\   /\\  ___\\   /\\__  _\\ /\\  ___\\   /\\ \\/\\ \\   /\\  __ \\   /\\  == \\   /\\  __-.  
\\ \\ \\  \\ \\ \\-.  \\  \\ \\ \\' /   \\ \\  __\\   \\ \\___  \\  \\/_/\\ \\/ \\ \\  __\\   \\ \\ \\_\\ \\  \\ \\  __ \\  \\ \\  __<   \\ \\ \\/\\ \\ 
 \\ \\_\\  \\ \\_\\\"\\_\\  \\ \\__|     \\ \\_____\\  \\/\\_____\\    \\ \\_\\  \\ \\_____\\  \\ \\_____\\  \\ \\_\\ \\_\\  \\ \\_\\ \\_\\  \\ \\____- 
  \\/_/   \\/_/ \\/_/   \\/_/       \\/_____/   \\/_____/     \\/_/   \\/_____/   \\/_____/   \\/_/\\/_/   \\/_/ /_/   \\/____/ 
                                                                                                                  
{Style.RESET_ALL}
"""

    slogan = f"{Fore.YELLOW}Your Shield in the World of Investments{Style.RESET_ALL}"
    intro_text = f"""
{Fore.GREEN}
InvestGuard is an open-source tool designed to provide comprehensive analysis and insights for investment opportunities. 
Whether you're a seasoned investor or just starting out, InvestGuard empowers you with valuable data and analytics to make informed decisions.

{Fore.RED}Please note that InvestGuard is not an official financial advisor. All investment decisions should be made based on your own research and consultation with a qualified financial professional.{Style.RESET_ALL}
"""

    type_text(logo)
    type_text(slogan)
    type_text(intro_text)
