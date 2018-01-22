import understand
import sys
# https://scitools.com/sup/api-2/
# https://scitools.com/documents/manuals/python/understand.html
# help (understand)

print("hello!")

db = understand.open("C:\\Users\\cb1782\\MyUnderstandProject.udb")

def getATFD(classObj):
    classATFD = 0
    for amethod in aclass.ents("Define", "Method"):
        # https://scitools.com/documents/manuals/html/understand_api/wwhelp/wwhimpl/js/html/wwhelp.htm
        # https://scitools.com/documents/manuals/html/understand_api/wwhelp/wwhimpl/js/html/wwhelp.htm
        # NOTE: Includes all foreign methods called, even if not a getter or setter
        for aent in amethod.ents("Call, Use, Set", "Method ~unresolved ~unknown, Variable ~unresolved ~unknown"):
            if aclass.longname() not in aent.longname():
                classATFD += 1
    return classATFD


def getWMC(classObj):
    return classObj.metric(["SumCyclomaticModified"])['SumCyclomaticModified'] or 0


def getTCC(classObj):
    methods = aclass.ents("Define", "Method")
    numberOfPairs = 0
    numberOfShares = 0
    for x in range(0, len(methods)):
        for y in range(x+1, len(methods)):
            numberOfPairs += 1
            atrrsAccessedInMethodX = methods[x].ents("Use, Set", "Variable ~unresolved ~unknown")
            atrrsAccessedInMethodY = methods[y].ents("Use, Set", "Variable ~unresolved ~unknown")
            atrrsAccessedInMethodXNames = set()
            atrrsAccessedInMethodYNames = set()
            for attr in atrrsAccessedInMethodX:
                atrrsAccessedInMethodXNames.add(attr.longname())
            for attr in atrrsAccessedInMethodY:
                atrrsAccessedInMethodYNames.add(attr.longname())
            commonAttrs = atrrsAccessedInMethodXNames.intersection(atrrsAccessedInMethodYNames)
            for atrrName in commonAttrs:
                if aclass.longname() in atrrName:
                    numberOfShares += 1
                    break
    if numberOfPairs == 0:
        # NOTE: Default is currently 1.0
        return 1.0
    else:
        return (numberOfShares/numberOfPairs)*1.0


godClasses = set()

for aclass in db.ents("Class"):
    classLongName = aclass.longname()

    # ---- Get Metrics ----
    classMetricATFD = getATFD(aclass)
    classMetricWMC = getWMC(aclass)
    classMetricTCC = getTCC(aclass)

    # ---- Determine Code Smells ----
    # TODO: Use non-constant values

    # God Class
    # - ATFD (Access to Foreign Data) > Few
    # - WMC (Weighted Method Count) >= Very High
    # - TCC (Tight Class Cohesion) < 1/3
    classSmellGod = (classMetricATFD > 10) and (classMetricWMC >= 50) and (classMetricTCC < 0.33)

    if classSmellGod:
        godClasses.add(classLongName)

    print("God Class = " + str(classSmellGod) + "\tATFD = " + str(classMetricATFD) + "\tWMC = " + str(classMetricWMC) + "\tTCC = " + str(classMetricTCC) + "\t" + classLongName)

print("God Classes (count = " + str(len(godClasses)) + "):")
print(godClasses)
