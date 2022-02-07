
import tqdm
import pandas as pd
import ensemble_boxes

def weighted_boxes_fuse(csv_file, weights_dict=None):
    df = pd.read_csv(csv_file)
    image_ids = list(df["image_id"].unique())

    return_df = []
    for image_id in tqdm.tqdm(image_ids):
        image_df = df[df["image_id"] == image_id]

        max_coordinate_value = image_df.loc[:, ["x_min", "y_min", "x_max", "y_max"]].values.max()
        image_df.loc[:, ["x_min", "y_min", "x_max", "y_max"]] /= max_coordinate_value

        image_annotations = {}
        weights = []
        for _, annotation in image_df.iterrows():
            rad_id = annotation["rad_id"]
            if rad_id not in image_annotations:
                image_annotations[rad_id] = {
                    "boxes_list": [], "labels_list": [], "scores_list": []
                }
                weights.append(weights_dict[rad_id]) if weights_dict is not None else weights.append(1.0)
            image_annotations[rad_id]["boxes_list"].append([annotation["x_min"], annotation["y_min"], annotation["x_max"], annotation["y_max"]]), image_annotations[rad_id]["labels_list"].append(annotation["class_id"]), image_annotations[rad_id]["scores_list"].append(annotation["score"])

        boxes_list, labels_list, scores_list = [], [], []
        for rad_id in image_annotations.keys():
            boxes_list.append(image_annotations[rad_id]["boxes_list"]), labels_list.append(image_annotations[rad_id]["labels_list"]), scores_list.append(image_annotations[rad_id]["scores_list"])

        boxes, labels, scores = ensemble_boxes.weighted_boxes_fusion(
            boxes_list, labels_list, scores_list
            , weights=weights, iou_thr=0.5
        )
        for box, label, score in zip(boxes, labels, scores):
            return_df.append({
                "image_id": image_id, 
                "x_min": int(round(box[0]*max_coordinate_value)), "y_min": int(round(box[1]*max_coordinate_value)), "x_max": int(round(box[2]*max_coordinate_value)), "y_max": int(round(box[3]*max_coordinate_value)), "class_id": int(label), "score": float(round(score*3)), 
                "rad_id": "wbf", 
                "image_width": image_df["image_width"].unique()[0], "image_height": image_df["image_height"].unique()[0], 
            })

    return_df = pd.DataFrame(return_df)
    return_df.to_csv(csv_file.replace(".csv", "_wbf.csv"), index=False)