#!/usr/bin/env bash
while getopts i:o: option
do
 case "${option}"
 in
 i) INPUT=${OPTARG};;
 o) OUTPUT=${OPTARG};;
 esac
done
I=0;
DIR="$OUTPUT/$I";
mkdir -p $DIR;
#a=0
#for test in $(seq 1 10)
#do
#    if [ $a = 5 ]; then
#        echo "entra"
#        break
#    fi
#    a=$(( $a + 1))
#done
#echo $a
echo $DIR
TIF=$(find $INPUT -iname '*.tif')
#for image in $(seq 1 1 2001)
for image in $TIF
do
    if [ $(( $I % 1000)) = 0 ]; then

        if [ $I = 20000 ]; then
            break
        fi

        DIR="$OUTPUT/$I";
        echo $DIR
        mkdir -p $DIR;
    fi
    convert "$image"  "$DIR/$(basename "$image" .tif).jpg";
    I=$(($I+1))
done

