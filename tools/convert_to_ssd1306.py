#!/usr/bin/env python3
import sys
import pygame


if __name__ == '__main__':
    ifname = sys.argv[1]
    ofname = sys.argv[2]

    image = pygame.image.load(ifname)
    buffer = bytearray((image.get_height() // 8) * image.get_width())
    i = 0
    for y in range(image.get_height() // 8):
        for x in range(image.get_width()):
            byte = 0
            for bit in range(8):
                pixel = image.get_at((x, y * 8 + bit))
                if pixel[0] != 255:
                    byte |= (1 << bit)
            buffer[i] = byte
            i += 1

    with open(ofname, 'wb') as f:
        f.write(buffer)

