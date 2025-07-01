PARENT_DIR=r"/eos/project/h/hiradmat/HRMT Experiments/2025/HRMT68 - FIREBALL 3/FB3 repository/HRMT68_data"

LOG_PATH=r"shot-log"

FOLDER_NAMES = {
            
            "ANDOR SPECTROMETER":r"tagged_data/andor",
            "ORCA STREAK":r"orca_streak/manual_save",
            
            "HRM3":r"chromox_cameras/HRM3",    
            "HRM4":r"chromox_cameras/HRM4",
            "HRM5":r"chromox_cameras/HRM5",
            "HRM6":r"chromox_cameras/HRM6",
            
            "SCOPE 1":"scope_pool05710001",
            "SCOPE 2":"scope_pool05720010",

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
        }

SCOPECACHE_PATH = "scopecache"