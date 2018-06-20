## Republishing from DITA source files

This article describes how to use Oxygen Author and the Zendesk production tools (ZEP) to transform DITA source files, then push the transformed articles to Help Center.

* [Transforming the articles](#transform)
* [Pushing the transformed articles](#push)

This is a specialized process used internally by the Zendesk Docs team.

For zep installation instructions, see [Setting up the Zendesk production tools](https://support.zendesk.com/hc/en-us/articles/215841938).


<!--
title: Republishing from DITA source files
url: https://support.zendesk.com/hc/en-us/articles/217117137
source: Zendesk Internal/Zendesk User Guides/production/zep/docs/managing_articles.md
-->


<h3 id="transform">Transforming the articles</h3>

1. If not already done, clean up the previous transformation project:
	* In Author, select **Project** > **Open Project**, navigate to `/production/staging/dita_source_files/`, then select the file named **user_docs.xpr** to open the project.
	* In the Author interface, click the **Project** tab in the sidebar to slide it open.
	* If the project has folders from a previous project, right-click the folder and select **Remove from Project**.
	* In Finder, archive or delete the old folders.

2. In Finder, create a new folder for the DITA files in `/dita_source_files/`. Example: **admin_guide**.

3. In Finder, copy all the DITA files you want to transform to the new folder.
	
4. If applicable, copy the **reusable_content** folder into the folder with the files.

	If you skip this step, conref'ed content won't be included in the HTML output.
	
5. If applicable, copy the **links.dita** file into the folder with the files.

	If you skip this step, some links will be blank in the HTML output.

5. In Author, click the **Project** tab in the sidebar to open it.

6. Right-click the **user_docs.xpr** file, select **Add Folder**, and choose your new folder to add it to the project.

	Tip: If the files don't appear in the project at first, right-click the project folder and click **Refresh**.

7. Still in the the Project view, open the folder and select the files you want to transform. 

	**Note**: Make sure any non-dita files are deselected.

8. Right-click the selected files and select **Transform** > **Transform With**, then choose **DITA XHTML (exclude Classic)** and click **Apply Selected Scenario**.

	The files are transformed but not opened in a browser. The HTML files are created in the folder named **out** in the folder's root. Example:
	
	`/staging/dita_source_files/admin_guide/out/`
	
	The html files will still have dita file names. That's okay. Examples:
	* zug\_sysreqs.html
	* zug\_tags.html
	* zug\_targets\_yammer.html

9. Spot test the HTML files.

	Look for problems like double links, missing conrefs, and any other wackiness caused by the transformation.

10. When satisfied, move the batch of html files to the following folder in your staging folder:

	`/staging/transformed_files/{your_folder}`
	
	where `{your_folder}` is a folder you created specifically for this push.

	**Note**: Make sure to archive or delete any transformed files from a previous project before moving the new files.


<h3 id="push">Pushing the transformed articles</h3>

This section describes how to push the transformed articles to Help Center.

Before you start, make sure you place the latest **ditamap.yml** file in the following folder:

`/production/staging/dita_map/ditamap.yml`

ZEP needs to refer to the dita map so it can get each article's Help Center id.

Get the latest **ditamap.yml** from the Documentation Team Drive (/Documentation/All products/production/).

Also make sure the following folder exists on your hard drive:

`/production/reports/publishing`

The tool prints a report of the push results (json and xlsx versions) in this folder. 

1. In the CLI, run the following command:

    ```
    $ python3 hc.py push_dita_html {folder_name} --write
    ```

    where `{folder_name}` is the name of the folder with transformed files in "production/staging/transformed_files/".

    The command checks each file in the folder to see if the article is in the dita map (so it can get the article's corresponding Help
Center and id). If the article passes the test, it's pushed to Help Center.

	**Recommended**: Omit the `--write` argument to do a dry run to check for errors. The results are displayed in the console but the files aren't actually push to Help Center.

    Example:

    ```bash
	$ python3 hc.py push_dita_html my_files
	```


