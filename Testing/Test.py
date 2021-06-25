import os
import numpy as np
import pandas as pd
from Main_For_Testing import image_reading, image_compression
import pickle
import sys

Brute_Force_Trials = 1
Genetic_Algorithm_Trials = 10


def Test():
    if not os.path.exists('.Stored_Parameters.pkl'):
        Stored_Parameters_File = open('Stored_Parameters.pkl', 'wb')
        Stored_Parameters = {
            "Dataset": os.listdir("../Dataset/"),
            "Dataset_Index": 0,
            "Brute_Force_Index": 0,
            "Genetic_Algorithm_Index": 0,
            "Records": [], }
        pickle.dump(Stored_Parameters, Stored_Parameters_File)
        Stored_Parameters_File.close()

    Stored_Parameters_File = open('Stored_Parameters.pkl', 'rb')
    Stored_Parameters = pickle.load(Stored_Parameters_File)
    Stored_Parameters_File.close()

    if len(Stored_Parameters["Records"]):
        print("=" * 150)
        print("Expected Remaining Time: " + str(
            np.mean([X["Execution_Time"] for X in Stored_Parameters["Records"]]) * (
                    len(Stored_Parameters["Dataset"]) - Stored_Parameters["Dataset_Index"]) * (
                    Brute_Force_Trials + Genetic_Algorithm_Trials) / (60.0 * 60.0 * 24.0)) + " Days")
        print("=" * 150)

    for Stored_Parameters["Dataset_Index"] in range(Stored_Parameters["Dataset_Index"],
                                                    len(Stored_Parameters["Dataset"])):
        file = "../Dataset/" + Stored_Parameters["Dataset"][Stored_Parameters["Dataset_Index"]]
        if not (file.endswith("gif") or file.endswith("png")):
            continue
        for Stored_Parameters["Brute_Force_Index"] in range(Stored_Parameters["Brute_Force_Index"],
                                                            Brute_Force_Trials):
            Stored_Parameters["Records"] += [
                image_compression(image_reading(file), file, use_genetic_algorithm=False, debug=False)]
            print(str(1 + Stored_Parameters["Dataset_Index"]) + ":BF(" + str(
                1 + Stored_Parameters["Brute_Force_Index"]) + "):" + str(
                Stored_Parameters["Records"][
                    Stored_Parameters["Dataset_Index"] * (Brute_Force_Trials + Genetic_Algorithm_Trials) +
                    Stored_Parameters["Brute_Force_Index"]]), flush=True)

            Stored_Parameters_File = open('Stored_Parameters.pkl', 'wb')
            pickle.dump(Stored_Parameters, Stored_Parameters_File)
            Stored_Parameters_File.close()

        Stored_Parameters["Brute_Force_Index"] = Brute_Force_Trials

        for Stored_Parameters["Genetic_Algorithm_Index"] in range(Stored_Parameters["Genetic_Algorithm_Index"],
                                                                  Genetic_Algorithm_Trials):
            Stored_Parameters["Records"] += [
                image_compression(image_reading(file), file, use_genetic_algorithm=True, debug=False)]
            print(str(1 + Stored_Parameters["Dataset_Index"]) + ":GA(" + str(
                1 + Stored_Parameters["Genetic_Algorithm_Index"]) + "):" + str(
                Stored_Parameters["Records"][
                    Stored_Parameters["Dataset_Index"] * (
                            Brute_Force_Trials + Genetic_Algorithm_Trials) + Brute_Force_Trials +
                    Stored_Parameters["Genetic_Algorithm_Index"]]), flush=True)

            Stored_Parameters_File = open('Stored_Parameters.pkl', 'wb')
            pickle.dump(Stored_Parameters, Stored_Parameters_File)
            Stored_Parameters_File.close()

        Stored_Parameters["Brute_Force_Index"] = 0
        Stored_Parameters["Genetic_Algorithm_Index"] = 0

        Stored_Parameters_File = open('Stored_Parameters.pkl', 'wb')
        pickle.dump(Stored_Parameters, Stored_Parameters_File)
        Stored_Parameters_File.close()

    Stored_Parameters["Dataset_Index"] = len(Stored_Parameters["Dataset"])

    Stored_Parameters_File = open('Stored_Parameters.pkl', 'rb')
    Stored_Parameters = pickle.load(Stored_Parameters_File)
    Stored_Parameters_File.close()

    df = pd.DataFrame.from_dict(Stored_Parameters["Records"])
    df.to_excel('Testing Records.xlsx')


def Flush_Outputs():
    if not os.path.exists('../Project Outputs/Outputs.pkl'):
        Stored_Parameters_File = open('Stored_Parameters.pkl', 'rb')
        Stored_Parameters = pickle.load(Stored_Parameters_File)
        Stored_Parameters_File.close()

        Outputs_File = open('../Project Outputs/Outputs.pkl', 'wb')
        Outputs = {
            "Dataset": [file for file in os.listdir("../Dataset/") if file.endswith(('.gif', '.png'))],
            "Records": Stored_Parameters["Records"],
            "Images": [],
        }
        pickle.dump(Outputs, Outputs_File)
        Outputs_File.close()

        Outputs_File = open('../Project Outputs/Outputs.pkl', 'rb')
        Outputs = pickle.load(Outputs_File)
        Outputs_File.close()

        Image_Index = 0
        for Image in Outputs["Dataset"]:
            print(Image + ":")
            Image_Records = [Record for Record in Outputs["Records"] if Record["File_Name"] == str("Dataset/" + Image)]
            for Record in Image_Records:
                print(Record)
            Outputs["Images"] += [{
                "File_Name": str("Dataset/" + Image),
                "Image_Width": Image_Records[0]["Image_Width"],
                "Image_Height": Image_Records[0]["Image_Height"],
                "Number_of_Possible_Block_Sizes": Image_Records[0]["Number_of_Possible_Block_Sizes"],
                "BF_Max_CR": np.mean(
                    [X["Max_CR"] for X in Image_Records if X["Brute_Force"] is True]),
                "BF_Execution_Time": np.mean(
                    [X["Execution_Time"] for X in Image_Records if X["Brute_Force"] is True]),
                "Average_GA_Max_CR": np.mean(
                    [X["Max_CR"] for X in Image_Records if X["Genetic_Algorithm"] is True]),
                "Average_GA_Execution_Time": np.mean(
                    [X["Execution_Time"] for X in Image_Records if X["Genetic_Algorithm"] is True]),
                "Average_GA_Generations_Counter": np.mean(
                    [X["Generations_Counter"] for X in Image_Records if X["Genetic_Algorithm"] is True]),
            }]
            print(Outputs["Images"][Image_Index])
            Image_Index += 1

        Outputs_File = open('../Project Outputs/Outputs.pkl', 'wb')
        pickle.dump(Outputs, Outputs_File)
        Outputs_File.close()

    Outputs_File = open('../Project Outputs/Outputs.pkl', 'rb')
    Outputs = pickle.load(Outputs_File)
    Outputs_File.close()

    Records_DataFrame = pd.DataFrame.from_dict(Outputs["Records"])
    print(Records_DataFrame)
    Records_DataFrame.to_excel('../Project Outputs/Flushed Outputs/Records.xlsx')

    Images_DataFrame = pd.DataFrame.from_dict(Outputs["Images"])
    print(Images_DataFrame)
    Images_DataFrame.to_excel('../Project Outputs/Flushed Outputs/Images.xlsx')


if __name__ == "__main__":
    # Test()
    # Flush_Outputs()
    pass
