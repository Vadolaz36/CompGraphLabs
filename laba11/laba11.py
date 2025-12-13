import numpy as np
import matplotlib.pyplot as plt

def tetra():
    v=np.array([[1,1,1],[1,-1,-1],[-1,1,-1],[-1,-1,1]],float)
    e=[(i,j) for i in range(4) for j in range(i+1,4)]
    return v,e

def octa():
    v=np.array([[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]],float)
    e=[]
    for i in range(6):
        for j in range(i+1,6):
            if np.allclose(v[i],-v[j]): continue
            e.append((i,j))
    return v,e

def Rx(a):
    c,s=np.cos(a),np.sin(a)
    return np.array([[1,0,0],[0,c,-s],[0,s,c]])

def Ry(a):
    c,s=np.cos(a),np.sin(a)
    return np.array([[c,0,s],[0,1,0],[-s,0,c]])

def Rz(a):
    c,s=np.cos(a),np.sin(a)
    return np.array([[c,-s,0],[s,c,0],[0,0,1]])

def normalize(v):
    return v/np.max(np.linalg.norm(v,axis=1))

def draw(v,e,title,R):
    v=normalize(v)
    p=(R@v.T).T
    fig,ax=plt.subplots(figsize=(4.2,4.2))
    for i,j in e:
        z=(p[i,2]+p[j,2])/2
        style='k-' if z>0 else 'k--'
        lw=1.8 if z>0 else 1.2
        ax.plot([p[i,0],p[j,0]],[p[i,1],p[j,1]],style,linewidth=lw)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(title)

R = Rz(np.deg2rad(30)) @ Ry(np.deg2rad(20)) @ Rx(np.deg2rad(10))

v,e=tetra()
draw(v,e,'Тетраэдр',R)

v,e=octa()
draw(v,e,'Октаэдр',R)

plt.show()
