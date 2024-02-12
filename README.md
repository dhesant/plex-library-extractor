# Plex Extraction Script

## Download
Use the following steps to extract the Plex API URL from app.plex.tv, then pass it into the following command to download the xml file.

1. Open app.plex.tv in Chrome
2. Open Chrome's Developer Tools (Ctrl+Shift+I or from the `More tools...` menu), and select the Network tab.
3. Navigate to the library you want to extract in Plex. Find the line in the Developer Tools that looks like `https://XXXXXXXXXXXXX.plex.direct:XXXXX/library/sections/X/all?type=2&XXXXXXXXXXXXXXXXX`.
4. Run the following command with the extracted URL and the desired file prefix.
5. The script will output a .xml file with the Plex extract in the current folder.

```bash
$ python process.py download <PLEX_URL> <XML_FILE_PREFIX>
```

## Parse
After downloading the .xml file from Plex, run the following command to convert it into a CSV.
```bash
$ python process.py csv <PATH_TO_YOUR_XML_FILE>
```
