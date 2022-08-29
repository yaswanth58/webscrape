

import pyautogui
import time
import keyboard
import pyperclip
from requests import *
from bs4 import *
from re import *
from tkinter import messagebox

# Function for returning what is highlighted by the cursor
def copyHighlight():
    pyperclip.copy("") # In case nothing is highlighted, this line prevents duplicate entries otherwise it copies what is highlighted
    pyautogui.hotkey('ctrl','c')
    time.sleep(0.01) # Suggested by stackoverflow user [soundstripe]: ctrl + C is fast but sometimes programs runs faster
    pyautogui.click(pyautogui.position()) # Dispels the highlighted text and indicates that the program has responded
    return pyperclip.paste() # Returns what has been copied as a STRING

# Functions for scraping Wikipedia.com, using the library BeautifulSoup4, or BS4
def getLink(search):
    # The get function "gets" the HTML/XML/JavaScript code from the website, "lxml" is a parser
    soup = BeautifulSoup(get("https://en.wikipedia.org/w/index.php?search="+search).content, "lxml")
    for link in soup.findAll("a") :  # a, from a href, is the tag that identifies links in websites
        link_href = link.get('href') # Extracts the actual link from within the <a></a> tag
        link_rank = link.get('data-serp-pos') # We noticed that all search elements in search have this numbered tag
        # This is how to identify search results from other links. If there is no rank, it is not a search result
        if (link_rank)!=None: # findAll gets ALL links, but if the rank exists, it is a search result
            if "wiki/" in link.get('href'): # There are some wiktionary links that pop in, but we needed the wikis only
                return(link.get('href')) # Returns the top search result of the input string

# Summarizing the Wikipedia entry was hard for two reasons: there are disambiguation pages and there are reference tags
# We used the Regular Expressions library, re, for separating the reference tags from the text
def getSummary(link, index):
    print(link) # For reference; since a link in the command prompt helps to debug where the code went wrong and it is harmless
    soup = BeautifulSoup(get(link).content,"lxml") # lxml is an efficient parser
    return(sub('\[\d*?\]','',soup.find_all('p')[index].text)) # This statement used the RegularExpressions library
    # Going through the statement character by character - RegularExpressions takes a general expression as a wildcard,
    # and the sub function replaces it with something else, in this case, a blank character
    # '\[' & '\]' are escaped square brackets. 'd*' describes a digit, '?' indicates any number of the digit

# Summarizing the UrbanDictionary entry was comparatively easier since it does not have <p> tags
# Instead, it has <div> tags with a ['meaning'] attribute.
# The search URL is easy to generate, and the rest of the code follows much of the same pattern as the code above for scraping Wikipedia
def summarizeUD(search): # Search is the returned variable from copyHighlight()
    respond = get("http://urbandictionary.com/define.php?term=" + search)
    soup = BeautifulSoup(respond.content, "lxml") # Gets the BeautifulSoup object, which contains the HTML code for the page
    string = "" # Initializing a string variable to later store the summary in it
    returnNext = False # Some meanings don't have examples, and therefore two different meanings may pop up
                       # This boolean prevents that from happening
    for tag in soup.find_all('div'): # In Wikipedia, we did this with the <p> tag. Here, we use the <div> tag
        if tag.get('class') == ['meaning']: # The meaning tag identifies the definitions from useless links and other text
            if not returnNext: # This prevents the function from returning multiple definitions
                string += tag.text + "\n" # The '\n' is a line break, so the example is better formatted when added
            else: # In the above statement, tag.text returns the text from the <div> tag
                return(string) # If the example has already been added, this simply returns the string and does not add it
        if tag.get('class') == ['example']: # The example tag identifies an example of the word in the given meaning
            string += "\nFor example, a sentence would be:\n" # Again, '\n' added for better formatting
            string += tag.text # tag.text gives the text from within the <div> tag
            return(string) # Returns string if an example has been succesfully appended

# Recursion based MessageBox
def PopUpWindow(response,index): # The response is the YES/NO at the end of the message-box. If Yes, this shows more information
    if response == 1: # 1 is YES, in this case
        index+=1 # The index is incremented so the next paragraph comes up
        # This is essentially identical to the original YES/NO prompt, except this ends in a recursive construct that terminates when the user presses NO
        response = messagebox.askyesno("Webscraping [Wiki] "+search, getSummary("https://en.wikipedia.org" + getLink(search + " -disambiguation"), index))
        PopUpWindow(response, index) # Recursive call
    print("") # Was having some issues with this function, but a print function seemed to fix things. Will have to look into why

# MAIN CODE
# The main code runs under a While(True) loop
takingResponse = True # This variable indicates whether the program is ready to take input, or not
while(True): # An infinite loop that keeps the program running
    if takingResponse: # This line of code prints out a message whenever the program is ready to take an input
        print("Taking responses NOW.")
        takingResponse = False # Keeps the program from spamming the same message over and over again
    if keyboard.is_pressed('f9'): # This is remappable,i.e, we can change to any other key here
        entered = copyHighlight() # Assigns to the variable what has been highlighted on screen
        print(entered) # Prints what has been entered for convenience to keep track of the running of the program
        string = summarizeUD(entered) # Summarizes the highlighted text
        print(string) # Again prints for convenience
        messagebox.showinfo("UD scraping", string) # Shows the MessageBox, with the definition and example
        takingResponse = True # Indicates that the program is ready for the next input
        continue # Loops back
    if keyboard.is_pressed('f2'): # Remappable, as before
        index = 0 # The index identifies from which paragraph to start extracting. Generally, 1 is the first line therefore 0 is usually unnecessary
        search = copyHighlight() # Assigns to the variable what is highlighted
        # The next line gets the summary. The '-disambiguation' makes it so that "Maybe you meant..." pages don't appear
        # The - [minus] operator is for searching for those articles specifically that do not have that word in them
        summary=getSummary("https://en.wikipedia.org"+getLink(search+" -disambiguation"),index) # Summarizes the text
        print(summary) # For convenience, this prints the text
        response = messagebox.askyesno("Wiki scraping [Wiki] "+search, summary) # Asks the user YES/NO to check if further info is wanted
        PopUpWindow(response, index) # Recursive function, described above that is used to cycle through long pages
        print("") # Blank print statement fixes a random bug. We don't exactly know why
        takingResponse = True # Indicates readiness for next input
        continue # Loops back

    if keyboard.is_pressed('f6'): # Remappable, as before
        exit() # Exits the program


