import PySimpleGUI as sg
import subprocess, psutil, os, os.path, time, webbrowser, sys, threading, tkinter, shutil, ctypes, platform
from ctypes import wintypes
from requests import get
try:
    import winreg
except:
    import _winreg as winreg


def InstallDependencies(): # FUNCTION FOR INSTALLING DEPENDENCIES

    if os.path.isfile(r'C:\Windows\Fonts\AmbexHeavy_0.ttf') == False: #and os.path.isfile(r'C:\Windows\Fonts\ambexheavy.ttf') == False:
        print("Installing missing font: AmbexHeavy")
        install_font(ResourcePath(r'Fonts\AmbexHeavy.ttf'))

    if os.path.isfile(r'C:\Windows\Fonts\AmbexHeavyOblique.ttf') == False:
        print("Installing missing font: AmbexHeavyOblique")
        install_font(ResourcePath(r'Fonts\AmbexHeavyOblique.ttf'))
        

def StopFreeLAN():                  # FUNCTION FOR STOPPING THE FREELAN SERVICE AND PROCESS
    for proc in psutil.process_iter():
        if proc.name() == "freelan.exe":
            proc.kill()
    print("Stopping FreeLAN...")
    subprocess.call('net stop "freelan service"')

def GetPublicIP():                  # FUNCTION FOR GETTING THE PUBLIC IP ADDRESS OF THE USER
    retries = 0
    while True:
        retries += 1
        ip = get('https://api.ipify.org').text
        ip_correct = False
        
        for x in range(0,10):
            if str(x) == ip[0]:
                ip_correct = True

        if ip_correct == True:
            break

        elif retries > 2:
            print("Could not acquire Public IP.")
            ip = "[Not Found]"
            break
    
        time.sleep(1)

    return ip

def CheckInput(uinput, inputtype):      # FUNCTION FOR CHECKING THE VALIDITY OF USER-INPUT
    correctinput = False

    if inputtype == "IP":   # Checks IP-type user inputs

        if uinput == "":
            print("Please enter a valid IP.")
            correctinput = False
            return correctinput

        sinput = uinput.split(".")

        for elem in sinput:
            for symb in elem:
                if ord(str(symb)) < 48 or ord(str(symb)) > 57:
                    print("Please enter a valid IP.")
                    return correctinput

        if len(sinput) != 4:
            print("Please enter a valid IP.")
            return correctinput

        for elem in sinput:
            if len(elem) > 3:
                print("Please enter a valid IP.")
                return correctinput

        correctinput = True
        return correctinput


    if inputtype == "ID":   # Checks ID-type user inputs

        if uinput == "":
            print("Please enter a valid ID.")
            correctinput = False
            return correctinput

        for symb in uinput:
            if ord(str(symb)) < 48 or ord(str(symb)) > 57:
                print("Please enter a valid ID.")
                return correctinput

        if int(uinput) > 254 or int(uinput) < 2:
            print("Please enter an ID between 2-254.")
            return correctinput

        correctinput = True
        return correctinput


    if inputtype == "PASS": # Checks passphrase-type user inputs

        if uinput == "":
            print("Please enter a valid passphrase.")
            correctinput = False
            return correctinput

        for symb in uinput:
            if ord(str(symb).upper()) < 65 or ord(str(symb).upper()) > 90:
                if ord(str(symb).upper()) < 48 or ord(str(symb).upper()) > 57:
                    print("Please only use letters and numbers when entering a passphrase.")
                    correctinput = False
                    return correctinput

        if len(uinput) > 30:
            print("Please enter a passphrase that does not exceed the 30-character limit.")
            correctinput = False
            return correctinput

        correctinput = True
        return correctinput



class StartHost(threading.Thread):      # FUNCTION FOR STARTING A HOST IN FREELAN
    def __init__(self, hpass):
        self.stdout = None
        self._hpass = hpass
        self.si = subprocess.STARTUPINFO()
        self.si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        threading.Thread.__init__(self)

    def run(self):
        subpcmd = FREELAN_EXE + " --security.passphrase " + self._hpass + " --switch.relay_mode_enabled yes --debug"
        subp = subprocess.Popen(subpcmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, startupinfo=self.si)

        while True:
            self.stdout = subp.stdout.readline().rstrip()
            if not self.stdout:
                break
            print(self.stdout)


