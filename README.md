# Autorize
Automatic authorization enforcement detection extension for burp suite written in Python developed by Barak Tawily, an application security expert at AppSec Labs in order to ease application security people work and allow them perform an automatic authorization tests

![alt tag](https://raw.githubusercontent.com/Quitten/Autorize/master/Autorize.png)
# Installation 
1. Download burp suite (obviously): http://portswigger.net/burp/download.html
2. Download Jython standalone JAR: http://www.jython.org/downloads.html
3. Open burp -> Extender -> Options -> Python Environment -> Select File -> Choose the Jython standalone JAR
4. Install Autorize from the BApp Store / keep follow the next steps:
5. Download the Autorize.py file.
6. Open burp -> Extender -> Extensions -> Add -> Choose Autorize.py file.
7. See the Autorize Tab and enjoy automatic authorization detection :)

# User Guide - How to use?
1. After installation, Autorize tab will be added to burp
2. Open Configuration tab (Autorize -> Configuration)
3. Get your low-privilieged user Authorization token header (Cookie / Authorization) and copy it to the textbox includes the text "Insert injected header here".
4. Click on the "Intercept is off" to start intercept the traffic in order to allow Autorize check for authroization enforcement
5. Open a browser configure the proxy settings so the traffic will be passed to burp.
6. Browse to the application you want to test with a high privilieged user.
7. Autorize table will show you the request's URL and Enforcement Status.
8. It is possbile to click on specific URL and see the Original/Modified request/response in order to invetigate the differences.

# Authorization Enforcement Status
There is a 3 enforcement statuses:

1. Authorization bypass! - Red color
2. Authorization enforced! - Green color
3. Authorization enforced??? (please configure enforcement detector) - Yellow color

The first 2 statuses is obvious, so i wont elaborate about that.

The 3th status, means that Autorize cant determine if the authorization enforced or not, thus, Autorize ask you to configure a filter in the Enforcement Detector tab.

The Enforcement Detector fitlers will allow Autorize to detect a authroization enfrocement via finger print (string in the message body) or content-lenght in the server's response.

For exmaple, in case the there is a request enforcemenet status that detected as "Authorization enforced??? (please configure enforcement detector)" it is possible to investigate the Modified/Original response and see that the Modified response body includes the string "You are not auhtorized to perform action", so you can add a filter with the finger print value "You are not auhtorized to perform action", thus, Autorize will look for this finger print and automatically will detect that the Authorization is enforced.
It is possbile to do the same by definding Content-Length filter.
