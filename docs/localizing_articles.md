## Getting articles localized

This article describes how to use the Zendesk production tools (ZEP) to prepare localization handoffs and publish the localized articles and images returned from the vendor.

For installation instructions, see [Setting up the Zendesk production tools](https://github.com/chucknado/zep/blob/master/docs/setup.md).

Workflow for creating a handoff:

1. [Package the articles](#add_articles)
2. [Package the images](#add_images)
3. [Clean up the files](#clean_files)
4. [Hand off the files](#handoff_files)
5. [Update the dita map](#update_map)

Workflow for publishing a handoff:

1. [Prepare the localized content](#prep_loc_content)
2. [Relink the files for Help Center](#relink)
3. [Push the files to Help Center and s3](#publish)


<!--
title: Getting articles localized
url: https://github.com/chucknado/zep/blob/master/docs/localizing_articles.md
source: Zendesk Internal/Zendesk User Guides/production/zep/docs/localizing_articles.md
-->


<h3 id="add_articles">Package the articles</h3>

1. Get the list of article ids from the [loc handoff worksheet](https://docs.google.com/spreadsheets/d/1jldaCDT5iYrUdmzAT1jWwFbYOwGECVVcwK9agHJeGE8/edit#gid=0) in Google Docs and add their ids as a column in the **/handoffs/\_loader.txt** file. Each id should be on one line with no other characters. Example:

	**\_loader.txt**
	```
	207323377
	213170757
	212533138
	...
	```

	**Caution**: Don't leave a blank line at the end of the list.

	**Tip**: You can also place the ids in a file with a different name and specify the file in Step 2.

2. In the CLI, navigate to the **zep** folder and run the following command:

	```bash
	$ python3 ho.py create {handoff_name} {product}
	```

	The only valid values for `product` (for now) are **explore**, **bime**, **help**, **chat**, or **support**. Example:

	```bash
	$ python3 ho.py create 2016-12-24 bime
	```

	The command reads the article ids in the loader file, downloads the English articles from your Help Center, and writes them in a new **handoffs/2016-12-24/articles** folder.

	If you listed the articles in a file with a different name, specify the filename with the `loader` option. Example:

	```bash
	$ python3 ho.py create 2016-12-24 bime --loader=bime_loader.txt
	```

	The custom file still has to be located in your **handoffs** folder.


<h3 id="add_images">Package the images</h3>

All the images in the handoff articles need to be on Amazon s3, and the `src` urls in the articles need to point there. When we get the localized images back and upload them to the respective locale folders on s3, the `src` urls in the localized articles can be easily updated by changing the "en-us" locale in the image url to the appropriate locale.

You can flag an article to use the English images in the localized versions of the article. This is sometimes necessary for community-contributed articles or for articles with images that are hard to reproduce. The exception should be noted in the loc handoff worksheet.

The tool checks to make sure all the `src` urls in the handoff articles point to files on s3. If some urls point elsewhere, the writer must manually move the images to s3 and update the `src` urls in the HC articles and in the dita source files before the handoff can proceed.

Before packaging the images, you must first update the **/handoffs/src** folder with any images that were added or updated on s3 since the last handoff (or, if this is the first handoff, since you [set up](#) the **src** folder). The tool  gets the source image files for the handoff from this folder, not from the server (yet).

1. In Cyberduck, go to the **/zen-marketing-documentation/docs/en** folder and click the top of the Modified column to sort the files. Make sure the most recently modified files are at the top.

2. Select all the images that were created or updated since the last handoff.

3. Select **Download To** in the **Action** menu on the toolbar, then select the **handoffs/src** folder as the destination folder to start the download.

4. In the CLI, run the following command to list all article images in the handoff articles that are not on the s3 server:

	```bash
	$ python3 ho.py check_images {handoff_name} {product} --exclude {id id ...}
	```

	The only valid values for `product` (for now) are **explore**, **bime**, **help**, **chat**, or **support**. Example:

	```bash
	$ python3 ho.py check_images 2016-12-24 chat
	```

	Specify the `exclude` argument if some articles have been flagged to use English images in the localized versions of the article. Specify the article ids to exclude. Example:

	```bash
	$ python3 ho.py check_images 2016-12-24 chat --exclude 203660036 203663816
	```

5. 	Ask the writer to upload any missing images to s3 and update the image urls in the HC articles and DITA source files. The handoff can't proceed until this is done. Rerun step 4 to make sure no missing images are reported.

6. After sorting out any missing images, run the following command to copy the modified images from the **src** folder to a new **images** folder alongside the **articles** folder in your handoff folder:

	```bash
	$ python3 ho.py copy_images {handoff_name} {product} --months={int} --exclude {id id ...}
	```

	The only valid values for `product` (for now) are **explore**, **bime**, **help**, **chat**, or **support**.

	The command creates the **images** folder in your handoff folder. You don't have to create it yourself.

	The optional `months` argument specifies the number of months since the images were last modified. The default is 4. Only images that were modified within this period will be included in the handoff. This is to prevent from localizing previously localized images. If some articles in the handoff have been in progress for more than 4 months, you can increase the number.

	Example:

	```bash
	$ python3 ho.py copy_images 2016-12-24 chat --months=6
	```

	The command copies all article images that were modified in the last 6 months.

7. Manually review each image in the **images** folder and remove text-less images that don't need to be localized (things like icons that don't have any text). List them in a note and make sure copies of them exist in all 5 language folders on s3. (For common icons and plan banners, they do.)

	If you're unsure any of the remaining files have already been localized, look for the image in a S3 language folder like "fr". If the image already exists in that folder, see if it's the same version with Quick Look in Cyberduck.

8. Manually add any vector source files (.psd, .ai) to the **images** folder. Example: Images with callouts in text layers.

	**Note**: Gerhard will query you about any bitmap image containing text that's not displayed in the UI. Translators update text layers; they don't recreate images.


<h3 id="clean_files">Clean up the files</h3>

You can use the tool to strip out HTML comments from the articles to prevent them from being accidently localized.

1. In the CLI, run the following command:

	```bash
	$ python3 ho.py clean {handoff_name} {product} --write
	```

	The only valid values for `product` (for now) are **explore**, **bime**, **help**, **chat**, or **support**.

	By default, the `clean` command strips out both HTML comments and Zendesk Classic notes from the articles.

	**Recommended**: Do a dry run first to check for errors by omitting the `--write` argument. The results are displayed in the console but the files aren't updated.


2. After creating updated versions of the files, do a manual, case-sensitive search for "Classic" in the files to remove the remaining instances. The script can't identify every permutation of Classic notes in our files.


<h3 id="handoff_files">Hand off the files</h3>

The article and image files need to be zipped and uploaded to the Localizers FTP server.

1. Zip the handoff folder and upload it to the Localizers FTP server using Cyberduck.

2. Notify Gerhard and Sabine that the handoff is up.

<!--
1. In the CLI, run the following command to create a zip file containing all the files:

	```bash
	$ python3 ho.py package {handoff_name} {product}
	```

	The only valid values for `product` (for now) are **explore**, **bime**, **help**, **chat**, or **support**.

	The command names the zip file **handoffname\_productname.zip** and places it in the handoff folder's root. Example:

	`/handoffs/2016-12-04/chat/2016-12-04_chat.zip`

2. Next, run the following command to upload the zip file to the Localizers FTP server:

	```bash
	$ python3 ho.py upload {handoff_name} {product}
	```

	If you get an error, make sure you specified the correct FTP settings in the **tools.ini** file. See [Configure Handoff Builder](#) in the setup doc. 

3. Notify Gerhard and Sabine that the handoff is up.
-->




<h3 id="update_map">Update the dita map</h3>

To do periodic mass updates of our content, we have to maintain a map of article ids and their corresponding DITA filenames. When we transform articles from DITA to HTML, the tool produces files named **filename.html**, such as **zug\_tags.html**. There's no information about the article's Help Center id. Without the map, we wouldn't know where to put the articles on Help Center.

1. Get a list of the *new* articles from the [loc handoff worksheet](https://docs.google.com/spreadsheets/d/1jldaCDT5iYrUdmzAT1jWwFbYOwGECVVcwK9agHJeGE8/edit#gid=0). Ignore the updated articles.

2. Navigate to the following folder in Team Drives:

	`Documentation/Zendesk User Guides/All products/production/`

3. Open the **ditamap.yml** file in a text editor.

4. Enter the following information for each article: DITA filename without the file extension, host Help Center, and article id. Example:

	```
    - dita: zug_placeholders
      hc: support
      id: 203662116
    - dita: zug_markdown
      hc: support
      id: 203661586
    ...
	```

	Make sure the article id is unique in the yml file. Also, don't include the **.dita** extension.


3. Save the file.

Rules:

* Indent lines as shown (it matters in yml)
* No EOL commas or quotation marks around strings
* No duplicate ids
* One yml item per article (indicated by the hyphen)
* No **.dita** file extension



<h3 id="prep_loc_content">Prep the localized content</h3>

After the localized content comes back from the localizers, you need to place the files in your handoff folder. You also need to scan the files to update the *links registry*. The links registry lists all the articles and images that are known to have been localized. It's used to update the links in the returned files.

Vendors ignore the HTML attributes in the files we hand off. That means the article and image links in the returned files still point to English destinations. The links registry is used to decide whether to update the links or not. If a link points to an article or image in the registry, then the link is updated. If not, the link is ignored.

1. In the folder with the other files for this handoff, create a folder named **localized**. Example:

	`handoffs/2016-12-14/support/localized/`

2. Copy the locale folders (DE, ES, FR, JA, PT) delivered by the vendor into this folder.

	**Tip**: Work with a copy of the returned files. In case something goes wrong and you need to revert, you can always make another copy of the original files.

	The folder structure should look as follows:

	```
	handoffs/
		2016-12-14/
			support/
			    articles/
			    images/
			    localized/
				    DE/
					    articles/
					    images/
				    ES/
					    articles/
					    images/

				    FR/
					    articles/
					    images/
	```

3. If the Portugese folder is named **PT**, change it to **PT-BR** so it matches the Help Center locale.

4. Check the **images** folder of each language to make sure the image files are in the root. Sometimes the folder will contain a **fullsize** and a **resized** folder. Move the images of these folders into the root and delete the subfolders.

5. Do a global search for and delete the tag `<!---delete---!>`, which is a translation artifact that screws up the parsing scripts.

6. In the CLI, navigate to the **zep** folder and run the following command to update the links registry:

	```bash
	$ python3 ho.py register {handoff_name} {product} --write
	```

	The only valid values for `product` (for now) are **explore**, **bime**, **help**, **chat**, or **support**. Example:

	```bash
	$ python3 ho.py register 2016-08-23 bime --write
	```

	The command adds new localized articles and images to the product-specific registry. Any links that point to these resources will be updated.

	**Recommended**: Do a dry run first to check for errors by omitting the `--write` argument. The results are displayed in the console but the registry isn't updated.

	The command also has the following optional arguments:
	* `articles` - add only articles to the registry
	* `images ` - add only images to the registry
	* `locales` - scans only the files in specific locale folders

	For example, to do a dry run of (1) scanning only the de and fr folders and (2) adding only new articles:

	```bash
	$ python3 ho.py register 2016-08-23 support --articles --locales de fr
	```


<h3 id="relink">Relink the files for Help Center</h3>

Before pushing the articles to Help Center, you need to update the article and image links where applicable. This applies only to links pointing to known localized content on Help Center. Because we don't track localized content outside Help Center, we can't automate the process of updating those links.

* In CLI, run the following command to update the article and image links in the articles:

	```bash
	$ python3 ho.py relink {handoff_name} {product} --write
	```

	The only valid values for `product` (for now) are **explore**, **bime**, **help**, **chat**, or **support**. Example:

	```bash
	$ python3 ho.py relink 2016-08-23 bime --write
	```

	The command updates article and image links.

	**Recommended**: Do a dry run first to check for errors by omitting the `--write` argument. The results are displayed in the console but the files aren't updated.

	The command also has the following optional arguments:
	* `hrefs` - update only article links (hrefs)
	* `srcs ` - update only image links (srcs)
	* `locales` - update only the files in specific locale folders

	For example, to do a dry run of updating only the article links in the es and pt-br folders:

	```bash
	$ python3 ho.py relink 2016-08-23 support --hrefs --locales es pt-br
	```


<h3 id="publish">Push the files to Help Center and S3</h3>

**Note**: If publishing to a new section in Help Center, make sure translations of the article's parent section exists (as well as translations of the section's parent category).


1. Use Cyberduck to upload all the images to the appropriate locale folders on s3.

2. In the CLI, run the following command to publish all the translations to Help Center:

	```bash
	$ python3 ho.py publish {handoff_name} {product} --write
	```

	The only valid values for `product` (for now) are **explore**, **bime**, **help**, **chat**, or **support**. Example:

	```bash
	$ python3 ho.py publish 2016-08-23 bime --write
	```

	**Recommended**: Do a dry run first to check for errors by omitting the `--write` argument. The results are displayed in the console but the files aren't actually published.

	The command also has a `locales` optional argument to publish only the content for a specific language or languages. Example:

	```bash
	$ python3 ho.py publish 2016-12-24 support --locales de es --write
	```

3. Notify the Docs team, Yoko Drain, and In Ju Hwang of the new translated articles.

4. Zip the handoff folder and upload it to **Team Drives/Documentation/All products/production/loc handoffs**.





