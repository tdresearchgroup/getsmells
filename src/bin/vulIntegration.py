import csv
import os
from collections import OrderedDict
import configparser
from src import DEFAULT_OUTPUT, PROJECT_PATH


def combineVul(vulPaths):
    """
    It combines vuls and smells together.
    The smells csv file should be in default location generated by main.py

    :param vulPaths: csv file contained in config.ini
    :return: None
    """

    print("Start combining vulnerability data")

    outDir = os.path.join(DEFAULT_OUTPUT, "smell&vul")
    if not os.path.exists(outDir):
        os.makedirs(outDir)

    for projName, vulPath in vulPaths:
        print(f"Start combining '{projName}' vulnerability data")
        smellPath = os.path.join(DEFAULT_OUTPUT, 'smells', projName+'.csv')
        outPath = os.path.join(outDir, projName+'.csv')

        if not os.path.isfile(vulPath):
            print(f"ERROR: Vulnerability data does not exist in path '{vulPath}', skip.")
            continue
        if not os.path.isfile(smellPath):
            print(f"ERROR: Vulnerability data does not exist in path '{smellPath}', skip.")
            continue

        with open(outPath, 'w') as out, open(smellPath, 'r') as smellIn, open(vulPath, 'r') as vulIn:
            smellReader = csv.DictReader(smellIn)
            vulReader = csv.DictReader(vulIn)

            header = getOrderedHeader(list(vulReader.fieldnames) + list(smellReader.fieldnames))

            smellDict = {(x['Name'], x['Version']): x for x in smellReader}
            vulDict = {(x['Name'], x['Version']): x for x in vulReader}

            for k, v in vulDict.items():
                if k in smellDict:
                    smellDict[k].update(v)
                else:
                    print(f"WARN: {k} pair is not in smell data")

            writer = csv.DictWriter(out, fieldnames=header, delimiter=",")
            writer.writeheader()
            writer.writerows(smellDict.values())


def getOrderedHeader(header):
    return list(OrderedDict.fromkeys(header))


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read(os.path.join(PROJECT_PATH, 'config.ini'))
    combineVul(config.items('vulIntegration.vulPath'))
