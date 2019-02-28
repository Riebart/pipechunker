# pipechunker

Accept content on stdin, split it into chunks of equal size, and process them with a command.

Designed for use with rclone for uploading a Windows Image of a system, but is versatile, and can be used with anything where you want to parallel process a stream with a command.

The pipeline I use for uploading Windows images is:

```bash
prima@MyMachine /mnt/e/WindowsImageBackup $ tar -cf - MyMachine/ |
  gpg --compress-algo none -er me@example.com | pv |
  python3 ~/Desktop/pipechunk.py
    --name "od:/WindowsImageBackup/MyMachine.2018-12-01/MyMachine-2018-12-01.tar.enc"
    --command '["rclone", "rcat", "--verbose", "--stats", "10s"]'
    --chunk-size 50000000
    --parallel 8
```

The above command (run in WSL, or really any Linux) will tar up the folder (including the VHDX files), encrypt (but not compress) with gpg, chunk them into 50-million byte pieces, handling 8 pieces at a time, and run `rclone rcat` on the chunks (which are all kept in memory, and just piped to stdin of the command that's spawned) to stuff them into OneDrive.

You can reassemble the parts without needing this script. On Linux:

```bash
rclone ls od:Path/to/files/ | sort -t ' ' -k2 | \
  while read size filename
  do
    rclone cat "od:Scratch/test/$filename"
  done | pv -l > combined.out
```

Note that this is not exactly speedy. You're limited to a single TCP connection to pull the files down (may not saturate much bandwidth, depending on your connection), and about 4-5s per file just in rclone negotiation overhead.
