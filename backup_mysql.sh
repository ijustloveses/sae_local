
dt=`date +%Y-%m-%d`

for tb in sae_loveses sae_mytips sae_marked;
do
    echo "mysqldump -uroot -p $tb > ${tb}_${dt}.sql";
    echo `mysqldump -uroot -p $tb > ${tb}_${dt}.sql`;
    echo "tar -czf ${tb}_${dt}.sql.tar.gz ${tb}_${dt}.sql"
    echo `tar -czf ${tb}_${dt}.sql.tar.gz ${tb}_${dt}.sql`
done
