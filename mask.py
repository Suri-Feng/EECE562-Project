from re import L
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import read_excel
import glob
import os


class area:
    # DONE
    def __init__(self, df_excel, clip_name):
        self.c = read_excel.clip_info(df_excel, clip_name)
        # "data/task_a01_5ml-l0-5-2021_06_04_08_51_29-segmentation mask 1.1/SegmentationObject/"
        data_dir = os.path.join(os.path.abspath(os.getcwd()), "data", "*")
        data_file_names = glob.glob(data_dir)
        for i in range(len(data_file_names)):
            if clip_name in data_file_names[i]:
                self.mask_folder_path = os.path.join(
                    data_file_names[i], "SegmentationObject", "*"
                )
                break

        self.start = self.c.zero_frame
        self.end = self.c.last_frame
        self.T = self.end - self.start + 1
        self.mask_frame_path = np.zeros(self.T)
        self.masks = self.get_masks()  # T*W*H
        self.all_frame_area_in_cm2 = self.get_all_frame_area()  # T*1

    # TODO
    def get_masks(self):
        mask_dir = glob.glob(self.mask_folder_path)
        mask_dir.sort()
        W, H = Image.open(mask_dir[0]).size
        masks_gray = np.zeros((self.T, W, H))
        for i in range(self.T):
            image = Image.open(mask_dir[self.start + i])
            data = np.transpose(np.asarray(image), (1, 0, 2))
            data_gray = 1 / 3 * (data[:, :, 0] + data[:, :, 1] + data[:, :, 2])
            masks_gray[i, :, :] = data_gray
        return masks_gray

    # DONE
    def get_all_frame_area(self):
        # 500 pixels -> 10 cm; 2500 pixel^2 -> 1cm^2
        return np.count_nonzero(self.masks.reshape(self.T, -1), axis=1) / 2500

    # DONE
    def frame_area(self, frame_num):
        return self.all_frame_area_in_cm2[frame_num - self.start]

    # DONE
    def percentage(self, frame_s, frame_l):
        return (
            self.all_frame_area_in_cm2[frame_l - self.start]
            - self.all_frame_area_in_cm2[frame_s - self.start]
        ) / self.all_frame_area_in_cm2[frame_l - self.start]

    # TODO
    def find_min_or_max_extreme_area(self):
        # max_value = np.max(data)
        pass


if __name__ == "__main__":
    excel_name = "A.xlsx"
    r_e = read_excel.r_excel(excel_name)

    clip_name = "a01_5ml-l0-5"
    r_c = read_excel.clip_info(r_e.df_excel, clip_name)

    a = area(r_e.df_excel, clip_name)
    gh_onset, gh_maximum = (
        int(r_c.df_clip["GHR"].iloc[0]),
        int(r_c.df_clip["GHM"].iloc[0]),
    )
    gh_onset_area = a.frame_area(gh_onset)
    gh_maximum_area = a.frame_area(gh_maximum)
    cal_percentage = a.percentage(gh_maximum, gh_onset)
    print(gh_onset, gh_maximum_area, cal_percentage)

