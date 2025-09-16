import os
from PIL import Image

import torchvision.transforms as transforms
from torch.utils.data.dataset import Dataset


def get_file_paths(folder_path, label):
    # Read paths and append them with their corresponding label as a tuple
    files = []
    for name in os.listdir(folder_path):
        full_path = os.path.join(folder_path, name)
        if os.path.isfile(full_path):
            files.append((full_path, label))
    return files


class SpurBreastDataset(Dataset):
    def __init__(self, data_folder, spurious_feature, tr_val_ts, aug=None):
        # Folder paths
        pos_im_folder = os.path.join(data_folder, spurious_feature, tr_val_ts, '1')
        neg_im_folder = os.path.join(data_folder, spurious_feature, tr_val_ts, '0')

        # Read images
        pos_images = get_file_paths(pos_im_folder, 1)
        neg_images = get_file_paths(neg_im_folder, 0)

        # Add paths
        self.image_label_list = []
        self.image_label_list.extend(pos_images)
        self.image_label_list.extend(neg_images)

        # Dataset size
        self.im_cnt = len(self.image_label_list)

        # Augs
        self.aug = aug
        print('SpurBreast', tr_val_ts ,'dataset initialized with', self.im_cnt,
              'images.', 'Spurious feature:', spurious_feature)

    def __getitem__(self, index):
        im_path, label = self.image_label_list[index]
        im_name = im_path[im_path.rfind('/'):-4]
        _, slice_id, patient_id = im_name.split('-')

        # Read image
        im = Image.open(im_path).convert('RGB')

        # Apply augmentation
        im = self.aug(im)

        # Return
        return im, label, (im_path, patient_id, slice_id, index)

    def __len__(self):
        return self.im_cnt


if __name__ == '__main__':
    data_folder = '../data/'
    spurious_features = ['field_strength', 'menopause',
                         'race_and_ethnicity', 'surgery_type',
                         'vertical_flip']
    selected_feature = 0  # e.g., field_strength
    spurious_feature = spurious_features[selected_feature]

    # Here is some training augmentation
    default_tr_aug = transforms.Compose([
            transforms.Resize([256, 256]),
            transforms.RandomResizedCrop(224),
            transforms.ToTensor()
    ])

    split = 'training'
    tr_dataset = SpurBreastDataset(data_folder, spurious_feature, split, default_tr_aug)

    default_ts_aug = transforms.Compose([
            transforms.Resize([224, 224]),
            transforms.ToTensor()
    ])

    split = 'validation'
    val_dataset = SpurBreastDataset(data_folder, spurious_feature, split, default_ts_aug)

    split = 'test'
    ts_dataset = SpurBreastDataset(data_folder, spurious_feature, split, default_ts_aug)

    # Example output of from the dataset
    im, label, others = tr_dataset[0]
