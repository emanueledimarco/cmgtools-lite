#! /bin/bash  

# assume root files with trees are in folder toydir
# merge file will be created in outdir and will have <charge> in its name

charge="comb_WchargeAsymmetry"
toydir="toys/diffXsec_el_2018_09_20_group10_legacySF/"
outdir="${toydir}${charge}/"
outname="toys_${charge}.root"
sizemin="1000"
maxFilePerHadd=100

goodfiles_tmp=`ls -l ${toydir} | grep root | awk -v sizemin="$sizemin" '$5 > sizemin {print $9}'`
ngood=`ls -l ${toydir} | grep root | awk -v sizemin="$sizemin" '$5 > sizemin {print $9}' | wc -l`
nTotFiles=`ls -l ${toydir} | grep root | wc -l`
echo "--------------------------------------------------------------"
echo "There are ${ngood}/${nTotFiles} files to merge (size > ${sizemin} bytes)"
echo "--------------------------------------------------------------"
echo "Output will be stored in ${outdir}"
mkdir -p ${outdir}

goodfiles=""
ifile=0
for file in ${goodfiles_tmp};
do
    tmpfile="${toydir}${file}"
    #echo "${tmpfile}"
    goodfiles="${goodfiles} ${tmpfile}"
    let ifile++
done


hadd -k -O -n ${maxFilePerHadd} ${outdir}${outname} ${goodfiles}

echo "--------------------------------------------------------------"
echo "THE END"
echo ""