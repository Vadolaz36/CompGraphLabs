import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

def sutherland_hodgman(subject, clip):
    def inside(p, a, b):
        return (b[0]-a[0])*(p[1]-a[1]) - (b[1]-a[1])*(p[0]-a[0]) >= 0

    def intersect(p1, p2, e1, e2):
        x1,y1 = p1; x2,y2 = p2
        x3,y3 = e1; x4,y4 = e2
        d = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
        if abs(d) < 1e-9:
            return None
        px = ((x1*y2-y1*x2)*(x3-x4)-(x1-x2)*(x3*y4-y3*x4))/d
        py = ((x1*y2-y1*x2)*(y3-y4)-(y1-y2)*(x3*y4-y3*x4))/d
        return (px,py)

    out = subject
    for i in range(len(clip)):
        inp = out
        out = []
        if not inp:
            break
        A = clip[i]
        B = clip[(i+1)%len(clip)]
        S = inp[-1]
        for E in inp:
            if inside(E,A,B):
                if not inside(S,A,B):
                    I = intersect(S,E,A,B)
                    if I: out.append(I)
                out.append(E)
            elif inside(S,A,B):
                I = intersect(S,E,A,B)
                if I: out.append(I)
            S = E
    return out

def bresenham(x0,y0,x1,y1):
    x0,y0,x1,y1 = map(int,map(round,(x0,y0,x1,y1)))
    dx,dy = abs(x1-x0),abs(y1-y0)
    sx,sy = (1,-1)[x0>x1],(1,-1)[y0>y1]
    err = dx-dy
    pts = []
    while True:
        pts.append((x0,y0))
        if x0==x1 and y0==y1:
            break
        e2 = 2*err
        if e2>-dy:
            err -= dy
            x0 += sx
        if e2<dx:
            err += dx
            y0 += sy
    return pts

def fill_scanline(poly,img,color):
    h,w,_ = img.shape
    ys = [p[1] for p in poly]
    y0,y1 = int(min(ys)),int(max(ys))
    for y in range(y0,y1+1):
        xs = []
        for i in range(len(poly)):
            x1,y1p = poly[i]
            x2,y2p = poly[(i+1)%len(poly)]
            if y1p==y2p:
                continue
            if y>=min(y1p,y2p) and y<max(y1p,y2p):
                x = x1 + (y-y1p)*(x2-x1)/(y2p-y1p)
                xs.append(x)
        xs.sort()
        for i in range(0,len(xs),2):
            if i+1<len(xs):
                x_start = int(np.ceil(xs[i]))
                x_end = int(np.floor(xs[i+1]))
                img[y,x_start:x_end+1] = color

def draw(img,poly,color):
    for i in range(len(poly)):
        for x,y in bresenham(*poly[i],*poly[(i+1)%len(poly)]):
            if 0<=x<img.shape[1] and 0<=y<img.shape[0]:
                img[y,x]=color

W,H = 800,500
img = np.ones((H,W,3),dtype=np.uint8)*255

subject = [
    (80,60),(240,40),(380,120),(340,230),
    (260,190),(200,320),(140,260),(60,180)
]

clip = [
    (220,100),(640,80),(720,220),(600,420),(260,380)
]

clipped = sutherland_hodgman(subject,clip)

fill_scanline(clipped,img,[220,60,60])
draw(img,subject,[0,0,0])
draw(img,clip,[0,180,0])
draw(img,clipped,[0,0,0])

Image.fromarray(img).save("результат.png")
plt.imshow(img)
plt.axis("off")
plt.show()
