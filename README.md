MyMachine# pipechunker

Accept content on stdin, split it into chunks of equal size, and process them with a command.

Designed for use with rclone for uploading a Windows Image of a system. The pipeline I use for that is:

```bash
prima@MyMachine /mnt/e/WindowsImageBackup $ tar -cf - MyMachine/ |
  gpg --compress-algo none -er me@example.com | pv |
  python3 ~/Desktop/pipechunk.py
    --name "od:/WindowsImageBackup/MyMachine.2018-12-01/MyMachine-2018-12-01.tar.enc"
    --command '["rclone", "rcat", "--verbose", "--stats", "10s"]'
    --chunk-size 50000000
    --parallel 8
```

The above command (run in WSL) will tar up the folder (including the VHDX files), encrypt (but not compress) with gpg, chunk them into 50-million byte pieces, handling 8 pieces at a time, and run `rclone rcat` on the chunks (which are all kept in member, and just piped to stdin of the command that's spawned) to stuff them in OneDrive.
