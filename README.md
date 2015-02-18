# Autorize
Autorize is an automatic authorization enforcement detection extension for Burp Suite. It was written in Python by Barak Tawily, an application security expert at AppSec Labs. Autorize was designed to help security testers by performing automatic authorization tests.

![alt tag](https://raw.githubusercontent.com/Quitten/Autorize/master/Autorize.png)
# Installation 
1.	Download Burp Suite (obviously): http://portswigger.net/burp/download.html
2.	Download Jython standalone JAR: http://www.jython.org/downloads.html
3.	Open burp -> Extender -> Options -> Python Environment -> Select File -> Choose the Jython standalone JAR
4.	Install Autorize from the BApp Store or follow these steps:
5.	Download the Autorize.py file.
6.	Open Burp -> Extender -> Extensions -> Add -> Choose Autorize.py file.
7.	See the Autorize tab and enjoy automatic authorization detection :)


# User Guide - How to use?
1.	After installation, the Autorize tab will be added to Burp.
2.	Open the configuration tab (Autorize -> Configuration).
3.	Get your low-privileged user authorization token header (Cookie / Authorization) and copy it into the textbox containing the text "Insert injected header here".
4.	Click on "Intercept is off" to start intercepting the traffic in order to allow Autorize to check for authorization enforcement.
5.	Open a browser and configure the proxy settings so the traffic will be passed to Burp.
6.	Browse to the application you want to test with a high privileged user.
7.	The Autorize table will show you the request's URL and enforcement status.
8.	It is possible to click on a specific URL and see the original/modified request/response in order to investigate the differences.


# Authorization Enforcement Status
There are 3 enforcement statuses:
1.	Authorization bypass! - Red color
2.	Authorization enforced! - Green color
3.	Authorization enforced??? (please configure enforcement detector) - Yellow color

The first 2 statuses are clear, so I won’t elaborate on them.

The 3rd status means that Autorize cannot determine if authorization is enforced or not, and so Autorize will ask you to configure a filter in the enforcement detector tab.

The enforcement detector filters will allow Autorize to detect authorization enforcement by fingerprint (string in the message body) or content-length in the server's response.

For example, if there is a request enforcement status that is detected as "Authorization enforced??? (please configure enforcement detector)" it is possible to investigate the modified/original response and see that the modified response body includes the string "You are not authorized to perform action", so you can add a filter with the fingerprint value "You are not authorized to perform action", so Autorize will look for this fingerprint and will automatically detect that authorization is enforced. It is possible to do the same by defining content-length filter.

