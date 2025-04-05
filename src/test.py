# module imports
import sys

sys.path.append(".")

import devices.device as dev
import devices.output as outp

def main():
    
    shot_no = 1
    cam_name = f"HRM3 (SHOT {shot_no})"
    data_path = "./example_data/HRM3.DigiCam_OD0_1714383312791697_1714383306135000.csv"

    outputs = []
    image = outp.Image(
        shot_no=shot_no,
        device_name=cam_name,
        output_name="image",
        data_path=data_path
    )
    outputs.append(image)

    camera = dev.Device(
        device_name=cam_name,
        shot_no=shot_no,
        outputs=outputs
    )

    camera.call_analysis()
    

if __name__ == "__main__":
    main()