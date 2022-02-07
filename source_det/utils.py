
import tqdm, os
import pandas as pd

def csv2txts(csv_file, txts_folder, format="xyxy", score=False, save_noobj=False):
    if not os.path.exists(txts_folder):
        os.mkdir(txts_folder)

    df = pd.read_csv(csv_file)
    image_ids = list(df["image_id"].unique())
    for image_id in tqdm.tqdm(image_ids):
        image_df = df[df["image_id"] == image_id]
        image_annotations = []
        for i in range(len(image_df)):
            item = image_df.iloc[i]

            class_id = item["class_id"]
            if class_id != 14:
                x_min, y_min, x_max, y_max = item["x_min"], item["y_min"], item["x_max"], item["y_max"]
                if format == "xyxy":
                    annotation = [x_min, y_min, x_max, y_max, class_id]
                    line = "{:4} {:4} {:4} {:4} {:2}"
                else:
                    x_center, y_center, width, height = (x_min + x_max)/2, (y_min + y_max)/2, (x_max - x_min), (y_max - y_min)
                    x_center, y_center, width, height = x_center/item["image_width"], y_center/item["image_height"], width/item["image_width"], height/item["image_height"]
                    annotation = [x_center, y_center, width, height, class_id]
                    line = "{:.6f} {:.6f} {:.6f} {:.6f} {:2}"

                if score:
                    annotation.append(item["score"])
                    line += " {:.6f}"
                image_annotations.append(annotation)

        if len(image_annotations) > 0:
            with open("{}/{}.txt".format(txts_folder, image_id), "w") as f:
                for annotation in image_annotations:
                    f.write("%s\n" % line.format(*annotation))
        else:
            if save_noobj:
                with open("{}/{}.txt".format(txts_folder, image_id), "w") as f:
                    if score:
                        f.write("%s\n" % line.format(*(0, 0, 1, 1, 14, 1)))
                    else:
                        f.write("%s\n" % line.format(*(0, 0, 1, 1, 14)))

def txts2csv(txts_folder, csv_file, score=False):
    image_ids = [s.split(".")[0] for s in os.listdir(txts_folder)]

    return_df = []
    for image_id in tqdm.tqdm(image_ids):
        with open("{}/{}.txt".format(txts_folder, image_id)) as f:
            lines = f.read().splitlines()
        for line in lines:
            if score:
                x_min, y_min, x_max, y_max, class_id, score = line.split()
                return_df.append({
                    "image_id": image_id, 
                    "x_min": int(x_min), "y_min": int(y_min), "x_max": int(x_max), "y_max": int(y_max), "class_id": int(class_id), "score": float(score), 
                    "image_width": -1, "image_height": -1, 
                })
            else:
                x_min, y_min, x_max, y_max, class_id = line.split()
                return_df.append({
                    "image_id": image_id, 
                    "x_min": int(x_min), "y_min": int(y_min), "x_max": int(x_max), "y_max": int(y_max), "class_id": int(class_id), 
                    "image_width": -1, "image_height": -1, 
                })

    return_df = pd.DataFrame(return_df)
    return_df.to_csv(csv_file, index=False)