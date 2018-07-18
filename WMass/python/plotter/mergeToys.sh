#! /bin/bash  

# assume root files with trees are in folder toys/<name>/<charge>
# merge file will be created in toys/<name>/ and will have <charge> in its name

charge="plus"
outdir="toys/diffXsec_2018_06_29_group10_absGenEta_moreEtaPtBin_newGenXsec/"
toydir="${outdir}${charge}/"
outname="toys_${charge}.root"
sizemin="1000"
maxFilePerHadd=100

goodfiles_tmp=`ls -l ${toydir} | awk -v sizemin="$sizemin" '$5 > sizemin {print $9}' | grep root`
ngood=`ls -l ${toydir} | awk -v sizemin="$sizemin" '$5 > sizemin {print $9}' | grep root | wc -l`
echo "--------------------------------------------------------------"
echo "There are ${ngood} files to merge (size > ${sizemin} bytes)"
echo "--------------------------------------------------------------"

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