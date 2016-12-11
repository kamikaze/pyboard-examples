# pyboard-examples
Example code of simple PyBoard projects


## To generate 4bpp frame files from gif animation with ImageMagick:
```bash
convert -coalesce anim.gif -depth 4 -alpha off -colors 16 -compress NONE -colorspace Gray -resize 256 -crop 256x64+0+32 -trim +repage anim_%05d.gray
```

