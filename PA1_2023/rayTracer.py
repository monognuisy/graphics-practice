#!/usr/bin/env python3
# -*- coding: utf-8 -*
# sample_python aims to allow seamless integration with lua.
# see examples below

import os
import sys
import pdb  # use pdb.set_trace() for debugging
# or use code.interact(local=dict(globals(), **locals()))  for debugging.
import code
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image
import scipy.linalg as sp
import math


class Color:
    def __init__(self, R, G, B):
        R = min(1, float(R))
        G = min(1, float(G))
        B = min(1, float(B))
        self.color = np.array([R, G, B]).astype(np.float)

    @classmethod
    def colorfromArray(clr, arr):
        return clr(*list(arr))

    def __mul__(self, others):
        return Color.colorfromArray(self.color * others)

    # Gamma corrects this color.
    # @param gamma the gamma value to use (2.2 is generally used).
    def gammaCorrect(self, gamma):
        inverseGamma = 1.0 / gamma
        self.color = np.power(self.color, inverseGamma)

    def toUINT8(self):
        return (np.clip(self.color, 0, 1)*255).astype(np.uint8)

def hadamard(c1: Color, c2: Color) -> Color:
    return Color.colorfromArray(c1.color * c2.color)

def colorSoftAdd(c1: Color, light: Color, weight: float) -> Color:
    return Color.colorfromArray(c1.color * weight + light.color * (1 - weight))

def colorHardAdd(c1: Color, light: Color, weight) -> Color:
    return Color.colorfromArray(c1.color + light.color * weight)

class Shader:
    def __init__(self, c):
        diffuseColor = c.findtext('diffuseColor')
        specularColor = c.findtext('specularColor')
        exponent = c.findtext('exponent')

        self.diffuseColor: Color = Color(*diffuseColor.split()) if diffuseColor else Color(.5,.5,.5)
        self.specularColor: Color = Color(*specularColor.split()) if specularColor else Color(1,1,1)
        self.exponent: float = float(exponent) if exponent else 50.0

        self.shaderType = c.get('type')
        self.shaderName = c.get('name')


class Ball:
    def __init__(self, c, shader):
        center = c.findtext('center')
        radius = c.findtext('radius')

        self.center = np.array(center.split()).astype(np.float) if center else np.array([0,0,0]).astype(np.float)
        self.radius: float = float(radius) if radius else 1.0

        self.shader: Shader = shader


def normalize(vec):
    return vec / np.linalg.norm(vec)

def checkIntersection(ball: Ball, d, viewPoint):
    p = viewPoint - ball.center

    det = (np.inner(d, p) ** 2) - np.inner(p, p) + (ball.radius ** 2)

    if (det < 0):
        return math.inf
    
    resA = -1 * np.inner(d, p) + (det ** 0.5)
    resB = -1 * np.inner(d, p) - (det ** 0.5)

    return resB if resB > 0 else resA if resA > 0 else math.inf 

def isIntersect(ball: Ball, d, start) -> bool:
    p = start - ball.center

    det = (np.inner(d, p) ** 2) - np.inner(p, p) + (ball.radius ** 2)

    if (det < 0):
        return False
    
    return True


