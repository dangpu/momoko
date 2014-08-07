
out()
{
    exit
}

trap "out" 2

while true
do
    string1=`ifconfig $1 | grep "bytes" | awk '{printf $2}'`
    rx1=${string1##bytes:}
    string2=`ifconfig $1 | grep "bytes" | awk '{printf $6}'`
    tx1=${string2##bytes:}
    sleep 1
    clear
    string3=`ifconfig $1 | grep "bytes" | awk '{printf $2}'`
    rx2=${string3##bytes:}
    string4=`ifconfig $1 | grep "bytes" | awk '{printf $6}'`
    tx2=${string4##bytes:}
    temp=`expr $rx2 - $rx1`
    r1=`expr $temp / 1024`
    echo 下载速度:$r1 kb/s
    temp=`expr $tx2 - $tx1`
    r2=`expr $temp / 1024`
    echo 上传速度:$r2 kb/s
done