class StartConnect(threading.Thread):   # FUNCTION FOR ATTEMPTING A CONNECTION IN FREELAN
    def __init__(self, cid, cip, cpass):
        self.stdout = None
        self._cid = cid
        self._cip = cip
        self._cpass = cpass
        self.si = subprocess.STARTUPINFO()
        self.si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        threading.Thread.__init__(self)

    def run(self):
        subpcmd = FREELAN_EXE + " --security.passphrase " + self._cpass + " --fscp.contact " + self._cip + ":12000 --tap_adapter.ipv4_address_prefix_length 9.0.0." + self._cid + "/28"
        subp = subprocess.Popen(subpcmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, startupinfo=self.si)

        while True:
            self.stdout = subp.stdout.readline().rstrip()
            if not self.stdout:
                break
            print(self.stdout)


def ResourcePath(relative_path):        # FUNCTION FOR GETTING PATH FOR DEPENDENCIES WHEN IN ONEFILE MODE
    try:
        base_path = sys._MEIPASS
        
    except Exception:
        base_path = os.path.abspath(".")


    return os.path.join(base_path, relative_path)



def install_font(src_path):             # FUNCTION FOR INSTALLING FONTS
    # copy the font to the Windows Fonts folder
    dst_path = os.path.join(os.environ['SystemRoot'], 'Fonts',
                            os.path.basename(src_path))
    shutil.copy(src_path, dst_path)
    # load the font in the current session
    if not gdi32.AddFontResourceW(dst_path):
        os.remove(dst_path)
        raise WindowsError('AddFontResource failed to load "%s"' % src_path)
    # notify running programs
    user32.SendMessageTimeoutW(HWND_BROADCAST, WM_FONTCHANGE, 0, 0,
                               SMTO_ABORTIFHUNG, 1000, None)
    # store the fontname/filename in the registry
    filename = os.path.basename(dst_path)
    fontname = os.path.splitext(filename)[0]
    # try to get the font's real name
    cb = wintypes.DWORD()
    if gdi32.GetFontResourceInfoW(filename, ctypes.byref(cb), None,
                                  GFRI_DESCRIPTION):
        buf = (ctypes.c_wchar * cb.value)()
        if gdi32.GetFontResourceInfoW(filename, ctypes.byref(cb), buf,
                                      GFRI_DESCRIPTION):
            fontname = buf.value
    is_truetype = wintypes.BOOL()
    cb.value = ctypes.sizeof(is_truetype)
    gdi32.GetFontResourceInfoW(filename, ctypes.byref(cb),
        ctypes.byref(is_truetype), GFRI_ISTRUETYPE)
    if is_truetype:
        fontname += ' (TrueType)'
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, FONTS_REG_PATH, 0,
                        winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, fontname, 0, winreg.REG_SZ, filename)


    # ----- FONT INSTALLER CTYPES DEFINITIONS -----

user32 = ctypes.WinDLL('user32', use_last_error=True)
gdi32 = ctypes.WinDLL('gdi32', use_last_error=True)

FONTS_REG_PATH = r'Software\Microsoft\Windows NT\CurrentVersion\Fonts'

HWND_BROADCAST   = 0xFFFF
SMTO_ABORTIFHUNG = 0x0002
WM_FONTCHANGE    = 0x001D
GFRI_DESCRIPTION = 1
GFRI_ISTRUETYPE  = 3

if not hasattr(wintypes, 'LPDWORD'):
    wintypes.LPDWORD = ctypes.POINTER(wintypes.DWORD)

user32.SendMessageTimeoutW.restype = wintypes.LPVOID
user32.SendMessageTimeoutW.argtypes = (
    wintypes.HWND,   # hWnd
    wintypes.UINT,   # Msg
    wintypes.LPVOID, # wParam
    wintypes.LPVOID, # lParam
    wintypes.UINT,   # fuFlags
    wintypes.UINT,   # uTimeout
    wintypes.LPVOID) # lpdwResult

gdi32.AddFontResourceW.argtypes = (
    wintypes.LPCWSTR,) # lpszFilename

gdi32.GetFontResourceInfoW.argtypes = (
    wintypes.LPCWSTR, # lpszFilename
    wintypes.LPDWORD, # cbBuffer
    wintypes.LPVOID,  # lpBuffer
    wintypes.DWORD)   # dwQueryType

    # ---------------------------------------------------------

