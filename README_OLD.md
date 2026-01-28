# SentinelXP ![GitHub All Releases](https://img.shields.io/github/downloads/C0m3b4ck/SentinelXP/total)
An antivirus for Windows XP focusing on diagnostics and user choice. Free, forever, no spyware, no bloatware.
# What is it?
A bunch of modules that help you stay safe on your XP.
# The Sentinel Project
SentinelXP will be remade for other Windows versions.
<br>**With online protection:** XP, Vista, 7, 8, maybe 10, other versions with spyware will be omitted - no need for AV when your OS (win 11 and on) is spyware
<br>**Without online protection:** 95, 98, 2000, NT, maybe ME
# Original Author 
Development was started on April 13th, 2025, by C0m3b4ck.
# Contributors 
 <br>***Code***<br>
As of now, there are no more contributors than the original author.
 # How can you contribute?
 Simply make a contribution here, on Github. Another, better way, would be to send me links to malware repositories so that I can train the antivirus.
 <br> Remember, you have to send me the links/files yourself, as I have no server to send the files to. When I will have, I will only send out file hashes with your explicit permission. You will be able to see that, as the project will be open-source forever.
 <br>**You can also join the conversation here:** https://www.xpforums.com/conversations/windowsxp-antivirus.272/
# Disclaimer!!!
**We are not viable for any damages you sustain due to malware!!!**
**The best antivirus is staying vigilant with what you do in the internet!!!**
# How to use
  **Just run the executable!**
# Build from source
<br>**Structure**
<br>**C++**
<br>Located here: https://github.com/C0m3b4ck/SentinelXP/blob/main/Source/structure.txt
<br>Once finished, will be pasted over.
# C++ 98
<br>Use gcc 3.4.5 from MinGW on Windows XP.
# Archival - Python
<br>*Leaving this in because I spent over 35 hours on this.
<br>You will need:
<br>__Py2Exe__
<br>You can get Py2Exe as .iso file mountable to VM here: <a href="https://github.com/Martingonn/SentinelXP/blob/main/Build/Build%20Tools/py2exe-0.6.9.iso">
<br>*__Steps:__*
<br>**1.** Mount py2exe .iso into your Windows XP
<br>**2.** Run the installer.
<br>**3.** Once you installed Py2Exe, make a "setupy.py" that looks like this:
<br>from distutils.core import setup
<br>import py2exe
<br>
<br>setup(console=['yourscript.py'])
<br>**4.** In the same directory, run:
<br>*python setup.py py2exe
<br>**5.** Done! 
<br> I wasted over 35 hours on this... trying out different ways... until finally...

# Future Additions
* Packet inspection
* Monitoring port connections
* Opening .exe and inspecting contents
* Anti-phishing website module
* GUI version (maybe)
* Menu module to operate on other modules
* Sneaky download prevention
* A LOT MORE
For more, check out ideas.txt: https://github.com/C0m3b4ck/SentinelXP/blob/main/Source/ideas.txt
