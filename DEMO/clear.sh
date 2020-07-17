#! /bin/bash

function getdir()
{
    for element in `ls $1`
    do
        dir_or_file=$1"/"$element
        if [ -d $dir_or_file ]
        then
            getdir $dir_or_file
        else
            fsize=`cat $dir_or_file | wc -l`
            echo $dir_or_file":"$fsize
            if [ $fsize -lt 2000 ]
            then
                echo "remove it"
                rm -rf $dir_or_file
                count=$[$count + 1]
            fi
        fi
    done
}

count = 0
pwd="/home/zzr/langtong/DEMO/logs/"       #初始化目录

getdir $pwd
echo "remove $count"