InstallDependencies()

FREELAN_EXE = ResourcePath(r'FreeLAN\bin\freelan.exe')

StopFreeLAN()


# GUI SETTINGS & STUFF

sg.SetOptions(background_color="#212123", element_background_color="#212123", button_color=["#A8C442", "#212123"], text_color="#A8C442", border_width=0)

NO_TITLEBAR = False

FONT = "AmbexHeavy"
TFONT = "AmbexHeavy Oblique"

def Seperate(w=0,h=0):
    return sg.Button("", disabled=True, button_color=["#212123","#212123"], size=[w,h], border_width=0)

    # SPLASH WINDOW

def SplashWLayout():
    SPLASH_SCREEN = ResourcePath(r"Images\Splash Screen\SScreen-blank.png")
    IMG_FREELAN = ResourcePath(r"Images\Splash Screen\FreeLanButton.png")
    B_HOST = sg.Button("HOST", font=(FONT, 25), key="SHost")
    B_JOIN = sg.Button("JOIN", font=(FONT, 25), key="SJoin")
    B_EXIT = sg.Button("EXIT", font=(FONT, 25), key="Exit")
    B_FREELAN = sg.Button(image_filename=IMG_FREELAN, key="SFreeLan", button_color=["#212123","#212123"], border_width=0)

    splashcolumn = [[B_FREELAN, Seperate(15), B_HOST, B_JOIN, Seperate(15), B_EXIT]]

    splashlayout = [  [sg.Image(SPLASH_SCREEN)],
                [sg.Column(splashcolumn, justification="center")]]

    return splashlayout

def SplashW(layout):
    return sg.Window('Splinter Cell P2P Direct', layout, default_element_size=(877, 600), element_justification="center", no_titlebar=NO_TITLEBAR, grab_anywhere=True)


    # HOST WINDOW

def HostWLayout(IP):
    HOST_TOP = ResourcePath(r"Images\Host Screen\HostScreen_top.png")
    T_IP = sg.Text('Your Public IP is: \n' + IP, background_color="#212123", font=(TFONT, 13))
    B_STARTHOST = sg.Button("Start Host", key="HHost", font=(FONT, 40))
    B_STOPHOST = sg.Button("Stop Host", key="HStop", font=(FONT, 40), visible=False)
    I_PASS = sg.Input(size=(30,2), key="HPass", background_color="#212129", font=(FONT, 14), text_color="#A8C442")
    B_EXIT = sg.Button("EXIT", key="Exit", font=(FONT, 15))
    B_BACK = sg.Button("BACK", key="Back", font=(FONT, 15))
    DEBUG_BOX = sg.Output(size=[90,20], background_color="#212129", text_color="#A8C442", font=("Consolas", 12))

    hostlayout = [  [sg.Image(HOST_TOP)],
                    [I_PASS],
                    [B_STARTHOST, B_STOPHOST],
                    [DEBUG_BOX],
                    [T_IP],
                    [B_EXIT, B_BACK]]
    
    return hostlayout

def HostW(layout):
    return sg.Window('Splinter Cell P2P Host', layout, default_element_size=(1067,600), element_justification="center", no_titlebar=NO_TITLEBAR, grab_anywhere=True)



    # CLIENT WINDOW

def ClientWLayout():
    T_CLID = sg.Text('Client ID', background_color="#212123", font=(TFONT, 15))
    I_CLID = sg.Input(size=(25,2), key="CID", background_color="#212129", font=(FONT, 14), text_color="#A8C442")
    T_HIP = sg.Text('Host IP', background_color="#212123", font=(TFONT, 15))
    I_HIP = sg.Input(size=(25,2), key="CIP", background_color="#212129", font=(FONT, 14), text_color="#A8C442")
    T_PASS = sg.Text('Passphrase', background_color="#212123", font=(TFONT, 15))
    I_PASS = sg.Input(size=(25,2), key="CPass", background_color="#212129", font=(FONT, 14), text_color="#A8C442")
    B_CONNECT = sg.Button('Connect', key="CConnect", font=(FONT, 25))
    B_DISCONNECT = sg.Button('Disconnect', key="CDisconnect", font=(FONT, 25), visible=False)
    B_EXIT = sg.Button("EXIT", key="Exit", font=(FONT, 15))
    B_BACK = sg.Button("BACK", key="Back", font=(FONT, 15))
    DEBUG_BOX = sg.Output(size=[90,20], background_color="#212129", text_color="#A8C442", font=("Consolas", 12))
    T_IPNOTE = sg.Text("Ask the host to come up with a unique number\nbetween 2-254 for you to serve as your unique ID.", background_color="#212123", font=(TFONT, 15))
    
    clientlayout = [    [I_CLID, T_CLID],
                        [I_HIP, T_HIP],
                        [I_PASS, T_PASS,],
                        [B_CONNECT, B_DISCONNECT],
                        [DEBUG_BOX],
                        [T_IPNOTE],
                        [B_EXIT, B_BACK]]
    
    return clientlayout

