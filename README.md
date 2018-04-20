# Wiki Converter

#### A simple wiki migration tool.

##### Supported wiki engines:
* MediaWiki
* TikiWiki
* JamWiki
* WikkaWiki
* WackoWiki

##### Features:
* Conversion of basic page markup such as headlines, lists, text formatting, embedded images, etc.
* Migration of image files
* Preserving page history and author names

##### Requirements:
* Wiki installations using a MySQL database as the data backend
* Access to the file system with both wiki installations for image migration
* Python (ver. 3.6 or above) and SQLAlchemy library (https://www.sqlalchemy.org/)

##### Usage:
![alt text](https://github.com/molsz011/wikiconverter/blob/master/media/gui.png "GUI")

1. __Admin username__ – the username of the administrator account of the database system with read and write access to the databases of both source and destination wikis
2. __Password__ – the password of the database administrator account
3. __Hostname__ – the hostname, IP address, or domain name of the server with the database, set to localhost by default
4. __Port__ – port of the above web server, set to 3306 by default
5. __Source__ Wiki – the engine on which the wiki that we migrate data from is based
6. __Source DB name__ – the name of the database of the source wiki on the web server
7. __Src. media directory__ – the folder on the server where the source wiki engine stores its images, by default these folders are:
    *	MediaWiki: 	[Installation directory]/images/
    * JamWiki:	[Installation directory]/uploads/en/
    * TikiWiki:	None – set manually by the user
    * WackoWiki:	[Installation directory]/files/global/
    * WikkaWiki:	[Installation directory]/images/
8. __Destination Wiki__ – the engine on which the wiki that we migrate data to is based
9. __Destination DB name__ – the name of the database of the destination wiki on the web server
10. __Dest. media directory__ – the folder on the server where the destination wiki engine stores its images (default folders are the same as above)

Note: the paths to the image folders can either be written manually into the text box, or chosen using the “Browse…” button. 