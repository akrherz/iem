It this causes your server to have kittens, it is your own fault.

Some IEM cluster details (so I can keep it straight!)

-[ ] one
-[x] two


#Shared Filesystems

    /mnt/gluster0 :: iem-dr{1,2} clustered replica meant for larger files
    /mnt/mesonet  :: primary /mesonet folder from iem21
    /mnt/mesonet2 :: secondary /mesonet folder from iemvm1

 Every system has a /mesonet base folder, with lots of sym links 

``` 
/mesonet
    /ARCHIVE
        /dailydata -> /mnt/longterm1/dailydata
        /data      -> /mnt/mesonet2/ARCHIVE/data
        /gempak    -> /mnt/longterm2/gempak
        /nexrad    -> /mnt/longterm1/nexrad3_iowa
        /raw       -> /mnt/mesonet2/ARCHIVE/raw
        /rer       -> /mnt/gluster0/rer
        /wunder    -> /mnt/mesonet2/ARCHIVE/wunder
    /data
        /agclimate -> /mnt/gluster0/data/
        /alerts    -> /mnt/mesonet2/data/
        /dm        -> /mnt/mesonet2/data/
        /dotcams   -> /mnt/mesonet2/data/
        /gempak    -> /mnt/mesonet2/data/
        /gis
            /images -> /mnt/gluster0/data/gis/
            /shape	-> /home/ldm/data/gis/
            /static is local to system
        /harry      -> /mnt/mesonet2/data/
        /iemre      -> /mnt/gluster0/data
        /incoming   -> /mnt/mesonet2/data
        /logs       -> /mnt/mesonet2/data
        /madis      -> /mnt/mesonet2/data
        /model      -> /mnt/mesonet2/data
        /nccf       -> /mnt/mesonet2/data
        /nexrad     -> /mnt/mesonet2/data
        /smos       -> /mnt/mesonet2/data
        /text       -> /mnt/mesonet2/data
    /share
        /cases    -> /mnt/gluster0/share/
        /climodat -> /mnt/mesonet2/share/ :: Regenerated daily
        /features -> /mnt/gluster0/share/
        /iemmaps  -> /mnt/gluster0/share/
        /lapses   -> /mnt/gluster0/share/
        /pickup   -> /mnt/mesonet2/share/ :: Temp files, more or less
        /pics     -> /mnt/gluster0/share/
        /present  -> /mnt/gluster0/share/
        /usage    -> /mnt/gluster0/share/
        /windrose -> /mnt/mesonet2/share/
    /TABLES
    /wepp -> /mnt/idep
    /www
        /apps
            /cocorahs
            /iemwebsite
            /nwnwebsite
            /roads
            /sustainablecorn -> sym link to /mnt/mesonet2/...
            /test.sustainablecorn.org -> sym link to /mnt/mesonet2/...
            /weather.im
            /weppwebsite
        /logs
```