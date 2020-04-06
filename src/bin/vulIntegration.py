import argparse
import csv
import os
import re

VERSION_RE = '[0-9]+.[0-9]+.[0-9]+'


def combineVul(vulDir, smellsOutDir):
    """
    It recursively walk through smellsOutDir.
    For each [proj]-[version]-xxx-overall.csv, generate csv file that maps the counts of vulnerabilities and smells together.

    Pre-requisite: smellsOutDir should be the same as the "main.py -> main -> outputPath".
    Each vulnerability file should be named as [proj].csv and should contain at least "name" and "version" columns

    :param vulDir: the directory contains all vulnerability data.
    :param smellsOutDir: the directory contains "smells" dir
    :return: None
    """
    print("Start combining vulnerability data")
    overalls = _getSmellOveralls(smellsOutDir)

    outDir = os.path.join(smellsOutDir, "smell&vul")
    if not os.path.exists(outDir):
        os.makedirs(outDir)

    for smellPath in overalls:
        project, version = _getProjInfo(smellPath)
        vulPath = os.path.join(vulDir, f"{project}.csv")
        outPath = os.path.join(outDir, f"{project}-{version}.csv")

        if not os.path.exists(vulPath):
            print(f'WARNING: Vulnerability data file for {project} does not exist. Skip.')
            continue
        with open(outPath, 'w') as out, open(smellPath, 'r') as smellIn, open(vulPath, 'r') as vulIn:

            smellReader = csv.DictReader(smellIn)
            vulReader = csv.DictReader(vulIn)
            updatedSmellDict = _getUpdatedSmellDict(smellReader, vulReader, project, version)

            columnNames = ['version'] + smellReader.fieldnames + ['Vulnerability']
            writer = csv.DictWriter(out, fieldnames=columnNames, delimiter=",")
            writer.writeheader()
            writer.writerows(updatedSmellDict.values())
    print("Combining vulnerability data done")


def _getUpdatedSmellDict(smellReader, vulReader, project, version):
    smells = {x['Name']: x for x in smellReader}
    for rows in smells.values():
        rows['version'] = version

    for vulRow in vulReader:
        if vulRow['version'].startswith(version):
            if vulRow['class'] in smells:
                smells[vulRow['class']]['Vulnerability'] = smells[vulRow['class']].get('Vulnerability', 0) + 1
            else:
                print(f"{vulRow['class']} not in {project}-{version} smell file. Something must be wrong")
    return smells


def _getSmellOveralls(smellsOutDir):
    overalls = []
    for root, dirs, files in os.walk(smellsOutDir):
        for file in files:
            if file.endswith('-overall.csv'):
                overalls.append(os.path.join(root, file))
    return overalls


def _getProjInfo(overallPath):
    filename = os.path.basename(overallPath)

    version = re.compile(VERSION_RE).search(filename)

    if version:
        version = version.group(0)
        project = filename.split(f"-{version}-")[0]
    else:
        raise Exception(f"Output file name({filename}) is wrong format. Cannot fetch version/project pair. "
                        f"Please see README for more information.")

    return project, version


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--smellDir", help="The output smell directory generated by main.py")
    parser.add_argument("-v", "--vulDir", help="The directory contains all vulnerability data")

    args = parser.parse_args()
    combineVul(args.vulDir, args.smellDir)
