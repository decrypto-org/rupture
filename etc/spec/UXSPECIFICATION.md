# Rupture

## Why a Rupture web UI

Rupture is a framework for easily conducting BREACH and other compression-based
attacks. The web UI aims to make the framework more well-known since it’s more
user-friendly and easier to run.

## Workflow

The Rupture web UI consists of two main pages and a modal window. The two main
pages are the *Network Overview* and the *Victim Attack Inspection*. The modal
window is for the target configuration and it’s called *Target Configuration*.

These are described below.

### Network Overview

The *Network Overview* is the start page. It displays the completed, the
currently running and the paused attacks. It also allows the user to initiate a
new attack either by adding a custom victim or by firstly scanning the network
for victims.

Each attack is represented by a PC icon. Beneath that icon are the victim’s IP
and machine name, the target endpoint name, the state of the attack, the
progress bar, the running time (hh:mm:ss) and a *more details* link.

The state of the attack is one of the following:

* Completed
* Running…
* Paused
* Not started

The *more details* link is a link to the *Victim Attack Inspection* page of each
attack.

Each completed attack is represented by a PC icon with a green screen and is
placed in the first line. The completed attacks’ progress bar is green.

Under the completed attacks are the running attacks and the paused attacks.
These are represented by a PC icon with a yellow screen. The screen has a pause
button ![pause button](http://imgur.com/MY4lRnx.png)
for the running attacks and a ![play button](http://imgur.com/PUBgQVB.gif) for
the paused ones.

The completed, running and paused attacks appear in chronological
order. The more left one PC icon is, the earlier the attack has started.

The yellow PC icons are clickable. When clicked, the running attacks pause and
the paused attacks resume running. The PC icon changes immediately after
click. Their progress bar is blue.

Each completed, running and paused attack has a close button which deletes the
attack. The button appears on hover. When clicked, the attack is deleted and
a notification *The victim has been deleted. [Undo]* appears at the top of the
page, where *[Undo]* is clickable. The notification disappears after 10 seconds
or if the user clicks its close button earlier.

At the top right of the page is a circle button with the WiFi symbol and a
small magnifier on its bottom right. Its name - *Scan for victims* - is written
beneath the button.

When the user clicks it, the name written underneath changes to *Scanning…*. Once
the scan is completed, the button name resumes to its initial state and PC
icons with a gray screen appear beneath the running and paused attacks,
representing the possible victims to attack. These PC icons appear in the same
order as they were found during scanning. Beneath each PC icon with the gray
screen are the state *Not started* and the victim’s IP and machine name. The user
can then click the PC icon with the desired IP to configure the target’s
options in the *Victim Attack Inspection* page. The possible victims remain shown
for 15 minutes. If the user rescans the network before that timeframe, the
previous possible victims disappear for the new ones to show up.

Under the scan for victims button, there is a ghost PC icon with low opacity
and with a plus button at its screen ![plus button](http://imgur.com/HQ3ZmCN.png).
Its name - *Add Custom Victim* - is written beneath the icon. The user will click
this PC icon if they already know the victim’s IP and don’t need to search
for other victims. When clicked, the user is directed to the *Victim Attack
Inspection* page to configure the victim’s options.

The lists of the completed, running and paused, and not started attacks are
collapsible but shown by default. Above each list is a collapsible header named
*Completed*, *Running & Paused* and *Not started* respectively. When the user clicks
one of them, the corresponding list of attacks disappears, so that the user
focuses on the attacks he mostly cares about. When reclicked, the hidden list
is reshown.

On the top of the page is a navigation bar with the Rupture logo on its left. When
the logo is clicked, the user is redirected to the *Network Overview* page. At
the left of the footer is a link button for the [RuptureIt](https://ruptureit.com/)
website.

![Rupture web UI before scanning](http://imgur.com/k2rzpY9.jpg)

*Rupture web UI before scanning*

![Rupture web UI after scanning](http://imgur.com/J886VtV.jpg)

*Rupture web UI after scanning*

### Victim Attack Inspection page

At the top of the page are the attack’s general details. If the attack is
already running or it has been paused and is about to resume, the *Victim Attack
Inspection* page displays the following list:

* Target endpoint with its logo if available
* Victim's IP,  Victim's machine name
* Decrypted secret
* Progress bar, as the one described in the *Network Overview* page

If the attack is about to begin and the user clicked the *Add custom victim*
button, the victim’s IP is a field for the user to add the IP.

If the attack is about to begin and the user has already chosen a victim, the
victim’s IP is already filled.

In both cases, the last two bullets are not displayed before the attack starts.
Instead of the name of the target endpoint, there is a dropdown list called
*Choose target*. There are some default target endpoints such as Gmail, Facebook
etc. The last option of the dropdown list is the *Add new target…* option. The *Add
new target* option requires that the user has already written a population
script for this specific target. If the user clicks the *Add new target…* option,
the modal window *Target Configuration* appears.

Below these is an *Attack* button which initiates the attack.

When the attacks are running, there is a table beneath the attack's general
info with one entry per batch:

| Round | Batch | Alignment alphabet | possible knownsecret   | confidence  |
|-------|-------|------------------- |------------------------|-------------|
|       |       |                    |                        |             |
|       |       |                    |                        |             |

Beneath this table are two buttons, the *Attack/Pause* button, for the user to
pause or reinitiate the attack and the *Delete* button if the user wants to
delete the attack. If the *Delete* button is clicked, the attack is deleted,
the user is redirected to the *Network Overview* page and a notification *The
victim has been deleted. [Undo]* appears at the top of the page, where *[Undo]*
is clickable. As described in the *Network Overview* section, the notification
disapears after 10 seconds or if the user clicks its close button earlier.

On the top of the page is a navigation bar with Rupture logo on its left. When
the logo is clicked, the user is redirected to the *Network Overview* page.
