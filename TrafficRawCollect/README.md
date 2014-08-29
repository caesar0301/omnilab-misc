This folder contains the files to capture network traffic of SEIEE, SJTU, from the border router.

They are:
* `nfm-addrules.sh`	To add rules to TCAM engine of NFM
* `worker[port].sh`	To start the capturing work at a specific port of NFE.
* `end_tcpdump.sh`	To end the capturing work.
* `mvdata.sh`		To compress and move the data from local host to shared NFS folder.
* `workschedule`	To describe the cron schedule of whole work flow.
* `README`	This file, to describe the usage of this foler.

For further explaination:
-------------------------

1. Add NFM rules.

Though all rules are removed before adding new ones, it's better to remove the 
rules manually before running the script:

    [nfmfolder]/bin/rules --deleteall -M
or

    [nfmfolder]/bin/rules -F

and restart NFM to clear TCAM cache:

    [nfmfolder]/bin/nfm-init.d restart

2. Capture traffic.

We use the tcpdump tool of NFM to dump raw network traffic with all payload. The parameters are:

    [nfmfolder]/bin/tcpdump -nnSs 0 -i nfe0.1.20 -G 30 -w "/home/front/trace_seiee_%Y%m%d-%H%M%S.pcap"

The rotating time period is 30 seconds, i.e., a new pcap file is created every 30 seconds.
If you want to change the file path following `-w`, please change the `worker*.sh` and `mvdata.sh` simultaniously.

3. Crontab work schedule.

We run the worker for one work-day hour every 7 days for a month.
You can add this work flow to system with command: `sudo crontab workschedule`
and remove all schedule to run `sudo crontab -r`

4. NFS shared folder.

The traffic data is stored in the NFS shared folder where you can mount it with command:

    mount -t nfs 10.50.4.13:/export/cxm_np [dir]

or other NFS IP address in the same segment, e.g., 10.50.8.13.

The data for each hour locates in: `[nfsfolder]/data.sjtu/passive-[year]/SEIEE/[timestamp_folder]/`

If you change the nfs mount folder, please also change the path in `mvdata.sh`.