def ClientW(layout):
    return sg.Window('Splinter Cell P2P Client', layout, default_element_size=(1067,600), element_justification="center", no_titlebar=NO_TITLEBAR, grab_anywhere=True)


    # GUI

def RunGUI():
    stopgui = False

    while True:
        splashlayout = SplashWLayout()
        splashwindow = SplashW(splashlayout)

        if stopgui == True:
            splashwindow.close()
            break

        sevent, svalues = splashwindow.read()

        if sevent == "Exit" or sevent == None:
            stopgui = True
            

        elif sevent == "SHost":     # - HOST WINDOW GUI -
            splashwindow.close()
            
            PublicIP = GetPublicIP()
            hostlayout = HostWLayout(PublicIP)
            hostwindow = HostW(hostlayout)

            while True:
                hevent, hvalues = hostwindow.read()

                if hevent == "Back":
                    StopFreeLAN()
                    hostwindow.close()
                    break

                elif hevent == "Exit" or hevent == None:
                    StopFreeLAN()
                    hostwindow.close()
                    stopgui = True
                    break

                elif hevent == "HHost": # When user clicks "Host" button:
                    if CheckInput(hvalues["HPass"], "PASS") == True:
                        print("Host started...")

                        hostwindow.Element("HHost").Update(visible=False)
                        hostwindow.Element("HStop").Update(visible=True)

                        hostflan = StartHost(hvalues["HPass"])
                        hostflan.start()

                        #subprocess.Popen(FREELAN_EXE + " --security.passphrase " + hvalues["HPass"] + " --switch.relay_mode_enabled yes --debug")

                elif hevent == "HStop": # When user clicks "Stop" button:
                    StopFreeLAN()
                    print("Host stopped.")
                    
                    hostwindow.Element("HStop").Update(visible=False)
                    hostwindow.Element("HHost").Update(visible=True)


        elif sevent == "SJoin":     # - CLIENT WINDOW GUI -
            splashwindow.close()

            clientlayout = ClientWLayout()
            clientwindow = ClientW(clientlayout)

            while True:
                cevent, cvalues = clientwindow.read()

                if cevent == "Back":
                    StopFreeLAN()
                    clientwindow.close()
                    break

                elif cevent == "Exit" or cevent == None:
                    StopFreeLAN()
                    clientwindow.close()
                    stopgui = True
                    break

                elif cevent == "CConnect":  # When user clicks "Connect" button:
                    if CheckInput(cvalues["CID"], "ID") == True and CheckInput(cvalues["CIP"], "IP") == True and CheckInput(cvalues["CPass"], "PASS") == True:
                        print("Connecting...")

                        clientwindow.Element("CConnect").Update(visible=False)
                        clientwindow.Element("CDisconnect").Update(visible=True)

                        connectflan = StartConnect(cvalues["CID"], cvalues["CIP"], cvalues["CPass"])
                        connectflan.start()

                elif cevent == "CDisconnect":   # When user clicks "Disconnect" button:
                    StopFreeLAN()
                    print("Disconnected.")
                    
                    clientwindow.Element("CDisconnect").Update(visible=False)
                    clientwindow.Element("CConnect").Update(visible=True)


        elif sevent == "SFreeLan":
            webbrowser.open('https://www.freelan.org/donate.html', new=2)

        splashwindow.close()


RunGUI() # Starts the program.
    
StopFreeLAN()

print("Splinter Cell P2P Direct has stopped.")
