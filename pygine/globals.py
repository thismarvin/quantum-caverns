# Yeah alright global variables are bad, but give me a break im only using one and it's for debugging purposes!
debugging = False

def toggle_debugging():
    global debugging
    debugging = not debugging