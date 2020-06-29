#! /bin/bash
count = 0

function getdir()
{
    for element in `ls $1`
    do
        dir_or_file=$1"/"$element
        if [[ $element =~ "curriculum" ]]
        then
            echo $element
            count=$[$count + 1]
            rm -rf $dir_or_file
        else
           if [ -d $dir_or_file ]
            then
                getdir $dir_or_file
            fi
        fi
    done
}

pwd="/home/zzr/langtong/DEMO/logs/"       #初始化目录

getdir $pwd
echo "remove $count"