def main():

    tree = ET.parse(sys.argv[1])
    root = tree.getroot()

    # how bright the light is.
    intensity = np.array([1, 1, 1]).astype(np.float)

    imgSize = np.array(root.findtext('image').split()).astype(np.int)

    # camera initialization
    for c in root.findall('camera'):
        viewPoint = c.findtext('viewPoint')
        viewDir = c.findtext('viewDir')
        viewUp = c.findtext('viewUp')
        viewWidth = c.findtext('viewWidth')
        viewHeight = c.findtext('viewHeight')
        projDistance = c.findtext('projDistance')

        viewPoint = np.array(viewPoint.split()).astype(np.float) if viewPoint else np.array([0, 0, 1]).astype(np.float)
        viewDir = np.array(viewDir.split()).astype(np.float) if viewDir else np.array([0, 0, -1]).astype(np.float)
        viewUp = np.array(viewUp.split()).astype(np.float) if viewUp else np.array([0, 1, 0]).astype(np.float)
        viewWidth = float(viewWidth) if viewWidth else 1.0
        viewHeight = float(viewHeight) if viewHeight else 1.0
        projDistance = float(projDistance) if projDistance else 1.0

        viewProjNormal = -1 * viewDir

        print('viewpoint', viewPoint)
        print('viewDir', viewDir)
        print('progDistance', projDistance)
        print('viewWidth', viewWidth)
        print('viewHeight', viewHeight)

    # image init
    imageZ = normalize(viewProjNormal)
    imageY = normalize(np.cross(viewProjNormal, viewUp))
    imageX = normalize(np.cross(imageY, imageZ))
    imageCenter = viewPoint - projDistance * imageZ
    imageOrigin = imageCenter - (viewWidth / 2) * imageX - (viewHeight / 2) * imageY
    pixelWidth = viewWidth / imgSize[0]
    pixelHeight = viewHeight / imgSize[1]

    print('imageX', imageX)
    print('imageY', imageY)
    print('imageZ', imageZ)
    print('imageOrigin', imageOrigin)

    # lights init
    for c in root.findall('light'):
        lightOrigin = c.findtext('position')
        lightColor = c.findtext('intensity')

        lightOrigin = np.array(lightOrigin.split()).astype(np.float) if lightOrigin else np.array([5,5,5]).astype(np.float)
        lightColor: Color = Color(*lightColor.split()) if lightColor else Color(1,1,1)

    # shaders init
    shaders = dict()
    for c in root.findall('shader'):
        shaders[c.get('name')] = Shader(c)

    # balls init
    balls: list[Ball] = []
    for c in root.findall('surface'):
        balls.append(Ball(c, shaders[c.find('shader').get('ref')]))

    # Create an empty image
    channels = 3
    img = np.zeros((imgSize[1], imgSize[0], channels), dtype=np.uint8)
    img[:, :] = 0


    for i in np.arange(imgSize[1]):
        for j in np.arange(imgSize[0]):
            imagePoint = imageOrigin + pixelWidth * (j + .5) * imageX + pixelHeight * (i + .5) * imageY
            d = normalize(imagePoint - viewPoint)

            # calculating minimum intersecting point
            intersections = []
            for index, ball in enumerate(balls):
                intersections.append((checkIntersection(ball, d, viewPoint), index))

            t, index = min(intersections)

            
            # rendering
            if (t >= math.inf):
                continue


            materialPoint = viewPoint + t * d
            whichBall: Ball = balls[index]

            pixelColor: Color = whichBall.shader.diffuseColor
            surfaceNormal = normalize(materialPoint - whichBall.center)
            
            l = normalize(lightOrigin - materialPoint)
                
            p = .5

            # add point light
            pixelColor = colorHardAdd(pixelColor, lightColor, 0.3) * (max(0, np.inner(l, surfaceNormal)) ** p)

            if (whichBall.shader.shaderType == 'Lambertian'):
                rayIntersect = False
                for ball in balls:
                    if rayIntersect:
                        break

                    if ball == whichBall: 
                        continue

                    if (checkIntersection(ball, l, materialPoint) < math.inf):
                        rayIntersect = True

                if rayIntersect:
                    pixelColor = Color(0,0,0)

            if (whichBall.shader.shaderType == 'Phong'):
                v = normalize(viewPoint - materialPoint)
                h = normalize(v + l)

                phongP = whichBall.shader.exponent

                pixelColor = colorHardAdd(pixelColor, lightColor * (max(0, np.inner(surfaceNormal, h))) ** phongP, 0.7) 

            img[imgSize[0] - j - 1][imgSize[1] - i - 1] = pixelColor.toUINT8()


    rawimg = Image.fromarray(img, 'RGB')
    rawimg.save(sys.argv[1]+'.png')


if __name__ == "__main__":
    main()
