***
## Getting Started
These are the README docs for the Fireball online data analysis framework.
- In order to check that the configuration is valid, navigate to the `./config` folder. 
	![[Screenshot 2025-07-03 at 11.48.26.png|250]]
- Then navigate to `paths.py`, which is inside of the config folder. ==Check that the directories listed in this folder are **correct for the computer/environment** where the code is being run==. By default, the repository is configured for a user accessing CERN's EOS service via the CERN SWAN service.
- In order to use the codebase on your local computer, you will need to download the Fireball-III data from [this link](https://cernbox.cern.ch/files/spaces/eos/project/h/hiradmat/HRMT%20Experiments/2025/HRMT68%20-%20FIREBALL%203/FB3%20repository/HRMT68_data?items-per-page=100&view-mode=resource-table-condensed&tiles-size=1&sort-by=name&sort-dir=desc) and **update the paths** in the `paths.py` file accordingly.
- The `background_shots.py` file is for users to store **UNIX timestamps** of shots that they would like to implement for background subtraction. Currently, background shots are specified from the `./main.ipynb` notebook's `input` variable (see "editing the input configuration" section below). However, it is trivial for users to modify the `main.ipynb` notebook to import shots from this `background_shots.py` file.
- After the path configuration has been checked, the user can move to running the code.
***
## Selecting Devices
- Navigate to the ==`./main.ipynb` **Jupyter Notebook**== in the parent directory.![[Screenshot 2025-07-01 at 17.51.02.png||250]]

- ==Edit the `device_names` list== in the **second cell** in order to specify which devices you would like analysis for.
	- ==Device names **must be spelled correctly**==. If you are unsure how to spell each device, navigate to ``./config/allowed_inputs.json`` and look under the `"DEVICE_NAME"` tab. 
	- Names are **CASE SENSITIVE**.
	![[Screenshot 2025-07-01 at 17.54.38.png]]


***
## Editing the Input Configuration
- Note that ==SWAN **does not** have native editing ability for `.json` files==.
- This means that I have replaced the `.json` with an input dictionary inside of the ``main.ipynb`` file, in cell 3.
	![[Screenshot 2025-07-01 at 17.57.28.png]]
- ==**DO NOT EDIT DIRECTORY INFORMATION**== IN THE INPUT CONFIGURATION DICTIONARY. This is set in the `./config/paths.py` configuration file (see above).
	![[Screenshot 2025-07-01 at 17.57.58.png|300]]

### What do each of the settings mean?
#### **Shot Selection**: 
Shot numbers can be specified by UNIX timestamp, as provided by the shot-log (see the section below, **Specifying by Timestamp- Details**) or via relative indexing, wherein supplying `[0, 1, 2]` would correspond to requesting the most-recent, second most-recent, and third most-recent shots by timestamp. Shot numbers must be passed as a list in both cases, even if only a single shot is desired. **==The code is not designed to allow mixing of relative indexing and UNIX timestamp==**.
- **`"EXP_SHOT_NOS"` *(List of integers)***: Foreground image shots (corresponding to interesting, non-background experimental conditions). As many shots as desired can be requested.
- **`"BKG_SHOT_NOS"` *(List of integers)***: Shot numbers corresponding to "background conditions", i.e. shots which we would like to subtract from the foreground images. If multiple shot numbers are supplied to this field, the code creates a composite "average" background image, which it then subtracts from the main image.
- **`"SPECIFY_TIMESTAMP_EXP"` *(Boolean)***: If `True`, then the code reads the integers passed to the  `EXP_SHOT_NOS` variables (specified above) as UNIX timestamps. If `False`, the code reads the integers in the relative-indexing manner (see above).
- **`"SPECIFY_TIMESTAMP_BKG"` *(Boolean)***: Identical to functionality of `"SPECIFY_TIMESTAMP_EXP"`, but dictates how the code handles the background shots.
- **``"BKG_NAME"`` *(String)***: Can be any string variable, which is the user-specified name of the background, if background shots are supplied. If background subtraction is requested, this `BKG_NAME` is displayed in the plot titles. If background subtraction is *not* requested, the string is passed to this variable will not be displayed, and the plots will be labelled "RAW".
- **``"BKG_STATUS"`` *(String)***: Specifies whether the background subtraction is being requested by the user. Note that ==**this can only take two values**: `"RAW"` or `"SUBTRACT"`==. `RAW` tells the code to not perform background subtraction, whereas `SUBTRACT` requests background subtraction from the code.

#### Operations Specifiers
- **`"PLOT_ONLY"` *(Boolean)***: If set to `True`, the code simply displays the requested shots (with or without background subtraction, as requested by user) without any analysis functions. This is to increase execution time for cases where we simply want to display the images.
- **`"NORM_PLOT"` *(True)***: If the device has methods for normalisation (dividing the image by the maximum pixel value), the normalised image is displayed and analysed.
- **`OPERATIONS` *(Dictionary)***:
	- **`"SHOW_SINGLESHOT_PLOTS"` *(Boolean)***: If set to `True`, the code will display each shot (with or without background subtraction, as specified by the user) individually. This was implemented to allow the user to skip displays from single shots if only the average data across several shots was desired (see below).
	- **`"LINEOUT_BIN_NO"` *(Integer)***: If the device's analysis method requires quantisation (i.e. is a chromox camera), this is the bin number requested for that quantisation. In order to produce radial and azimuthal marginals for the chromox images, a conversion from Cartesians $(x, y)$ to plane polar coordinates $(r, \theta)$ is necessary, and this is done via binning each pixel into a $r$ and $\theta$ band.
	- **``"SHOW_AVERAGE_SHOTS"`` *(Boolean)***: If `True`, the code will display the average (either raw or background-subtracted, as specified by the user) across all of the supplied `EXP_SHOT_NOS`. If only a single shot was supplied, this is identical to displaying the single shot alone.
	- **`"SUBTRACT_DC_OFFSET"` *(Boolean)***: If `True`, and if the device is a probe, this subtracts the mean value of voltage (amplitude) from the probe trace before analysis, which can help reduce spikes in the Fourier Transforms close to frequencies of 0.
	- **`"VMAX"` *(Integer)***: If the device uses a `plt.imshow()` method during analysis (i.e. is a chromox camera, Andor, or ORCA), this is the `VMAX` used during plotting.

#### Directory Information
These are ***not to be edited*** by the user, and are imported from external files (e.g. the `paths.py` files). These variables were introduced to reduce clutter in the `main.ipynb` file by removing input configuration variables that were not expected to change often (for example, paths to data).
- **`"PARENT_DIR"` *(String \[Path\])***: Path to the "parent directory" of all the data. This directory should look something like the following, where each subdirectory contains device data: 
	![[Screenshot 2025-07-03 at 12.35.10.png]]
- **`"LOG_PATH"` *(String \[Path\])***: Path to the shot-log. Online, the code uses this to store metadata from the ORCA and Andor devices.
- **`"FOLDER_NAMES"` *(Dictionary)***: Dictionary of each device's relative path, relative to the path provided in the `PARENT_DIR` variable above.
 - **`"EXTENSION_DICT"` *(Dictionary)***: Dictionary containing the file extension/file type for each device's raw data files.
- **`"TIMESTAMP_SLICE"` *(Dictionary)***: This was in case the tagging software we were planning to use in order to stamp filenames by cyclestamp had worked; the slice tuples provided in this dictionary would have told the code which part of the filename strings to look for cyclestamps in.
- **`"SCOPECACHE_PATH"` *(String)***: This is used to provide online subtraction between longitudinal channels for the downstream B-dot probe, which are split across two scopes. This works as follows: if both scopes are called in the `DEVICE_NAMES` list, the code will store relevant data from the first oscilloscope which is called, cache it at the `SCOPECACHE_PATH`, and keep it safe until the second oscilloscope is called. After the run, data in the scopecache is deleted.

***
## Specifying by Timestamp- Details
In order to check which timestamps correspond to which shots, navigate to the `./shot-log` directory:
	![[Screenshot 2025-07-03 at 11.58.54.png | 250]]
- Here, users can find a ==**summary of timestamps** for each device==. Note that these ==differ from the timestamps found in the experiment's overall shot log== in the CERNbox directory, for the following reasons:
	- The `shot-log` for this project was generated by scraping CERNbox directories for the time of most-recent modification, which corresponded to the **upload time** on CERNbox
	- This was **==different to the accelerator cycle UNIX timestamp==** due to latencies in upload.