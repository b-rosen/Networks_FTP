			########### How to run ###########

Run the python module Server/Server_FTP.py to start the server.

The client program is run using the python module Client/clientGUI.py.


			########### How to use ###########

- If running the client and server on the same machine:
	* Enter 'localhost' in the server name box.
	* Enter '2400' for the port
- Otherwise:
	* Use the IP address or other identifier and port 21

Login details for three users is specified in Server/Users.py. One such example is to use 'Benjy' as the username and 'Hello' as password. The file specifies whether the user needs a password or account to log in.

- The main screen has the function buttons in the top left corner.
- The main file viewer box in the centre shows the list of files/folders in the current directory.
- The 'list' button refreshes the list shown in the file viewer box.
- Clicking the 'logout' button in the top right corner will return the user to the start page.

The server has a unique folder for each user, in Server/User_Folders. When creating a new user, also ensure that a new folder is also created.


			########### Shortcuts ###########

- Double clicking on a folder will change the directory to that folder and list its files/folders.
- Double clicking on a file will download the file to Client/Downloads. Note that files with the same name will be overwritten.
- Closing the program (from terminal or clicking the X on the window) will automatically log the user out first.