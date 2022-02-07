
import tqdm
import numpy as np, pandas as pd

def perturb_annotations(csv_file, skill_level):
    df = pd.read_csv(csv_file)
    image_ids = list(df["image_id"].unique())

    return_df = []
    for image_id in tqdm.tqdm(image_ids):
        image_df = df[df["image_id"] == image_id]

        for i in range(len(image_df)):
            item = image_df.iloc[i]
            x_min, y_min, x_max, y_max, class_id = item["x_min"], item["y_min"], item["x_max"], item["y_max"], item["class_id"]

            if class_id != 14:
                perturbed_std, classes = (1 - skill_level)*0.1*320, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 14]
                perturbed_x_min, perturbed_y_min, perturbed_x_max, perturbed_y_max = int(np.random.normal(x_min, perturbed_std)), int(np.random.normal(y_min, perturbed_std)), int(np.random.normal(x_max, perturbed_std)), int(np.random.normal(y_max, perturbed_std))
                perturbed_x_min, perturbed_y_min, perturbed_x_max, perturbed_y_max = np.clip(perturbed_x_min, 0, 319), np.clip(perturbed_y_min, 0, 319), np.clip(perturbed_x_max, 0, 319), np.clip(perturbed_y_max, 0, 319)
                if np.random.random() <= skill_level:
                    return_df.append({
                        "image_id": image_id, 
                        "x_min": perturbed_x_min, "y_min": perturbed_y_min, "x_max": perturbed_x_max, "y_max": perturbed_y_max, "class_id": class_id, 
                        "image_width": item["image_width"], "image_height": item["image_height"], 
                    })
                else:
                    classes.remove(class_id)
                    perturbed_class_id = int(np.random.choice(classes, 1)[0])
                    if perturbed_class_id != 14:
                        return_df.append({
                            "image_id": image_id, 
                            "x_min": perturbed_x_min, "y_min": perturbed_y_min, "x_max": perturbed_x_max, "y_max": perturbed_y_max, "class_id": perturbed_class_id, 
                            "image_width": item["image_width"], "image_height": item["image_height"], 
                        })
            else:
                return_df.append({
                    "image_id": image_id, 
                    "x_min": x_min, "y_min": y_min, "x_max": x_max, "y_max": y_max, "class_id": class_id, 
                    "image_width": item["image_width"], "image_height": item["image_height"], 
                })

    return_df = pd.DataFrame(return_df)
    return_df.to_csv(csv_file.replace(".csv", "_perturbed.csv"), index=False)