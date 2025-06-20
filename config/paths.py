PARENT_DIR=r"\\eosproject-smb\eos\project\h\hiradmat\HRMT Experiments\2025\HRMT68 - FIREBALL 3\FB3 repository\HRMT68_data"

LOG_PATH=r"H:\user\h\hramm\shot-log"

FOLDER_NAMES = {
            
            "ANDOR SPECTROMETER":r"tagged_data\\andor",
            "ORCA STREAK":r"orca_streak\\manual_save",
            
            "HRM3":"chromox_cameras\\HRM3",    
            "HRM4":"chromox_cameras\\HRM4",
            "HRM5":r"/Users/hayden/Desktop/FIREBALL/HRMT68_data/HRM5",
            "HRM6":"chromox_cameras\\HRM6",
            
            "SCOPE 1":r"/Users/hayden/Desktop/FIREBALL/HRMT68_data/scope_pool05710001",
            "SCOPE 2":"scope_pool05720010",
            
            "LDV":"ldv_and_strain_gauges\\Triggers\\2025\\06\\2",
            "PT100":"temperatures",

            "CHROMOX TEST":"plasmacell_cams"

    }

EXTENSION_DICT = {
            "ANDOR SPECTROMETER": ".asc",
            "ORCA STREAK": ".dac",
            "HRM3":".csv",    
            "HRM4":".csv",
            "HRM5":".csv",
            "HRM6":".csv",
            "SCOPE 1": ".csv",
            "SCOPE 2": ".csv",
            "SCOPE 3": ".csv",
            "LDV": ".tdms",
            "PT100": ".csv",
        }

SCOPECACHE_PATH = "scopecache"