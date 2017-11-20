#!/usr/bin/python

import os
import sys

if len(sys.argv) != 2:
    print('Usage: %s [plyfilename]' % sys.argv[0])
    sys.exit(1)

path,fn = os.path.split(sys.argv[1])
bn,ext = os.path.splitext(fn)

assert ext == '.ply', 'Must specify .ply file'

f = open(sys.argv[1]).read().split('\n')
assert f[0] == 'ply', 'Not valid ply'
assert f[1] == 'format ascii 1.0', 'Not valid ply'

iHeader = 2
has = []
while iHeader < len(f):
    if f[iHeader].startswith('comment '):
        iHeader += 1
        continue
    if f[iHeader] == 'end_header':
        iHeader += 1
        break
    if f[iHeader].startswith('element vertex '):
        vc = int(f[iHeader].split(' ')[2])
    if f[iHeader].startswith('element face '):
        fc = int(f[iHeader].split(' ')[2])
    if f[iHeader].startswith('property '):
        has += [f[iHeader].split(' ')[-1]]
    iHeader += 1

assert 'x' in has and 'y' in has and 'z' in has, 'Could not find position'
assert 'nx' in has and 'ny' in has and 'nz' in has, 'Could not find normal'
assert 'red' in has and 'green' in has and 'blue' in has, 'Could not find color'
assert 'vertex_indices' in has, 'Could not find indices'

print('Vertex count: %d\nFace count: %d' % (vc,fc))

pos = []
norm = []
color = []

for iFace in range(fc):
    lf = map(int, f[iHeader + vc + iFace].split(' '))
    if lf[0] == 3:
        vi = lf[1:]
    if lf[0] == 4:
        vi = [lf[1],lf[2],lf[3],lf[1],lf[3],lf[4]]
    for iVert in vi:
        lv = map(float, f[iHeader + iVert].split(' '))
        pos   += [lv[0],lv[1],lv[2]]
        norm  += [lv[3],lv[4],lv[5]]
        color += [lv[6]/255.0,lv[7]/255.0,lv[8]/255.0,1.0]

assert len(pos)/3 == len(norm)/3
assert len(pos)/3 == len(color)/4
print('Count: %d' % (len(pos)/3))

pos = map(str,pos)
norm = map(str,norm)
color = map(str,color)

def write(f, arrayname, data, size):
    while data:
        size = min(size, len(data))
        dataset,data = data[:size],data[size:]
        f.write('%s.push(%s);\n' % (arrayname,','.join(dataset)))


f = open(os.path.join(path, '%s.js'%bn),'wt')
f.write('function generate_%s() {\n' % bn)
f.write('    var data = {pos:[],norm:[],color:[],length:0};\n');
write(f,'    data.pos', pos, 200*3)
write(f,'    data.norm', norm, 200*3)
write(f,'    data.color', color, 200*4)
f.write('    data.length = %d;\n' % (len(pos)/3));
f.write('    return dataToObject(data);\n');
f.write('}\n');