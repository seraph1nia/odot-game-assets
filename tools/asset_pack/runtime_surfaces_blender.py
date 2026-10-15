"""Independent serialized glTF triangle/attribute audit (including zero-area faces).

Uses Blender's matrix algebra/KDTree, not the optimizer's transform code or the
Blender glTF importer. No triangle is dropped, area-thresholded or deduplicated.
"""
import json
from collections import defaultdict

from mathutils import Matrix, Quaternion, Vector
from mathutils.kdtree import KDTree

from tools.asset_catalog.runtime_glb import read, accessor


def triangles(path):
    doc,binary=read(path)
    result=defaultdict(list)
    # glTF world -> authored Blender world, independently of the importer.
    axes=Matrix(((1,0,0,0),(0,0,-1,0),(0,1,0,0),(0,0,0,1)))
    def visit(index,parent):
        node=doc['nodes'][index]
        if 'matrix' in node:
            local=Matrix([node['matrix'][i:i+4] for i in range(0,16,4)]).transposed()
        else:
            x,y,z,w=node.get('rotation',(0,0,0,1))
            local=Matrix.LocRotScale(Vector(node.get('translation',(0,0,0))),Quaternion((w,x,y,z)),Vector(node.get('scale',(1,1,1))))
        world=parent@local
        if 'mesh' in node:
            normals=world.to_3x3().inverted().transposed(); mirrored=world.to_3x3().determinant()<0
            for p in doc['meshes'][node['mesh']]['primitives']:
                attributes={k:accessor(doc,binary,v) for k,v in p['attributes'].items()}
                names=tuple(sorted(attributes)); corners=[]
                for i in range(len(attributes['POSITION'])):
                    values=[]
                    for name in names:
                        value=attributes[name][i]
                        if name=='POSITION': value=tuple(world@Vector(value))
                        elif name=='NORMAL':
                            assert abs(sum(v*v for v in value)-1)<.00002,'nonunit serialized normal'
                            value=tuple((normals@Vector(value)).normalized())
                        elif name=='TANGENT': value=(*tuple((world.to_3x3()@Vector(value[:3])).normalized()),value[3]*(-1 if mirrored else 1))
                        values.append(value)
                    corners.append(tuple(values))
                idx=[v[0] for v in accessor(doc,binary,p['indices'])]
                mat=doc['materials'][p['material']]
                key=(json.dumps({k:v for k,v in mat.items() if k!='name'},sort_keys=True),names)
                for i in range(0,len(idx),3):
                    indices=idx[i:i+3]
                    if mirrored: indices[1],indices[2]=indices[2],indices[1]
                    result[key].append(tuple(corners[j] for j in indices))
        for child in node.get('children',[]):visit(child,world)
    for root in doc['scenes'][doc.get('scene',0)]['nodes']:visit(root,axes)
    return result


def compare(before,after):
    assert set(before)==set(after), 'serialized material/vertex-layout ownership differs'
    maximum=0; count=0; exact_zero_before=0; exact_zero_after=0
    for key,left in before.items():
        right=after[key];assert len(left)==len(right),('serialized triangle multiplicity',key,len(left),len(right))
        names=key[1];pi=names.index('POSITION')
        def center(tri):return tuple(sum(c[pi][axis] for c in tri)/3 for axis in range(3))
        def zero(tri):
            a,b,c=(corner[pi] for corner in tri)
            ab=tuple(b[i]-a[i] for i in range(3));ac=tuple(c[i]-a[i] for i in range(3))
            return (ab[1]*ac[2]-ab[2]*ac[1],ab[2]*ac[0]-ab[0]*ac[2],ab[0]*ac[1]-ab[1]*ac[0])==(0,0,0)
        exact_zero_before+=sum(zero(t) for t in left);exact_zero_after+=sum(zero(t) for t in right)
        tree=KDTree(len(right))
        for i,tri in enumerate(right):tree.insert(center(tri),i)
        tree.balance();available=set(range(len(right)))
        for tri in left:
            found=None
            for _,index,_ in tree.find_range(center(tri),3e-5):
                if index not in available:continue
                candidate=right[index]
                for rotation in range(3):
                    error=0;valid=True
                    for corner in range(3):
                        for ai,name in enumerate(names):
                            a=tri[corner][ai];b=candidate[(corner+rotation)%3][ai]
                            e=max(abs(x-y) for x,y in zip(a,b,strict=True))
                            tolerance=.00002
                            if e>=tolerance:valid=False;break
                            error=max(error,e)
                        if not valid:break
                    if valid:found=(index,error);break
                if found is not None:break
            assert found is not None,('serialized transformed triangle/UV/normal mismatch',key,tri)
            available.remove(found[0]);maximum=max(maximum,found[1]);count+=1
        assert not available, 'unexpected serialized triangles'
    return {'serialized_triangle_count':count,'one_to_one_transformed_triangle_attributes_equal':True,
            'zero_area_triangles_not_filtered':True,'exact_zero_area_before':exact_zero_before,
            'exact_zero_area_after':exact_zero_after,'max_attribute_component_error':maximum}
