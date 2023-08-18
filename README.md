# SpaceTraders

This is a GUI for SpaseTraders : https://docs.spacetraders.io/
using pySimpleGUI : https://www.pysimplegui.org/en/latest/

Not finished yet
Not *manualy* usable yet
Usable with auto-mode

## What is usable for the moment:
- creat an account (register)
- connect to an account with the token (login, with the token field filled)
- connect with the username (if already registered on the machin previously)
- when connected :
  - display the map of the System (click on the "*map*" button on the top-left)
  - use the auto mode, for the moment it does (**BEFORE** using the auto-mode, it is necessary to display the map first, see above):
    -  buy a mining drone if no excavator in the fleet
    -  navigate to the asteroid field
    -  extract ressources if cargo have places
    -  when cargo is full, dock to sell goods (whiches are not needed for the contract)
    -  when cargo is full of contract needs, navigate to contract to deliver cargo
    -  navigate to the asteroid to continue mining

be carefull, if the deadline to fil contract is passed, your ship will travel between asteroids field and the contract delivery point (navigate will cost fuel) this will cause a loss of credits.
  
## Update to come: 
- auto-mode : fulfill contract (will be implement and test during the next periode after the reset, I think it began the 2023.08.19)
- auto-mode : get out of the auto mode if the contract is passed or for others reasons
- possibility to play the game (cause for the moment only auto mode is possible.....)
  - buttons on the map to navigate, refuel and all the possibilities of the game
- display each ship with his specificities (especially his type and his mount. (number of crew, moral, fuel etc... will probably come within))
- animation on the map and on the ship display zone
- negociate a second contract ? (I've seen this request but never tried)
- exploration of the univers ? (chart etc...)
- other stuff maybe ?

## Good to know:
- if your token is not up to date, delete the "datas.json" file at the root of this program or just delete his content, and make the registration processus again. (with your *pseudo* and your *faction*)
- I'll make an .exe and other stuff when the GUI will be practicable.

## You:

Feel free to use it for you, especially to validate your first contract and learn how *request* works, then creat whatever you want by extend this GUI to fit your needs. GL Space Trader !