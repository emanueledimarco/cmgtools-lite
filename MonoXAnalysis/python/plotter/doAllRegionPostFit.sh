#!/bin/bash/

selstep=""
variable=""
lumi=""
other_options=""  # read from user

if [[ "X$1" == "X" ]]; then echo "Provide selection step!"; exit; fi
selstep="$1"; shift;
if [[ "X$1" == "X" ]]; then echo "Provide variables to use for shape analyis!"; exit; fi
variable="$1"; shift;
echo "Will do postfit plots for ${variable}"
if [[ "X$1" == "X" ]]; then echo "Provide luminosity!"; exit; fi
lumi="$1"; shift;
echo "MC components will be normalized to ${lumi}/fb"

if [[ "X$1" != "X" ]]; then
    other_options="$1"; shift;
    echo "These options were passed: ${other_options}"
fi

# if no data in SR (because you are blinding) keep SR line commented

# SR
#python postFitPlots.py vbfdm/mca-80X-sync.txt templates/SR/${selstep}/plots.root ${variable} templates/cards/${selstep}/${variable}/125.0/mlfit.root SR -l ${lumi} ${other_options}
# ZM CR
echo "python postFitPlots.py vbfdm/mca-80X-muonCR.txt templates/ZMCR/${selstep}/plots.root ${variable} templates/cards/${selstep}/${variable}/125.0/mlfit.root ZM -l ${lumi} ${other_options}" | bash
# WM
echo "python postFitPlots.py vbfdm/mca-80X-muonCR.txt templates/WMCR/${selstep}/plots.root ${variable} templates/cards/${selstep}/${variable}/125.0/mlfit.root WM -l ${lumi} ${other_options}" | bash
# ZE CR
echo "python postFitPlots.py vbfdm/mca-80X-electronCR.txt templates/ZECR/${selstep}/plots.root ${variable} templates/cards/${selstep}/${variable}/125.0/mlfit.root ZE -l ${lumi} ${other_options}" | bash
# WE CR
echo "python postFitPlots.py vbfdm/mca-80X-electronCR.txt templates/WECR/${selstep}/plots.root ${variable} templates/cards/${selstep}/${variable}/125.0/mlfit.root WE -l ${lumi} ${other_options}" | bash

